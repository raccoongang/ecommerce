"""HTTP endpoint to get the currency of the current site."""
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from ecommerce.extensions.api.serializers import CurrencySerializer


class CurrencyAPIView(APIView):
    serializer_class = CurrencySerializer
    
    def get(self, request, *args, **kwargs):
        return Response({'currency': self.request.site.siteconfiguration.currency or settings.OSCAR_DEFAULT_CURRENCY})
