from django.db import migrations


def seed_coupons(apps, schema_editor):
    Coupon = apps.get_model('orders', 'Coupon')
    coupons = [
        {'code': 'WELCOME10', 'discount_type': 'percent', 'discount_value': 10, 'is_active': True, 'min_order_amount': 0},
        {'code': 'FLAT5',     'discount_type': 'fixed',   'discount_value': 5,  'is_active': True, 'min_order_amount': 30},
    ]
    for data in coupons:
        Coupon.objects.get_or_create(code=data['code'], defaults=data)


def remove_coupons(apps, schema_editor):
    Coupon = apps.get_model('orders', 'Coupon')
    Coupon.objects.filter(code__in=['WELCOME10', 'FLAT5']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_add_coupon_model'),
    ]

    operations = [
        migrations.RunPython(seed_coupons, remove_coupons),
    ]
