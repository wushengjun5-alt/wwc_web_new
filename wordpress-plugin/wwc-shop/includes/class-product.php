<?php
/**
 * WWC Shop Product Helper
 *
 * Helper functions for product display
 *
 * @package WWC_Shop
 */

defined('ABSPATH') || exit;

class WWC_Product {

    /**
     * Render star rating
     */
    public static function render_stars($rating, $max = 5) {
        $rating = floatval($rating);
        $full_stars = floor($rating);
        $half_star = ($rating - $full_stars) >= 0.5;
        $empty_stars = $max - $full_stars - ($half_star ? 1 : 0);

        $html = '<span class="wwc-stars">';

        for ($i = 0; $i < $full_stars; $i++) {
            $html .= '<span class="wwc-star wwc-star-full">★</span>';
        }

        if ($half_star) {
            $html .= '<span class="wwc-star wwc-star-half">★</span>';
        }

        for ($i = 0; $i < $empty_stars; $i++) {
            $html .= '<span class="wwc-star wwc-star-empty">☆</span>';
        }

        $html .= '</span>';

        return $html;
    }

    /**
     * Get product URL
     */
    public static function get_url($slug) {
        return home_url('/product/' . $slug . '/');
    }

    /**
     * Get product badges HTML
     */
    public static function render_badges($product) {
        $badges = [];

        if (!empty($product['is_natural'])) {
            $badges[] = '<span class="wwc-badge wwc-badge-natural">' .
                       esc_html__('100% NATURELLE', 'wwc-shop') . '</span>';
        }

        if (!empty($product['is_organic'])) {
            $badges[] = '<span class="wwc-badge wwc-badge-organic">' .
                       esc_html__('COSMÉTIQUE BIO', 'wwc-shop') . '</span>';
        }

        if (!empty($product['is_handmade'])) {
            $badges[] = '<span class="wwc-badge wwc-badge-handmade">' .
                       esc_html__('FAIT MAIN', 'wwc-shop') . '</span>';
        }

        if (!empty($product['is_vegan'])) {
            $badges[] = '<span class="wwc-badge wwc-badge-vegan">' .
                       esc_html__('VEGAN', 'wwc-shop') . '</span>';
        }

        return implode('', $badges);
    }

    /**
     * Get impact badge HTML
     */
    public static function render_impact_badge($product) {
        if (empty($product['impact_quantity']) || empty($product['impact_item'])) {
            return '';
        }

        $impact_text = sprintf(
            /* translators: 1: quantity, 2: item type, 3: school name */
            __('Grâce à cet achat, %1$d %2$s peuvent être fournies à des enfants de %3$s', 'wwc-shop'),
            $product['impact_quantity'],
            $product['impact_item'],
            $product['impact_school']
        );

        return '<div class="wwc-impact-badge">💝 ' . esc_html($impact_text) . '</div>';
    }

    /**
     * Get primary image URL
     */
    public static function get_image_url($product, $size = 'full') {
        if (!empty($product['primary_image']['image'])) {
            return $product['primary_image']['image'];
        }

        if (!empty($product['images']) && is_array($product['images'])) {
            return $product['images'][0]['image'] ?? '';
        }

        // Return placeholder
        return WWC_SHOP_PLUGIN_URL . 'assets/images/placeholder.png';
    }

    /**
     * Check if product is on sale
     */
    public static function is_on_sale($product) {
        return !empty($product['compare_at_price_tnd']) &&
               $product['compare_at_price_tnd'] > $product['price_tnd'];
    }

    /**
     * Get discount percentage
     */
    public static function get_discount_percentage($product) {
        if (!self::is_on_sale($product)) {
            return 0;
        }

        $original = floatval($product['compare_at_price_tnd']);
        $current = floatval($product['price_tnd']);

        return round((($original - $current) / $original) * 100);
    }

    /**
     * Get stock status HTML
     */
    public static function render_stock_status($product) {
        if (!empty($product['is_in_stock'])) {
            if (!empty($product['is_low_stock'])) {
                return '<span class="wwc-stock wwc-stock-low">' .
                       esc_html__('Stock limité', 'wwc-shop') . '</span>';
            }
            return '<span class="wwc-stock wwc-stock-in">' .
                   esc_html__('En stock', 'wwc-shop') . '</span>';
        }

        return '<span class="wwc-stock wwc-stock-out">' .
               esc_html__('Rupture de stock', 'wwc-shop') . '</span>';
    }

    /**
     * Get localized name
     */
    public static function get_name($product, $lang = null) {
        if ($lang === null) {
            $lang = substr(get_locale(), 0, 2);
        }

        $name_field = "name_{$lang}";
        if (!empty($product[$name_field])) {
            return $product[$name_field];
        }

        return $product['name'] ?? '';
    }

    /**
     * Get localized description
     */
    public static function get_description($product, $lang = null) {
        if ($lang === null) {
            $lang = substr(get_locale(), 0, 2);
        }

        $desc_field = "description_{$lang}";
        if (!empty($product[$desc_field])) {
            return $product[$desc_field];
        }

        return $product['description'] ?? '';
    }
}
