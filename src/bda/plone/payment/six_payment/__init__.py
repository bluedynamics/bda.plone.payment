# -*- coding: utf-8 -*-
from .. import Payment
from .. import Payments
from ..interfaces import IPaymentData
from lxml import etree
from plone import api
from Products.Five import BrowserView
from zExceptions import Redirect
from zope.i18nmessageid import MessageFactory

import logging
import six.moves.urllib.parse
import six.moves.urllib.request


logger = logging.getLogger("bda.plone.payment")
_ = MessageFactory("bda.plone.payment")


ACCOUNTID = "99867-94913159"
PASSWORD = "XAjc3Kna"
VTCONFIG = ""
CREATE_PAY_INIT_URL = "https://www.saferpay.com/hosting/CreatePayInit.asp"
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


def perform_request(url, params=None):
    if params:
        query = six.moves.urllib.parse.urlencode(params)
        url = "%s?%s" % (url, query)
    stream = six.moves.urllib.request.urlopen(url)
    res = stream.read()
    stream.close()
    return res


def create_pay_init(
    accountid,
    password,
    vtconfig,
    amount,
    currency,
    description,
    ordernumber,
    successlink,
    faillink,
    backlink,
):
    params = {
        "ACCOUNTID": accountid,
        "spPassword": password,
        "VTCONFIG": vtconfig,
        "AMOUNT": amount,
        "CURRENCY": currency,
        "DESCRIPTION": description,
        "ORDERID": ordernumber,
        "SUCCESSLINK": successlink,
        "FAILLINK": faillink,
        "BACKLINK": backlink,
        "SHOWLANGUAGES": "yes",
    }
    return perform_request(CREATE_PAY_INIT_URL, params)


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
            accountid = ACCOUNTID
            password = PASSWORD
            vtconfig = VTCONFIG
            amount = data["amount"]
            currency = data["currency"]
            description = data["description"]
            ordernumber = data["ordernumber"]
            successlink = "%s/@@six_payment_success" % base_url
            faillink = "%s/@@six_payment_failed?uid=%s" % (base_url, order_uid)
            backlink = "%s/@@six_payment_aborted?uid=%s" % (base_url, order_uid)
            redirect_url = create_pay_init(
                accountid,
                password,
                vtconfig,
                amount,
                currency,
                description,
                ordernumber,
                successlink,
                faillink,
                backlink,
            )
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
