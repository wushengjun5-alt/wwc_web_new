"""
Migration: Add ShippingRate and SiteSettings models with seed data.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_add_pending_checkout'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShippingRate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country_code', models.CharField(db_index=True, max_length=2, unique=True, verbose_name='Country Code')),
                ('country_name', models.CharField(max_length=100, verbose_name='Country Name')),
                ('rate_tnd', models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='Rate (TND)')),
                ('free_threshold_tnd', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Free Shipping Threshold (TND)')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
            ],
            options={
                'verbose_name': 'Shipping Rate',
                'verbose_name_plural': 'Shipping Rates',
                'ordering': ['country_code'],
            },
        ),
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tnd_to_eur_rate', models.DecimalField(
                    decimal_places=6, default='0.300000', max_digits=10,
                    verbose_name='TND → EUR Rate',
                    help_text='Multiply TND price by this to get EUR price'
                )),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
            ],
            options={
                'verbose_name': 'Site Settings',
                'verbose_name_plural': 'Site Settings',
            },
        ),
        # Seed initial shipping rates matching the previous hardcoded values
        migrations.RunSQL(
            sql="""
                INSERT INTO orders_shippingrate (country_code, country_name, rate_tnd, free_threshold_tnd, is_active, updated_at)
                VALUES
                    ('TN', 'Tunisie',     7.00,  100.00, 1, CURRENT_TIMESTAMP),
                    ('FR', 'France',      15.00,  50.00, 1, CURRENT_TIMESTAMP),
                    ('BE', 'Belgique',    15.00,  50.00, 1, CURRENT_TIMESTAMP),
                    ('CH', 'Suisse',      20.00,  75.00, 1, CURRENT_TIMESTAMP),
                    ('DE', 'Allemagne',   20.00,  75.00, 1, CURRENT_TIMESTAMP);
            """,
            reverse_sql="DELETE FROM orders_shippingrate;",
        ),
        # Seed default site settings row
        migrations.RunSQL(
            sql="INSERT INTO orders_sitesettings (tnd_to_eur_rate, updated_at) VALUES (0.300000, CURRENT_TIMESTAMP);",
            reverse_sql="DELETE FROM orders_sitesettings;",
        ),
    ]
