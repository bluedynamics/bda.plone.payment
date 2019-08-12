# -*- coding: utf-8 -*-
from .. import Payment
from .. import Payments
from ..interfaces import IPaymentData
from plone import api
from Products.Five import BrowserView
from zExceptions import Redirect
from zope.i18nmessageid import MessageFactory
import base64
import json
import logging
import requests
import uuid


logger = logging.getLogger("bda.plone.payment")
_ = MessageFactory("bda.plone.payment")


###############################################################################
# Account settings
USERNAME = ''
PASSWORD = ''
CUSTOMER_ID = ''
TERMINAL_ID = ''
TESTING = False
# End account settings
###############################################################################


class SaferPayError(Exception):
    """Raised if SIX payment return an error.
    """


class SaferPay(object):
    spec_version = '1.12'

    @property
    def testing(self):
        return TESTING

    @property
    def username(self):
        return USERNAME

    @property
    def password(self):
        return PASSWORD

    @property
    def customer_id(self):
        return CUSTOMER_ID

    @property
    def treminal_id(self):
        return TERMINAL_ID

    @property
    def base_url(self):
        if self.testing:
            return 'https://test.saferpay.com/api'
        return 'https://www.saferpay.com/api'

    @property
    def initialize_url(self):
        return '{}/Payment/v1/PaymentPage/Initialize'.format(self.base_url)

    @property
    def assert_url(self):
        return '{}/Payment/v1/PaymentPage/Assert'.format(self.base_url)

    @property
    def capture_url(self):
        return '{}/Payment/v1/Transaction/Capture'.format(self.base_url)

    @property
    def cancel_url(self):
        return '{}/Payment/v1/Transaction/Cancel'.format(self.base_url)

    @property
    def credentials(self):
        username = self.username
        password = self.password
        if not isinstance(username, bytes):
            username = username.encode('utf-8')
        if not isinstance(password, bytes):
            password = password.encode('utf-8')
        credentials = username + b':' + password
        return base64.b64encode(credentials)

    def request(self, url, data):
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'application/json',
            'Authorization': 'Basic {}'.format(self.credentials)
        }
        request_id = str(uuid.uuid4())
        data['RequestHeader'] = {
            'SpecVersion': self.spec_version,
            'CustomerId': self.customer_id,
            'RequestId': request_id,
            'RetryIndicator': 0
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        # XXX: check status code
        # 200 OK (No error)
        # 400 Validation error
        # 401 Authentication of the request failed
        # 402 Requested action failed
        # 403 Access denied
        # 406 Not acceptable (wrong accept header)
        # 415 Unsupported media type (wrong content-type header)
        # 500 Internal error
        # XXX: check response content type
        # if application/json, an error message is present
        rdata = response.json()
        header = rdata['ResponseHeader']
        if header['RequestId'] != request_id:
            msg = u'Unknown response: {} != {}'.format(
                header['RequestId'],
                request_id
            )
            raise SaferPayError(msg)
        # XXX: check status code instead of error in data
        if 'ErrorName' in rdata:
            msg = u'Error in response: {} {}'.format(
                rdata['ErrorName'],
                rdata['ErrorMessage']
            )
            raise SaferPayError(msg)
        return rdata

    def initialize(
        self,
        amount,
        currency,
        order_id,
        payment_description,
        success_link,
        fail_link
    ):
        data = {
            'TerminalId': self.terminal_id,
            'Payment': {
                'Amount': {
                    'Value': amount,
                    'CurrencyCode': currency
                },
                'OrderId': order_id,
                'Description': payment_description
            },
            'ReturnUrls': {
                'Success': success_link,
                'Fail': fail_link
            }
        }
        return self.request(self.initialize_url, data)

    def assert_(self, token):
        data = {
            'Token': token
        }
        return self.request(self.assert_url, data)

    def capture(self, tid):
        data = {
            'TransactionReference': {
                'TransactionId': tid
            }
        }
        return self.request(self.capture_url, data)

    def cancel(self, tid):
        data = {
            'TransactionReference': {
                'TransactionId': tid
            }
        }
        return self.request(self.cancel_url, data)


class SixPayment(Payment):
    pid = "six_payment"
    label = _("six_payment", "Six Payment")

    def init_url(self, uid):
        return "{}/@@saferpay_initialize?uid={}".format(
            self.context.absolute_url(),
            uid
        )


class SaferPayInitialize(BrowserView):

    def __call__(self):
        base_url = self.context.absolute_url()
        order_uid = self.request["uid"]
        try:
            p_data = IPaymentData(self.context)
            data = p_data.data(order_uid)
            ordernumber = data['ordernumber']
            response = SaferPay().initialize(
                data["amount"],
                data["currency"],
                data["ordernumber"],
                data["description"],
                '{}/@@saferpay_assert?uid='.format(base_url, order_uid),
                '{}/@@saferpay_failed?uid={}'.format(base_url, order_uid)
            )
            annotations = p_data.annotations(ordernumber)
            annotations['saferpay_token'] = response['Token']
            redirect_url = response['RedirectUrl']
        except Exception as e:
            logger.error(u"Could not initialize payment: '%s'" % str(e))
            redirect_url = "%s/@@saferpay_failed?uid=%s" % (base_url, order_uid)
        raise Redirect(redirect_url)


class SaferPayAssert(BrowserView):

    def __call__(self):
        """
        {
          "ResponseHeader": {
            "SpecVersion": "1.10",
            "RequestId": "[your request id]"
          },
          "Transaction": {
            "Type": "PAYMENT",
            "Status": "AUTHORIZED",
            "Id": "723n4MAjMdhjSAhAKEUdA8jtl9jb",
            "Date": "2015-01-30T12:45:22.258+01:00",
            "Amount": {
              "Value": "100",
              "CurrencyCode": "CHF"
            },
            "AcquirerName": "Saferpay Test Card",
            "AcquirerReference": "000000",
            "SixTransactionReference": "0:0:3:723n4MAjMdhjSAhAKEUdA8jtl9jb",
            "ApprovalCode": "012345"
          },
          "PaymentMeans": {
            "Brand": {
              "PaymentMethod": "VISA",
              "Name": "VISA Saferpay Test"
            },
            "DisplayText": "9123 45xx xxxx 1234",
            "Card": {
              "MaskedNumber": "912345xxxxxx1234",
              "ExpYear": 2015,
              "ExpMonth": 9,
              "HolderName": "Max Mustermann",
              "CountryCode": "CH"
            }
          },
          "Liability": {
            "LiabilityShift": true,
            "LiableEntity": "ThreeDs",
            "ThreeDs": {
              "Authenticated": true,
              "LiabilityShift": true,
              "Xid": "ARkvCgk5Y1t/BDFFXkUPGX9DUgs=",
              "VerificationValue": "AAABBIIFmAAAAAAAAAAAAAAAAAA="
            },
            "FraudFree": {
              "Id": "deab90a0458bdc9d9946f5ed1b36f6e8",
              "LiabilityShift": false,
              "Score": 0.6,
              "InvestigationPoints": [
                "susp_bill_ad",
                "susp_machine"
              ]
            }
          }
        }
        """
        import pdb;pdb.set_trace()
        base_url = self.context.absolute_url()
        order_uid = self.request["uid"]
        try:
            p_data = IPaymentData(self.context)
            data = p_data.data(order_uid)
            ordernumber = data['ordernumber']
            annotations = p_data.annotations(ordernumber)
            token = annotations['saferpay_token']
            sp = SaferPay()
            response = sp.assert_(token)
            transaction = response['Transaction']
            status = transaction['Status']
            tid = transaction['Id']
            ordernumber = response['OrderId']
            if status == 'PENDING':
                # currently only paydirect
                msg = 'Paydirect not supported yet'
                raise NotImplementedError(msg)
            elif status == 'AUTHORIZED':
                captured_response = sp.capture(tid)
                c_status = captured_response['Staus']
                if c_status == 'PENDING':
                    msg = 'Paydirect not supported yet'
                    raise NotImplementedError(msg)
                elif c_status == 'CAPTURED':
                    capture_id = captured_response['CaptureId']
                else:
                    msg = 'Unknown capture status: {}'.format(c_status)
                    raise SaferPayError(msg)
            elif status == 'CAPTURED':
                capture_id = transaction['CaptureId']
            else:
                msg = 'Unknown transaction status: {}'.format(status)
                raise SaferPayError(msg)
            redirect_url = '{}/@@saferpay_success?uid='.format(base_url, order_uid),
            redirect_url = '{}/@@saferpay_failed?uid={}'.format(base_url, order_uid)
        except Exception as e:
            logger.error(u"Could not initialize payment: '%s'" % str(e))
            redirect_url = "%s/@@saferpay_failed?uid=%s" % (base_url, order_uid)
        raise Redirect(redirect_url)


def shopmaster_mail(context):
    # XXX this is a soft dependency indirection on bda.plone.shop
    name = "bda.plone.shop.interfaces.IShopSettings.admin_email"
    shopsettings = api.portal.get_registry_record(name=name, default=None)
    if shopsettings is not None:
        return shopsettings.admin_email
    logger.warning("No shop master email was set.")
    return "(no shopmaster email set)"


class SaferPaySuccess(BrowserView):

    def finalize(self):
        base_url = self.context.absolute_url()
        order_uid = self.request["uid"]
        try:
            p_data = IPaymentData(self.context)
            data = p_data.data(order_uid)
            ordernumber = data['ordernumber']
            payment = Payments(self.context).get("six_payment")
            evt_data = {"tid": tid}
            payment.succeed(self.request, order_uid, evt_data)
        except Exception:
            logger.exception("Payment verification failed.")
        return False

    @property
    def shopmaster_mail(self):
        return shopmaster_mail(self.context)


class SaferPayFailed(BrowserView):

    def finalize(self):
        payment = Payments(self.context).get("six_payment")
        payment.failed(self.request, self.request["uid"], {"tid": "none"})

    @property
    def shopmaster_mail(self):
        return shopmaster_mail(self.context)
