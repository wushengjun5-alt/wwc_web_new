<?php
/**
 * WWC Shop API Client
 *
 * Handles all communication with the Django REST API backend
 *
 * @package WWC_Shop
 */

defined('ABSPATH') || exit;

class WWC_API_Client {

    /**
     * API base URL
     */
    private $api_url;

    /**
     * API key (if required)
     */
    private $api_key;

    /**
     * Cache duration in seconds
     */
    private $cache_duration = 300; // 5 minutes

    /**
     * Constructor
     */
    public function __construct() {
        $this->api_url = rtrim(get_option('wwc_api_url', 'https://api.wallahwecan.org'), '/');
        $this->api_key = get_option('wwc_api_key', '');
    }

    /**
     * Make API request
     *
     * @param string $endpoint API endpoint
     * @param string $method HTTP method
     * @param array $data Request data
     * @param bool $use_cache Whether to use caching
     * @return array|WP_Error
     */
    public function request($endpoint, $method = 'GET', $data = [], $use_cache = true) {
        $url = $this->api_url . '/api/v1/' . ltrim($endpoint, '/');

        // Check cache for GET requests
        if ($method === 'GET' && $use_cache) {
            $cache_key = 'wwc_api_' . md5($url . serialize($data));
            $cached = get_transient($cache_key);
            if ($cached !== false) {
                return $cached;
            }
        }

        // Build request args
        $args = [
            'method' => $method,
            'timeout' => 30,
            'headers' => [
                'Content-Type' => 'application/json',
                'Accept' => 'application/json',
            ],
        ];

        // Add API key if set
        if (!empty($this->api_key)) {
            $args['headers']['Authorization'] = 'Token ' . $this->api_key;
        }

        // Add session key for cart operations
        $session_key = $this->get_session_key();
        if ($session_key) {
            $args['headers']['X-Session-Key'] = $session_key;
        }

        // Add JWT token if user is logged in
        $token = $this->get_jwt_token();
        if ($token) {
            $args['headers']['Authorization'] = 'Bearer ' . $token;
        }

        // Add data to request
        if ($method === 'GET' && !empty($data)) {
            $url = add_query_arg($data, $url);
        } elseif (!empty($data)) {
            $args['body'] = json_encode($data);
        }

        // Make request
        $response = wp_remote_request($url, $args);

        // Check for errors
        if (is_wp_error($response)) {
            return $response;
        }

        $status_code = wp_remote_retrieve_response_code($response);
        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);

        // Handle non-success status codes
        if ($status_code >= 400) {
            $error_message = isset($data['error']) ? $data['error'] : 'API request failed';
            return new WP_Error('api_error', $error_message, ['status' => $status_code]);
        }

        // Cache successful GET requests
        if ($method === 'GET' && $use_cache) {
            set_transient($cache_key, $data, $this->cache_duration);
        }

        return $data;
    }

    /**
     * GET request
     */
    public function get($endpoint, $params = [], $use_cache = true) {
        return $this->request($endpoint, 'GET', $params, $use_cache);
    }

    /**
     * POST request
     */
    public function post($endpoint, $data = []) {
        return $this->request($endpoint, 'POST', $data, false);
    }

    /**
     * PATCH request
     */
    public function patch($endpoint, $data = []) {
        return $this->request($endpoint, 'PATCH', $data, false);
    }

    /**
     * DELETE request
     */
    public function delete($endpoint) {
        return $this->request($endpoint, 'DELETE', [], false);
    }

    /**
     * Get session key for guest users
     */
    private function get_session_key() {
        if (!session_id()) {
            @session_start();
        }
        return session_id();
    }

    /**
     * Get JWT token for logged in users
     */
    private function get_jwt_token() {
        if (is_user_logged_in()) {
            $user_id = get_current_user_id();
            return get_user_meta($user_id, 'wwc_jwt_token', true);
        }
        return null;
    }

    /**
     * Set JWT token for user
     */
    public function set_jwt_token($user_id, $token) {
        update_user_meta($user_id, 'wwc_jwt_token', $token);
    }

    // ============================================
    // Product Methods
    // ============================================

    /**
     * Get all products
     */
    public function get_products($params = []) {
        $response = $this->get('products/', $params);

        if (is_wp_error($response)) {
            return $response;
        }

        // Handle paginated response
        if (isset($response['results'])) {
            return $response['results'];
        }

        return $response;
    }

    /**
     * Get single product by slug
     */
    public function get_product($slug) {
        return $this->get("products/{$slug}/");
    }

    /**
     * Get featured products
     */
    public function get_featured_products($limit = 8) {
        return $this->get('products/featured/', ['limit' => $limit]);
    }

    /**
     * Get related products
     */
    public function get_related_products($slug) {
        return $this->get("products/{$slug}/related/");
    }

    /**
     * Get product reviews
     */
    public function get_product_reviews($slug) {
        return $this->get("products/{$slug}/reviews/");
    }

    // ============================================
    // Category Methods
    // ============================================

    /**
     * Get all categories
     */
    public function get_categories($params = []) {
        $response = $this->get('categories/', $params);

        if (is_wp_error($response)) {
            return $response;
        }

        if (isset($response['results'])) {
            return $response['results'];
        }

        return $response;
    }

    /**
     * Get single category
     */
    public function get_category($slug) {
        return $this->get("categories/{$slug}/");
    }

    // ============================================
    // Cart Methods
    // ============================================

    /**
     * Get cart
     */
    public function get_cart() {
        return $this->get('cart/', [], false);
    }

    /**
     * Add item to cart
     */
    public function add_to_cart($product_id, $quantity = 1) {
        return $this->post('cart/add/', [
            'product_id' => $product_id,
            'quantity' => $quantity,
        ]);
    }

    /**
     * Update cart item
     */
    public function update_cart_item($item_id, $quantity) {
        return $this->patch("cart/update/{$item_id}/", [
            'quantity' => $quantity,
        ]);
    }

    /**
     * Remove item from cart
     */
    public function remove_from_cart($item_id) {
        return $this->delete("cart/remove/{$item_id}/");
    }

    /**
     * Clear cart
     */
    public function clear_cart() {
        return $this->delete('cart/clear/');
    }

    /**
     * Get cart impact
     */
    public function get_cart_impact() {
        return $this->get('cart/impact/', [], false);
    }

    // ============================================
    // Checkout Methods
    // ============================================

    /**
     * Create order
     */
    public function create_order($checkout_data) {
        return $this->post('checkout/', $checkout_data);
    }

    /**
     * Create payment session
     */
    public function create_payment_session($order_number) {
        return $this->post('payments/create-session/', [
            'order_number' => $order_number,
            'success_url' => home_url('/checkout/success/'),
            'cancel_url' => home_url('/checkout/'),
        ]);
    }

    /**
     * Get payment status
     */
    public function get_payment_status($order_number) {
        return $this->get("payments/status/{$order_number}/", [], false);
    }

    // ============================================
    // Order Methods
    // ============================================

    /**
     * Get orders for current user
     */
    public function get_orders() {
        return $this->get('orders/', [], false);
    }

    /**
     * Get single order
     */
    public function get_order($order_number) {
        return $this->get("orders/{$order_number}/", [], false);
    }

    // ============================================
    // Customer Methods
    // ============================================

    /**
     * Get customer dashboard
     */
    public function get_customer_dashboard() {
        return $this->get('customer/dashboard/', [], false);
    }

    /**
     * Get customer profile
     */
    public function get_customer_profile() {
        return $this->get('customer/profile/', [], false);
    }

    /**
     * Update customer profile
     */
    public function update_customer_profile($data) {
        return $this->patch('customer/profile/', $data);
    }

    // ============================================
    // Impact Methods
    // ============================================

    /**
     * Get impact summary
     */
    public function get_impact_summary() {
        return $this->get('impact/summary/');
    }

    /**
     * Get impact events
     */
    public function get_impact_events($params = []) {
        return $this->get('impact-events/', $params);
    }

    // ============================================
    // Auth Methods
    // ============================================

    /**
     * Register user
     */
    public function register_user($data) {
        return $this->post('auth/register/', $data);
    }

    /**
     * Login user
     */
    public function login_user($email, $password) {
        $response = $this->post('../token/', [
            'username' => $email,
            'password' => $password,
        ]);

        if (!is_wp_error($response) && isset($response['access'])) {
            // Store token
            if (is_user_logged_in()) {
                $this->set_jwt_token(get_current_user_id(), $response['access']);
            }
        }

        return $response;
    }

    /**
     * Clear API cache
     */
    public function clear_cache($pattern = '') {
        global $wpdb;

        if (empty($pattern)) {
            $pattern = 'wwc_api_%';
        }

        $wpdb->query(
            $wpdb->prepare(
                "DELETE FROM {$wpdb->options} WHERE option_name LIKE %s",
                '_transient_' . $pattern
            )
        );
    }
}
