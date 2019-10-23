""" Views for interacting with the LiqPay payment processor. """
from __future__ import unicode_literals

import logging

from base64 import b64decode
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
import json
from oscar.apps.partner import strategy
from oscar.apps.payment.exceptions import PaymentError
from oscar.core.loading import get_class, get_model

from ecommerce.extensions.checkout.mixins import EdxOrderPlacementMixin
from ecommerce.extensions.checkout.utils import get_receipt_page_url
from ecommerce.extensions.payment.exceptions import DuplicateReferenceNumber, InvalidBasketError, InvalidSignatureError
from ecommerce.extensions.payment.processors.liqpay import Liqpay


logger = logging.getLogger(__name__)

Applicator = get_class('offer.applicator', 'Applicator')
Basket = get_model('basket', 'Basket')
BillingAddress = get_model('order', 'BillingAddress')
Country = get_model('address', 'Country')
NoShippingRequired = get_class('shipping.methods', 'NoShippingRequired')
Order = get_model('order', 'Order')
OrderNumberGenerator = get_class('order.utils', 'OrderNumberGenerator')
OrderTotalCalculator = get_class('checkout.calculators', 'OrderTotalCalculator')
PaymentProcessorResponse = get_model('payment', 'PaymentProcessorResponse')


class LiqpayPaymentCallbackView(EdxOrderPlacementMixin, View):
    """Execute an approved LiqPay payment and place an order for paid products as appropriate."""

    @property
    def payment_processor(self):
        return Liqpay(self.request.site)

    # Disable atomicity for the view. Otherwise, we'd be unable to commit to the database
    # until the request had concluded; Django will refuse to commit when an atomic() block
    # is active, since that would break atomicity. Without an order present in the database
    # at the time fulfillment is attempted, asynchronous order fulfillment tasks will fail.
    @method_decorator(transaction.non_atomic_requests)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(LiqpayPaymentCallbackView, self).dispatch(request, *args, **kwargs)

    def _get_basket(self, basket_id):
        if not basket_id:
            return None

        try:
            basket_id = int(basket_id)
            basket = Basket.objects.get(id=basket_id)
            basket.strategy = strategy.Default()
            Applicator().apply(basket, basket.owner, self.request)
            return basket
        except (ValueError, ObjectDoesNotExist):
            return None

    def post(self, request):
        """Handle an incoming user returned to us by LiqPay after approving payment."""

        data = request.POST.get('data')
        decode_data = json.loads(b64decode(data).decode('utf-8'))
        basket = None
        transaction_id = None

        try:
            transaction_id = decode_data.get('transaction_id')
            order_number = decode_data.get('order_id')
            basket_id = OrderNumberGenerator().basket_id(order_number)

            logger.info(
                'Received LiqPay merchant notification for transaction [%s], associated with basket [%d].',
                transaction_id,
                basket_id
            )

            basket = self._get_basket(basket_id)

            if not basket:
                logger.error('Received payment for non-existent basket [%s].', basket_id)
                raise InvalidBasketError
        finally:
            # Store the response in the database.
            ppr = self.payment_processor.record_processor_response(decode_data, transaction_id=transaction_id,
                                                                   basket=basket)
            logger.info("Successfully executed LiqPay payment [%s] for basket [%d].", transaction_id, basket.id)

        receipt_url = get_receipt_page_url(
            order_number=basket.order_number,
            site_configuration=basket.site.siteconfiguration
        )

        try:
            liqpay_response = request.POST.dict()
            # Explicitly delimit operations which will be rolled back if an exception occurs.
            with transaction.atomic():
                try:
                    self.handle_payment(liqpay_response, basket)
                except InvalidSignatureError:
                    logger.exception(
                        'Received an invalid LiqPay response. The payment response was recorded in entry [%d].',
                        ppr.id
                    )
                    return redirect(self.payment_processor.error_url)
                except DuplicateReferenceNumber:
                    if Order.objects.filter(number=order_number).exists() or PaymentProcessorResponse.objects.filter(
                            basket=basket).exclude(transaction_id__isnull=True).exclude(transaction_id='').exists():
                        logger.info(
                            'Received LiqPay payment notification for basket [%d] which is associated '
                            'with existing order [%s] or had an existing valid payment notification. '
                            'No payment was collected, and no new order will be created.',
                            basket.id,
                            order_number
                        )
                    else:
                        logger.info(
                            'Received duplicate LiqPay payment notification for basket [%d] which is not associated '
                            'with any existing order (Missing Order Issue)',
                            basket.id,
                        )
                    return redirect(self.payment_processor.error_url)
                except PaymentError:
                    logger.exception(
                        'LiqPay payment failed for basket [%d]. The payment response was recorded in entry [%d].',
                        basket.id,
                        ppr.id
                    )
                    return redirect(self.payment_processor.error_url)
        except:  # pylint: disable=bare-except
            logger.exception('Attempts to handle payment for basket [%d] failed.', basket.id)
            return redirect(receipt_url)

        try:
            # Note (CCB): In the future, if we do end up shipping physical products, we will need to
            # properly implement shipping methods. For more, see
            # http://django-oscar.readthedocs.org/en/latest/howto/how_to_configure_shipping.html.
            shipping_method = NoShippingRequired()
            shipping_charge = shipping_method.calculate(basket)

            # Note (CCB): This calculation assumes the payment processor has not sent a partial authorization,
            # thus we use the amounts stored in the database rather than those received from the payment processor.
            user = basket.owner
            order_total = OrderTotalCalculator().calculate(basket, shipping_charge)

            order = self.handle_order_placement(
                order_number=order_number,
                user=user,
                basket=basket,
                shipping_address=None,
                shipping_method=shipping_method,
                shipping_charge=shipping_charge,
                billing_address=None,
                order_total=order_total,
                request=request
            )

            self.handle_post_order(order)
            return redirect(receipt_url)
        except Exception as e:  # pylint: disable=broad-except
            logger.exception(self.order_placement_failure_msg, basket.id, e)
            return redirect(receipt_url)
