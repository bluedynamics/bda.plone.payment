=================
bda.plone.payment
=================

Payment processors for ``bda.plone.shop``.


Installation
============

This package is part of the ``bda.plone.shop`` stack. Please refer to
``https://github.com/bluedynamics/bda.plone.shop`` for installation
instructions.


Available Processors
====================

Following payment processors are available


Cash
----

Useful when selling stuff which gets paid on-site.

All Data is sent via email.

Administrators exports orders or teller staff marks orders billed instantly
in backend.


Cash in advance
---------------

All Data is sent via email.

Administrators send an invoice by e-mail.

Administrators need to mark the order as billed manually after they received
the payment.


Cash on delivery
----------------

All Data is sent via email.

Administrators send an invoice by e-mail.

Administrators need to mark the order as billed manually after sending with
service providing cash on delivery.


Debit Order
-----------

Useful when customers are well known and permission to perform debit orders
is granted.

All Data is sent via email.

Administrators take action and mark orders salaried.


Invoice
-------

All Data is sent via email.

Administrators send an invoice by e-mail.

Administrators need to mark the order as billed manually after they received
the payment.


SIX-Payment
-----------

Redirect payment using ``https://www.saferpay.com``.

Order is marked automatically salaried if payment succeed.

Administrator needs to take action if payment failed.

**TODO**: move six payment processor to ``bda.plone.sixpayment``


Addon Payment processors
========================

Following addon payment processors are known:

* https://github.com/intk/bda.plone.ogonepayment
* https://github.com/intk/bda.plone.molliepayment
* https://github.com/intk/bda.plone.easyidealpayment
* https://github.com/espenmn/bda.plone.klarnainvoice
* https://github.com/espenmn/bda.plone.klarnapayment
* https://github.com/espenmn/bda.plone.dibspayment

If you have implemented another payment processors or know other
implementations than the listed one, please let us know.


Providing a payment processor
=============================

XXX


Customize existing payment processors
=====================================

To de-activate a payment processor unconfigure it using `z3c.unconfigure`_::

    <include package="z3c.unconfigure" file="meta.zcml"/>
    <include package="bda.plone.payment"/>
    <unconfigure>
      <adapter
        name="six_payment"
        factory="bda.plone.payment.six_payment.SixPayment" />
    </unconfigure>

.. _`z3c.unconfigure`: https://pypi.python.org/pypi/z3c.unconfigure


Create translations
===================

::
    $ cd src/bda/plone/payment/
    $ ./i18n.sh


Contributors
============

- Robert Niederreiter (Author)
- Harald Frießnegger
- Peter Holzer
