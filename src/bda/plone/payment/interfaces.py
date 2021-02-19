# -*- coding: utf-8 -*-
from zope.interface import Attribute
from zope.interface import Interface


class IPaymentExtensionLayer(Interface):
    """Browser layer for bda.plone.payment.
    """


class IPaymentEvent(Interface):
    """Payment related event.
    """

    context = Attribute(u"Context in which this event was triggered.")

    request = Attribute(u"Current request.")

    payment = Attribute(u"Payment instance.")

    order_uid = Attribute(u"Referring order uid.")

    data = Attribute(u"Optional data as dict")


class IPaymentSuccessEvent(IPaymentEvent):
    """This event gets triggered when payment was successful.
    """


class IPaymentFailedEvent(IPaymentEvent):
    """This event gets triggered when payment failed.
    """


class IPaymentSettings(Interface):
    """Payment availability and default settings.
    """

    available = Attribute(u"List of available payment method ids")

    default = Attribute(u"Default payment method")


class IPayment(Interface):
    """Single payment.
    """

    pid = Attribute(
        u"Unique payment id. Payment adapter is also registered " u"under this name."
    )

    label = Attribute(u"Payment label")

    clear_session = Attribute(
        u"Clear cart immediately on checkout success. Defaults to True. "
        u"May be set to False in redirect payments. If so, cart session "
        u"clearance must be handled in payment success and failed event handlers."
    )

    available = Attribute(
        u"Flag whether payment is available in recent " u"payment cycle"
    )

    default = Attribute(u"Flag whether this payment is default payment.")

    def init_url(uid):
        """Return payment initialization URL.
        """

    def succeed(request, order_uid, data=dict()):
        """Notify ``IPaymentSuccessEvent``.
        """

    def failed(request, order_uid, data=dict()):
        """Notify ``IPaymentFailedEvent``.
        """


class IPaymentData(Interface):
    """Interface for providing data required by payment.
    """

    def uid_for(ordernumber):
        """Return order_uid for ordernumber.
        """

    def annotations(ordernumber):
        """Dict like object for annotating payment related data.
        """

    def data(order_uid):
        """Return dict containing payment related order data like:

        {
            'amount': '1000',
            'currency': 'EUR',
            'description': 'description',
            'ordernumber': '1234567890',
        }
        """
