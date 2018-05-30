import hashlib
import json
from base64 import b64decode

from django.conf import settings

from Crypto.Cipher import AES


def get_credit_payment_info(request):
    decryptor = AES.new(key=hashlib.md5(settings.EDX_API_KEY).hexdigest(), mode=AES.MODE_ECB)
    credit_payment_info_from_request = request.GET.get('credit_payment_info', '')
    # Replace the space character with plus because browsers encoded `+` as `%20`
    # and Django decode it back as a space character.
    credit_payment_info = b64decode(credit_payment_info_from_request.replace(' ', '+'))
    if len(credit_payment_info) == 0:
        return {}
    return json.loads(decryptor.decrypt(credit_payment_info))
