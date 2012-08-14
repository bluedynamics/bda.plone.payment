from zope.interface import (
    Interface,
    Attribute,
)


class IPaymentExtensionLayer(Interface):
    """Browser layer for bda.plone.payment.
    """


class IPayment(Interface):
    """Single payment.
    """
    
    label = Attribute(u"Payment label")
    
    available = Attribute(u"Flag whether payment is available in recent "
                          u"payment cycle")
    
    default = Attribute(u"Flag whether this payment is default payment.")