<?php
/**
 * WWC Shop Inline Translations
 *
 * Provides FR/EN/AR translations for all UI strings in templates.
 * No .po/.mo files needed — language is read from the wwc_lang cookie.
 *
 * Usage:
 *   WWC_I18n::t('Ajouter au panier')
 *   WWC_I18n::e('Ajouter au panier')   // echoes escaped
 *   WWC_I18n::attr('Ajouter au panier') // for HTML attributes
 *
 * @package WWC_Shop
 */

defined('ABSPATH') || exit;

class WWC_I18n {

    private static $lang = null;

    /**
     * Returns the active language (reads wwc_lang cookie once, caches).
     */
    public static function lang(): string {
        if (self::$lang === null) {
            $allowed = ['fr', 'en', 'ar'];
            $l = sanitize_text_field($_COOKIE['wwc_lang'] ?? 'fr');
            self::$lang = in_array($l, $allowed, true) ? $l : 'fr';
        }
        return self::$lang;
    }

    /**
     * Translations table.
     * Keys are the French source strings.
     * 'en' and 'ar' entries are only required when different from the key.
     */
    private static function strings(): array {
        return [
            // --- Format strings ---
            '%d résultat(s) pour « %s »' => [
                'en' => '%d result(s) for "%s"',
                'ar' => '%d نتيجة لـ "%s"',
            ],
            'Page %d sur %d' => [
                'en' => 'Page %d of %d',
                'ar' => 'الصفحة %d من %d',
            ],
            'Commande #%s' => [
                'en' => 'Order #%s',
                'ar' => 'الطلب #%s',
            ],
            '%d %s' => [
                'en' => '%d %s',
                'ar' => '%d %s',
            ],

            // --- Misc UI ---
            'Changer de langue' => [
                'en' => 'Change language',
                'ar' => 'تغيير اللغة',
            ],

            // --- Cart sidebar ---
            'Mon Panier' => [
                'en' => 'My Cart',
                'ar' => 'سلة التسوق',
            ],
            'Fermer' => [
                'en' => 'Close',
                'ar' => 'إغلاق',
            ],
            'Chargement...' => [
                'en' => 'Loading...',
                'ar' => 'جارٍ التحميل...',
            ],
            'Sous-total' => [
                'en' => 'Subtotal',
                'ar' => 'المجموع الفرعي',
            ],
            'Frais de livraison calculés à la caisse' => [
                'en' => 'Shipping calculated at checkout',
                'ar' => 'يُحسب الشحن عند الدفع',
            ],
            'Voir le panier' => [
                'en' => 'View Cart',
                'ar' => 'عرض السلة',
            ],
            'Passer la commande' => [
                'en' => 'Checkout',
                'ar' => 'إتمام الطلب',
            ],
            'Votre panier est vide' => [
                'en' => 'Your cart is empty',
                'ar' => 'سلة التسوق فارغة',
            ],
            'Continuer vos achats' => [
                'en' => 'Continue shopping',
                'ar' => 'مواصلة التسوق',
            ],
            'Supprimer' => [
                'en' => 'Remove',
                'ar' => 'حذف',
            ],

            // --- Product grid ---
            'Recherche' => [
                'en' => 'Search',
                'ar' => 'بحث',
            ],
            'Rechercher…' => [
                'en' => 'Search…',
                'ar' => 'ابحث…',
            ],
            'Catégorie' => [
                'en' => 'Category',
                'ar' => 'الفئة',
            ],
            'Toutes' => [
                'en' => 'All',
                'ar' => 'الكل',
            ],
            'Prix (DT)' => [
                'en' => 'Price (TND)',
                'ar' => 'السعر (د.ت)',
            ],
            'Min' => [
                'en' => 'Min',
                'ar' => 'أدنى',
            ],
            'Max' => [
                'en' => 'Max',
                'ar' => 'أقصى',
            ],
            'Filtres' => [
                'en' => 'Filters',
                'ar' => 'الفلاتر',
            ],
            'Naturel' => [
                'en' => 'Natural',
                'ar' => 'طبيعي',
            ],
            'Bio' => [
                'en' => 'Organic',
                'ar' => 'عضوي',
            ],
            'En stock seulement' => [
                'en' => 'In stock only',
                'ar' => 'المتوفر فقط',
            ],
            'Trier par' => [
                'en' => 'Sort by',
                'ar' => 'ترتيب حسب',
            ],
            'Par défaut' => [
                'en' => 'Default',
                'ar' => 'افتراضي',
            ],
            'Prix croissant' => [
                'en' => 'Price: low to high',
                'ar' => 'السعر: من الأدنى',
            ],
            'Prix décroissant' => [
                'en' => 'Price: high to low',
                'ar' => 'السعر: من الأعلى',
            ],
            'Mieux notés' => [
                'en' => 'Top rated',
                'ar' => 'الأعلى تقييماً',
            ],
            'Nouveautés' => [
                'en' => 'Newest',
                'ar' => 'الأحدث',
            ],
            'Appliquer' => [
                'en' => 'Apply',
                'ar' => 'تطبيق',
            ],
            'Effacer les filtres' => [
                'en' => 'Clear filters',
                'ar' => 'مسح الفلاتر',
            ],
            'Aucun produit trouvé.' => [
                'en' => 'No products found.',
                'ar' => 'لم يُعثر على منتجات.',
            ],
            'Rupture de stock' => [
                'en' => 'Out of stock',
                'ar' => 'نفد المخزون',
            ],
            'Ajouter au panier' => [
                'en' => 'Add to cart',
                'ar' => 'أضف إلى السلة',
            ],
            'Pagination' => [
                'en' => 'Pagination',
                'ar' => 'ترقيم الصفحات',
            ],
            'Précédent' => [
                'en' => 'Previous',
                'ar' => 'السابق',
            ],
            'Suivant' => [
                'en' => 'Next',
                'ar' => 'التالي',
            ],

            // --- Single product ---
            'En stock' => [
                'en' => 'In stock',
                'ar' => 'متوفر',
            ],
            'Stock limité' => [
                'en' => 'Low stock',
                'ar' => 'مخزون محدود',
            ],
            '100% NATURELLE' => [
                'en' => '100% NATURAL',
                'ar' => '100% طبيعي',
            ],
            'COSMÉTIQUE BIO' => [
                'en' => 'ORGANIC',
                'ar' => 'عضوي',
            ],
            'FAIT MAIN' => [
                'en' => 'HANDMADE',
                'ar' => 'صنع يدوي',
            ],
            'VEGAN' => [
                'en' => 'VEGAN',
                'ar' => 'نباتي',
            ],
            'Quantité' => [
                'en' => 'Quantity',
                'ar' => 'الكمية',
            ],
            'Impact' => [
                'en' => 'Impact',
                'ar' => 'الأثر',
            ],
            'Le producteur' => [
                'en' => 'The producer',
                'ar' => 'المنتج',
            ],
            'Complétez ce rituel avec' => [
                'en' => 'Complete this ritual with',
                'ar' => 'أكمل هذا الروتين مع',
            ],
            'Avis clients' => [
                'en' => 'Customer reviews',
                'ar' => 'آراء العملاء',
            ],
            'Laisser un avis' => [
                'en' => 'Leave a review',
                'ar' => 'اترك تقييماً',
            ],
            'Votre note' => [
                'en' => 'Your rating',
                'ar' => 'تقييمك',
            ],
            'Votre avis' => [
                'en' => 'Your review',
                'ar' => 'رأيك',
            ],
            'Envoyer mon avis' => [
                'en' => 'Submit review',
                'ar' => 'إرسال التقييم',
            ],
            'Utilisation' => [
                'en' => 'Usage',
                'ar' => 'طريقة الاستخدام',
            ],
            'Lire plus' => [
                'en' => 'Read more',
                'ar' => 'اقرأ المزيد',
            ],
            'Fabriqués par des producteurs locaux' => [
                'en' => 'Made by local producers',
                'ar' => 'مصنوع من قِبل منتجين محليين',
            ],
            'Produits 100% naturels' => [
                'en' => '100% natural products',
                'ar' => 'منتجات 100% طبيعية',
            ],
            'Commerce équitable' => [
                'en' => 'Fair trade',
                'ar' => 'تجارة عادلة',
            ],
            'Voir la vidéo' => [
                'en' => 'Watch the video',
                'ar' => 'شاهد الفيديو',
            ],
            'Nos engagements' => [
                'en' => 'Our commitments',
                'ar' => 'التزاماتنا',
            ],
            'Rejoignez le mouvement' => [
                'en' => 'Join the movement',
                'ar' => 'انضم إلى الحركة',
            ],

            // --- Auth forms ---
            'Créer un compte' => [
                'en' => 'Create account',
                'ar' => 'إنشاء حساب',
            ],
            'Prénom' => [
                'en' => 'First name',
                'ar' => 'الاسم الأول',
            ],
            'Nom' => [
                'en' => 'Last name',
                'ar' => 'الاسم الأخير',
            ],
            'Adresse e-mail' => [
                'en' => 'Email address',
                'ar' => 'البريد الإلكتروني',
            ],
            'Mot de passe' => [
                'en' => 'Password',
                'ar' => 'كلمة المرور',
            ],
            'Confirmer le mot de passe' => [
                'en' => 'Confirm password',
                'ar' => 'تأكيد كلمة المرور',
            ],
            'Type de compte' => [
                'en' => 'Account type',
                'ar' => 'نوع الحساب',
            ],
            'Particulier' => [
                'en' => 'Individual',
                'ar' => 'فرد',
            ],
            'Professionnel' => [
                'en' => 'Business (B2B)',
                'ar' => 'شركة (B2B)',
            ],
            'Nom de la société' => [
                'en' => 'Company name',
                'ar' => 'اسم الشركة',
            ],
            'Connexion' => [
                'en' => 'Login',
                'ar' => 'تسجيل الدخول',
            ],
            'Se connecter' => [
                'en' => 'Sign in',
                'ar' => 'تسجيل الدخول',
            ],
            'Déjà un compte ?' => [
                'en' => 'Already have an account?',
                'ar' => 'هل لديك حساب؟',
            ],
            'Mot de passe oublié ?' => [
                'en' => 'Forgot your password?',
                'ar' => 'نسيت كلمة المرور؟',
            ],
            'Déconnexion' => [
                'en' => 'Logout',
                'ar' => 'تسجيل الخروج',
            ],
            'Mot de passe oublié' => [
                'en' => 'Forgot password',
                'ar' => 'نسيت كلمة المرور',
            ],
            'Entrez votre adresse e-mail et nous vous enverrons un lien pour réinitialiser votre mot de passe.' => [
                'en' => 'Enter your email address and we will send you a link to reset your password.',
                'ar' => 'أدخل بريدك الإلكتروني وسنرسل لك رابطاً لإعادة تعيين كلمة المرور.',
            ],
            'Envoyer le lien' => [
                'en' => 'Send reset link',
                'ar' => 'إرسال رابط الإعادة',
            ],
            'Retour à la connexion' => [
                'en' => 'Back to login',
                'ar' => 'العودة لتسجيل الدخول',
            ],
            'Demander un nouveau lien' => [
                'en' => 'Request a new link',
                'ar' => 'طلب رابط جديد',
            ],
            'Nouveau mot de passe' => [
                'en' => 'New password',
                'ar' => 'كلمة المرور الجديدة',
            ],
            'Réinitialiser le mot de passe' => [
                'en' => 'Reset password',
                'ar' => 'إعادة تعيين كلمة المرور',
            ],
            'Lien de réinitialisation invalide ou expiré.' => [
                'en' => 'Invalid or expired reset link.',
                'ar' => 'رابط الإعادة غير صالح أو منتهي الصلاحية.',
            ],

            // --- Checkout ---
            'Récapitulatif de commande' => [
                'en' => 'Order summary',
                'ar' => 'ملخص الطلب',
            ],
            'Récapitulatif' => [
                'en' => 'Summary',
                'ar' => 'ملخص',
            ],
            'Informations de contact' => [
                'en' => 'Contact information',
                'ar' => 'معلومات الاتصال',
            ],
            'Email' => [
                'en' => 'Email',
                'ar' => 'البريد الإلكتروني',
            ],
            'Téléphone' => [
                'en' => 'Phone',
                'ar' => 'الهاتف',
            ],
            'Adresse de livraison' => [
                'en' => 'Shipping address',
                'ar' => 'عنوان الشحن',
            ],
            'Adresse' => [
                'en' => 'Address',
                'ar' => 'العنوان',
            ],
            'Ville' => [
                'en' => 'City',
                'ar' => 'المدينة',
            ],
            'Code postal' => [
                'en' => 'Postal code',
                'ar' => 'الرمز البريدي',
            ],
            'Pays' => [
                'en' => 'Country',
                'ar' => 'البلد',
            ],
            'Gouvernorat' => [
                'en' => 'Governorate',
                'ar' => 'الولاية',
            ],
            'Sélectionner' => [
                'en' => 'Select',
                'ar' => 'اختر',
            ],
            'Méthode de paiement' => [
                'en' => 'Payment method',
                'ar' => 'طريقة الدفع',
            ],
            'Paiement sécurisé' => [
                'en' => 'Secure payment',
                'ar' => 'دفع آمن',
            ],
            'Notes de commande' => [
                'en' => 'Order notes',
                'ar' => 'ملاحظات الطلب',
            ],
            'Instructions spéciales' => [
                'en' => 'Special instructions',
                'ar' => 'تعليمات خاصة',
            ],
            'optionnel' => [
                'en' => 'optional',
                'ar' => 'اختياري',
            ],
            'Confirmer la commande' => [
                'en' => 'Place order',
                'ar' => 'تأكيد الطلب',
            ],
            'Calculé selon le pays' => [
                'en' => 'Calculated by country',
                'ar' => 'يُحسب حسب البلد',
            ],
            'Livraison' => [
                'en' => 'Shipping',
                'ar' => 'الشحن',
            ],
            'Total' => [
                'en' => 'Total',
                'ar' => 'الإجمالي',
            ],
            'Produit' => [
                'en' => 'Product',
                'ar' => 'المنتج',
            ],
            'Qté' => [
                'en' => 'Qty',
                'ar' => 'الكمية',
            ],
            'Prix unitaire' => [
                'en' => 'Unit price',
                'ar' => 'سعر الوحدة',
            ],
            'Prix' => [
                'en' => 'Price',
                'ar' => 'السعر',
            ],
            'Entreprise' => [
                'en' => 'Company',
                'ar' => 'الشركة',
            ],
            'Instructions de virement bancaire' => [
                'en' => 'Bank transfer instructions',
                'ar' => 'تعليمات التحويل البنكي',
            ],
            'Bénéficiaire' => [
                'en' => 'Beneficiary',
                'ar' => 'المستفيد',
            ],
            'Montant' => [
                'en' => 'Amount',
                'ar' => 'المبلغ',
            ],
            'Banque' => [
                'en' => 'Bank',
                'ar' => 'البنك',
            ],
            'Référence (obligatoire)' => [
                'en' => 'Reference (required)',
                'ar' => 'المرجع (مطلوب)',
            ],
            'Votre commande est en attente de paiement. Veuillez effectuer le virement avec les informations suivantes :' => [
                'en' => 'Your order is awaiting payment. Please make the transfer with the following details:',
                'ar' => 'طلبك في انتظار الدفع. يرجى إجراء التحويل بالمعلومات التالية:',
            ],
            'Votre commande sera traitée dès réception du virement. Pensez à indiquer le numéro de commande comme référence.' => [
                'en' => 'Your order will be processed upon receipt of the transfer. Please include the order number as reference.',
                'ar' => 'سيتم معالجة طلبك عند استلام التحويل. يرجى ذكر رقم الطلب كمرجع.',
            ],

            // --- Order success ---
            'Merci pour votre commande !' => [
                'en' => 'Thank you for your order!',
                'ar' => 'شكراً على طلبك!',
            ],
            'Commande confirmée !' => [
                'en' => 'Order confirmed!',
                'ar' => 'تم تأكيد الطلب!',
            ],
            'Merci pour votre achat. Vous recevrez bientôt un email de confirmation.' => [
                'en' => 'Thank you for your purchase. You will receive a confirmation email shortly.',
                'ar' => 'شكراً لشرائك. ستتلقى بريداً إلكترونياً للتأكيد قريباً.',
            ],
            'Un email de confirmation a été envoyé à votre adresse.' => [
                'en' => 'A confirmation email has been sent to your address.',
                'ar' => 'تم إرسال بريد إلكتروني للتأكيد إلى عنوانك.',
            ],
            'Commande' => [
                'en' => 'Order',
                'ar' => 'الطلب',
            ],
            'Continuer mes achats' => [
                'en' => 'Continue shopping',
                'ar' => 'مواصلة التسوق',
            ],
            'Voir mes commandes' => [
                'en' => 'View my orders',
                'ar' => 'عرض طلباتي',
            ],

            // --- Customer dashboard ---
            'Bienvenue dans votre espace personnel. Suivez votre impact et vos commandes.' => [
                'en' => 'Welcome to your personal space. Track your impact and orders.',
                'ar' => 'مرحباً بك في مساحتك الشخصية. تابع أثرك وطلباتك.',
            ],
            'Votre Impact' => [
                'en' => 'Your Impact',
                'ar' => 'أثرك',
            ],
            'Votre impact' => [
                'en' => 'Your impact',
                'ar' => 'أثرك',
            ],
            'Notre Impact Collectif' => [
                'en' => 'Our Collective Impact',
                'ar' => 'أثرنا الجماعي',
            ],
            'Détail de votre impact' => [
                'en' => 'Your impact breakdown',
                'ar' => 'تفاصيل أثرك',
            ],
            'Commandes récentes' => [
                'en' => 'Recent orders',
                'ar' => 'الطلبات الأخيرة',
            ],
            'commandes' => [
                'en' => 'orders',
                'ar' => 'طلبات',
            ],
            'commandes solidaires' => [
                'en' => 'solidarity orders',
                'ar' => 'طلبات تضامنية',
            ],
            'Articles' => [
                'en' => 'Items',
                'ar' => 'عناصر',
            ],
            'items fournis' => [
                'en' => 'items provided',
                'ar' => 'عناصر مُقدَّمة',
            ],
            'items fournis aux étudiants' => [
                'en' => 'items provided to students',
                'ar' => 'عناصر مُقدَّمة للطلاب',
            ],
            'Impact social direct' => [
                'en' => 'Direct social impact',
                'ar' => 'الأثر الاجتماعي المباشر',
            ],
            'distribués' => [
                'en' => 'distributed',
                'ar' => 'موزعة',
            ],
            'fourni(e)s à des étudiants' => [
                'en' => 'provided to students',
                'ar' => 'مُقدَّمة للطلاب',
            ],
            'Événements Récents' => [
                'en' => 'Recent Events',
                'ar' => 'الأحداث الأخيرة',
            ],
            'Statut' => [
                'en' => 'Status',
                'ar' => 'الحالة',
            ],
            'Date' => [
                'en' => 'Date',
                'ar' => 'التاريخ',
            ],
            'Suivi' => [
                'en' => 'Tracking',
                'ar' => 'التتبع',
            ],
            'Retour à mon compte' => [
                'en' => 'Back to my account',
                'ar' => 'العودة إلى حسابي',
            ],
            'Découvrir nos produits' => [
                'en' => 'Discover our products',
                'ar' => 'اكتشف منتجاتنا',
            ],
            'Chaque achat contribue à améliorer la vie des étudiants de GreenSchool.' => [
                'en' => 'Every purchase helps improve the lives of GreenSchool students.',
                'ar' => 'كل عملية شراء تساهم في تحسين حياة طلاب GreenSchool.',
            ],
            'Votre impact avec cette commande:' => [
                'en' => 'Your impact with this order:',
                'ar' => 'أثرك من هذا الطلب:',
            ],

            // --- AJAX messages (class-cart.php) ---
            'Product added to cart' => [
                'en' => 'Product added to cart',
                'ar' => 'تمت إضافة المنتج إلى السلة',
            ],
            'Product removed from cart' => [
                'en' => 'Product removed from cart',
                'ar' => 'تمت إزالة المنتج من السلة',
            ],
            'Cart updated' => [
                'en' => 'Cart updated',
                'ar' => 'تم تحديث السلة',
            ],
            'Cart cleared' => [
                'en' => 'Cart cleared',
                'ar' => 'تم تفريغ السلة',
            ],
            'Invalid product' => [
                'en' => 'Invalid product',
                'ar' => 'منتج غير صالح',
            ],
            'Invalid cart item' => [
                'en' => 'Invalid cart item',
                'ar' => 'عنصر سلة غير صالح',
            ],
            'Please enter a coupon code' => [
                'en' => 'Please enter a coupon code',
                'ar' => 'يرجى إدخال رمز القسيمة',
            ],
            'Coupon functionality coming soon' => [
                'en' => 'Coupon functionality coming soon',
                'ar' => 'ميزة القسائم قادمة قريباً',
            ],
            'Retiré des favoris' => [
                'en' => 'Removed from wishlist',
                'ar' => 'تمت الإزالة من المفضلة',
            ],
            'Ajouté aux favoris' => [
                'en' => 'Added to wishlist',
                'ar' => 'تمت الإضافة إلى المفضلة',
            ],
            'Veuillez sélectionner une note entre 1 et 5.' => [
                'en' => 'Please select a rating between 1 and 5.',
                'ar' => 'يرجى اختيار تقييم بين 1 و5.',
            ],
            'Avis soumis. Il sera publié après modération.' => [
                'en' => 'Review submitted. It will be published after moderation.',
                'ar' => 'تم إرسال التقييم. سيُنشر بعد المراجعة.',
            ],
            'Impossible de créer la session de paiement.' => [
                'en' => 'Unable to create payment session.',
                'ar' => 'تعذّر إنشاء جلسة الدفع.',
            ],
            'Commande créée' => [
                'en' => 'Order created',
                'ar' => 'تم إنشاء الطلب',
            ],
            'Pas encore de compte ?' => [
                'en' => 'No account yet?',
                'ar' => 'ليس لديك حساب؟',
            ],
            "S'inscrire" => [
                'en' => 'Sign up',
                'ar' => 'التسجيل',
            ],
            "Calculée à l'étape suivante" => [
                'en' => 'Calculated at next step',
                'ar' => 'يُحسب في الخطوة التالية',
            ],
            "Grâce à votre achat, vous contribuez directement à l'initiative GreenSchool :" => [
                'en' => 'Thanks to your purchase, you directly contribute to the GreenSchool initiative:',
                'ar' => 'بفضل شرائك، تساهم مباشرة في مبادرة GreenSchool:',
            ],
            "Complément d'adresse" => [
                'en' => 'Address line 2',
                'ar' => 'تفاصيل إضافية للعنوان',
            ],
            "d'achats" => [
                'en' => 'in purchases',
                'ar' => 'في المشتريات',
            ],
            "Vous n'avez pas encore passé de commande." => [
                'en' => 'You have not placed any orders yet.',
                'ar' => 'لم تقم بأي طلب بعد.',
            ],
            "Ce qu'il y a dans mon produit" => [
                'en' => 'What is in my product',
                'ar' => 'مكونات منتجي',
            ],
            'Grâce à cet achat, %1$d %2$s peuvent être fournies à des enfants de %3$s' => [
                'en' => 'Thanks to this purchase, %1$d %2$s can be provided to children at %3$s',
                'ar' => 'بفضل هذا الشراء، يمكن توفير %1$d %2$s لأطفال %3$s',
            ],
        ];
    }

    /**
     * Translate a string. Returns the French key unchanged if no translation found.
     */
    public static function t(string $key): string {
        $lang = self::lang();
        if ($lang === 'fr') {
            return $key;
        }
        $strings = self::strings();
        return $strings[$key][$lang] ?? $key;
    }

    /**
     * Echo the translated string, HTML-escaped.
     */
    public static function e(string $key): void {
        echo esc_html(self::t($key));
    }

    /**
     * Return the translated string, HTML-escaped (for use in attributes).
     */
    public static function attr(string $key): string {
        return esc_attr(self::t($key));
    }
}
