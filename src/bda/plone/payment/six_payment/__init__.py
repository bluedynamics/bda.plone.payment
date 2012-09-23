import urllib
import urllib2
import urlparse
import logging
from lxml import etree
from zExceptions import Redirect
from zope.i18nmessageid import MessageFactory
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from ..interfaces import IPaymentData
from .. import (
    Payment,
    Payments,
)


logger = logging.getLogger('bda.plone.payment')
_ = MessageFactory('bda.plone.payment')


ACCOUNTID = "99867-94913159"
PASSWORD = "XAjc3Kna"
CREATE_PAY_INIT_URL = "https://www.saferpay.com/hosting/CreatePayInit.asp"
VERIFY_PAY_CONFIRM_URL = "https://www.saferpay.com/hosting/VerifyPayConfirm.asp"
PAY_COMPLETE_URL = "https://www.saferpay.com/hosting/PayCompleteV2.asp"


class ISixPaymentData(IPaymentData):
    """Data adapter interface for SIX payment.
    """
    
    def uid_for(ordernumber):
        """Return order_uid for ordernumber.
        """
    
    def data(order_uid):
        """Return dict in following format:
        
        {
            'amount': '1000',
            'currency': 'EUR',
            'description': 'description',
            'ordernumber': '1234567890',
        }
        """


class SixPayment(Payment):
    pid = 'six_payment'
    label = _('six_payment', 'Six Payment')
    available = True
    default = True
    
    def init_url(self, uid):
        return '%s/@@six_payment?uid=%s' % (self.context.absolute_url(), uid)


class SaferPayError(Exception):
    """Raised if SIX payment return an error.
    """


def perform_request(url, params=None):
    if params:
        query = urllib.urlencode(params)
        url = '%s?%s' % (url, query)
    stream = urllib2.urlopen(url)
    res = stream.read()
    stream.close()
    return res


def create_pay_init(accountid, password, amount, currency, description,
                    ordernumber, successlink, faillink, backlink):
    params = {
        'ACCOUNTID': accountid,
        'spPassword': password,
        'AMOUNT': amount,
        'CURRENCY': currency,
        'DESCRIPTION': description,
        'ORDERID': ordernumber,
        'SUCCESSLINK': successlink,
        'FAILLINK': faillink,
        'BACKLINK': backlink,
        'SHOWLANGUAGES': 'yes',
    }
    return perform_request(CREATE_PAY_INIT_URL, params)


def verify_pay_confirm(data, signature):
    params = {
        'DATA': data,
        'SIGNATURE': signature,
    }
    res = perform_request(VERIFY_PAY_CONFIRM_URL, params)
    if res[:2] != 'OK':
        raise SaferPayError(u"Payment Verification Failed: '%s'" % res[7:]) 
    return urlparse.parse_qs(res[3:])


def pay_complete(accountid, password, id):
    params = {
        'ACCOUNTID': accountid,
        'spPassword': password,
        'ID': id,
    }
    res = perform_request(PAY_COMPLETE_URL, params)
    if res[:2] != 'OK':
        raise SaferPayError(u"Pay Complete Failed: '%s'" % res[7:])
    return True


class SaferPay(BrowserView):
    
    def __call__(self):
        base_url = self.context.absolute_url()
        order_uid = self.request['uid']
        try:
            data = ISixPaymentData(self.context).data(order_uid)
            accountid = ACCOUNTID
            password = PASSWORD
            amount = data['amount']
            currency = data['currency']
            description = data['description']
            ordernumber = data['ordernumber']
            successlink = '%s/@@six_payment_success' % base_url
            faillink = '%s/@@six_payment_failed?uid=%s' \
                % (base_url, order_uid)
            backlink = '%s/@@six_payment_aborted?uid=%s' \
                % (base_url, order_uid)
            redirect_url = create_pay_init(accountid, password, amount,
                                           currency, description, ordernumber,
                                           successlink, faillink, backlink)
        except Exception, e:
            logger.error(u"Could not initialize payment: '%s'" % str(e))
            redirect_url = '%s/@@six_payment_failed?uid=%s' \
                % (base_url, order_uid)
        raise Redirect(redirect_url)


def shopmaster_mail(context):
    props = getToolByName(context, 'portal_properties')
    return props.site_properties.email_from_address


class SaferPaySuccess(BrowserView):
    
    def verify(self):
        try:
            data = self.request.get('DATA', '')
            signature = self.request.get('SIGNATURE', '')
            res = verify_pay_confirm(data, signature)
            tid = res['ID'][0]
            accountid = ACCOUNTID
            password = PASSWORD
            success = False
            try:
                success = pay_complete(accountid, password, tid)
            except Exception, e:
                logger.error(u"Payment completion failed: '%s'" % str(e))
            data = etree.fromstring(data)
            ordernumber = data.get('ORDERID')
            order_uid = ISixPaymentData(self.context).uid_for(ordernumber)
            payment = Payments(self.context).get('six_payment')
            evt_data = {'tid': tid}
            if success:
                payment.succeed(self.request, order_uid, evt_data)
                return True
            else:
                payment.failed(self.request, order_uid, evt_data)
                return False
        except Exception, e:
            logger.error(u"Payment verification failed: '%s'" % str(e))
            return False
    
    @property
    def shopmaster_mail(self):
        return shopmaster_mail(self.context)


class SaferPayFailed(BrowserView):
    
    def finalize(self):
        payment = Payments(self.context).get('six_payment')
        payment.failed(self.request, self.request['uid'], {'tid': 'none'})
    
    @property
    def shopmaster_mail(self):
        return shopmaster_mail(self.context)
