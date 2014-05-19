from zope.i18nmessageid import MessageFactory
from Products.Five import BrowserView
# TODO: fix dependency on bda.plone.orders.
# this invalidates the dependency chain.
from bda.plone.orders.common import get_order
from bda.plone.payment import Payment
from bda.plone.payment import Payments


_ = MessageFactory('bda.plone.payment')


class CashInAdvance(Payment):
    pid = 'cash_in_advance'
    label = _('cash_in_advance', default=u'Cash in advance')

    def init_url(self, uid):
        return '%s/@@cash_in_advance?uid=%s' % (self.context.absolute_url(), uid)


class DoCashInAdvance(BrowserView):

    def __call__(self, **kw):
        uid = self.request['uid']
        payment = Payments(self.context).get('cash')
        payment.succeed(self.request, uid)
        url = '%s/@@cash_in_advance_done?uid=%s' % (
            self.context.absolute_url(), uid)
        self.request.response.redirect(url)


class CashInAdvanceFinished(BrowserView):

    def id(self):
        uid = self.request.get('uid', None)
        try:
            order = get_order(self.context, uid)
        except ValueError:
            return None
        return order.attrs.get('ordernumber')
