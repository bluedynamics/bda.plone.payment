# -*- coding:utf-8 -*-
from plone.base.interfaces import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):
        """Do not show on Plone's list of installable profiles.
        """
        return []

    def getNonInstallableProducts(self):
        """Do not show on QuickInstaller's list of installable products.
        """
        return []
