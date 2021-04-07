from django.conf.urls import url

from ecommerce.rg_extensions.currency.api.v2.views import currency as currency_views

urlpatterns = [
    url(r'^currency/', currency_views.CurrencyAPIView.as_view(), name='currency'),
]