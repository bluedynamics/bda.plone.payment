from zope.interface import (
    implementer,
    Interface,
)
from zope.component import (
    adapter,
    getAdapter,
    getAdapters,
)
from zope.i18nmessageid import MessageFactory
from .interfaces import IPayment

_ = MessageFactory('bda.plone.payment')


class Payments(object):
    
    def __init__(self, context):
        self.context = context
    
    def get(self, name):
        return getAdapter((self.context,), IPayment, name=name)
    
    @property
    def payments(self):
        adapters = getAdapters((self.context,), IPayment)
        return [_[1] for _ in adapters]
    
    @property
    def vocab(self):
        adapters = getAdapters((self.context,), IPayment)
        return [_[0] for _[1].label in adapters]
    
    @property
    def default(self):
        adapters = getAdapters((self.context,), IPayment)
        for name, payment in getAdapters((self.context,), IPayment):
            if payment.default:
                return name
        if adapters:
            return adapters[0][0]


@implementer(IPayment)
@adapter(Interface)
class Payment(object):
    label = None
    available = False
    default = False
    
    def __init__(self, context):
        self.context = context


class Invoice(Payment):
    label = _('invoice', 'Invoice')
    available = True
    default = False


class CreditCard(Payment):
    label = _('credit_card', 'Credit card')
    available = True
    default = True