from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from ecommerce.core.models import SiteConfiguration


class Currency(models.Model):

    name = models.CharField(
        verbose_name=_('Currency'),
        help_text=_('Currency code on the site (for example, USD, GBR, UAH etc.). Default {currency}').format(
            currency=settings.OSCAR_DEFAULT_CURRENCY
        ),
        max_length=3,
        blank=True
    )
    site_configuration = models.OneToOneField(SiteConfiguration, on_delete=models.CASCADE, primary_key=True)
