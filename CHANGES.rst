
Changelog
=========

0.7.dev0
--------

- Plone 5 update


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
