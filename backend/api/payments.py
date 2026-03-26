"""
Payment integration for WWC Shop.

Supported payment methods:
- stripe: card payment (EUR or TND via customer's bank conversion)
- cash_on_delivery: pay on delivery
"""

import stripe
import logging
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from api.views import CsrfExemptSessionAuthentication

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

        send_mail(
            subject=subject,
            message="\n".join(message_lines),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error("Failed to send order confirmation email for %s: %s", order.order_number, e)


def _send_shipping_confirmation_email(order):
    """Send shipping confirmation email to customer when order is marked as shipped."""
    try:
        tracking = order.tracking_number
        subject = f"Votre commande {order.order_number} est en route ! - Wallah We Can"

        message_lines = [
            f"Bonjour {order.shipping_first_name},",
            "",
            f"Bonne nouvelle ! Votre commande {order.order_number} vient d'être expédiée.",
            "",
        ]
        if tracking:
            message_lines += [
                f"Numéro de suivi : {tracking}",
                "",
            ]
        message_lines += [
            "--- Articles expédiés ---",
        ]
        for item in order.items.all():
            message_lines.append(
                f"  {item.quantity}x {item.product_name}"
            )
        message_lines += [
            "",
            f"Adresse de livraison :",
            f"  {order.shipping_first_name} {order.shipping_last_name}",
            f"  {order.shipping_address}",
            f"  {order.shipping_city}, {order.shipping_country}",
            "",
            "Merci de soutenir l'initiative GreenSchool de Wallah We Can.",
            "L'équipe WWC",
        ]

        send_mail(
            subject=subject,
            message="\n".join(message_lines),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error("Failed to send shipping confirmation email for %s: %s", order.order_number, e)


class CreateCheckoutSessionView(APIView):
    """
    Create Stripe Checkout Session for EUR orders.
    Creates a Stripe Checkout Session for the given order.
    """
    authentication_classes = [JWTAuthentication, CsrfExemptSessionAuthentication]
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

        # Always charge in EUR via Stripe.
        # If order is in TND, convert at fixed rate; EUR orders charge directly.
        stripe_currency = 'eur'
        from orders.models import SiteSettings
        tnd_to_eur = SiteSettings.get_tnd_to_eur()

        def to_cents(amount, currency):
            """Convert an amount to Stripe cents (EUR). Always >= 1 cent."""
            if currency == 'EUR':
                cents = int(round(float(amount) * 100))
            else:
                cents = int(round(float(amount) * tnd_to_eur * 100))
            return max(cents, 1)

        line_items = []
        for item in order.items.all():
            line_items.append({
                'price_data': {
                    'currency': stripe_currency,
                    'product_data': {
                        'name': item.product_name,
                        'description': f"Impact: {item.impact_quantity} {item.impact_item}",
                    },
                    'unit_amount': to_cents(item.unit_price, order.currency),
                },
                'quantity': item.quantity,
            })

        if order.shipping_cost > 0:
            line_items.append({
                'price_data': {
                    'currency': stripe_currency,
                    'product_data': {'name': 'Livraison'},
                    'unit_amount': to_cents(order.shipping_cost, order.currency),
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


class StripeWebhookView(APIView):
    """Handle Stripe webhooks for EUR payments."""
    authentication_classes = [CsrfExemptSessionAuthentication]
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
        metadata = session.get('metadata', {})
        pending_checkout_id = metadata.get('pending_checkout_id')
        order_number = metadata.get('order_number')
        donation_id = metadata.get('donation_id')

        # New flow: create order from PendingCheckout
        if pending_checkout_id:
            self._fulfil_pending_checkout(session, pending_checkout_id)
            return

        # Legacy flow: order already existed (COD/bank transfer won't reach here,
        # but keep for backwards compat with any old sessions in flight)
        if order_number:
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

        if donation_id:
            try:
                from donations.models import Donation as DonationModel
                donation = DonationModel.objects.get(pk=donation_id)
                if donation.status == 'pending':
                    donation.status = 'completed'
                    donation.payment_id = session.get('payment_intent', '')
                    donation.save()
            except Exception as e:
                logger.warning("Webhook: donation %s not found or error: %s", donation_id, e)

    def _fulfil_pending_checkout(self, session, pending_checkout_id):
        """Create the real Order from a PendingCheckout after Stripe payment confirmed."""
        from orders.models import PendingCheckout
        from api.views import _create_order_items_from_snapshot
        from decimal import Decimal

        try:
            pending = PendingCheckout.objects.get(pk=pending_checkout_id)
        except PendingCheckout.DoesNotExist:
            logger.warning("Webhook: PendingCheckout %s not found", pending_checkout_id)
            return

        fd = pending.form_data
        snapshot = pending.cart_snapshot

        impact_summary = {}
        for item in snapshot['items']:
            key = item['impact_item'] or 'items'
            impact_summary[key] = impact_summary.get(key, 0) + item['impact_quantity']
        total_impact = sum(impact_summary.values())

        order = Order.objects.create(
            user=pending.user,
            email=fd['email'],
            phone=fd['phone'],
            status='paid',
            currency=snapshot['currency'],
            subtotal=Decimal(fd['_subtotal']),
            discount_amount=Decimal(fd['_discount_amount']),
            shipping_cost=Decimal(fd['_shipping_cost']),
            tax_amount=Decimal(fd['_gift_packaging_fee']),
            total=Decimal(fd['_total']),
            total_impact_items=total_impact,
            impact_summary=impact_summary,
            payment_method='stripe',
            payment_id=session.get('payment_intent', ''),
            paid_at=timezone.now(),
            shipping_first_name=fd['shipping_first_name'],
            shipping_last_name=fd['shipping_last_name'],
            shipping_company=fd.get('shipping_company', ''),
            shipping_address_1=fd['shipping_address_1'],
            shipping_address_2=fd.get('shipping_address_2', ''),
            shipping_city=fd['shipping_city'],
            shipping_state=fd.get('shipping_state', ''),
            shipping_postal_code=fd['shipping_postal_code'],
            shipping_country=fd.get('shipping_country', 'TN'),
            billing_same_as_shipping=fd.get('billing_same_as_shipping', True),
            billing_first_name=fd.get('billing_first_name', ''),
            billing_last_name=fd.get('billing_last_name', ''),
            billing_company=fd.get('billing_company', ''),
            billing_address_1=fd.get('billing_address_1', ''),
            billing_address_2=fd.get('billing_address_2', ''),
            billing_city=fd.get('billing_city', ''),
            billing_postal_code=fd.get('billing_postal_code', ''),
            billing_country=fd.get('billing_country', ''),
            customer_notes=fd.get('customer_notes', ''),
            coupon_code=fd.get('coupon_code', ''),
        )

        _create_order_items_from_snapshot(order, snapshot)

        # Mark coupon as used
        coupon_code = fd.get('coupon_code', '').strip().upper()
        if coupon_code:
            try:
                from orders.models import Coupon
                coupon = Coupon.objects.get(code=coupon_code)
                coupon.used_count += 1
                coupon.save(update_fields=['used_count'])
            except Exception:
                pass

        # Update customer impact stats
        if pending.user and hasattr(pending.user, 'customer'):
            pending.user.customer.update_impact_stats()

        # Update producer stats
        for item in order.items.all():
            if item.producer:
                item.producer.total_products_sold += item.quantity
                item.producer.total_earnings += item.subtotal
                item.producer.save()

        _send_order_confirmation_email(order)

        # Store order number on pending checkout for the success page to retrieve
        pending.form_data['_order_number'] = order.order_number
        pending.save(update_fields=['form_data'])

        # Clean up old pending checkouts (best effort)
        try:
            PendingCheckout.objects.filter(created_at__lt=timezone.now() - timedelta(hours=6)).delete()
        except Exception:
            pass

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


class PendingCheckoutStatusView(APIView):
    """Poll for the order created from a PendingCheckout (Stripe flow)."""
    authentication_classes = [JWTAuthentication, CsrfExemptSessionAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, pending_id):
        from orders.models import PendingCheckout
        try:
            pending = PendingCheckout.objects.get(pk=pending_id)
        except (PendingCheckout.DoesNotExist, Exception):
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        order_number = pending.form_data.get('_order_number')
        if order_number:
            return Response({'ready': True, 'order_number': order_number})
        return Response({'ready': False})


class PaymentStatusView(APIView):
    """Check payment status for an order."""
    authentication_classes = [JWTAuthentication, CsrfExemptSessionAuthentication]
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
