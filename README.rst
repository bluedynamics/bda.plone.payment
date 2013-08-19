=================
bda.plone.payment
=================


Available Processors
====================

This package registers different payment processors:


Invoice
-------

All Data is sent via email.

Administrators send an invoice by e-mail.

Administrators need to mark the order as billed manually after they received the
payment.


Cash
-------

All Data is sent via email.
An e-mail with the order is sent.


Debit Order
-----------

All Data is sent via email.
An e-mail with the order is sent.



SIX-Payment
-----------

Uses https://www.saferpay.com


DIBS-Payment
-------------

Uses http://www.dibspayment.com
( http://www.dibs.dk http://www.dibs.no http://www.dibs.se )


Customization
=============

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

- Robert Niederreiter, Author

- Harald Frießnegger, Webmeisterei GmbH
