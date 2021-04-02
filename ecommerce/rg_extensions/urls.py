from django.conf.urls import include, url

urlpatterns = [
    url(r'^api/', include('ecommerce.rg_extensions.currency.api.urls', namespace='rg_api')),
]
