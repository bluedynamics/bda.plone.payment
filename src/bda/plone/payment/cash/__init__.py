from zope.i18nmessageid import MessageFactory
from Products.Five import BrowserView
# TODO: fix dependency on bda.plone.orders.
# this invalidates the dependency chain.
from bda.plone.orders.common import get_order
from bda.plone.payment import Payment
from bda.plone.payment import Payments


_ = MessageFactory('bda.plone.payment')


class Cash(Payment):
    pid = 'cash'
    label = _('cash', 'Cash')
    available = True
    default = False

    def init_url(self, uid):
        return '%s/@@cash?uid=%s' % (self.context.absolute_url(), uid)


class DoCash(BrowserView):

    def __call__(self, **kw):
        uid = self.request['uid']
        payment = Payments(self.context).get('cash')
        payment.succeed(self.request, uid)
        url = '%s/@@cashed?uid=%s' % (self.context.absolute_url(), uid)
        self.request.response.redirect(url)


class CashFinished(BrowserView):

    def id(self):
        uid = self.request.get('uid', None)
        try:
            order = get_order(self.context, uid)
        except ValueError:
            return None
        return order.attrs.get('ordernumber')
