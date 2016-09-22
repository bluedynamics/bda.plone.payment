# -*- coding: utf-8 -*-
from zope.i18nmessageid import MessageFactory
from Products.Five import BrowserView
from bda.plone.orders.common import get_order
from bda.plone.payment import Payment
from bda.plone.payment import Payments


_ = MessageFactory('bda.plone.payment')


class Invoice(Payment):
    pid = 'invoice'
    label = _('invoice', default=u'Invoice')

    def init_url(self, uid):
        return '%s/@@invoice?uid=%s' % (self.context.absolute_url(), uid)


class DoInvoice(BrowserView):

    def __call__(self, **kw):
        uid = self.request['uid']
        payment = Payments(self.context).get('invoice')
        payment.succeed(self.request, uid)
        url = '%s/@@invoiced?uid=%s' % (self.context.absolute_url(), uid)
        self.request.response.redirect(url)


class InvoiceFinished(BrowserView):

    def id(self):
        uid = self.request.get('uid', None)
        try:
            order = get_order(self.context, uid)
        except ValueError:
            return None
        return order.attrs.get('ordernumber')
