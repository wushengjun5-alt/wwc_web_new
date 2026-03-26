"""
Order signals for WWC Shop.

Restores product stock when an order is cancelled or refunded.
"""

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db import transaction, models


@receiver(pre_save, sender='orders.Order')
def restore_stock_on_cancel_or_refund(sender, instance, **kwargs):
    """
    When an order transitions to 'cancelled' or 'refunded', restore
    the stock quantity for all tracked products in the order.
    Only fires when the status actually changes to one of those states.
    """
    if not instance.pk:
        return  # new order, nothing to restore

    try:
        previous = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    TERMINAL_STATES = {'cancelled', 'refunded'}
    status_changed_to_terminal = (
        instance.status in TERMINAL_STATES and
        previous.status not in TERMINAL_STATES
    )

    if not status_changed_to_terminal:
        return

    # Restore stock for each order item whose product tracks inventory
    with transaction.atomic():
        for item in instance.items.select_related('product').all():
            product = getattr(item, 'product', None)
            if product and product.track_inventory:
                product.__class__.objects.filter(pk=product.pk).update(
                    stock_quantity=models.F('stock_quantity') + item.quantity
                )
