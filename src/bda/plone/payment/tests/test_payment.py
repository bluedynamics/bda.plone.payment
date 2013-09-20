import unittest2 as unittest
from bda.plone.payment.tests import (
    Payment_INTEGRATION_TESTING,
    set_browserlayer,
)


class TestPayment(unittest.TestCase):
    layer = Payment_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        set_browserlayer(self.request)

    def test_foo(self):
        self.assertEquals(1, 1)
