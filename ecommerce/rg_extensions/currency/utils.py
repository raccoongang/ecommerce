""" utility methods for currency """
from django.conf import settings
from threadlocals.threadlocals import get_current_request


def get_currency(site=None):
    """
    Get currency for current site
    
    Returns the currency value from the site configuration if it exists,
    else it returns the value from the settings.
    """
    if not site:
        site = get_current_request().site
        
    if hasattr(site.siteconfiguration, 'currency'):
        return site.siteconfiguration.currency.name
    
    return settings.OSCAR_DEFAULT_CURRENCY
