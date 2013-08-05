import logging
from Acquisition import aq_inner
from zope.component import getMultiAdapter
from zope.i18nmessageid import MessageFactory
from Products.Five import BrowserView
from bda.plone.orders.common import get_order
from bda.plone.payment import (
    Payment,
    Payments,
)

from ..six_payment import ISixPaymentData

from bda.plone.shop.interfaces import IShopSettings
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

#from ZTUtils import make_query

_ = MessageFactory('bda.plone.payment')
logger = logging.getLogger('bda.plone.payment')

CREATE_PAY_INIT_URL = "https://sat1.dibspayment.com/dibspaymentwindow/entrypoint"
#CREATE_PAY_INIT_URL = "https://payment.architrade.com/paymentweb/start.action2"

class Dibs(Payment):
    pid = 'dibs'
    label = _('dibs', 'Kortbetaling')
    available = True
    default = False

    def init_url(self, uid):
        return '%s/@@dibs?uid=%s' % (self.context.absolute_url(), uid)


class DoDibs(BrowserView):
    """ Assembles an url to dibs.
        Need to check how to use 
        make_query() 
    """
    def __call__(self, **kw):
        order_uid = self.request['uid']
        #registry = getUtility(IRegistry)
        #settings = registry.forInterface(IShopSettings)

        #get language
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        #current_language = portal_state.language()
        current_language = "nb_NO"
        dibs_url = CREATE_PAY_INIT_URL
        uid = self.request['uid']
        
        data = ISixPaymentData(self.context).data(order_uid)        
        payment = Payments(self.context).get('dibs')
        payment.succeed(self.request, uid)
        
        amount = data['amount']
        currency = data['currency']
        description = data['description']
        ordernumber = data['ordernumber']
        
        parameters = {
            'amount':           amount,
            'currency':         currency,
            'merchant':         4255617,
            'language':         current_language,
            'acceptReturnUrl':  self.context.absolute_url() + '/dibsed?uid=' + order_uid,
            'cancelreturnurl':  self.context.absolute_url() + '/dibs_payment_aborted',
            'orderId':          ordernumber,
            'test':             1,
        }

        
        #assembles final url
        param = []
        for k, v in parameters.items():
            param.append("%s=%s" % (k, v))
        
        param = "&".join(param)
        
        #need to change this to make_query() instead
        self.request.response.redirect("%s?%s" % (dibs_url, param))
        


class DibsFinished(BrowserView):

    def id(self):
        uid = self.request.get('uid', None)
        try:
            order = get_order(self.context, uid)
        except ValueError:
            return None
        return order.attrs.get('ordernumber')
