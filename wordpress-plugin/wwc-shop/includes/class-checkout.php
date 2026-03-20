<?php
/**
 * WWC Shop Checkout Handler
 *
 * Handles checkout process and payment integration
 *
 * @package WWC_Shop
 */

defined('ABSPATH') || exit;

class WWC_Checkout {

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
     * Get shipping countries
     */
    public static function get_shipping_countries() {
        return [
            'TN' => __('Tunisia', 'wwc-shop'),
            'FR' => __('France', 'wwc-shop'),
            'BE' => __('Belgium', 'wwc-shop'),
            'CH' => __('Switzerland', 'wwc-shop'),
            'DE' => __('Germany', 'wwc-shop'),
        ];
    }

    /**
     * Get available payment methods.
     * Stripe accepts all currencies; the customer's bank handles conversion.
     *
     * @param string $currency Unused, kept for API compatibility.
     * @return array
     */
    public static function get_payment_methods($currency = null) {
        return [
            'stripe' => [
                'id'          => 'stripe',
                'title'       => __('Paiement par carte', 'wwc-shop'),
                'description' => __('Visa, Mastercard, ou carte prépayée — paiement sécurisé', 'wwc-shop'),
                'icon'        => 'credit-card',
            ],
        ];
    }

    /**
     * Get Tunisia governorates (states)
     */
    public static function get_tunisia_states() {
        return [
            'Ariana' => 'Ariana',
            'Beja' => 'Béja',
            'Ben Arous' => 'Ben Arous',
            'Bizerte' => 'Bizerte',
            'Gabes' => 'Gabès',
            'Gafsa' => 'Gafsa',
            'Jendouba' => 'Jendouba',
            'Kairouan' => 'Kairouan',
            'Kasserine' => 'Kasserine',
            'Kebili' => 'Kébili',
            'Kef' => 'Le Kef',
            'Mahdia' => 'Mahdia',
            'Manouba' => 'La Manouba',
            'Medenine' => 'Médenine',
            'Monastir' => 'Monastir',
            'Nabeul' => 'Nabeul',
            'Sfax' => 'Sfax',
            'Sidi Bouzid' => 'Sidi Bouzid',
            'Siliana' => 'Siliana',
            'Sousse' => 'Sousse',
            'Tataouine' => 'Tataouine',
            'Tozeur' => 'Tozeur',
            'Tunis' => 'Tunis',
            'Zaghouan' => 'Zaghouan',
        ];
    }

    /**
     * Calculate shipping cost
     */
    public static function calculate_shipping($country, $total) {
        // Fixed shipping rates
        $rates = [
            'TN' => 7.00,   // 7 TND for Tunisia
            'FR' => 15.00,  // 15 EUR for France
            'default' => 20.00,
        ];

        // Free shipping threshold
        $free_shipping_threshold = [
            'TN' => 100.00,
            'FR' => 50.00,
            'default' => 75.00,
        ];

        $threshold = $free_shipping_threshold[$country] ?? $free_shipping_threshold['default'];

        if ($total >= $threshold) {
            return 0;
        }

        return $rates[$country] ?? $rates['default'];
    }

    /**
     * Validate checkout data
     */
    public static function validate_checkout_data($data) {
        $errors = [];

        // Required fields
        $required = [
            'email' => __('Email', 'wwc-shop'),
            'phone' => __('Phone', 'wwc-shop'),
            'shipping_first_name' => __('First name', 'wwc-shop'),
            'shipping_last_name' => __('Last name', 'wwc-shop'),
            'shipping_address_1' => __('Address', 'wwc-shop'),
            'shipping_city' => __('City', 'wwc-shop'),
            'shipping_postal_code' => __('Postal code', 'wwc-shop'),
        ];

        foreach ($required as $field => $label) {
            if (empty($data[$field])) {
                $errors[$field] = sprintf(__('%s is required', 'wwc-shop'), $label);
            }
        }

        // Email validation
        if (!empty($data['email']) && !is_email($data['email'])) {
            $errors['email'] = __('Please enter a valid email address', 'wwc-shop');
        }

        // Phone validation
        if (!empty($data['phone']) && !preg_match('/^[+]?[0-9\s\-]{8,20}$/', $data['phone'])) {
            $errors['phone'] = __('Please enter a valid phone number', 'wwc-shop');
        }

        return $errors;
    }
}
