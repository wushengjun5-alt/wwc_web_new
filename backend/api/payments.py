"""
Stripe payment integration for WWC Shop
"""

import stripe
from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from orders.models import Order, Cart

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class CreatePaymentIntentView(APIView):
    """Create Stripe PaymentIntent for checkout"""
    permission_classes = [AllowAny]

    def post(self, request):
        order_number = request.data.get('order_number')

        if not order_number:
            return Response(
                {'error': 'order_number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            order = Order.objects.get(order_number=order_number)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if order.status != 'pending':
            return Response(
                {'error': 'Order is not pending payment'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Convert amount to cents (Stripe uses smallest currency unit)
        amount = int(order.total * 100)

        # Map currency to Stripe format
        currency = order.currency.lower()
        if currency == 'tnd':
            # TND needs to be handled - Stripe doesn't support TND directly
            # For now, we'll use the amount as-is
            currency = 'eur'
            # Convert TND to EUR (simplified - should use real exchange rate)
            amount = int(amount * 0.30)

        try:
            # Create PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                metadata={
                    'order_number': order.order_number,
                    'order_id': str(order.id),
                },
                description=f"WWC Shop Order {order.order_number}",
                receipt_email=order.email,
            )

            return Response({
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id,
                'amount': amount,
                'currency': currency,
            })

        except stripe.error.StripeError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CreateCheckoutSessionView(APIView):
    """Create Stripe Checkout Session (hosted checkout)"""
    permission_classes = [AllowAny]

    def post(self, request):
        order_number = request.data.get('order_number')
        success_url = request.data.get('success_url', f"{settings.SITE_URL}/checkout/success")
        cancel_url = request.data.get('cancel_url', f"{settings.SITE_URL}/checkout/cancel")

        if not order_number:
            return Response(
                {'error': 'order_number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            order = Order.objects.get(order_number=order_number)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if order.status != 'pending':
            return Response(
                {'error': 'Order is not pending payment'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Build line items
        line_items = []
        for item in order.items.all():
            unit_amount = int(item.unit_price * 100)

            # Convert TND to EUR for Stripe
            if order.currency == 'TND':
                unit_amount = int(unit_amount * 0.30)

            line_items.append({
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': item.product_name,
                        'description': f"Impact: {item.impact_quantity} {item.impact_item}",
                    },
                    'unit_amount': unit_amount,
                },
                'quantity': item.quantity,
            })

        # Add shipping as line item
        if order.shipping_cost > 0:
            shipping_amount = int(order.shipping_cost * 100)
            if order.currency == 'TND':
                shipping_amount = int(shipping_amount * 0.30)

            line_items.append({
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': 'Shipping',
                    },
                    'unit_amount': shipping_amount,
                },
                'quantity': 1,
            })

        try:
            # Create Checkout Session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}&order={order.order_number}",
                cancel_url=f"{cancel_url}?order={order.order_number}",
                customer_email=order.email,
                metadata={
                    'order_number': order.order_number,
                    'order_id': str(order.id),
                },
                shipping_address_collection={
                    'allowed_countries': ['TN', 'FR', 'BE', 'CH', 'DE'],
                },
            )

            return Response({
                'checkout_url': session.url,
                'session_id': session.id,
            })

        except stripe.error.StripeError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class StripeWebhookView(APIView):
    """Handle Stripe webhooks"""
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        webhook_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError:
            # Invalid payload
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            # Invalid signature
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            self.handle_checkout_completed(session)

        elif event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            self.handle_payment_succeeded(payment_intent)

        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            self.handle_payment_failed(payment_intent)

        return Response({'status': 'success'})

    def handle_checkout_completed(self, session):
        """Handle successful checkout session"""
        order_number = session['metadata'].get('order_number')
        if not order_number:
            return

        try:
            order = Order.objects.get(order_number=order_number)
            order.status = 'paid'
            order.payment_id = session.get('payment_intent')
            order.paid_at = timezone.now()
            order.save()

            # Update customer stats
            if order.user and hasattr(order.user, 'customer'):
                order.user.customer.update_impact_stats()

            # Update producer stats
            for item in order.items.all():
                if item.producer:
                    item.producer.total_products_sold += item.quantity
                    item.producer.total_earnings += item.subtotal
                    item.producer.save()

            # Send confirmation email (implement later)
            # send_order_confirmation_email(order)

        except Order.DoesNotExist:
            pass

    def handle_payment_succeeded(self, payment_intent):
        """Handle successful PaymentIntent"""
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

                # Update customer stats
                if order.user and hasattr(order.user, 'customer'):
                    order.user.customer.update_impact_stats()

        except Order.DoesNotExist:
            pass

    def handle_payment_failed(self, payment_intent):
        """Handle failed payment"""
        order_number = payment_intent['metadata'].get('order_number')
        if not order_number:
            return

        try:
            order = Order.objects.get(order_number=order_number)
            order.admin_notes += f"\nPayment failed: {payment_intent.get('last_payment_error', {}).get('message', 'Unknown error')}"
            order.save()
        except Order.DoesNotExist:
            pass


class PaymentStatusView(APIView):
    """Check payment status for an order"""
    permission_classes = [AllowAny]

    def get(self, request, order_number):
        try:
            order = Order.objects.get(order_number=order_number)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({
            'order_number': order.order_number,
            'status': order.status,
            'paid': order.status in ['paid', 'processing', 'shipped', 'delivered'],
            'paid_at': order.paid_at,
            'total': str(order.total),
            'currency': order.currency,
        })
