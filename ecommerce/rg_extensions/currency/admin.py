from django.contrib import admin

from ecommerce.rg_extensions.currency.models import Currency


class CurrencyInline(admin.StackedInline):
    model = Currency
    can_delete = False