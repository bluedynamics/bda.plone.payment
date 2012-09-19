from zope.i18nmessageid import MessageFactory
from Products.Five import BrowserView
from bda.plone.payment import (
    Payment,
    Payments,
)


_ = MessageFactory('bda.plone.payment')


class Invoice(Payment):
    label = _('invoice', 'Invoice')
    available = True
    default = False
    deferred = False
    
    @property
    def init_url(self):
        return '%s/@@invoice' % self.context.absolute_url()


class InvoiceFinished(BrowserView):
    
    def finalize(self):
        payment = Payments(self.context).get('invoice')
        payment.succeed(self.request)
