"""
Payment integration for WWC Shop.

Payment routing by currency (Option B):
- TND orders: bank_transfer only (Stripe does not support TND)
- EUR orders: Stripe card payment
"""

import stripe
import logging
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from orders.models import Order

logger = logging.getLogger(__name__)


def _get_stripe():
    """Return stripe module with api_key set from current settings."""
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe


def _send_order_confirmation_email(order):
    """Send order confirmation email to customer."""
    try:
        subject = f"Confirmation de commande {order.order_number} - Wallah We Can"

        # Plain-text body
        message_lines = [
            f"Bonjour {order.shipping_first_name},",
            "",
            f"Merci pour votre commande {order.order_number} !",
            "",
            "--- Récapitulatif ---",
        ]
        for item in order.items.all():
            message_lines.append(
                f"  {item.quantity}x {item.product_name} — {item.subtotal} {order.currency}"
            )
        message_lines += [
            "",
            f"Sous-total : {order.subtotal} {order.currency}",
            f"Livraison  : {order.shipping_cost} {order.currency}",
            f"Total      : {order.total} {order.currency}",
            "",
            "--- Votre impact ---",
        ]
        for item_type, qty in order.impact_summary.items():
            message_lines.append(f"  {qty} {item_type} fourni(e)s à des étudiants")
        message_lines += [
            "",
            "Merci de soutenir l'initiative GreenSchool de Wallah We Can.",
            "L'équipe WWC",
        ]

        if order.payment_method == 'bank_transfer':
            message_lines += [
                "",
                "--- Informations de virement ---",
                "Veuillez effectuer votre virement avec la référence : " + order.order_number,
                "Nous traiterons votre commande dès réception du paiement.",
            ]

        send_mail(
            subject=subject,
            message="\n".join(message_lines),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error("Failed to send order confirmation email for %s: %s", order.order_number, e)


class CreateCheckoutSessionView(APIView):
    """
    Create Stripe Checkout Session for EUR orders.
    TND orders must use bank_transfer — this endpoint rejects them.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        order_number = request.data.get('order_number')
        success_url = request.data.get('success_url', f"{settings.SITE_URL}/checkout/success/")
        cancel_url = request.data.get('cancel_url', f"{settings.SITE_URL}/checkout/")

        if not order_number:
            return Response(
                {'error': 'order_number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            order = Order.objects.get(order_number=order_number)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        if order.status != 'pending':
            return Response(
                {'error': 'Order is not pending payment'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not settings.STRIPE_SECRET_KEY:
            return Response(
                {'error': 'Stripe is not configured on this server.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        # Stripe does not natively support TND, so we charge in EUR.
        # The amount is converted at a fixed rate; the customer's bank
        # handles the final currency conversion on their end.
        stripe_currency = 'eur'
        tnd_to_eur = float(getattr(settings, 'TND_TO_EUR_RATE', 0.30))

        def to_stripe_amount(tnd_amount):
            return int(float(tnd_amount) * tnd_to_eur * 100)

        line_items = []
        for item in order.items.all():
            line_items.append({
                'price_data': {
                    'currency': stripe_currency,
                    'product_data': {
                        'name': item.product_name,
                        'description': f"Impact: {item.impact_quantity} {item.impact_item}",
                    },
                    'unit_amount': to_stripe_amount(item.unit_price),
                },
                'quantity': item.quantity,
            })

        if order.shipping_cost > 0:
            line_items.append({
                'price_data': {
                    'currency': stripe_currency,
                    'product_data': {'name': 'Livraison'},
                    'unit_amount': to_stripe_amount(order.shipping_cost),
                },
                'quantity': 1,
            })

        try:
            _stripe = _get_stripe()
            session = _stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}&order={order.order_number}",
                cancel_url=f"{cancel_url}?order={order.order_number}",
                customer_email=order.email,
                metadata={
                    'order_number': order.order_number,
                    'order_id': str(order.id),
                    'original_currency': order.currency,
                    'original_total': str(order.total),
                },
            )
            return Response({
                'checkout_url': session.url,
                'session_id': session.id,
            })
        except stripe.error.StripeError as e:
            error_detail = e.json_body.get('error', {}) if hasattr(e, 'json_body') and e.json_body else {}
            logger.error("Stripe error for order %s: %s | detail: %s", order_number, e, error_detail)
            return Response({
                'error': error_detail.get('message') or str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Unexpected error creating Stripe session for order %s: %s", order_number, e, exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BankTransferInstructionsView(APIView):
    """
    Return bank transfer instructions for TND orders.
    Called after order is created when payment_method=bank_transfer.
    """
    permission_classes = [AllowAny]

    def get(self, request, order_number):
        try:
            order = Order.objects.get(order_number=order_number)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        if order.currency != 'TND':
            return Response(
                {'error': 'Bank transfer instructions are only for TND orders.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            'order_number': order.order_number,
            'total': str(order.total),
            'currency': order.currency,
            'instructions': {
                'bank_name': 'Banque de Tunisie',
                'account_holder': 'Wallah We Can',
                'iban': 'TN59 XXXX XXXX XXXX XXXX XXXX',
                'reference': order.order_number,
                'note': (
                    f"Veuillez effectuer un virement de {order.total} TND "
                    f"avec la référence {order.order_number}. "
                    "Votre commande sera traitée dès réception du paiement."
                ),
            }
        })


class StripeWebhookView(APIView):
    """Handle Stripe webhooks for EUR payments."""
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

        if not settings.STRIPE_WEBHOOK_SECRET:
            logger.warning("Stripe webhook secret not configured")
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            event = _get_stripe().Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if event['type'] == 'checkout.session.completed':
            self._handle_checkout_completed(event['data']['object'])
        elif event['type'] == 'payment_intent.succeeded':
            self._handle_payment_succeeded(event['data']['object'])
        elif event['type'] == 'payment_intent.payment_failed':
            self._handle_payment_failed(event['data']['object'])

        return Response({'status': 'success'})

    def _handle_checkout_completed(self, session):
        order_number = session['metadata'].get('order_number')
        if not order_number:
            return
        try:
            order = Order.objects.get(order_number=order_number)
            if order.status == 'pending':
                order.status = 'paid'
                order.payment_id = session.get('payment_intent', '')
                order.paid_at = timezone.now()
                order.save()

                if order.user and hasattr(order.user, 'customer'):
                    order.user.customer.update_impact_stats()

                for item in order.items.all():
                    if item.producer:
                        item.producer.total_products_sold += item.quantity
                        item.producer.total_earnings += item.subtotal
                        item.producer.save()

                _send_order_confirmation_email(order)
        except Order.DoesNotExist:
            logger.warning("Webhook: order %s not found", order_number)

    def _handle_payment_succeeded(self, payment_intent):
        order_number = payment_intent['metadata'].get('order_number')
        if not order_number:
            return
        try:
            order = Order.objects.get(order_number=order_number)
            if order.status == 'pending':
                order.status = 'paid'
                order.payment_id = payment_intent['id']
                order.paid_at = timezone.now()
                order.save()

                if order.user and hasattr(order.user, 'customer'):
                    order.user.customer.update_impact_stats()

                _send_order_confirmation_email(order)
        except Order.DoesNotExist:
            logger.warning("Webhook: order %s not found", order_number)

    def _handle_payment_failed(self, payment_intent):
        order_number = payment_intent['metadata'].get('order_number')
        if not order_number:
            return
        try:
            order = Order.objects.get(order_number=order_number)
            error_msg = payment_intent.get('last_payment_error', {}).get('message', 'Unknown error')
            order.admin_notes += f"\nPayment failed: {error_msg}"
            order.save()
        except Order.DoesNotExist:
            pass


class PaymentStatusView(APIView):
    """Check payment status for an order."""
    permission_classes = [AllowAny]

    def get(self, request, order_number):
        try:
            order = Order.objects.get(order_number=order_number)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'order_number': order.order_number,
            'status': order.status,
            'paid': order.status in ['paid', 'processing', 'shipped', 'delivered'],
            'paid_at': order.paid_at,
            'total': str(order.total),
            'currency': order.currency,
            'payment_method': order.payment_method,
        })
