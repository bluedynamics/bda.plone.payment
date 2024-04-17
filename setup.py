# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

import os


version = "2.0.dev0"
shortdesc = "Payment"
longdesc = open(os.path.join(os.path.dirname(__file__), "README.rst")).read()
longdesc += open(os.path.join(os.path.dirname(__file__), "CHANGES.rst")).read()
longdesc += open(os.path.join(os.path.dirname(__file__), "LICENSE.rst")).read()


setup(
    name="bda.plone.payment",
    version=version,
    description=shortdesc,
    long_description=longdesc,
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: Addon",
        "Framework :: Zope",
        "Framework :: Zope :: 5",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    author="BlueDynamics Alliance",
    author_email="dev@bluedynamics.com",
    license="GNU General Public Licence",
    packages=find_packages("src"),
    package_dir={"": "src"},
    namespace_packages=["bda", "bda.plone"],
    include_package_data=True,
    zip_safe=False,
    install_requires=["setuptools", "Products.CMFPlone", "requests"],
    extras_require={"test": ["plone.app.testing"]},
)
