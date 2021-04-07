"""HTTP endpoint to get the currency of the current site."""
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from ecommerce.rg_extensions.currency.utils import get_currency


class CurrencyAPIView(APIView):
    
    def get(self, request, *args, **kwargs):
        return Response({'currency': get_currency(self.request.site)})
