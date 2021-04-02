"""Serializers for data manipulated by ecommerce API endpoints."""
from rest_framework import serializers


class CurrencySerializer(serializers.Serializer):
    currency = serializers.CharField(max_length=3)
