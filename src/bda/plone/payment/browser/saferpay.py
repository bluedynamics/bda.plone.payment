import urllib
import urllib2
from Products.Five import BrowserView


ACCOUNTID = "99867-94913159"
PASSWORD = "XAjc3Kna"

CREATE_PAY_INIT_URL = "https://www.saferpay.com/hosting/CreatePayInit.asp"
VERIFY_PAY_CONFIRM_URL = "https://www.saferpay.com/hosting/VerifyPayConfirm.asp"
PAY_COMPLETE_URL = "https://www.saferpay.com/hosting/PayCompleteV2.asp"


class SaferPayError(Exception):
    pass


def perform_request(url, params=None):
    if params:
        query = urllib.urlencode(params)
        url = '%s?%s' % (url, query)
    return urllib2.urlopen(url)


def success_link(context):
    """Payment success link.
    """
    return '%s/@@saferpay_success' % context.absolute_url()


def verify_pay_confirm(data, signature):
    params = {
        'DATA': data,
        'SIGNATURE': sugnature,
    }
    res = perform_request(VERIFY_PAY_CONFIRM_URL, params)
    if res[:2] != 'OK':
        raise SaferPayError(u"Verification Failed") 
    print res


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
    pass