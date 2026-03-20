"""
Django management command to create sample orders with realistic data
Usage: python manage.py create_sample_orders
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import random
from datetime import timedelta

from products.models import Product, ProductCategory, Producer
from orders.models import Order, OrderItem
from customers.models import Customer


class Command(BaseCommand):
    help = 'Create sample orders with realistic data for testing and demo purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of sample orders to create (default: 10)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing sample data before creating new'
        )

    def handle(self, *args, **options):
        count = options['count']
        clear = options['clear']

        if clear:
            self.stdout.write('Clearing existing sample data...')
            Order.objects.filter(order_number__startswith='WWC-').delete()
            User.objects.filter(username__startswith='customer_').delete()
            self.stdout.write(self.style.SUCCESS('Cleared existing sample data'))

        # Ensure we have products
        if not Product.objects.exists():
            self.stdout.write(self.style.WARNING('No products found. Creating sample products first...'))
            self.create_sample_products()

        # Ensure we have customers
        self.create_sample_customers()

        # Create orders
        self.stdout.write(f'Creating {count} sample orders...')
        created_orders = self.create_orders(count)

        self.stdout.write(self.style.SUCCESS(
            f'Successfully created {len(created_orders)} sample orders!'
        ))

        # Display summary
        for order in created_orders[:5]:  # Show first 5
            self.stdout.write(f'  - {order.order_number}: {order.total} {order.currency} ({order.status})')

        if len(created_orders) > 5:
            self.stdout.write(f'  ... and {len(created_orders) - 5} more')

    def create_sample_products(self):
        """Create sample products if they don't exist"""
        # Create category
        category, _ = ProductCategory.objects.get_or_create(
            slug='soins',
            defaults={
                'name': 'SOINS',
                'name_en': 'Care',
                'description': 'Produits de soins naturels',
            }
        )

        # Create producer
        producer, _ = Producer.objects.get_or_create(
            slug='farm-sidi',
            defaults={
                'name': 'Farm Sidi Mechreg',
                'location': 'Sidi Mechreg, Tunisia',
                'bio': 'Parents de GreenSchool produisant des produits naturels',
            }
        )

        # Create sample products
        sample_products = [
            {
                'sku': 'ROLLCALME-001',
                'name': 'Roll-on Calme',
                'description': 'Roll-on apaisant aux huiles essentielles naturelles',
                'price_tnd': Decimal('25.00'),
                'price_eur': Decimal('8.50'),
                'stock_quantity': 100,
            },
            {
                'sku': 'HUILE-LAV-001',
                'name': 'Huile de Lavande',
                'description': 'Huile essentielle de lavande 100% naturelle',
                'price_tnd': Decimal('35.00'),
                'price_eur': Decimal('12.00'),
                'stock_quantity': 75,
            },
            {
                'sku': 'SAVON-OLV-001',
                'name': 'Savon à l\'Olive',
                'description': 'Savon artisanal à l\'huile d\'olive',
                'price_tnd': Decimal('15.00'),
                'price_eur': Decimal('5.00'),
                'stock_quantity': 150,
            },
        ]

        for prod_data in sample_products:
            Product.objects.get_or_create(
                sku=prod_data['sku'],
                defaults={
                    **prod_data,
                    'category': category,
                    'producer': producer,
                    'impact_description': '6 barres énergétiques fournies aux enfants',
                    'impact_school': 'Sidi Mechreg',
                    'impact_quantity': 6,
                    'impact_item': 'barres énergétiques',
                    'is_active': True,
                }
            )

        self.stdout.write(self.style.SUCCESS('Created sample products'))

    def create_sample_customers(self):
        """Create sample customers"""
        sample_customers = [
            {
                'username': 'customer_ahmed',
                'email': 'ahmed.ben@example.tn',
                'first_name': 'Ahmed',
                'last_name': 'Ben Ali',
                'customer_type': 'individual',
                'phone': '+216 20 123 456',
            },
            {
                'username': 'customer_fatima',
                'email': 'fatima.said@example.tn',
                'first_name': 'Fatima',
                'last_name': 'Said',
                'customer_type': 'individual',
                'phone': '+216 22 456 789',
            },
            {
                'username': 'customer_company1',
                'email': 'contact@greencorp.tn',
                'first_name': 'Mohamed',
                'last_name': 'Triki',
                'customer_type': 'company',
                'phone': '+216 71 123 456',
                'company_name': 'GreenCorp Tunisia',
            },
            {
                'username': 'customer_marie',
                'email': 'marie.dupont@example.fr',
                'first_name': 'Marie',
                'last_name': 'Dupont',
                'customer_type': 'individual',
                'phone': '+33 6 12 34 56 78',
            },
        ]

        for customer_data in sample_customers:
            user, created = User.objects.get_or_create(
                username=customer_data['username'],
                defaults={
                    'email': customer_data['email'],
                    'first_name': customer_data['first_name'],
                    'last_name': customer_data['last_name'],
                }
            )

            if created:
                user.set_password('demo123')
                user.save()

                # Update customer profile
                customer = user.customer
                customer.customer_type = customer_data['customer_type']
                customer.phone = customer_data['phone']

                if customer_data.get('company_name'):
                    customer.company_name = customer_data['company_name']

                customer.save()

        self.stdout.write(self.style.SUCCESS('Created sample customers'))

    def create_orders(self, count):
        """Create sample orders"""
        users = User.objects.filter(username__startswith='customer_')
        products = list(Product.objects.filter(is_active=True))

        if not users.exists():
            self.stdout.write(self.style.ERROR('No customers found'))
            return []

        if not products:
            self.stdout.write(self.style.ERROR('No products found'))
            return []

        statuses = ['paid', 'processing', 'shipped', 'delivered', 'pending']
        currencies = ['TND', 'EUR']

        # Shipping methods by country
        tunisia_transporters = ['Aramex Tunisia', 'La Poste Tunisienne', 'DHL Tunisia', 'Chronopost Tunisia', 'Rapid Post']
        france_transporters = ['Colissimo', 'Chronopost', 'DHL Express', 'UPS', 'Mondial Relay']

        tunisia_cities = [
            ('Tunis', '1000'),
            ('Sfax', '3000'),
            ('Sousse', '4000'),
            ('Kairouan', '3100'),
            ('Bizerte', '7000'),
        ]

        france_cities = [
            ('Paris', '75001'),
            ('Lyon', '69001'),
            ('Marseille', '13001'),
        ]

        orders = []

        for i in range(count):
            user = random.choice(users)
            customer = user.customer

            # Determine currency based on customer
            if 'fr' in user.email:
                currency = 'EUR'
                cities = france_cities
                country = 'FR'
                transporters = france_transporters
            else:
                currency = 'TND'
                cities = tunisia_cities
                country = 'TN'
                transporters = tunisia_transporters

            # Random number of items (1-5)
            num_items = random.randint(1, 5)
            selected_products = random.sample(products, min(num_items, len(products)))

            # Calculate totals
            subtotal = Decimal('0.00')
            impact_summary = {}

            order_items_data = []

            for product in selected_products:
                quantity = random.randint(1, 3)
                is_b2b = customer.customer_type == 'company'
                unit_price = product.get_price(currency, is_b2b, quantity)
                item_subtotal = unit_price * quantity

                subtotal += item_subtotal

                # Track impact
                impact_item = product.impact_item
                impact_qty = product.impact_quantity * quantity
                impact_summary[impact_item] = impact_summary.get(impact_item, 0) + impact_qty

                order_items_data.append({
                    'product': product,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'subtotal': item_subtotal,
                })

            shipping_cost = Decimal('7.00') if currency == 'TND' else Decimal('5.00')
            total = subtotal + shipping_cost

            # Random city
            city, postal_code = random.choice(cities)

            # Random status
            status = random.choice(statuses)

            # Create order with random past date (last 60 days)
            days_ago = random.randint(0, 60)
            created_date = timezone.now() - timedelta(days=days_ago)

            # Shipping method and tracking number
            shipping_method = ''
            tracking_number = ''

            # Only add shipping info for shipped/delivered orders
            if status in ['shipped', 'delivered']:
                shipping_method = random.choice(transporters)
                # Generate realistic tracking number
                if country == 'TN':
                    tracking_number = f'TN{random.randint(100000000, 999999999)}'
                else:
                    tracking_number = f'FR{random.randint(10000000000, 99999999999)}'

            order = Order.objects.create(
                user=user,
                email=user.email,
                phone=customer.phone or '+216 20 000 000',
                status=status,
                currency=currency,
                subtotal=subtotal,
                shipping_cost=shipping_cost,
                total=total,
                total_impact_items=sum(impact_summary.values()),
                impact_summary=impact_summary,
                shipping_first_name=user.first_name,
                shipping_last_name=user.last_name,
                shipping_address_1=f'{random.randint(1, 999)} Avenue Habib Bourguiba' if country == 'TN' else f'{random.randint(1, 100)} Rue de la République',
                shipping_city=city,
                shipping_postal_code=postal_code,
                shipping_country=country,
                payment_method='stripe' if random.random() > 0.3 else 'bank_transfer',
                shipping_method=shipping_method,
                tracking_number=tracking_number,
                customer_notes='',
                created_at=created_date,
            )

            # Set paid_at for paid orders
            if status in ['paid', 'processing', 'shipped', 'delivered']:
                order.paid_at = created_date + timedelta(hours=random.randint(1, 24))

            if status in ['shipped', 'delivered']:
                order.shipped_at = created_date + timedelta(days=random.randint(1, 3))

            if status == 'delivered':
                order.delivered_at = created_date + timedelta(days=random.randint(3, 7))

            order.save()

            # Create order items
            for item_data in order_items_data:
                OrderItem.objects.create(
                    order=order,
                    product=item_data['product'],
                    producer=item_data['product'].producer,
                    product_name=item_data['product'].name,
                    product_sku=item_data['product'].sku,
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    subtotal=item_data['subtotal'],
                    impact_quantity=item_data['product'].impact_quantity,
                    impact_item=item_data['product'].impact_item,
                    impact_school=item_data['product'].impact_school,
                )

            orders.append(order)

        return orders
