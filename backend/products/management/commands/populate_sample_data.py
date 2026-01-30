"""
Management command to populate sample data for testing the WWC Shop.
"""
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import ProductCategory, Producer, Product, Review

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate the database with sample products, categories, and producers'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...\n')

        # Create Categories
        self.stdout.write('Creating categories...')
        categories_data = [
            {'name': 'Soins', 'name_en': 'Care', 'name_ar': 'العناية', 'slug': 'soins', 'icon': '🧴', 'description': 'Produits de soins naturels pour le corps et le visage', 'order': 1},
            {'name': 'Nutrition', 'name_en': 'Nutrition', 'name_ar': 'التغذية', 'slug': 'nutrition', 'icon': '🥗', 'description': 'Aliments sains et nutritifs', 'order': 2},
            {'name': 'Bien-être', 'name_en': 'Wellness', 'name_ar': 'الرفاهية', 'slug': 'bien-etre', 'icon': '🧘', 'description': 'Produits pour votre bien-être quotidien', 'order': 3},
            {'name': 'Maison', 'name_en': 'Home', 'name_ar': 'المنزل', 'slug': 'maison', 'icon': '🏠', 'description': 'Produits écologiques pour la maison', 'order': 4},
            {'name': 'Coffrets', 'name_en': 'Gift Sets', 'name_ar': 'علب الهدايا', 'slug': 'coffrets', 'icon': '🎁', 'description': 'Coffrets cadeaux soigneusement composés', 'order': 5},
            {'name': "Cadeaux d'entreprise", 'name_en': 'Corporate Gifts', 'name_ar': 'هدايا الشركات', 'slug': 'cadeaux-entreprise', 'icon': '💼', 'description': 'Solutions cadeaux pour les entreprises', 'order': 6},
            {'name': 'Composer ma box', 'name_en': 'Build My Box', 'name_ar': 'اصنع صندوقي', 'slug': 'composer-box', 'icon': '📦', 'description': 'Créez votre propre coffret personnalisé', 'order': 7},
        ]

        categories = {}
        for cat_data in categories_data:
            cat, created = ProductCategory.objects.update_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories[cat_data['slug']] = cat
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'  {status}: {cat.name}')

        # Create Producers (using correct field names: bio instead of description/story)
        self.stdout.write('\nCreating producers...')
        producers_data = [
            {
                'name': 'Coopérative Femmes de Zaghouan',
                'slug': 'coop-zaghouan',
                'bio': 'Coopérative de femmes artisanes produisant des cosmétiques naturels à base de plantes locales. Fondée en 2018, notre coopérative réunit 25 femmes de la région de Zaghouan.',
                'location': 'Zaghouan, Tunisie',
            },
            {
                'name': 'Ferme Bio El Jem',
                'slug': 'ferme-el-jem',
                'bio': 'Ferme biologique certifiée produisant des aliments sains et naturels. Notre ferme familiale pratique l\'agriculture biologique depuis 2010.',
                'location': 'El Jem, Tunisie',
            },
            {
                'name': 'Atelier Artisanal de Sidi Bou Said',
                'slug': 'atelier-sidi-bou',
                'bio': 'Atelier d\'artisans créant des produits pour la maison avec des matériaux recyclés. Notre atelier emploie des jeunes du quartier.',
                'location': 'Sidi Bou Said, Tunisie',
            },
            {
                'name': 'Les Ruches de Béja',
                'slug': 'ruches-beja',
                'bio': 'Apiculteurs passionnés produisant du miel pur et des produits de la ruche. Nos abeilles butinent dans les forêts préservées de Béja.',
                'location': 'Béja, Tunisie',
            },
        ]

        producers = {}
        for prod_data in producers_data:
            producer, created = Producer.objects.update_or_create(
                slug=prod_data['slug'],
                defaults=prod_data
            )
            producers[prod_data['slug']] = producer
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'  {status}: {producer.name}')

        # Create Products (using correct field names)
        self.stdout.write('\nCreating products...')

        # Generate unique SKUs
        import uuid
        def gen_sku(prefix):
            return f"{prefix}-{uuid.uuid4().hex[:6].upper()}"

        products_data = [
            # SOINS
            {
                'name': 'Huile d\'Argan Pure',
                'name_en': 'Pure Argan Oil',
                'name_ar': 'زيت أركان نقي',
                'slug': 'huile-argan-pure',
                'sku': gen_sku('SOINS'),
                'description': 'Huile d\'argan 100% pure et naturelle, pressée à froid. Idéale pour la peau et les cheveux.',
                'description_en': 'Pure and natural 100% argan oil, cold pressed. Ideal for skin and hair.',
                'price_tnd': Decimal('45.00'),
                'price_eur': Decimal('13.50'),
                'b2b_price_tnd': Decimal('38.00'),
                'category': categories['soins'],
                'producer': producers['coop-zaghouan'],
                'stock_quantity': 50,
                'is_natural': True,
                'is_organic': True,
                'impact_quantity': 3,
                'impact_item': 'kits scolaires',
                'impact_school': 'GreenSchool Zaghouan',
                'impact_description': 'Grâce à votre achat, 3 kits scolaires seront fournis aux élèves de GreenSchool Zaghouan',
            },
            {
                'name': 'Savon au Lait de Chèvre',
                'name_en': 'Goat Milk Soap',
                'name_ar': 'صابون حليب الماعز',
                'slug': 'savon-lait-chevre',
                'sku': gen_sku('SOINS'),
                'description': 'Savon artisanal au lait de chèvre frais. Doux et hydratant pour tous types de peau.',
                'price_tnd': Decimal('18.00'),
                'price_eur': Decimal('5.40'),
                'b2b_price_tnd': Decimal('14.00'),
                'category': categories['soins'],
                'producer': producers['coop-zaghouan'],
                'stock_quantity': 100,
                'is_natural': True,
                'is_organic': False,
                'impact_quantity': 2,
                'impact_item': 'repas',
                'impact_school': 'GreenSchool Zaghouan',
                'impact_description': 'Grâce à votre achat, 2 repas seront fournis aux élèves de GreenSchool Zaghouan',
            },
            {
                'name': 'Crème Hydratante à l\'Olive',
                'name_en': 'Olive Moisturizing Cream',
                'name_ar': 'كريم مرطب بالزيتون',
                'slug': 'creme-hydratante-olive',
                'sku': gen_sku('SOINS'),
                'description': 'Crème hydratante riche à base d\'huile d\'olive extra vierge tunisienne.',
                'price_tnd': Decimal('32.00'),
                'price_eur': Decimal('9.60'),
                'b2b_price_tnd': Decimal('26.00'),
                'category': categories['soins'],
                'producer': producers['coop-zaghouan'],
                'stock_quantity': 75,
                'is_natural': True,
                'is_organic': True,
                'impact_quantity': 4,
                'impact_item': 'livres',
                'impact_school': 'GreenSchool Tunis',
                'impact_description': 'Grâce à votre achat, 4 livres seront fournis aux élèves de GreenSchool Tunis',
            },

            # NUTRITION
            {
                'name': 'Miel de Forêt Bio',
                'name_en': 'Organic Forest Honey',
                'name_ar': 'عسل الغابة العضوي',
                'slug': 'miel-foret-bio',
                'sku': gen_sku('NUTR'),
                'description': 'Miel pur récolté dans les forêts de Béja. Riche en antioxydants.',
                'price_tnd': Decimal('55.00'),
                'price_eur': Decimal('16.50'),
                'b2b_price_tnd': Decimal('45.00'),
                'category': categories['nutrition'],
                'producer': producers['ruches-beja'],
                'stock_quantity': 40,
                'is_natural': True,
                'is_organic': True,
                'impact_quantity': 5,
                'impact_item': 'barres énergétiques',
                'impact_school': 'GreenSchool Béja',
                'impact_description': 'Grâce à votre achat, 5 barres énergétiques seront fournies aux élèves de GreenSchool Béja',
            },
            {
                'name': 'Dattes Deglet Nour Premium',
                'name_en': 'Premium Deglet Nour Dates',
                'name_ar': 'تمر دقلة نور ممتاز',
                'slug': 'dattes-deglet-nour',
                'sku': gen_sku('NUTR'),
                'description': 'Dattes Deglet Nour de première qualité, récoltées à la main dans les oasis du Sud.',
                'price_tnd': Decimal('28.00'),
                'price_eur': Decimal('8.40'),
                'b2b_price_tnd': Decimal('22.00'),
                'category': categories['nutrition'],
                'producer': producers['ferme-el-jem'],
                'stock_quantity': 60,
                'is_natural': True,
                'is_organic': True,
                'impact_quantity': 3,
                'impact_item': 'goûters',
                'impact_school': 'GreenSchool Tozeur',
                'impact_description': 'Grâce à votre achat, 3 goûters seront fournis aux élèves de GreenSchool Tozeur',
            },
            {
                'name': 'Huile d\'Olive Extra Vierge',
                'name_en': 'Extra Virgin Olive Oil',
                'name_ar': 'زيت زيتون بكر ممتاز',
                'slug': 'huile-olive-extra-vierge',
                'sku': gen_sku('NUTR'),
                'description': 'Huile d\'olive extra vierge première pression à froid. Goût fruité et intense.',
                'price_tnd': Decimal('38.00'),
                'price_eur': Decimal('11.40'),
                'b2b_price_tnd': Decimal('30.00'),
                'category': categories['nutrition'],
                'producer': producers['ferme-el-jem'],
                'stock_quantity': 80,
                'is_natural': True,
                'is_organic': True,
                'impact_quantity': 4,
                'impact_item': 'repas',
                'impact_school': 'GreenSchool El Jem',
                'impact_description': 'Grâce à votre achat, 4 repas seront fournis aux élèves de GreenSchool El Jem',
            },
            {
                'name': 'Harissa Traditionnelle',
                'name_en': 'Traditional Harissa',
                'name_ar': 'هريسة تقليدية',
                'slug': 'harissa-traditionnelle',
                'sku': gen_sku('NUTR'),
                'description': 'Harissa préparée selon la recette traditionnelle avec des piments séchés au soleil.',
                'price_tnd': Decimal('12.00'),
                'price_eur': Decimal('3.60'),
                'b2b_price_tnd': Decimal('9.00'),
                'category': categories['nutrition'],
                'producer': producers['ferme-el-jem'],
                'stock_quantity': 120,
                'is_natural': True,
                'is_organic': False,
                'impact_quantity': 1,
                'impact_item': 'kit scolaire',
                'impact_school': 'GreenSchool El Jem',
                'impact_description': 'Grâce à votre achat, 1 kit scolaire sera fourni aux élèves de GreenSchool El Jem',
            },

            # BIEN-ÊTRE
            {
                'name': 'Encens Naturel au Romarin',
                'name_en': 'Natural Rosemary Incense',
                'name_ar': 'بخور طبيعي بإكليل الجبل',
                'slug': 'encens-romarin',
                'sku': gen_sku('BIEN'),
                'description': 'Bâtonnets d\'encens naturel au romarin pour une atmosphère apaisante.',
                'price_tnd': Decimal('15.00'),
                'price_eur': Decimal('4.50'),
                'b2b_price_tnd': Decimal('11.00'),
                'category': categories['bien-etre'],
                'producer': producers['coop-zaghouan'],
                'stock_quantity': 90,
                'is_natural': True,
                'is_organic': False,
                'impact_quantity': 2,
                'impact_item': 'cahiers',
                'impact_school': 'GreenSchool Zaghouan',
                'impact_description': 'Grâce à votre achat, 2 cahiers seront fournis aux élèves de GreenSchool Zaghouan',
            },
            {
                'name': 'Huile Essentielle de Lavande',
                'name_en': 'Lavender Essential Oil',
                'name_ar': 'زيت اللافندر العطري',
                'slug': 'huile-essentielle-lavande',
                'sku': gen_sku('BIEN'),
                'description': 'Huile essentielle de lavande pure, distillée artisanalement.',
                'price_tnd': Decimal('42.00'),
                'price_eur': Decimal('12.60'),
                'b2b_price_tnd': Decimal('35.00'),
                'category': categories['bien-etre'],
                'producer': producers['coop-zaghouan'],
                'stock_quantity': 45,
                'is_natural': True,
                'is_organic': True,
                'impact_quantity': 3,
                'impact_item': 'kits artistiques',
                'impact_school': 'GreenSchool Zaghouan',
                'impact_description': 'Grâce à votre achat, 3 kits artistiques seront fournis aux élèves de GreenSchool Zaghouan',
            },
            {
                'name': 'Tisane Détox aux Herbes',
                'name_en': 'Detox Herbal Tea',
                'name_ar': 'شاي أعشاب للتخلص من السموم',
                'slug': 'tisane-detox',
                'sku': gen_sku('BIEN'),
                'description': 'Mélange de plantes locales pour une cure détox naturelle.',
                'price_tnd': Decimal('22.00'),
                'price_eur': Decimal('6.60'),
                'b2b_price_tnd': Decimal('17.00'),
                'category': categories['bien-etre'],
                'producer': producers['ferme-el-jem'],
                'stock_quantity': 70,
                'is_natural': True,
                'is_organic': True,
                'impact_quantity': 2,
                'impact_item': 'repas',
                'impact_school': 'GreenSchool El Jem',
                'impact_description': 'Grâce à votre achat, 2 repas seront fournis aux élèves de GreenSchool El Jem',
            },

            # MAISON
            {
                'name': 'Bougie Parfumée Fleur d\'Oranger',
                'name_en': 'Orange Blossom Scented Candle',
                'name_ar': 'شمعة معطرة بزهر البرتقال',
                'slug': 'bougie-fleur-oranger',
                'sku': gen_sku('MAIS'),
                'description': 'Bougie artisanale en cire naturelle parfumée à la fleur d\'oranger.',
                'price_tnd': Decimal('35.00'),
                'price_eur': Decimal('10.50'),
                'b2b_price_tnd': Decimal('28.00'),
                'category': categories['maison'],
                'producer': producers['atelier-sidi-bou'],
                'stock_quantity': 55,
                'is_natural': True,
                'is_organic': False,
                'impact_quantity': 3,
                'impact_item': 'stylos',
                'impact_school': 'GreenSchool Sidi Bou Said',
                'impact_description': 'Grâce à votre achat, 3 stylos seront fournis aux élèves de GreenSchool Sidi Bou Said',
            },
            {
                'name': 'Panier Tressé Traditionnel',
                'name_en': 'Traditional Woven Basket',
                'name_ar': 'سلة تقليدية مجدولة',
                'slug': 'panier-tresse',
                'sku': gen_sku('MAIS'),
                'description': 'Panier tressé à la main par des artisanes locales. Parfait pour le rangement.',
                'price_tnd': Decimal('48.00'),
                'price_eur': Decimal('14.40'),
                'b2b_price_tnd': Decimal('40.00'),
                'category': categories['maison'],
                'producer': producers['atelier-sidi-bou'],
                'stock_quantity': 30,
                'is_natural': True,
                'is_organic': False,
                'impact_quantity': 4,
                'impact_item': 'livres',
                'impact_school': 'GreenSchool Sidi Bou Said',
                'impact_description': 'Grâce à votre achat, 4 livres seront fournis aux élèves de GreenSchool Sidi Bou Said',
            },
            {
                'name': 'Savon Ménager Écologique',
                'name_en': 'Eco-Friendly Household Soap',
                'name_ar': 'صابون منزلي بيئي',
                'slug': 'savon-menager-eco',
                'sku': gen_sku('MAIS'),
                'description': 'Savon ménager naturel pour nettoyer toute la maison sans produits chimiques.',
                'price_tnd': Decimal('14.00'),
                'price_eur': Decimal('4.20'),
                'b2b_price_tnd': Decimal('10.00'),
                'category': categories['maison'],
                'producer': producers['atelier-sidi-bou'],
                'stock_quantity': 100,
                'is_natural': True,
                'is_organic': False,
                'impact_quantity': 1,
                'impact_item': 'cahier',
                'impact_school': 'GreenSchool Sidi Bou Said',
                'impact_description': 'Grâce à votre achat, 1 cahier sera fourni aux élèves de GreenSchool Sidi Bou Said',
            },

            # COFFRETS
            {
                'name': 'Coffret Découverte Soins',
                'name_en': 'Care Discovery Set',
                'name_ar': 'علبة اكتشاف العناية',
                'slug': 'coffret-decouverte-soins',
                'sku': gen_sku('COFF'),
                'description': 'Coffret contenant nos meilleurs produits de soins en format découverte.',
                'price_tnd': Decimal('85.00'),
                'price_eur': Decimal('25.50'),
                'b2b_price_tnd': Decimal('70.00'),
                'category': categories['coffrets'],
                'producer': producers['coop-zaghouan'],
                'stock_quantity': 25,
                'is_natural': True,
                'is_organic': True,
                'impact_quantity': 8,
                'impact_item': 'kits scolaires',
                'impact_school': 'GreenSchool Zaghouan',
                'impact_description': 'Grâce à votre achat, 8 kits scolaires seront fournis aux élèves de GreenSchool Zaghouan',
            },
            {
                'name': 'Coffret Saveurs de Tunisie',
                'name_en': 'Flavors of Tunisia Set',
                'name_ar': 'علبة نكهات تونس',
                'slug': 'coffret-saveurs-tunisie',
                'sku': gen_sku('COFF'),
                'description': 'Coffret gourmand avec miel, huile d\'olive, dattes et harissa.',
                'price_tnd': Decimal('120.00'),
                'price_eur': Decimal('36.00'),
                'b2b_price_tnd': Decimal('95.00'),
                'category': categories['coffrets'],
                'producer': producers['ferme-el-jem'],
                'stock_quantity': 20,
                'is_natural': True,
                'is_organic': True,
                'impact_quantity': 12,
                'impact_item': 'repas',
                'impact_school': 'GreenSchool El Jem',
                'impact_description': 'Grâce à votre achat, 12 repas seront fournis aux élèves de GreenSchool El Jem',
            },
            {
                'name': 'Coffret Bien-être Complet',
                'name_en': 'Complete Wellness Set',
                'name_ar': 'علبة الرفاهية الكاملة',
                'slug': 'coffret-bien-etre',
                'sku': gen_sku('COFF'),
                'description': 'Tout pour se détendre: bougie, encens, huile essentielle et tisane.',
                'price_tnd': Decimal('95.00'),
                'price_eur': Decimal('28.50'),
                'b2b_price_tnd': Decimal('78.00'),
                'category': categories['coffrets'],
                'producer': producers['atelier-sidi-bou'],
                'stock_quantity': 15,
                'is_natural': True,
                'is_organic': False,
                'impact_quantity': 10,
                'impact_item': 'livres',
                'impact_school': 'GreenSchool Sidi Bou Said',
                'impact_description': 'Grâce à votre achat, 10 livres seront fournis aux élèves de GreenSchool Sidi Bou Said',
            },
        ]

        for prod_data in products_data:
            product, created = Product.objects.update_or_create(
                slug=prod_data['slug'],
                defaults=prod_data
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'  {status}: {product.name} - {product.price_tnd} DT')

        # Create sample users for reviews
        self.stdout.write('\nCreating sample users for reviews...')
        sample_users = []
        users_data = [
            {'username': 'sarah_m', 'email': 'sarah@example.com', 'first_name': 'Sarah'},
            {'username': 'ahmed_b', 'email': 'ahmed@example.com', 'first_name': 'Ahmed'},
            {'username': 'fatima_k', 'email': 'fatima@example.com', 'first_name': 'Fatima'},
            {'username': 'youssef_n', 'email': 'youssef@example.com', 'first_name': 'Youssef'},
            {'username': 'nadia_l', 'email': 'nadia@example.com', 'first_name': 'Nadia'},
            {'username': 'karim_s', 'email': 'karim@example.com', 'first_name': 'Karim'},
        ]
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                }
            )
            sample_users.append(user)
            if created:
                user.set_password('samplepassword123')
                user.save()

        # Create sample reviews
        self.stdout.write('\nCreating sample reviews...')
        reviews_data = [
            # Huile d'Argan reviews
            {'product_slug': 'huile-argan-pure', 'user': sample_users[0], 'rating': 5,
             'title': 'Produit exceptionnel!',
             'comment': 'Cette huile d\'argan est vraiment pure et de très haute qualité. Ma peau est transformée après seulement deux semaines d\'utilisation. Je recommande vivement!',
             'is_verified_purchase': True, 'is_approved': True},
            {'product_slug': 'huile-argan-pure', 'user': sample_users[1], 'rating': 5,
             'title': 'Excellent rapport qualité-prix',
             'comment': 'Très satisfait de mon achat. L\'huile sent bon et s\'absorbe facilement. Et en plus on aide une bonne cause!',
             'is_verified_purchase': True, 'is_approved': True},
            {'product_slug': 'huile-argan-pure', 'user': sample_users[2], 'rating': 4,
             'title': 'Bon produit',
             'comment': 'Bonne huile, j\'aurais aimé un flacon un peu plus grand. Mais la qualité est au rendez-vous.',
             'is_verified_purchase': True, 'is_approved': True},

            # Savon au Lait de Chèvre reviews
            {'product_slug': 'savon-lait-chevre', 'user': sample_users[3], 'rating': 5,
             'title': 'Peau de bébé!',
             'comment': 'Ce savon est une merveille. Ma peau sensible l\'adore! Plus de rougeurs ni d\'irritations.',
             'is_verified_purchase': True, 'is_approved': True},
            {'product_slug': 'savon-lait-chevre', 'user': sample_users[4], 'rating': 4,
             'title': 'Très doux',
             'comment': 'Savon très doux qui mousse bien. J\'apprécie aussi le fait qu\'il soit artisanal et naturel.',
             'is_verified_purchase': True, 'is_approved': True},

            # Miel de Forêt Bio reviews
            {'product_slug': 'miel-foret-bio', 'user': sample_users[0], 'rating': 5,
             'title': 'Le meilleur miel que j\'ai goûté',
             'comment': 'Un goût incroyable! On sent vraiment la différence avec le miel industriel. Je ne peux plus m\'en passer.',
             'is_verified_purchase': True, 'is_approved': True},
            {'product_slug': 'miel-foret-bio', 'user': sample_users[5], 'rating': 5,
             'title': 'Authentique miel de forêt',
             'comment': 'Produit d\'excellente qualité, livraison rapide. Mes enfants l\'adorent au petit-déjeuner!',
             'is_verified_purchase': True, 'is_approved': True},
            {'product_slug': 'miel-foret-bio', 'user': sample_users[2], 'rating': 4,
             'title': 'Très bon',
             'comment': 'Miel délicieux et authentique. Prix un peu élevé mais la qualité justifie.',
             'is_verified_purchase': False, 'is_approved': True},

            # Dattes Deglet Nour reviews
            {'product_slug': 'dattes-deglet-nour', 'user': sample_users[1], 'rating': 5,
             'title': 'Dattes exceptionnelles',
             'comment': 'Les meilleures dattes! Moelleuses et sucrées à souhait. Parfaites pour le ramadan.',
             'is_verified_purchase': True, 'is_approved': True},
            {'product_slug': 'dattes-deglet-nour', 'user': sample_users[4], 'rating': 5,
             'title': 'Qualité premium',
             'comment': 'Vraiment des dattes de première qualité. Emballage soigné, produit frais.',
             'is_verified_purchase': True, 'is_approved': True},

            # Huile d'Olive Extra Vierge reviews
            {'product_slug': 'huile-olive-extra-vierge', 'user': sample_users[3], 'rating': 5,
             'title': 'Un délice',
             'comment': 'Cette huile d\'olive est fantastique! Goût fruité et légèrement piquant en fin de bouche. Parfaite pour mes salades.',
             'is_verified_purchase': True, 'is_approved': True},
            {'product_slug': 'huile-olive-extra-vierge', 'user': sample_users[5], 'rating': 4,
             'title': 'Bonne huile tunisienne',
             'comment': 'Je suis content de retrouver le goût de l\'huile d\'olive de chez nous. À recommander!',
             'is_verified_purchase': True, 'is_approved': True},

            # Bougie Parfumée reviews
            {'product_slug': 'bougie-fleur-oranger', 'user': sample_users[0], 'rating': 5,
             'title': 'Parfum envoûtant',
             'comment': 'Le parfum de fleur d\'oranger est absolument divin! Ça me rappelle le jardin de ma grand-mère en Tunisie.',
             'is_verified_purchase': True, 'is_approved': True},
            {'product_slug': 'bougie-fleur-oranger', 'user': sample_users[2], 'rating': 4,
             'title': 'Belle bougie',
             'comment': 'Jolie présentation et bon parfum. La bougie brûle bien et longtemps.',
             'is_verified_purchase': True, 'is_approved': True},

            # Coffret Découverte Soins reviews
            {'product_slug': 'coffret-decouverte-soins', 'user': sample_users[4], 'rating': 5,
             'title': 'Cadeau parfait!',
             'comment': 'J\'ai offert ce coffret à ma mère pour son anniversaire. Elle a adoré! Tous les produits sont de qualité.',
             'is_verified_purchase': True, 'is_approved': True},
            {'product_slug': 'coffret-decouverte-soins', 'user': sample_users[1], 'rating': 5,
             'title': 'Excellente idée cadeau',
             'comment': 'Coffret très bien composé avec des produits variés. Le packaging est aussi très soigné.',
             'is_verified_purchase': True, 'is_approved': True},

            # Coffret Saveurs de Tunisie reviews
            {'product_slug': 'coffret-saveurs-tunisie', 'user': sample_users[5], 'rating': 5,
             'title': 'Un voyage gustatif',
             'comment': 'Ce coffret est une vraie pépite! Tous les produits sont délicieux et authentiques. C\'est comme si j\'étais en Tunisie.',
             'is_verified_purchase': True, 'is_approved': True},

            # Crème Hydratante reviews
            {'product_slug': 'creme-hydratante-olive', 'user': sample_users[3], 'rating': 4,
             'title': 'Très hydratante',
             'comment': 'Cette crème nourrit bien ma peau sèche. Le parfum est discret et agréable.',
             'is_verified_purchase': True, 'is_approved': True},

            # Tisane Détox reviews
            {'product_slug': 'tisane-detox', 'user': sample_users[0], 'rating': 4,
             'title': 'Bonne tisane',
             'comment': 'Goût agréable et effet détox ressenti. Je la prends tous les soirs avant de dormir.',
             'is_verified_purchase': True, 'is_approved': True},
        ]

        reviews_created = 0
        products_to_update = set()
        for review_data in reviews_data:
            try:
                product = Product.objects.get(slug=review_data['product_slug'])
                review, created = Review.objects.get_or_create(
                    product=product,
                    user=review_data['user'],
                    defaults={
                        'rating': review_data['rating'],
                        'title': review_data['title'],
                        'comment': review_data['comment'],
                        'is_verified_purchase': review_data['is_verified_purchase'],
                        'is_approved': review_data['is_approved'],
                    }
                )
                if created:
                    reviews_created += 1
                    products_to_update.add(product)
            except Product.DoesNotExist:
                self.stdout.write(f'  Product {review_data["product_slug"]} not found, skipping review')

        # Update product ratings
        self.stdout.write(f'  Created {reviews_created} reviews')
        self.stdout.write(f'  Updating product ratings...')
        for product in products_to_update:
            product.update_rating()
            self.stdout.write(f'    Updated: {product.name} - {product.average_rating}/5 ({product.review_count} reviews)')

        self.stdout.write(self.style.SUCCESS(f'\nSample data created successfully!'))
        self.stdout.write(f'  - {ProductCategory.objects.count()} categories')
        self.stdout.write(f'  - {Producer.objects.count()} producers')
        self.stdout.write(f'  - {Product.objects.count()} products')
        self.stdout.write(f'  - {Review.objects.count()} reviews')
