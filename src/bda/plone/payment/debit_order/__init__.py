# -*- coding: utf-8 -*-
from bda.plone.orders.common import get_order
from bda.plone.payment import Payment
from bda.plone.payment import Payments
from Products.Five import BrowserView
from zope.i18nmessageid import MessageFactory


_ = MessageFactory("bda.plone.payment")


class DebitOrder(Payment):
    pid = "debit_order"
    label = _("debit_order", default=u"Debit Order")

    def init_url(self, uid):
        return "%s/@@debit_order?uid=%s" % (self.context.absolute_url(), uid)


class DoDebitOrder(BrowserView):
    def __call__(self, **kw):
        uid = self.request["uid"]
        payment = Payments(self.context).get("debit_order")
        payment.succeed(self.request, uid)
        url = "%s/@@debit_ordered?uid=%s" % (self.context.absolute_url(), uid)
        self.request.response.redirect(url)


class DebitOrderFinished(BrowserView):
    def id(self):
        uid = self.request.get("uid", None)
        try:
            order = get_order(self.context, uid)
        except ValueError:
            return None
        return order.attrs.get("ordernumber")
