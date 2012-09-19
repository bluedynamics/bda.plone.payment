from zope.interface import (
    Interface,
    Attribute,
)


class IPaymentExtensionLayer(Interface):
    """Browser layer for bda.plone.payment.
    """


class IPaymentEvent(Interface):
    """Payment related event
    """
    context = Attribute(u"Context in which this event was triggered.")
    
    request = Attribute(u"Current request.")
    
    payment = Attribute(u"Payment instance.")
    

class IPaymentSuccessEvent(IPaymentEvent):
    """This event gets triggered when payment was successful.
    """
    

class IPaymentFailedEvent(IPaymentEvent):
    """This event gets triggered when payment failed.
    """


class IPayment(Interface):
    """Single payment.
    """
    label = Attribute(u"Payment label")
    
    available = Attribute(u"Flag whether payment is available in recent "
                          u"payment cycle")
    
    default = Attribute(u"Flag whether this payment is default payment.")
    
    deferred = Attribute(u"Flag whether checkout notification shoud be "
                         u"deferred. Needed by 3rd party payment systems to "
                         u"defer mail notification.")
    
    init_url = Attribute(u"Payment initialization URL.")
    
    def succeed(request):
        """Notify ``IPaymentSuccessEvent``.
        """
    
    def failed(request):
        """Notify ``IPaymentFailedEvent``.
        """
