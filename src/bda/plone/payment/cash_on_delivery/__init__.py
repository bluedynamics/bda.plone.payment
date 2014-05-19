from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.interface import Attribute
from Products.Five import BrowserView
# TODO: fix dependency on bda.plone.orders.
# this invalidates the dependency chain.
from bda.plone.orders.common import get_order
from bda.plone.payment import Payment
from bda.plone.payment import Payments


_ = MessageFactory('bda.plone.payment')


class ICashOnDeliverySettings(Interface):
    costs = Attribute(u"Costs of cash on delivery as decimal in gross")


class CashOnDelivery(Payment):
    pid = 'cash_on_delivery'

    @property
    def label(self):
        return _('cash_on_delivery',
                 default=u'Cash on delivery. An extra fee of ${costs} will be '
                         u'charged on order delivery',
                 mapping={
                     'costs': ICashOnDeliverySettings(self.context).costs
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
