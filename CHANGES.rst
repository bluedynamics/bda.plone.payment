
Changelog
=========

2.0.dev0 (unreleased)
---------------------

- Turn hard depenency indirection on bda.plone.shop into soft dependency with failover.
  [jensens]

- Avoid circular import (testing only).
  [jensens]

- Python 2/3 compatibility
  [agitator]

- Update version and classifiers - 2.x targets Plone 5.1/5.2 without Archetypes
  [agitator]


1.0a1 (unreleased)
------------------

- Replace unittest2 by unittest
  [llisa123]

- Rename invoice payment related views to avoid conflicts with bda.plone.orders
  invoice view.
  [rnix]

- Fix shop admin email address lookup in sic payment.
  [rnix]

- Fix: Provide plone.protect authenticator token in invoice payment process
  [jensens]

- Plone 5 update
  [rnix, agitator]


0.5
---

- Add ``bda.plone.payment.cash_on_delivery.ICashOnDeliverySettings``.
  [rnix]

- Add "Cash on delivery" payment.
  [rnix]

- Add "Cash in advance" payment.
  [rnix]


0.4
---

- Remove ``available`` and ``default`` attributes from
  ``bda.plone.payment.cash.Cash``,
  ``bda.plone.payment.debit_order.DebitOrder``,
  ``bda.plone.payment.invoice.Invoice`` and
  ``bda.plone.payment.six_payment.SixPayment`` since they are provided by base
  class now. **Note** - Remove class patches for ``availability`` and
  ``default`` settings from your integration packages and and use controlpanel
  settings in ``bda.plone.shop``.
  [rnix]

- Add missing ``pid`` attribute to ``bda.plone.payment.Payment``.
  [rnix]

- Implement ``available`` and ``default`` properties on
  ``bda.plone.payment.Payment`` using settings from
  ``bda.plone.payment.interfaces.IPaymentSettings``.
  [rnix]

- Introduce ``bda.plone.payment.interfaces.IPaymentSettings``.
  [rnix]


0.3
---

- Remove ``bda.plone.payment.six_payment.ISixPaymentData`` interface. Use
  ``bda.plone.payment.interfaces.IPaymentData`` instead.
  [rnix]


0.2
---

- show "emails sent" status message when displaying the
  "thanks for your order" page of the invoce payment processor.
  in addition, show the order id
  [fRiSi]

- fix lookup for default IPayment adapter in case no default adapter
  is registered
  [fRiSi]


0.1
---

- initial work
  [rnix]
