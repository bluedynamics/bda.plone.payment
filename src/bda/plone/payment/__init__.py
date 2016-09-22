# -*- coding: utf-8 -*-
from bda.plone.payment.interfaces import IPayment
from bda.plone.payment.interfaces import IPaymentEvent
from bda.plone.payment.interfaces import IPaymentFailedEvent
from bda.plone.payment.interfaces import IPaymentSettings
from bda.plone.payment.interfaces import IPaymentSuccessEvent
from zope.component import adapter
from zope.component import getAdapter
from zope.component import getAdapters
from zope.event import notify
from zope.interface import implementer
from zope.interface import Interface


@implementer(IPaymentEvent)
class PaymentEvent(object):

    def __init__(self, context, request, payment, order_uid, data):
        self.context = context
        self.request = request
        self.payment = payment
        self.order_uid = order_uid
        self.data = data


@implementer(IPaymentSuccessEvent)
class PaymentSuccessEvent(PaymentEvent): pass


@implementer(IPaymentFailedEvent)
class PaymentFailedEvent(PaymentEvent): pass


class Payments(object):

    def __init__(self, context):
        self.context = context

    def get(self, name):
        return getAdapter(self.context, IPayment, name=name)

    @property
    def payments(self):
        adapters = getAdapters((self.context,), IPayment)
        return [_[1] for _ in adapters]

    @property
    def vocab(self):
        adapters = getAdapters((self.context,), IPayment)
        return [(_[0], _[1].label) for _ in adapters if _[1].available]

    @property
    def default(self):
        adapters = getAdapters((self.context,), IPayment)
        for name, payment in adapters:
            if payment.default:
                return name
        if adapters:
            return adapters[0][0]


@implementer(IPayment)
@adapter(Interface)
class Payment(object):
    pid = None
    label = None
    deferred = False

    def __init__(self, context):
        self.context = context

    @property
    def available(self):
        settings = IPaymentSettings(self.context)
        return self.pid in settings.available

    @property
    def default(self):
        settings = IPaymentSettings(self.context)
        return self.pid == settings.default

    def succeed(self, request, order_uid, data=dict()):
        evt = PaymentSuccessEvent(self.context, request, self, order_uid, data)
        notify(evt)

    def failed(self, request, order_uid, data=dict()):
        evt = PaymentFailedEvent(self.context, request, self, order_uid, data)
        notify(evt)

    def init_url(self, uid):
        raise NotImplementedError(u"Abstract ``Payment`` does not implement "
                                  u"``init_url``")
