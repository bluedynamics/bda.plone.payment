import urllib
import urllib2
import urlparse
import logging
from zope.i18nmessageid import MessageFactory
from Products.Five import BrowserView
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
    
    def data(order_uid):
        """Return dict in following format:
        
        {
            'amount': '1000',
            'currency': 'EUR',
            'description': 'description',
            'orderid': '12345',
        }
        """


class SixPayment(Payment):
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
                    orderid, successlink, faillink, backlink):
    params = {
        'ACCOUNTID': accountid,
        'spPassword': password,
        'AMOUNT': amount,
        'CURRENCY': currency,
        'DESCRIPTION': description,
        'ORDERID': orderid,
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
        raise SaferPayError(u"Pay Complete Failed")
    print res


class SaferPay(BrowserView):
    
    @property
    def payment_url(self):
        data = ISixPaymentData(self.context).data(self.request['uid'])
        accountid = ACCOUNTID
        password = PASSWORD
        amount = data['amount']
        currency = data['currency']
        description = data['description']
        orderid = data['orderid']
        base_url = self.context.absolute_url()
        successlink = '%s/@@six_payment_success' % base_url
        faillink = '%s/@@six_payment_failed' % base_url
        backlink = '%s/@@cart' % base_url
        return create_pay_init(accountid, password, amount, currency,
                               description, orderid, successlink, faillink,
                               backlink)


def shopmaster_mail(context):
    return 'foo@bar.baz' # XXX


class SaferPaySuccess(BrowserView):
    
    def verify(self):
        try:
            data = self.request.get('DATA', '')
            signature = self.request.get('SIGNATURE', '')
            res = verify_pay_confirm(data, signature)
            
            # XXX: res['ID'] and res['token'] -> what to do with?
            
            success = True # XXX: finish request
            
            payment = Payments(self.context).get('six_payment')
            if success:
                payment.succeed(self.request, order_uid)
                return True
            else:
                payment.failed(self.request, order_uid)
                return False
        except Exception, e:
            logger.error(u"Payment verification failed: %s" % str(e))
            return False
    
    @property
    def shopmaster_mail(self):
        return shopmaster_mail(self.context)


class SaferPayFailed(BrowserView):
    
    @property
    def shopmaster_mail(self):
        return shopmaster_mail(self.context)
