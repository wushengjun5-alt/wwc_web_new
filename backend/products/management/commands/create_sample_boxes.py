"""
Management command to create sample ComposableBox entries for the WWC Shop.

Usage:
    python manage.py create_sample_boxes
    python manage.py create_sample_boxes --clear   # delete existing boxes first
"""
from decimal import Decimal
from django.core.management.base import BaseCommand
from products.models import ComposableBox, Product


BOXES = [
    {
        'name': 'Petite Box Bien-etre',
        'slug': 'petite-box-bienetre',
        'description': (
            'Composez votre box bien-etre avec 3 à 5 produits naturels de votre choix. '
            'Idéale pour découvrir nos gammes ou offrir un cadeau personnalisé.'
        ),
        'min_items': 3,
        'max_items': 5,
        'price_tnd': Decimal('89.00'),
        'price_eur': Decimal('27.00'),
    },
    {
        'name': 'Box Cadeau Premium',
        'slug': 'box-cadeau-premium',
        'description': (
            'Offrez une box cadeau personnalisée avec 4 à 6 produits artisanaux tunisiens. '
            'Présentée dans un coffret élégant, prête à offrir.'
        ),
        'min_items': 4,
        'max_items': 6,
        'price_tnd': Decimal('119.00'),
        'price_eur': Decimal('36.00'),
    },
    {
        'name': 'Grande Box Decouverte',
        'slug': 'box-decouverte-grande',
        'description': (
            'Créez votre box découverte avec 5 à 8 produits sélectionnés parmi nos meilleures '
            'références. Parfaite pour une expérience complète.'
        ),
        'min_items': 5,
        'max_items': 8,
        'price_tnd': Decimal('149.00'),
        'price_eur': Decimal('45.00'),
    },
]

# Product slugs/ids to exclude from eligible products (gift sets, bundles)
EXCLUDE_SLUGS = ['coffret-saveurs-de-tunisie', 'ferrari']


class Command(BaseCommand):
    help = 'Create sample composable boxes and assign eligible products'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all existing ComposableBox records before creating new ones',
        )

    def handle(self, *args, **options):
        if options['clear']:
            deleted, _ = ComposableBox.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Deleted {deleted} existing box(es).'))

        # Build eligible product queryset: all active products excluding gift sets
        eligible_qs = Product.objects.filter(is_active=True).exclude(
            slug__in=EXCLUDE_SLUGS
        )
        eligible_count = eligible_qs.count()

        if eligible_count == 0:
            self.stdout.write(self.style.WARNING(
                'No active products found. Run populate_sample_data first.'
            ))
            return

        self.stdout.write(f'Found {eligible_count} eligible product(s).')

        created = 0
        updated = 0

        for box_data in BOXES:
            box, is_new = ComposableBox.objects.update_or_create(
                slug=box_data['slug'],
                defaults={
                    'name':        box_data['name'],
                    'description': box_data['description'],
                    'min_items':   box_data['min_items'],
                    'max_items':   box_data['max_items'],
                    'price_tnd':   box_data['price_tnd'],
                    'price_eur':   box_data['price_eur'],
                    'is_active':   True,
                },
            )
            box.eligible_products.set(eligible_qs)

            if is_new:
                created += 1
                self.stdout.write(self.style.SUCCESS(
                    f'  Created : {box.name} ({box.min_items}–{box.max_items} items, '
                    f'{box.price_tnd} DT, {box.eligible_products.count()} products)'
                ))
            else:
                updated += 1
                self.stdout.write(
                    f'  Updated : {box.name} ({box.eligible_products.count()} products)'
                )

        self.stdout.write(self.style.SUCCESS(
            f'\nDone. {created} box(es) created, {updated} box(es) updated.'
        ))
