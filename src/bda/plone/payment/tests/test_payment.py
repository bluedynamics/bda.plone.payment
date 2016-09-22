# -*- coding: utf-8 -*-
from bda.plone.payment.tests import Payment_INTEGRATION_TESTING
from bda.plone.payment.tests import set_browserlayer

import unittest2 as unittest


class TestPayment(unittest.TestCase):
    layer = Payment_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        set_browserlayer(self.request)

    def test_foo(self):
        self.assertEquals(1, 1)
