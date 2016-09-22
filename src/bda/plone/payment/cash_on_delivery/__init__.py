# -*- coding: utf-8 -*-
# TODO: fix dependency on bda.plone.orders.
# this invalidates the dependency chain.
from bda.plone.orders.common import get_order
from bda.plone.payment import Payment
from bda.plone.payment import Payments
from Products.Five import BrowserView
from zope.i18nmessageid import MessageFactory
from zope.interface import Attribute
from zope.interface import Interface


_ = MessageFactory('bda.plone.payment')


class ICashOnDeliverySettings(Interface):

    currency = Attribute(u"Currency of cash on delivery")

    costs = Attribute(u"Costs of cash on delivery as decimal in gross")


class CashOnDelivery(Payment):
    pid = 'cash_on_delivery'

    @property
    def label(self):
        settings = ICashOnDeliverySettings(self.context)
        return _('cash_on_delivery',
                 default=u'Cash on delivery. An extra fee of ${costs} '
                         u'${currency} will be charged on order delivery',
                 mapping={
                     'costs': settings.costs,
                     'currency': settings.currency
                 })

    def init_url(self, uid):
        return '%s/@@cash_on_delivery?uid=%s' % (self.context.absolute_url(), uid)


class DoCashOnDelivery(BrowserView):

    def __call__(self, **kw):
        uid = self.request['uid']
        payment = Payments(self.context).get('cash')
        payment.succeed(self.request, uid)
        url = '%s/@@cash_on_delivery_done?uid=%s' % (
            self.context.absolute_url(), uid)
        self.request.response.redirect(url)


class CashOnDeliveryFinished(BrowserView):

    def id(self):
        uid = self.request.get('uid', None)
        try:
            order = get_order(self.context, uid)
        except ValueError:
            return None
        return order.attrs.get('ordernumber')
