"""Payment processor constants."""


from django.utils.translation import ugettext_lazy as _

CARD_TYPES = {
    'american_express': {
        'display_name': _('American Express'),
        'cybersource_code': '003',
        'apple_pay_network': 'amex',
        'stripe_brand': 'American Express',
    },
    'discover': {
        'display_name': _('Discover'),
        'cybersource_code': '004',
        'apple_pay_network': 'discover',
        'stripe_brand': 'Discover',
    },
    'mastercard': {
        'display_name': _('MasterCard'),
        'cybersource_code': '002',
        'apple_pay_network': 'mastercard',
        'stripe_brand': 'MasterCard',
    },
    'visa': {
        'display_name': _('Visa'),
        'cybersource_code': '001',
        'apple_pay_network': 'visa',
        'stripe_brand': 'Visa',
    },
}

CARD_TYPE_CHOICES = ((key, value['display_name']) for key, value in CARD_TYPES.items())

# In Python 3.5 dicts aren't ordered so having this unsorted causes new migrations to happen on almost every
# run of makemigrations. Sorting fixes that. This can be removed in Python 3.6+.
CARD_TYPE_CHOICES = sorted(CARD_TYPE_CHOICES, key=lambda tup: tup[0])

CYBERSOURCE_CARD_TYPE_MAP = {
    value['cybersource_code']: key for key, value in CARD_TYPES.items() if 'cybersource_code' in value
}

CLIENT_SIDE_CHECKOUT_FLAG_NAME = 'enable_client_side_checkout'

# Paypal only supports 4 languages, which are prioritized by country.
# https://developer.paypal.com/docs/classic/api/locale_codes/
PAYPAL_LOCALES = {
    'zh': 'CN',
    'fr': 'FR',
    'en': 'US',
    'es': 'MX',
}

APPLE_PAY_CYBERSOURCE_CARD_TYPE_MAP = {
    value['apple_pay_network']: value['cybersource_code'] for value in CARD_TYPES.values() if
    'cybersource_code' in value
}

STRIPE_CARD_TYPE_MAP = {
    value['stripe_brand']: key for key, value in CARD_TYPES.items() if 'stripe_brand' in value
}
