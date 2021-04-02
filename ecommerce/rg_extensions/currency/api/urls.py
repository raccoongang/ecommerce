from django.conf.urls import include, url

urlpatterns = [
    url(r'^v2/', include('ecommerce.rg_extensions.currency.api.v2.urls', namespace='rg_api')),
]
