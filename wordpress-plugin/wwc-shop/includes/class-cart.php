<?php
/**
 * WWC Shop Cart Handler
 *
 * Handles cart operations and AJAX requests
 *
 * @package WWC_Shop
 */

defined('ABSPATH') || exit;

class WWC_Cart {

    /**
     * API Client
     */
    private $api;

    /**
     * Constructor
     */
    public function __construct($api) {
        $this->api = $api;
    }

    /**
     * AJAX: Add to cart
     */
    public function ajax_add_to_cart() {
        check_ajax_referer('wwc-shop-nonce', 'nonce');

        $product_id = isset($_POST['product_id']) ? intval($_POST['product_id']) : 0;
        $quantity = isset($_POST['quantity']) ? intval($_POST['quantity']) : 1;

        if (!$product_id) {
            wp_send_json_error(['message' => __('Invalid product', 'wwc-shop')]);
        }

        $result = $this->api->add_to_cart($product_id, $quantity);

        if (is_wp_error($result)) {
            wp_send_json_error(['message' => $result->get_error_message()]);
        }

        wp_send_json_success([
            'message' => __('Product added to cart', 'wwc-shop'),
            'cart' => $result['cart'] ?? $result,
            'cart_count' => $this->get_cart_count($result['cart'] ?? $result),
        ]);
    }

    /**
     * AJAX: Update cart item
     */
    public function ajax_update_cart() {
        check_ajax_referer('wwc-shop-nonce', 'nonce');

        $item_id = isset($_POST['item_id']) ? intval($_POST['item_id']) : 0;
        $quantity = isset($_POST['quantity']) ? intval($_POST['quantity']) : 1;

        if (!$item_id) {
            wp_send_json_error(['message' => __('Invalid cart item', 'wwc-shop')]);
        }

        $result = $this->api->update_cart_item($item_id, $quantity);

        if (is_wp_error($result)) {
            wp_send_json_error(['message' => $result->get_error_message()]);
        }

        wp_send_json_success([
            'message' => __('Cart updated', 'wwc-shop'),
            'cart' => $result,
            'cart_count' => $this->get_cart_count($result),
        ]);
    }

    /**
     * AJAX: Remove from cart
     */
    public function ajax_remove_from_cart() {
        check_ajax_referer('wwc-shop-nonce', 'nonce');

        $item_id = isset($_POST['item_id']) ? intval($_POST['item_id']) : 0;

        if (!$item_id) {
            wp_send_json_error(['message' => __('Invalid cart item', 'wwc-shop')]);
        }

        $result = $this->api->remove_from_cart($item_id);

        if (is_wp_error($result)) {
            wp_send_json_error(['message' => $result->get_error_message()]);
        }

        wp_send_json_success([
            'message' => __('Product removed from cart', 'wwc-shop'),
            'cart' => $result,
            'cart_count' => $this->get_cart_count($result),
        ]);
    }

    /**
     * AJAX: Get cart
     */
    public function ajax_get_cart() {
        check_ajax_referer('wwc-shop-nonce', 'nonce');

        $result = $this->api->get_cart();

        if (is_wp_error($result)) {
            wp_send_json_error(['message' => $result->get_error_message()]);
        }

        wp_send_json_success([
            'cart' => $result,
            'cart_count' => $this->get_cart_count($result),
        ]);
    }

    /**
     * AJAX: Clear cart
     */
    public function ajax_clear_cart() {
        check_ajax_referer('wwc-shop-nonce', 'nonce');

        $result = $this->api->clear_cart();

        if (is_wp_error($result)) {
            wp_send_json_error(['message' => $result->get_error_message()]);
        }

        wp_send_json_success([
            'message' => __('Cart cleared', 'wwc-shop'),
            'cart_count' => 0,
        ]);
    }

    /**
     * AJAX: Apply coupon
     */
    public function ajax_apply_coupon() {
        check_ajax_referer('wwc-shop-nonce', 'nonce');

        $coupon_code = isset($_POST['coupon_code']) ? sanitize_text_field($_POST['coupon_code']) : '';

        if (empty($coupon_code)) {
            wp_send_json_error(['message' => __('Please enter a coupon code', 'wwc-shop')]);
        }

        // TODO: Implement coupon validation via API
        wp_send_json_error(['message' => __('Coupon functionality coming soon', 'wwc-shop')]);
    }

    /**
     * AJAX: Process checkout
     */
    public function ajax_checkout() {
        check_ajax_referer('wwc-shop-nonce', 'nonce');

        // Collect checkout data
        $checkout_data = [
            'email' => sanitize_email($_POST['email'] ?? ''),
            'phone' => sanitize_text_field($_POST['phone'] ?? ''),
            'shipping_first_name' => sanitize_text_field($_POST['shipping_first_name'] ?? ''),
            'shipping_last_name' => sanitize_text_field($_POST['shipping_last_name'] ?? ''),
            'shipping_company' => sanitize_text_field($_POST['shipping_company'] ?? ''),
            'shipping_address_1' => sanitize_text_field($_POST['shipping_address_1'] ?? ''),
            'shipping_address_2' => sanitize_text_field($_POST['shipping_address_2'] ?? ''),
            'shipping_city' => sanitize_text_field($_POST['shipping_city'] ?? ''),
            'shipping_state' => sanitize_text_field($_POST['shipping_state'] ?? ''),
            'shipping_postal_code' => sanitize_text_field($_POST['shipping_postal_code'] ?? ''),
            'shipping_country' => sanitize_text_field($_POST['shipping_country'] ?? 'TN'),
            'payment_method' => sanitize_text_field($_POST['payment_method'] ?? 'stripe'),
            'customer_notes' => sanitize_textarea_field($_POST['customer_notes'] ?? ''),
        ];

        // Validate required fields
        $required = ['email', 'phone', 'shipping_first_name', 'shipping_last_name',
                    'shipping_address_1', 'shipping_city', 'shipping_postal_code'];

        foreach ($required as $field) {
            if (empty($checkout_data[$field])) {
                wp_send_json_error([
                    'message' => sprintf(__('%s is required', 'wwc-shop'), ucfirst(str_replace('_', ' ', $field)))
                ]);
            }
        }

        // Create order via API
        $order_result = $this->api->create_order($checkout_data);

        if (is_wp_error($order_result)) {
            wp_send_json_error(['message' => $order_result->get_error_message()]);
        }

        $order_number = $order_result['order_number'];

        // All orders go through Stripe; redirect to hosted checkout
        $payment_result = $this->api->create_payment_session($order_number);

        if (is_wp_error($payment_result)) {
            wp_send_json_error(['message' => $payment_result->get_error_message()]);
        }

        // API returned an error field (e.g. Stripe not configured, Stripe error)
        if (isset($payment_result['error'])) {
            wp_send_json_error(['message' => $payment_result['error']]);
        }

        if (empty($payment_result['checkout_url'])) {
            wp_send_json_error(['message' => __('Impossible de créer la session de paiement.', 'wwc-shop')]);
        }

        wp_send_json_success([
            'message'      => __('Commande créée', 'wwc-shop'),
            'order_number' => $order_number,
            'checkout_url' => $payment_result['checkout_url'],
            'redirect'     => true,
        ]);
    }

    /**
     * Get cart item count from cart data
     */
    private function get_cart_count($cart) {
        if (isset($cart['item_count'])) {
            return $cart['item_count'];
        }

        if (isset($cart['items']) && is_array($cart['items'])) {
            $count = 0;
            foreach ($cart['items'] as $item) {
                $count += $item['quantity'] ?? 1;
            }
            return $count;
        }

        return 0;
    }

    /**
     * AJAX: Toggle wishlist (add if not in wishlist, remove if already there)
     */
    public function ajax_toggle_wishlist() {
        check_ajax_referer('wwc-shop-nonce', 'nonce');

        $product_id = isset($_POST['product_id']) ? intval($_POST['product_id']) : 0;
        if (!$product_id) {
            wp_send_json_error(['message' => __('Invalid product', 'wwc-shop')]);
        }

        // First check current wishlist state
        $wishlist = $this->api->get_wishlist();
        if (is_wp_error($wishlist)) {
            wp_send_json_error(['message' => $wishlist->get_error_message()]);
        }

        // Look for existing wishlist item for this product
        $existing_id = null;
        $items = is_array($wishlist) ? ($wishlist['results'] ?? $wishlist) : [];
        foreach ($items as $item) {
            $pid = $item['product']['id'] ?? $item['product_id'] ?? null;
            if ($pid == $product_id) {
                $existing_id = $item['id'];
                break;
            }
        }

        if ($existing_id) {
            $result = $this->api->remove_from_wishlist($existing_id);
            if (is_wp_error($result)) {
                wp_send_json_error(['message' => $result->get_error_message()]);
            }
            wp_send_json_success(['in_wishlist' => false, 'message' => __('Retiré des favoris', 'wwc-shop')]);
        } else {
            $result = $this->api->add_to_wishlist($product_id);
            if (is_wp_error($result)) {
                wp_send_json_error(['message' => $result->get_error_message()]);
            }
            wp_send_json_success(['in_wishlist' => true, 'message' => __('Ajouté aux favoris', 'wwc-shop')]);
        }
    }

    /**
     * AJAX: Submit a product review
     */
    public function ajax_add_review() {
        check_ajax_referer('wwc-shop-nonce', 'nonce');

        $product_slug = isset($_POST['product_slug']) ? sanitize_text_field($_POST['product_slug']) : '';
        $rating       = isset($_POST['rating']) ? intval($_POST['rating']) : 0;
        $comment      = isset($_POST['comment']) ? sanitize_textarea_field($_POST['comment']) : '';

        if (empty($product_slug) || $rating < 1 || $rating > 5) {
            wp_send_json_error(['message' => __('Veuillez sélectionner une note entre 1 et 5.', 'wwc-shop')]);
        }

        $result = $this->api->add_review($product_slug, $rating, $comment);

        if (is_wp_error($result)) {
            wp_send_json_error(['message' => $result->get_error_message()]);
        }

        wp_send_json_success(['message' => __('Avis soumis. Il sera publié après modération.', 'wwc-shop')]);
    }

    /**
     * Get current cart (for templates)
     */
    public function get_current_cart() {
        return $this->api->get_cart();
    }

    /**
     * Format price for display
     */
    public static function format_price($amount, $currency = null) {
        if ($currency === null) {
            $currency = get_option('wwc_default_currency', 'TND');
        }

        $amount = floatval($amount);

        switch ($currency) {
            case 'EUR':
                return number_format($amount, 2, ',', ' ') . ' €';
            case 'TND':
            default:
                return number_format($amount, 2, ',', ' ') . ' DT';
        }
    }
}
