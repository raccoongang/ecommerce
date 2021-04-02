""" utility methods for currency """
from django.conf import settings
from threadlocals.threadlocals import get_current_request


def get_currency(site=None):
    """
    Get currency for site
    
    Returns the currency name from the site configuration if it exists,
    else it returns the value from the settings.OSCAR_DEFAULT_CURRENCY.
    
    Arguments:
        site (Site): The site for which we get the currency.

    Returns:
        str: String value of currency name (ex.: 'USD', 'GBR', 'EUR' etc.).
    """
    if not site:
        site = get_current_request().site
        
    if hasattr(site.siteconfiguration, 'currency'):
        return site.siteconfiguration.currency.name
    
    return settings.OSCAR_DEFAULT_CURRENCY
