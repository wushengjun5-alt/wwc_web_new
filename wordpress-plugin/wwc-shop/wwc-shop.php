<?php
/**
 * Plugin Name: WWC Shop - Wallah We Can E-Commerce
 * Plugin URI: https://wallahwecan.org
 * Description: E-commerce platform for GreenSchool products with social impact tracking. Integrates with Django REST API backend.
 * Version: 1.0.0
 * Author: Wallah We Can
 * Author URI: https://wallahwecan.org
 * Text Domain: wwc-shop
 * Domain Path: /languages
 * Requires at least: 6.0
 * Requires PHP: 8.0
 * License: GPL v2 or later
 */

// Prevent direct access
defined('ABSPATH') || exit;

// Plugin constants
define('WWC_SHOP_VERSION', '1.0.0');
define('WWC_SHOP_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('WWC_SHOP_PLUGIN_URL', plugin_dir_url(__FILE__));
define('WWC_SHOP_PLUGIN_BASENAME', plugin_basename(__FILE__));

/**
 * Main WWC Shop Class
 */
final class WWC_Shop {

    /**
     * Single instance of the class
     */
    private static $instance = null;

    /**
     * API Client instance
     */
    public $api;

    /**
     * Cart instance
     */
    public $cart;

    /**
     * Auth instance
     */
    public $auth;

    /**
     * Get single instance of the class
     */
    public static function get_instance() {
        if (null === self::$instance) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    /**
     * Constructor
     */
    private function __construct() {
        $this->load_dependencies();
        $this->init_hooks();
    }

    /**
     * Load required files
     */
    private function load_dependencies() {
        // Core classes
        require_once WWC_SHOP_PLUGIN_DIR . 'includes/class-api-client.php';
        require_once WWC_SHOP_PLUGIN_DIR . 'includes/class-cart.php';
        require_once WWC_SHOP_PLUGIN_DIR . 'includes/class-product.php';
        require_once WWC_SHOP_PLUGIN_DIR . 'includes/class-checkout.php';
        require_once WWC_SHOP_PLUGIN_DIR . 'includes/class-impact.php';
        require_once WWC_SHOP_PLUGIN_DIR . 'includes/class-auth.php';

        // Admin classes (only in admin)
        if (is_admin()) {
            require_once WWC_SHOP_PLUGIN_DIR . 'admin/class-products-admin.php';
        }

        // Initialize API client
        $this->api  = new WWC_API_Client();
        $this->cart = new WWC_Cart($this->api);
        $this->auth = new WWC_Auth($this->api);
    }

    /**
     * Initialize hooks
     */
    private function init_hooks() {
        // Load text domain
        add_action('plugins_loaded', [$this, 'load_textdomain']);

        // Enqueue assets on frontend
        add_action('wp_enqueue_scripts', [$this, 'enqueue_assets']);

        // Register shortcodes
        add_action('init', [$this, 'register_shortcodes']);

        // AJAX handlers
        $this->register_ajax_handlers();

        // Add cart sidebar to footer
        add_action('wp_footer', [$this, 'render_cart_sidebar']);

        // Inject cart count badge into theme nav menus
        add_filter('wp_nav_menu_items', [$this, 'add_cart_count_to_menu'], 10, 2);

        // Admin menu
        add_action('admin_menu', [$this, 'add_admin_menu']);

        // Register settings
        add_action('admin_init', [$this, 'register_settings']);
    }

    /**
     * Load plugin textdomain
     */
    public function load_textdomain() {
        load_plugin_textdomain(
            'wwc-shop',
            false,
            dirname(WWC_SHOP_PLUGIN_BASENAME) . '/languages'
        );
    }

    /**
     * Enqueue frontend assets
     */
    public function enqueue_assets() {
        // Only load on relevant pages
        if (!$this->should_load_assets()) {
            return;
        }

        // Main stylesheet
        wp_enqueue_style(
            'wwc-shop-styles',
            WWC_SHOP_PLUGIN_URL . 'assets/css/shop.css',
            [],
            WWC_SHOP_VERSION
        );

        // Cart JavaScript
        wp_enqueue_script(
            'wwc-shop-cart',
            WWC_SHOP_PLUGIN_URL . 'assets/js/cart.js',
            ['jquery'],
            WWC_SHOP_VERSION,
            true
        );

        // Product JavaScript
        wp_enqueue_script(
            'wwc-shop-product',
            WWC_SHOP_PLUGIN_URL . 'assets/js/product.js',
            ['jquery'],
            WWC_SHOP_VERSION,
            true
        );

        // Auth JavaScript
        wp_enqueue_script(
            'wwc-shop-auth',
            WWC_SHOP_PLUGIN_URL . 'assets/js/auth.js',
            ['jquery', 'wwc-shop-cart'],
            WWC_SHOP_VERSION,
            true
        );

        // Localize scripts
        wp_localize_script('wwc-shop-cart', 'wwcShop', [
            'ajaxUrl' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('wwc-shop-nonce'),
            'apiUrl' => get_option('wwc_api_url', 'https://api.wallahwecan.org'),
            'currency' => get_option('wwc_default_currency', 'TND'),
            'cartUrl' => home_url('/cart/'),
            'checkoutUrl' => home_url('/checkout/'),
            'i18n' => [
                'addedToCart' => __('Product added to cart', 'wwc-shop'),
                'removedFromCart' => __('Product removed from cart', 'wwc-shop'),
                'cartUpdated' => __('Cart updated', 'wwc-shop'),
                'error' => __('An error occurred', 'wwc-shop'),
                'outOfStock' => __('Out of stock', 'wwc-shop'),
            ]
        ]);
    }

    /**
     * Check if assets should be loaded
     */
    private function should_load_assets() {
        // Load on all pages for cart functionality
        return true;
    }

    /**
     * Register shortcodes
     */
    public function register_shortcodes() {
        add_shortcode('wwc_products', [$this, 'products_shortcode']);
        add_shortcode('wwc_product', [$this, 'single_product_shortcode']);
        add_shortcode('wwc_categories', [$this, 'categories_shortcode']);
        add_shortcode('wwc_cart', [$this, 'cart_shortcode']);
        add_shortcode('wwc_checkout', [$this, 'checkout_shortcode']);
        add_shortcode('wwc_checkout_success', [$this, 'checkout_success_shortcode']);
        add_shortcode('wwc_customer_dashboard', [$this, 'dashboard_shortcode']);
        add_shortcode('wwc_impact', [$this, 'impact_shortcode']);
        add_shortcode('wwc_order_detail', [$this, 'order_detail_shortcode']);
        add_shortcode('wwc_login', [$this, 'login_shortcode']);
        add_shortcode('wwc_register', [$this, 'register_shortcode']);
        add_shortcode('wwc_forgot_password', [$this, 'forgot_password_shortcode']);
        add_shortcode('wwc_reset_password', [$this, 'reset_password_shortcode']);
    }

    /**
     * Products grid shortcode
     */
    public function products_shortcode($atts) {
        $atts = shortcode_atts([
            'category' => '',
            'featured' => '',
            'limit'    => 12,
            'columns'  => 3,
            'filters'  => 'false', // set to "true" to show filter sidebar
        ], $atts, 'wwc_products');

        // Build API params — merge shortcode atts with URL query params (user-applied filters)
        $params = ['page_size' => intval($atts['limit'])];

        if (!empty($atts['category'])) {
            $params['category'] = sanitize_text_field($atts['category']);
        }
        if ($atts['featured'] === 'true') {
            $params['is_featured'] = 'true';
        }

        // Allow URL query params to override/extend (search, filters, pagination)
        $allowed_query_params = ['category', 'search', 'ordering', 'min_price', 'max_price',
                                 'is_natural', 'is_organic', 'in_stock', 'page'];
        foreach ($allowed_query_params as $qp) {
            $val = sanitize_text_field($_GET[$qp] ?? '');
            if ($val !== '') {
                $params[$qp] = $val;
            }
        }

        $response  = $this->api->get_products($params, true);
        $show_filters = $atts['filters'] === 'true';

        if (is_wp_error($response)) {
            return '<p class="wwc-error">' . esc_html__('Impossible de charger les produits.', 'wwc-shop') . '</p>';
        }

        $products   = $response['results'] ?? $response;
        $total      = $response['count'] ?? count($products);
        $page_size  = $params['page_size'];
        $current_page = max(1, intval($_GET['page'] ?? 1));
        $total_pages  = $page_size > 0 ? ceil($total / $page_size) : 1;

        // Fetch categories for filter sidebar
        $categories = $show_filters ? $this->api->get_categories() : [];
        if (is_wp_error($categories)) $categories = [];

        ob_start();
        include WWC_SHOP_PLUGIN_DIR . 'templates/product-grid.php';
        return ob_get_clean();
    }

    /**
     * Single product shortcode
     */
    public function single_product_shortcode($atts) {
        $atts = shortcode_atts([
            'slug' => '',
            'id' => '',
        ], $atts, 'wwc_product');

        $slug = !empty($atts['slug']) ? $atts['slug'] : get_query_var('product_slug');

        if (empty($slug) && empty($atts['id'])) {
            return '<p class="wwc-error">' . esc_html__('Product not found', 'wwc-shop') . '</p>';
        }

        $product = $this->api->get_product($slug);

        if (is_wp_error($product) || empty($product)) {
            return '<p class="wwc-error">' . esc_html__('Product not found', 'wwc-shop') . '</p>';
        }

        ob_start();
        include WWC_SHOP_PLUGIN_DIR . 'templates/single-product.php';
        return ob_get_clean();
    }

    /**
     * Categories navigation shortcode
     */
    public function categories_shortcode($atts) {
        $atts = shortcode_atts([
            'menu' => 'true',
        ], $atts, 'wwc_categories');

        $params = [];
        if ($atts['menu'] === 'true') {
            $params['menu'] = 'true';
            $params['parent_only'] = 'true';
        }

        $categories = $this->api->get_categories($params);

        if (is_wp_error($categories)) {
            return '';
        }

        ob_start();
        include WWC_SHOP_PLUGIN_DIR . 'templates/categories-nav.php';
        return ob_get_clean();
    }

    /**
     * Cart page shortcode
     */
    public function cart_shortcode($atts) {
        ob_start();
        include WWC_SHOP_PLUGIN_DIR . 'templates/cart-page.php';
        return ob_get_clean();
    }

    /**
     * Checkout page shortcode
     */
    public function checkout_shortcode($atts) {
        ob_start();
        include WWC_SHOP_PLUGIN_DIR . 'templates/checkout.php';
        return ob_get_clean();
    }

    /**
     * Checkout success / order confirmation shortcode
     */
    public function checkout_success_shortcode($atts) {
        ob_start();
        include WWC_SHOP_PLUGIN_DIR . 'templates/checkout-success.php';
        return ob_get_clean();
    }

    /**
     * Customer dashboard shortcode
     */
    public function dashboard_shortcode($atts) {
        ob_start();
        include WWC_SHOP_PLUGIN_DIR . 'templates/customer-dashboard.php';
        return ob_get_clean();
    }

    /**
     * Login shortcode
     */
    public function login_shortcode($atts) {
        if ($this->api->is_authenticated()) {
            return '<p>' . sprintf(
                __('You are already logged in. <a href="%s">Go to your account</a>.', 'wwc-shop'),
                esc_url(home_url('/mon-compte/'))
            ) . '</p>';
        }
        ob_start();
        include WWC_SHOP_PLUGIN_DIR . 'templates/auth-login.php';
        return ob_get_clean();
    }

    /**
     * Register shortcode
     */
    public function register_shortcode($atts) {
        if ($this->api->is_authenticated()) {
            return '<p>' . sprintf(
                __('You are already logged in. <a href="%s">Go to your account</a>.', 'wwc-shop'),
                esc_url(home_url('/mon-compte/'))
            ) . '</p>';
        }
        ob_start();
        include WWC_SHOP_PLUGIN_DIR . 'templates/auth-register.php';
        return ob_get_clean();
    }

    /**
     * Forgot password shortcode
     */
    public function forgot_password_shortcode($atts) {
        ob_start();
        include WWC_SHOP_PLUGIN_DIR . 'templates/auth-forgot-password.php';
        return ob_get_clean();
    }

    /**
     * Reset password confirm shortcode
     */
    public function reset_password_shortcode($atts) {
        ob_start();
        include WWC_SHOP_PLUGIN_DIR . 'templates/auth-reset-password.php';
        return ob_get_clean();
    }

    /**
     * Impact section shortcode
     */
    public function impact_shortcode($atts) {
        $atts = shortcode_atts([
            'limit' => 5,
        ], $atts, 'wwc_impact');

        $impact = $this->api->get_impact_summary();

        if (is_wp_error($impact)) {
            return '';
        }

        ob_start();
        include WWC_SHOP_PLUGIN_DIR . 'templates/impact-section.php';
        return ob_get_clean();
    }

    /**
     * Register AJAX handlers
     */
    private function register_ajax_handlers() {
        $cart_actions = [
            'wwc_add_to_cart',
            'wwc_update_cart',
            'wwc_remove_from_cart',
            'wwc_get_cart',
            'wwc_clear_cart',
            'wwc_apply_coupon',
            'wwc_checkout',
            'wwc_toggle_wishlist',
            'wwc_add_review',
        ];

        foreach ($cart_actions as $action) {
            add_action("wp_ajax_{$action}", [$this->cart, str_replace('wwc_', 'ajax_', $action)]);
            add_action("wp_ajax_nopriv_{$action}", [$this->cart, str_replace('wwc_', 'ajax_', $action)]);
        }

        // Auth AJAX actions (available to both logged-in and guests)
        $auth_actions = [
            'wwc_register'               => 'ajax_register',
            'wwc_login'                  => 'ajax_login',
            'wwc_logout'                 => 'ajax_logout',
            'wwc_password_reset_request' => 'ajax_password_reset_request',
            'wwc_password_reset_confirm' => 'ajax_password_reset_confirm',
        ];

        foreach ($auth_actions as $action => $method) {
            add_action("wp_ajax_{$action}",        [$this->auth, $method]);
            add_action("wp_ajax_nopriv_{$action}", [$this->auth, $method]);
        }
    }

    /**
     * Render cart sidebar
     */
    public function render_cart_sidebar() {
        include WWC_SHOP_PLUGIN_DIR . 'templates/cart-sidebar.php';
    }

    /**
     * Add admin menu
     */
    public function add_admin_menu() {
        add_menu_page(
            __('WWC Shop', 'wwc-shop'),
            __('WWC Shop', 'wwc-shop'),
            'manage_options',
            'wwc-shop',
            [$this, 'admin_page'],
            'dashicons-cart',
            56
        );

        add_submenu_page(
            'wwc-shop',
            __('Settings', 'wwc-shop'),
            __('Settings', 'wwc-shop'),
            'manage_options',
            'wwc-shop-settings',
            [$this, 'settings_page']
        );
    }

    /**
     * Admin dashboard page
     */
    public function admin_page() {
        include WWC_SHOP_PLUGIN_DIR . 'admin/dashboard.php';
    }

    /**
     * Settings page
     */
    public function settings_page() {
        include WWC_SHOP_PLUGIN_DIR . 'admin/settings.php';
    }

    /**
     * Register plugin settings
     */
    public function register_settings() {
        register_setting('wwc_shop_settings', 'wwc_api_url');
        register_setting('wwc_shop_settings', 'wwc_api_key');
        register_setting('wwc_shop_settings', 'wwc_admin_api_key');
        register_setting('wwc_shop_settings', 'wwc_default_currency');
        register_setting('wwc_shop_settings', 'wwc_stripe_public_key');
        register_setting('wwc_shop_settings', 'wwc_stripe_secret_key');

        add_settings_section(
            'wwc_api_settings',
            __('API Settings', 'wwc-shop'),
            null,
            'wwc-shop-settings'
        );

        add_settings_field(
            'wwc_api_url',
            __('API URL', 'wwc-shop'),
            [$this, 'render_text_field'],
            'wwc-shop-settings',
            'wwc_api_settings',
            ['field' => 'wwc_api_url', 'default' => 'https://api.wallahwecan.org']
        );

        add_settings_field(
            'wwc_admin_api_key',
            __('Admin API Key', 'wwc-shop'),
            [$this, 'render_password_field'],
            'wwc-shop-settings',
            'wwc_api_settings',
            [
                'field' => 'wwc_admin_api_key',
                'description' => __('Secret key for admin product management. Must match ADMIN_API_KEY in Django settings.', 'wwc-shop')
            ]
        );

        add_settings_field(
            'wwc_default_currency',
            __('Default Currency', 'wwc-shop'),
            [$this, 'render_select_field'],
            'wwc-shop-settings',
            'wwc_api_settings',
            [
                'field' => 'wwc_default_currency',
                'options' => ['TND' => 'TND (Tunisian Dinar)', 'EUR' => 'EUR (Euro)']
            ]
        );
    }

    /**
     * Render text field
     */
    public function render_text_field($args) {
        $value = get_option($args['field'], $args['default'] ?? '');
        printf(
            '<input type="text" name="%s" value="%s" class="regular-text">',
            esc_attr($args['field']),
            esc_attr($value)
        );
        if (!empty($args['description'])) {
            printf('<p class="description">%s</p>', esc_html($args['description']));
        }
    }

    /**
     * Render password field
     */
    public function render_password_field($args) {
        $value = get_option($args['field'], '');
        printf(
            '<input type="password" name="%s" value="%s" class="regular-text" autocomplete="new-password">',
            esc_attr($args['field']),
            esc_attr($value)
        );
        if (!empty($args['description'])) {
            printf('<p class="description">%s</p>', esc_html($args['description']));
        }
    }

    /**
     * Append cart count badge to nav menu
     */
    public function add_cart_count_to_menu($items, $args) {
        $cart_link = sprintf(
            '<li class="wwc-cart-nav-item"><a href="%s" class="wwc-cart-toggle" data-action="open-cart" aria-label="%s">%s <span class="wwc-cart-count">0</span></a></li>',
            esc_url(home_url('/cart/')),
            esc_attr__('Panier', 'wwc-shop'),
            esc_html__('Panier', 'wwc-shop')
        );
        return $items . $cart_link;
    }

    /**
     * Order detail shortcode
     */
    public function order_detail_shortcode($atts) {
        if (!$this->api->is_authenticated()) {
            $login_url = add_query_arg('redirect', urlencode(get_permalink()), home_url('/connexion/'));
            return '<p>' . sprintf(
                __('Veuillez <a href="%s">vous connecter</a> pour voir cette commande.', 'wwc-shop'),
                esc_url($login_url)
            ) . '</p>';
        }

        $order_number = sanitize_text_field($_GET['order'] ?? '');
        if (empty($order_number)) {
            return '<p class="wwc-error">' . esc_html__('Numéro de commande manquant.', 'wwc-shop') . '</p>';
        }

        ob_start();
        include WWC_SHOP_PLUGIN_DIR . 'templates/order-detail.php';
        return ob_get_clean();
    }

    /**
     * Render select field
     */
    public function render_select_field($args) {
        $value = get_option($args['field'], '');
        echo '<select name="' . esc_attr($args['field']) . '">';
        foreach ($args['options'] as $key => $label) {
            printf(
                '<option value="%s" %s>%s</option>',
                esc_attr($key),
                selected($value, $key, false),
                esc_html($label)
            );
        }
        echo '</select>';
    }
}

/**
 * Initialize the plugin
 */
function wwc_shop() {
    return WWC_Shop::get_instance();
}

// Start the plugin
wwc_shop();

/**
 * Activation hook
 */
register_activation_hook(__FILE__, function() {
    // Set default options
    add_option('wwc_api_url', 'https://api.wallahwecan.org');
    add_option('wwc_default_currency', 'TND');

    // Flush rewrite rules
    flush_rewrite_rules();
});

/**
 * Deactivation hook
 */
register_deactivation_hook(__FILE__, function() {
    // Flush rewrite rules
    flush_rewrite_rules();
});
