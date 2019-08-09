# -*- coding: utf-8 -*-
from .. import Payment
from .. import Payments
from ..interfaces import IPaymentData
from lxml import etree
from plone import api
from Products.Five import BrowserView
from zExceptions import Redirect
from zope.i18nmessageid import MessageFactory
import base64
import json
import logging
import requests
import six.moves.urllib.parse
import six.moves.urllib.request
import uuid


logger = logging.getLogger("bda.plone.payment")
_ = MessageFactory("bda.plone.payment")


###############################################################################
# Account settings
USERNAME = ''
PASSWORD = ''
CUSTOMER_ID = ''
TERMINAL_ID = ''
DCC = False
# End account settings
###############################################################################

SPEC_VERSION = '1.10'

# BASE_URL = 'https://www.saferpay.com/api'
BASE_URL = 'https://test.saferpay.com/api'
PAYMENT_PAGE_INITIALIZE_URL = "{}/Payment/v1/PaymentPage/Initialize".format(BASE_URL)

VERIFY_PAY_CONFIRM_URL = "https://www.saferpay.com/hosting/VerifyPayConfirm.asp"
PAY_COMPLETE_URL = "https://www.saferpay.com/hosting/PayCompleteV2.asp"


class SixPayment(Payment):
    pid = "six_payment"
    label = _("six_payment", "Six Payment")

    def init_url(self, uid):
        return "%s/@@six_payment?uid=%s" % (self.context.absolute_url(), uid)


class SaferPayError(Exception):
    """Raised if SIX payment return an error.
    """


def payment_page_initialize(
    username,
    password,
    customer_id,
    request_id,
    retry_indicator,
    terminal_id,
    amount,
    currency,
    order_id,
    payment_description,
    success_link,
    fail_link
):
    if not isinstance(username, bytes):
        username = username.encode('utf-8')
    if not isinstance(password, bytes):
        password = password.encode('utf-8')
    credentials = username + b':' + password
    encoded_credentials = base64.b64encode(credentials)
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'application/json',
        'Authorization': 'Basic {}'.format(encoded_credentials)
    }
    data = {
        'RequestHeader': {
            'SpecVersion': SPEC_VERSION,
            'CustomerId': customer_id,
            'RequestId': request_id,
            'RetryIndicator': retry_indicator
        },
        'TerminalId': terminal_id,
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
    res = requests.post(
        PAYMENT_PAGE_INITIALIZE_URL,
        headers=headers,
        data=json.dumps(data)
    )
    return res.json()


def perform_request(url, params=None):
    if params:
        query = six.moves.urllib.parse.urlencode(params)
        url = "%s?%s" % (url, query)
    stream = six.moves.urllib.request.urlopen(url)
    res = stream.read()
    stream.close()
    return res


def verify_pay_confirm(data, signature):
    params = {"DATA": data, "SIGNATURE": signature}
    res = perform_request(VERIFY_PAY_CONFIRM_URL, params)
    if res[:2] != "OK":
        raise SaferPayError(u"Payment Verification Failed: '%s'" % res[7:])
    return six.moves.urllib.parse.parse_qs(res[3:])


def pay_complete(accountid, password, id):
    params = {"ACCOUNTID": accountid, "spPassword": password, "ID": id}
    res = perform_request(PAY_COMPLETE_URL, params)
    if res[:2] != "OK":
        raise SaferPayError(u"Pay Complete Failed: '%s'" % res[7:])
    return True


class SaferPay(BrowserView):
    def __call__(self):
        base_url = self.context.absolute_url()
        order_uid = self.request["uid"]
        try:
            data = IPaymentData(self.context).data(order_uid)
            request_id = str(uuid.uuid4())
            retry_indicator = 0
            response = payment_page_initialize(
                USERNAME,
                PASSWORD,
                CUSTOMER_ID,
                request_id,
                retry_indicator,
                TERMINAL_ID,
                data["amount"],
                data["currency"],
                data["ordernumber"],
                data["description"],
                '{}/@@six_payment_success'.format(base_url),
                '{}/@@six_payment_failed?uid={}'.format(base_url, order_uid)
            )
            header = response['ResponseHeader']
            if header['RequestId'] != request_id:
                msg = u'Unknown response: {} != {}'.format(
                    header['RequestId'],
                    request_id
                )
                raise SaferPayError(msg)
            if 'ErrorName' in response:
                msg = u'Error in response: {} {}'.format(
                    response['ErrorName'],
                    response['ErrorMessage']
                )
                raise SaferPayError(msg)
            # XXX: store token on order?
            # token = response['Token']
            redirect_url = response['RedirectUrl']
        except Exception as e:
            logger.error(u"Could not initialize payment: '%s'" % str(e))
            redirect_url = "%s/@@six_payment_failed?uid=%s" % (base_url, order_uid)
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
    def verify(self):
        try:
            data = self.request.get("DATA", "")
            signature = self.request.get("SIGNATURE", "")
            res = verify_pay_confirm(data, signature)
            tid = res["ID"][0]
            accountid = ACCOUNTID
            password = PASSWORD
            success = False
            try:
                success = pay_complete(accountid, password, tid)
            except Exception:
                logger.exception("Payment completion failed.")
            data = etree.fromstring(data)
            ordernumber = data.get("ORDERID")
            order_uid = IPaymentData(self.context).uid_for(ordernumber)
            payment = Payments(self.context).get("six_payment")
            evt_data = {"tid": tid}
            if success:
                payment.succeed(self.request, order_uid, evt_data)
                return True
            payment.failed(self.request, order_uid, evt_data)
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
