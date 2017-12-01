# -*- coding: utf-8 -*-
from bda.plone.orders.common import get_order
from bda.plone.payment import Payment
from bda.plone.payment import Payments
from plone.protect.authenticator import createToken
from Products.Five import BrowserView
from zope.i18nmessageid import MessageFactory


_ = MessageFactory('bda.plone.payment')


class Invoice(Payment):
    pid = 'invoice'
    label = _('invoice', default=u'Invoice')

    def init_url(self, uid):
        return '{url}/@@pay_invoice?uid={uid}&_authenticator={token}'.format(
            url=self.context.absolute_url(),
            uid=uid,
            token=createToken()
        )


class DoInvoice(BrowserView):

    def __call__(self, **kw):
        uid = self.request['uid']
        payment = Payments(self.context).get('invoice')
        payment.succeed(self.request, uid)
        url = '{url}/@@pay_invoice_done?uid={uid}&_authenticator={token}'.format(
            url=self.context.absolute_url(),
            uid=uid,
            token=createToken()
        )
        self.request.response.redirect(url)


class InvoiceFinished(BrowserView):

    def id(self):
        uid = self.request.get('uid', None)
        try:
            order = get_order(self.context, uid)
        except ValueError:
            return None
        return order.attrs.get('ordernumber')
