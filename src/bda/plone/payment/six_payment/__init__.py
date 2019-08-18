# -*- coding: utf-8 -*-
from .. import Payment
from .. import Payments
from ..interfaces import IPaymentData
from plone import api
from plone.keyring.interfaces import IKeyManager
from plone.protect.authenticator import createToken
from plone.protect.utils import getRoot
from plone.protect.utils import getRootKeyManager
from Products.Five import BrowserView
from zExceptions import Redirect
from zope.component import ComponentLookupError
from zope.component import getUtility
from zope.i18nmessageid import MessageFactory
import base64
import json
import logging
import requests
import transaction
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
    def terminal_id(self):
        return TERMINAL_ID

    @property
    def base_url(self):
        if self.testing:
            return 'https://test.saferpay.com/api/Payment/v1'
        return 'https://www.saferpay.com/api/Payment/v1'

    @property
    def initialize_url(self):
        return '{}/PaymentPage/Initialize'.format(self.base_url)

    @property
    def assert_url(self):
        return '{}/PaymentPage/Assert'.format(self.base_url)

    @property
    def capture_url(self):
        return '{}/Transaction/Capture'.format(self.base_url)

    @property
    def cancel_url(self):
        return '{}/Transaction/Cancel'.format(self.base_url)

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
        """Response status codes:
            200 - OK (No error)
            400 - Validation error
            401 - Authentication of the request failed
            402 - Requested action failed
            403 - Access denied
            406 - Not acceptable (wrong accept header)
            415 - Unsupported media type (wrong content-type header)
            500 - Internal error

        If response content type 'application/json', an error message is
        present.
        """
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
        if response.status_code != 200:
            if response.headers['Content-Type'].find('application/json') == -1:
                msg = 'An error occurred: {}'.format(response.status_code)
                raise SaferPayError(msg)
            rdata = response.json()
            msg = u'Error in response: {} {}'.format(
                rdata['ErrorName'],
                rdata['ErrorMessage']
            )
            raise SaferPayError(msg)
        rdata = response.json()
        header = rdata['ResponseHeader']
        if header['RequestId'] != request_id:
            msg = u'Unknown response: {} != {}'.format(
                header['RequestId'],
                request_id
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


class URLMixin(object):

    def payment_link(self, base_url, view_name, order_uid):
        try:
            key_manager = getUtility(IKeyManager)
        except ComponentLookupError:
            key_manager = getRootKeyManager(getRoot(self.context))
        authenticator = createToken(manager=key_manager)
        return '{}/@@{}?uid={}&_authenticator={}'.format(
            base_url,
            view_name,
            order_uid,
            authenticator
        )


class SixPayment(Payment, URLMixin):
    pid = "six_payment"
    label = _("six_payment", "Six Payment")

    def init_url(self, uid):
        return self.payment_link(
            self.context.absolute_url(),
            'saferpay_initialize',
            uid
        )


class SaferPayBaseView(BrowserView, URLMixin):

    @property
    def shopmaster_mail(self):
        # This is a soft dependency indirection on bda.plone.shop
        name = "bda.plone.shop.interfaces.IShopSettings.admin_email"
        email = api.portal.get_registry_record(name=name, default=None)
        if email is not None:
            return email
        logger.warning("No shop master email was set.")
        return "(no shopmaster email set)"


class SaferPayInitialize(SaferPayBaseView):

    def __call__(self):
        base_url = self.context.absolute_url()
        order_uid = self.request['uid']
        success_link = self.payment_link(base_url, 'saferpay_assert', order_uid)
        fail_link = self.payment_link(base_url, 'saferpay_failed', order_uid)
        try:
            p_data = IPaymentData(self.context)
            data = p_data.data(order_uid)
            ordernumber = data['ordernumber']
            sp = SaferPay()
            response = sp.initialize(
                data["amount"],
                data["currency"],
                data["ordernumber"],
                data["description"],
                success_link,
                fail_link
            )
            annotations = p_data.annotations(ordernumber)
            annotations['saferpay_token'] = response['Token']
            redirect_url = response['RedirectUrl']
            transaction.commit()
        except Exception as e:
            logger.error("Cannot initialize payment: '{}'".format(e))
            redirect_url = fail_link
        raise Redirect(redirect_url)


class SaferPayAssert(SaferPayBaseView):

    def __call__(self):
        base_url = self.context.absolute_url()
        order_uid = self.request['uid']
        success_link = self.payment_link(base_url, 'saferpay_success', order_uid)
        fail_link = self.payment_link(base_url, 'saferpay_failed', order_uid)
        try:
            p_data = IPaymentData(self.context)
            data = p_data.data(order_uid)
            ordernumber = data['ordernumber']
            annotations = p_data.annotations(ordernumber)
            token = annotations['saferpay_token']
            sp = SaferPay()
            response = sp.assert_(token)
            ta = response['Transaction']
            status = ta['Status']
            tid = ta['Id']
            annotations['saferpay_transaction_id'] = tid
            ordernumber = ta['OrderId']
            if status == 'PENDING':
                # Currently only paydirect
                msg = 'Paydirect not supported yet'
                raise NotImplementedError(msg)
            elif status == 'AUTHORIZED':
                captured_response = sp.capture(tid)
                c_status = captured_response['Status']
                if c_status == 'PENDING':
                    # Currently only paydirect
                    msg = 'Paydirect not supported yet'
                    raise NotImplementedError(msg)
                elif c_status == 'CAPTURED':
                    capture_id = captured_response['CaptureId']
                    annotations['saferpay_capture_id'] = capture_id
                else:
                    msg = 'Unknown capture status: {}'.format(c_status)
                    raise SaferPayError(msg)
            elif status == 'CAPTURED':
                capture_id = ta['CaptureId']
                annotations['saferpay_capture_id'] = capture_id
            else:
                msg = 'Unknown transaction status: {}'.format(status)
                raise SaferPayError(msg)
            redirect_url = success_link
            transaction.commit()
        except Exception as e:
            logger.error("Cannot finalize payment: '{}'".format(e))
            redirect_url = fail_link
        raise Redirect(redirect_url)


class SaferPaySuccess(SaferPayBaseView):

    def finalize(self):
        order_uid = self.request['uid']
        p_data = IPaymentData(self.context)
        data = p_data.data(order_uid)
        ordernumber = data['ordernumber']
        annotations = p_data.annotations(ordernumber)
        tid = annotations['saferpay_transaction_id']
        evt_data = {'tid': tid}
        payment = Payments(self.context).get('six_payment')
        payment.succeed(self.request, order_uid, evt_data)


class SaferPayFailed(SaferPayBaseView):

    def finalize(self):
        payment = Payments(self.context).get('six_payment')
        payment.failed(self.request, self.request['uid'], {'tid': 'none'})
