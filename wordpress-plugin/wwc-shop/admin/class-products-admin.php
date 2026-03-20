<?php
/**
 * WWC Shop Products Admin
 *
 * Handles product management in WordPress admin for marketing users.
 * Communicates with Django REST API using admin API key.
 *
 * @package WWC_Shop
 */

defined('ABSPATH') || exit;

/**
 * Products Admin Class
 */
class WWC_Products_Admin {

    /**
     * API Client instance
     *
     * @var WWC_API_Client
     */
    private $api;

    /**
     * Admin API key
     *
     * @var string
     */
    private $admin_api_key;

    /**
     * Constructor
     */
    public function __construct() {
        $this->admin_api_key = get_option('wwc_admin_api_key', '');

        add_action('admin_menu', [$this, 'add_menu_pages']);
        add_action('admin_enqueue_scripts', [$this, 'enqueue_admin_assets']);
        add_action('wp_ajax_wwc_admin_save_product', [$this, 'ajax_save_product']);
        add_action('wp_ajax_wwc_admin_delete_product', [$this, 'ajax_delete_product']);
        add_action('wp_ajax_wwc_admin_bulk_action', [$this, 'ajax_bulk_action']);
        add_action('wp_ajax_wwc_admin_upload_image', [$this, 'ajax_upload_image']);
        add_action('wp_ajax_wwc_admin_delete_image', [$this, 'ajax_delete_image']);
        add_action('wp_ajax_wwc_admin_set_primary_image', [$this, 'ajax_set_primary_image']);
        add_action('wp_ajax_wwc_admin_get_product', [$this, 'ajax_get_product']);
        add_action('wp_ajax_wwc_admin_duplicate_product', [$this, 'ajax_duplicate_product']);
    }

    /**
     * Add admin menu pages
     */
    public function add_menu_pages() {
        // Products list page
        add_submenu_page(
            'wwc-shop',
            __('Products', 'wwc-shop'),
            __('Products', 'wwc-shop'),
            'manage_options',
            'wwc-products',
            [$this, 'render_products_page'],
            1
        );

        // Add/Edit product page (hidden from menu)
        add_submenu_page(
            null, // No parent - hidden
            __('Edit Product', 'wwc-shop'),
            __('Edit Product', 'wwc-shop'),
            'manage_options',
            'wwc-product-edit',
            [$this, 'render_product_edit_page']
        );
    }

    /**
     * Enqueue admin assets
     */
    public function enqueue_admin_assets($hook) {
        // Only load on our admin pages
        if (!in_array($hook, ['wwc-shop_page_wwc-products', 'admin_page_wwc-product-edit'])) {
            return;
        }

        // WordPress media uploader
        wp_enqueue_media();

        // Admin styles
        wp_enqueue_style(
            'wwc-admin-products',
            WWC_SHOP_PLUGIN_URL . 'admin/css/products-admin.css',
            [],
            WWC_SHOP_VERSION
        );

        // Admin scripts
        wp_enqueue_script(
            'wwc-admin-products',
            WWC_SHOP_PLUGIN_URL . 'admin/js/products-admin.js',
            ['jquery', 'wp-util'],
            WWC_SHOP_VERSION,
            true
        );

        // Localize script
        wp_localize_script('wwc-admin-products', 'wwcAdminProducts', [
            'ajaxUrl' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('wwc-admin-products'),
            'apiUrl' => rtrim(get_option('wwc_api_url', 'http://127.0.0.1:8000'), '/') . '/api/v1',
            'adminApiKey' => $this->admin_api_key,
            'productsListUrl' => admin_url('admin.php?page=wwc-products'),
            'editUrl' => admin_url('admin.php?page=wwc-product-edit'),
            'i18n' => [
                'confirmDelete' => __('Are you sure you want to delete this product?', 'wwc-shop'),
                'confirmBulkDelete' => __('Are you sure you want to delete the selected products?', 'wwc-shop'),
                'saving' => __('Saving...', 'wwc-shop'),
                'saved' => __('Product saved successfully!', 'wwc-shop'),
                'deleted' => __('Product deleted successfully!', 'wwc-shop'),
                'error' => __('An error occurred. Please try again.', 'wwc-shop'),
                'uploadError' => __('Image upload failed.', 'wwc-shop'),
                'selectImage' => __('Select or Upload Image', 'wwc-shop'),
                'useImage' => __('Use this image', 'wwc-shop'),
                'frRequired' => __('French name is required.', 'wwc-shop'),
                'skuRequired' => __('SKU is required.', 'wwc-shop'),
                'priceRequired' => __('Price (TND) is required.', 'wwc-shop'),
                'categoryRequired' => __('Category is required.', 'wwc-shop'),
            ]
        ]);
    }

    /**
     * Make admin API request
     *
     * @param string $endpoint API endpoint
     * @param string $method HTTP method
     * @param array $data Request data
     * @return array|WP_Error Response data or error
     */
    private function admin_api_request($endpoint, $method = 'GET', $data = []) {
        $api_url = rtrim(get_option('wwc_api_url', 'http://127.0.0.1:8000'), '/');
        $url = $api_url . '/api/v1/admin/' . ltrim($endpoint, '/');

        $args = [
            'method' => $method,
            'timeout' => 30,
            'headers' => [
                'Authorization' => 'Api-Key ' . $this->admin_api_key,
                'Content-Type' => 'application/json',
                'Accept' => 'application/json',
            ],
        ];

        if ($method === 'GET' && !empty($data)) {
            $url = add_query_arg($data, $url);
        } elseif (!empty($data)) {
            $args['body'] = json_encode($data);
        }

        $response = wp_remote_request($url, $args);

        if (is_wp_error($response)) {
            return $response;
        }

        $code = wp_remote_retrieve_response_code($response);
        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);

        if ($code >= 400) {
            $error_msg = isset($data['detail']) ? $data['detail'] :
                        (isset($data['error']) ? $data['error'] : 'API Error');
            return new WP_Error('api_error', $error_msg, ['status' => $code, 'body' => $data]);
        }

        return $data;
    }

    /**
     * Render products list page
     */
    public function render_products_page() {
        // Get filter parameters
        $search = isset($_GET['s']) ? sanitize_text_field($_GET['s']) : '';
        $status = isset($_GET['status']) ? sanitize_text_field($_GET['status']) : '';
        $category = isset($_GET['category']) ? sanitize_text_field($_GET['category']) : '';
        $page = isset($_GET['paged']) ? absint($_GET['paged']) : 1;

        // Fetch products from API
        $params = [
            'page' => $page,
            'page_size' => 20,
        ];

        if ($search) {
            $params['search'] = $search;
        }
        if ($status) {
            $params['status'] = $status;
        }
        if ($category) {
            $params['category'] = $category;
        }

        $products = $this->admin_api_request('products/', 'GET', $params);
        $categories = $this->admin_api_request('categories/');
        $stats = $this->admin_api_request('stats/');

        include WWC_SHOP_PLUGIN_DIR . 'admin/views/products-list.php';
    }

    /**
     * Render product edit page
     */
    public function render_product_edit_page() {
        $product_id = isset($_GET['id']) ? absint($_GET['id']) : 0;
        $product = null;

        if ($product_id) {
            $product = $this->admin_api_request("products/{$product_id}/");
            if (is_wp_error($product)) {
                wp_die(__('Product not found.', 'wwc-shop'));
            }
        }

        // Fetch categories and producers for dropdowns
        $categories = $this->admin_api_request('categories/');
        $producers = $this->admin_api_request('producers/');

        include WWC_SHOP_PLUGIN_DIR . 'admin/views/product-edit.php';
    }

    /**
     * AJAX: Save product
     */
    public function ajax_save_product() {
        check_ajax_referer('wwc-admin-products', 'nonce');

        if (!current_user_can('manage_options')) {
            wp_send_json_error(['message' => __('Permission denied.', 'wwc-shop')]);
        }

        $product_id = isset($_POST['product_id']) ? absint($_POST['product_id']) : 0;
        $data = isset($_POST['product']) ? $_POST['product'] : [];

        // Sanitize data
        $product_data = $this->sanitize_product_data($data);

        // Make API request
        if ($product_id) {
            // Update existing product
            $result = $this->admin_api_request("products/{$product_id}/", 'PATCH', $product_data);
        } else {
            // Create new product
            $result = $this->admin_api_request('products/', 'POST', $product_data);
        }

        if (is_wp_error($result)) {
            wp_send_json_error([
                'message' => $result->get_error_message(),
                'errors' => $result->get_error_data()['body'] ?? []
            ]);
        }

        wp_send_json_success([
            'message' => __('Product saved successfully!', 'wwc-shop'),
            'product' => $result
        ]);
    }

    /**
     * AJAX: Delete product
     */
    public function ajax_delete_product() {
        check_ajax_referer('wwc-admin-products', 'nonce');

        if (!current_user_can('manage_options')) {
            wp_send_json_error(['message' => __('Permission denied.', 'wwc-shop')]);
        }

        $product_id = isset($_POST['product_id']) ? absint($_POST['product_id']) : 0;

        if (!$product_id) {
            wp_send_json_error(['message' => __('Invalid product ID.', 'wwc-shop')]);
        }

        $result = $this->admin_api_request("products/{$product_id}/", 'DELETE');

        if (is_wp_error($result)) {
            wp_send_json_error(['message' => $result->get_error_message()]);
        }

        wp_send_json_success(['message' => __('Product deleted successfully!', 'wwc-shop')]);
    }

    /**
     * AJAX: Bulk action
     */
    public function ajax_bulk_action() {
        check_ajax_referer('wwc-admin-products', 'nonce');

        if (!current_user_can('manage_options')) {
            wp_send_json_error(['message' => __('Permission denied.', 'wwc-shop')]);
        }

        $action = isset($_POST['bulk_action']) ? sanitize_text_field($_POST['bulk_action']) : '';
        $product_ids = isset($_POST['product_ids']) ? array_map('absint', $_POST['product_ids']) : [];

        if (empty($action) || empty($product_ids)) {
            wp_send_json_error(['message' => __('Invalid request.', 'wwc-shop')]);
        }

        $result = $this->admin_api_request('products/bulk/', 'POST', [
            'action' => $action,
            'product_ids' => $product_ids
        ]);

        if (is_wp_error($result)) {
            wp_send_json_error(['message' => $result->get_error_message()]);
        }

        wp_send_json_success(['message' => $result['message'] ?? __('Action completed.', 'wwc-shop')]);
    }

    /**
     * AJAX: Upload image
     */
    public function ajax_upload_image() {
        check_ajax_referer('wwc-admin-products', 'nonce');

        if (!current_user_can('manage_options')) {
            wp_send_json_error(['message' => __('Permission denied.', 'wwc-shop')]);
        }

        $product_id = isset($_POST['product_id']) ? absint($_POST['product_id']) : 0;

        if (!$product_id) {
            wp_send_json_error(['message' => __('Invalid product ID.', 'wwc-shop')]);
        }

        if (empty($_FILES['image'])) {
            wp_send_json_error(['message' => __('No image uploaded.', 'wwc-shop')]);
        }

        // Handle WordPress media upload
        require_once(ABSPATH . 'wp-admin/includes/image.php');
        require_once(ABSPATH . 'wp-admin/includes/file.php');
        require_once(ABSPATH . 'wp-admin/includes/media.php');

        $attachment_id = media_handle_upload('image', 0);

        if (is_wp_error($attachment_id)) {
            wp_send_json_error(['message' => $attachment_id->get_error_message()]);
        }

        $image_url = wp_get_attachment_url($attachment_id);
        $is_primary = isset($_POST['is_primary']) && $_POST['is_primary'] === 'true';
        $alt_text = isset($_POST['alt_text']) ? sanitize_text_field($_POST['alt_text']) : '';

        // Upload to Django API
        $api_url = rtrim(get_option('wwc_api_url', 'http://127.0.0.1:8000'), '/');
        $url = $api_url . "/api/v1/admin/products/{$product_id}/images/";

        $image_path = get_attached_file($attachment_id);
        $boundary = wp_generate_password(24, false);

        $body = '';
        $body .= "--{$boundary}\r\n";
        $body .= "Content-Disposition: form-data; name=\"image\"; filename=\"" . basename($image_path) . "\"\r\n";
        $body .= "Content-Type: " . mime_content_type($image_path) . "\r\n\r\n";
        $body .= file_get_contents($image_path) . "\r\n";
        $body .= "--{$boundary}\r\n";
        $body .= "Content-Disposition: form-data; name=\"is_primary\"\r\n\r\n";
        $body .= ($is_primary ? 'true' : 'false') . "\r\n";
        $body .= "--{$boundary}\r\n";
        $body .= "Content-Disposition: form-data; name=\"alt_text\"\r\n\r\n";
        $body .= $alt_text . "\r\n";
        $body .= "--{$boundary}--\r\n";

        $response = wp_remote_post($url, [
            'method' => 'POST',
            'timeout' => 60,
            'headers' => [
                'Authorization' => 'Api-Key ' . $this->admin_api_key,
                'Content-Type' => 'multipart/form-data; boundary=' . $boundary,
            ],
            'body' => $body,
        ]);

        if (is_wp_error($response)) {
            wp_send_json_error(['message' => $response->get_error_message()]);
        }

        $code = wp_remote_retrieve_response_code($response);
        $result = json_decode(wp_remote_retrieve_body($response), true);

        if ($code >= 400) {
            wp_send_json_error(['message' => $result['detail'] ?? __('Upload failed.', 'wwc-shop')]);
        }

        wp_send_json_success([
            'message' => __('Image uploaded successfully!', 'wwc-shop'),
            'image' => $result
        ]);
    }

    /**
     * AJAX: Delete image
     */
    public function ajax_delete_image() {
        check_ajax_referer('wwc-admin-products', 'nonce');

        if (!current_user_can('manage_options')) {
            wp_send_json_error(['message' => __('Permission denied.', 'wwc-shop')]);
        }

        $product_id = isset($_POST['product_id']) ? absint($_POST['product_id']) : 0;
        $image_id = isset($_POST['image_id']) ? absint($_POST['image_id']) : 0;

        if (!$product_id || !$image_id) {
            wp_send_json_error(['message' => __('Invalid request.', 'wwc-shop')]);
        }

        $result = $this->admin_api_request("products/{$product_id}/images/{$image_id}/", 'DELETE');

        if (is_wp_error($result)) {
            wp_send_json_error(['message' => $result->get_error_message()]);
        }

        wp_send_json_success(['message' => __('Image deleted successfully!', 'wwc-shop')]);
    }

    /**
     * AJAX: Set primary image
     */
    public function ajax_set_primary_image() {
        check_ajax_referer('wwc-admin-products', 'nonce');

        if (!current_user_can('manage_options')) {
            wp_send_json_error(['message' => __('Permission denied.', 'wwc-shop')]);
        }

        $product_id = isset($_POST['product_id']) ? absint($_POST['product_id']) : 0;
        $image_id = isset($_POST['image_id']) ? absint($_POST['image_id']) : 0;

        if (!$product_id || !$image_id) {
            wp_send_json_error(['message' => __('Invalid request.', 'wwc-shop')]);
        }

        $result = $this->admin_api_request("products/{$product_id}/images/{$image_id}/primary/", 'PATCH');

        if (is_wp_error($result)) {
            wp_send_json_error(['message' => $result->get_error_message()]);
        }

        wp_send_json_success(['message' => __('Primary image updated!', 'wwc-shop')]);
    }

    /**
     * AJAX: Get product
     */
    public function ajax_get_product() {
        check_ajax_referer('wwc-admin-products', 'nonce');

        if (!current_user_can('manage_options')) {
            wp_send_json_error(['message' => __('Permission denied.', 'wwc-shop')]);
        }

        $product_id = isset($_GET['product_id']) ? absint($_GET['product_id']) : 0;

        if (!$product_id) {
            wp_send_json_error(['message' => __('Invalid product ID.', 'wwc-shop')]);
        }

        $result = $this->admin_api_request("products/{$product_id}/");

        if (is_wp_error($result)) {
            wp_send_json_error(['message' => $result->get_error_message()]);
        }

        wp_send_json_success(['product' => $result]);
    }

    /**
     * AJAX: Duplicate product
     */
    public function ajax_duplicate_product() {
        check_ajax_referer('wwc-admin-products', 'nonce');

        if (!current_user_can('manage_options')) {
            wp_send_json_error(['message' => __('Permission denied.', 'wwc-shop')]);
        }

        $product_id = isset($_POST['product_id']) ? absint($_POST['product_id']) : 0;

        if (!$product_id) {
            wp_send_json_error(['message' => __('Invalid product ID.', 'wwc-shop')]);
        }

        $result = $this->admin_api_request("products/{$product_id}/duplicate/", 'POST');

        if (is_wp_error($result)) {
            wp_send_json_error(['message' => $result->get_error_message()]);
        }

        wp_send_json_success([
            'message' => __('Product duplicated!', 'wwc-shop'),
            'product' => $result
        ]);
    }

    /**
     * Sanitize product data
     *
     * @param array $data Raw data
     * @return array Sanitized data
     */
    private function sanitize_product_data($data) {
        $sanitized = [];

        // Text fields
        $text_fields = ['name', 'name_en', 'name_ar', 'slug', 'sku', 'short_description',
                        'impact_school', 'impact_item', 'impact_item_en',
                        'meta_title', 'dimensions'];
        foreach ($text_fields as $field) {
            if (isset($data[$field])) {
                $sanitized[$field] = sanitize_text_field($data[$field]);
            }
        }

        // Rich text fields (allow some HTML)
        $rich_fields = ['description', 'description_en', 'description_ar',
                        'ingredients', 'ingredients_en', 'usage', 'usage_en',
                        'impact_description', 'impact_description_en', 'impact_description_ar',
                        'meta_description'];
        foreach ($rich_fields as $field) {
            if (isset($data[$field])) {
                $sanitized[$field] = wp_kses_post($data[$field]);
            }
        }

        // Integer fields
        $int_fields = ['category', 'producer', 'stock_quantity', 'low_stock_threshold',
                       'b2b_min_quantity', 'impact_quantity'];
        foreach ($int_fields as $field) {
            if (isset($data[$field]) && $data[$field] !== '') {
                $sanitized[$field] = absint($data[$field]);
            }
        }

        // Decimal fields
        $decimal_fields = ['price_tnd', 'price_eur', 'compare_at_price_tnd',
                          'b2b_price_tnd', 'b2b_price_eur', 'weight'];
        foreach ($decimal_fields as $field) {
            if (isset($data[$field]) && $data[$field] !== '') {
                $sanitized[$field] = floatval($data[$field]);
            }
        }

        // Boolean fields
        $bool_fields = ['is_active', 'is_featured', 'is_natural', 'is_organic',
                        'is_handmade', 'is_vegan', 'is_cruelty_free',
                        'track_inventory', 'allow_backorder'];
        foreach ($bool_fields as $field) {
            if (isset($data[$field])) {
                $sanitized[$field] = filter_var($data[$field], FILTER_VALIDATE_BOOLEAN);
            }
        }

        // Enum fields
        if (isset($data['unit_type'])) {
            $valid_types = ['individual', 'box', 'composable'];
            $sanitized['unit_type'] = in_array($data['unit_type'], $valid_types)
                ? $data['unit_type'] : 'individual';
        }

        return $sanitized;
    }
}

// Initialize
new WWC_Products_Admin();
