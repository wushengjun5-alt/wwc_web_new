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
     * Get the active language for API requests.
     * Reads from the wwc_lang cookie; defaults to 'fr'.
     */
    public function get_lang() {
        $allowed = ['fr', 'en', 'ar'];
        $lang    = sanitize_text_field($_COOKIE['wwc_lang'] ?? 'fr');
        return in_array($lang, $allowed, true) ? $lang : 'fr';
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

        // Append language param to all requests
        if ($method === 'GET') {
            $data['lang'] = $this->get_lang();
        }

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

        // Add session key for cart operations (guest identity)
        $session_key = $this->get_session_key();
        if ($session_key) {
            $args['headers']['X-Session-Key'] = $session_key;
        }

        // Add JWT token if the customer is logged in (takes priority over admin key)
        $token = $this->get_jwt_token();
        if ($token) {
            $args['headers']['Authorization'] = 'Bearer ' . $token;
        } elseif (!empty($this->api_key) && strpos($endpoint, 'admin/') === 0) {
            // Only send the admin API key on admin-prefixed endpoints
            $args['headers']['Authorization'] = 'Api-Key ' . $this->api_key;
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
            $error_message = $this->extract_error_message($data, $status_code);
            return new WP_Error('api_error', $error_message, ['status' => $status_code, 'data' => $data]);
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
     * Extract a human-readable error message from a DRF error response.
     * DRF can return: {'detail':'...'}, {'error':'...'}, {'field':['msg',...]}, or lists.
     */
    private function extract_error_message($data, $status_code) {
        if (!is_array($data)) {
            return 'API request failed (HTTP ' . $status_code . ')';
        }
        // Standard DRF detail / our own error key
        if (isset($data['detail'])) {
            return is_string($data['detail']) ? $data['detail'] : json_encode($data['detail']);
        }
        if (isset($data['error'])) {
            return is_string($data['error']) ? $data['error'] : json_encode($data['error']);
        }
        if (isset($data['message'])) {
            return is_string($data['message']) ? $data['message'] : json_encode($data['message']);
        }
        // DRF validation errors: {'field': ['msg1', ...], ...}
        $messages = [];
        foreach ($data as $field => $errors) {
            if (is_array($errors)) {
                foreach ($errors as $err) {
                    $messages[] = is_string($err) ? $err : json_encode($err);
                }
            } elseif (is_string($errors)) {
                $messages[] = $errors;
            }
        }
        return !empty($messages) ? implode(' ', $messages) : 'API request failed (HTTP ' . $status_code . ')';
    }

    /**
     * Get a stable session key for guest users.
     * Stored in a cookie so it persists across requests and page loads.
     */
    private function get_session_key() {
        $cookie_name = 'wwc_cart_token';

        if (!empty($_COOKIE[$cookie_name])) {
            return sanitize_text_field($_COOKIE[$cookie_name]);
        }

        // Generate a new token and set cookie for 30 days
        $token = bin2hex(random_bytes(16));
        setcookie($cookie_name, $token, [
            'expires'  => time() + 30 * DAY_IN_SECONDS,
            'path'     => '/',
            'httponly' => true,
            'samesite' => 'Lax',
        ]);
        $_COOKIE[$cookie_name] = $token; // make it available immediately this request

        return $token;
    }

    /**
     * Get JWT token from cookie, only if it is structurally valid and not expired.
     * A JWT has three base64url parts separated by dots. The payload contains 'exp'.
     * If the token is missing, malformed, or expired we return null so the request
     * goes out as a guest (X-Session-Key only) instead of sending a bad token.
     */
    private function get_jwt_token() {
        $token = $_COOKIE['wwc_access_token'] ?? null;
        if (!$token) {
            return null;
        }

        // Basic structural check: three dot-separated segments
        $parts = explode('.', $token);
        if (count($parts) !== 3) {
            return null;
        }

        // Decode payload (second segment) — base64url, no padding required
        $payload_json = base64_decode(strtr($parts[1], '-_', '+/'));
        if (!$payload_json) {
            return null;
        }
        $payload = json_decode($payload_json, true);
        if (!is_array($payload)) {
            return null;
        }

        // Check expiry
        if (isset($payload['exp']) && $payload['exp'] < time()) {
            // Token expired — clear the stale cookie so we don't keep sending it
            $this->clear_tokens();
            return null;
        }

        return $token;
    }

    // ============================================
    // Product Methods
    // ============================================

    /**
     * Get all products
     */
    public function get_products($params = [], $paginated = false) {
        $response = $this->get('products/', $params);

        if (is_wp_error($response)) {
            return $response;
        }

        if ($paginated) {
            return $response; // return full { count, next, previous, results }
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
     * Create Stripe Checkout Session (EUR orders only)
     */
    public function create_payment_session($order_number) {
        return $this->post('payments/create-session/', [
            'order_number' => $order_number,
            'success_url' => home_url('/checkout/success/'),
            'cancel_url' => home_url('/checkout/'),
        ]);
    }

    /**
     * Get bank transfer instructions (TND orders only)
     */
    public function get_bank_transfer_instructions($order_number) {
        return $this->get("payments/bank-transfer/{$order_number}/", [], false);
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
    // Wishlist Methods
    // ============================================

    /**
     * Get wishlist items
     */
    public function get_wishlist() {
        return $this->get('wishlist/', [], false);
    }

    /**
     * Add product to wishlist
     */
    public function add_to_wishlist($product_id) {
        return $this->post('wishlist/', ['product' => $product_id]);
    }

    /**
     * Remove product from wishlist by wishlist item ID
     */
    public function remove_from_wishlist($wishlist_item_id) {
        return $this->delete("wishlist/{$wishlist_item_id}/");
    }

    // ============================================
    // Review Methods
    // ============================================

    /**
     * Submit a product review
     */
    public function add_review($product_slug, $rating, $comment) {
        return $this->post("products/{$product_slug}/add_review/", [
            'rating'  => $rating,
            'comment' => $comment,
        ]);
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
     * Login user — uses our custom login endpoint
     */
    public function login_user($email, $password) {
        $response = $this->post('auth/login/', [
            'email'    => $email,
            'password' => $password,
        ]);

        if (!is_wp_error($response) && isset($response['access'])) {
            $this->store_tokens($response['access'], $response['refresh'] ?? '');
        }

        return $response;
    }

    /**
     * Request password reset email
     */
    public function request_password_reset($email) {
        return $this->post('auth/password-reset/', ['email' => $email]);
    }

    /**
     * Confirm password reset
     */
    public function confirm_password_reset($uid, $token, $password, $password_confirm) {
        return $this->post('auth/password-reset/confirm/', [
            'uid'              => $uid,
            'token'            => $token,
            'password'         => $password,
            'password_confirm' => $password_confirm,
        ]);
    }

    /**
     * Store JWT tokens in a cookie (not user meta — works for non-WP users too)
     */
    public function store_tokens($access, $refresh = '') {
        // 1-hour access token cookie
        setcookie('wwc_access_token', $access, [
            'expires'  => time() + 3600,
            'path'     => '/',
            'httponly' => true,
            'samesite' => 'Lax',
        ]);
        $_COOKIE['wwc_access_token'] = $access;

        if ($refresh) {
            setcookie('wwc_refresh_token', $refresh, [
                'expires'  => time() + 7 * DAY_IN_SECONDS,
                'path'     => '/',
                'httponly' => true,
                'samesite' => 'Lax',
            ]);
            $_COOKIE['wwc_refresh_token'] = $refresh;
        }
    }

    /**
     * Clear JWT tokens (logout)
     */
    public function clear_tokens() {
        setcookie('wwc_access_token', '', ['expires' => time() - 3600, 'path' => '/']);
        setcookie('wwc_refresh_token', '', ['expires' => time() - 3600, 'path' => '/']);
        unset($_COOKIE['wwc_access_token'], $_COOKIE['wwc_refresh_token']);
    }

    /**
     * Check if user is authenticated with Django
     */
    public function is_authenticated() {
        return !empty($_COOKIE['wwc_access_token']);
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
