bda.plone.payment
=================


Create translations
-------------------

::

    cd src/bda/plone/payment/
    
    i18ndude rebuild-pot --pot locales/bda.plone.payment.pot \
        --merge locales/manual.pot --create bda.plone.payment .
    
    i18ndude sync --pot locales/bda.plone.payment.pot \
        locales/de/LC_MESSAGES/bda.plone.payment.po
