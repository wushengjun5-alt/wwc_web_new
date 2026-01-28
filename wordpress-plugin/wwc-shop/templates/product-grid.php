<?php
/**
 * Product Grid Template
 *
 * @package WWC_Shop
 */

defined('ABSPATH') || exit;

$columns = isset($atts['columns']) ? intval($atts['columns']) : 3;
$products_list = $products ?? [];
?>

<div class="wwc-products-wrapper">
    <?php if (empty($products_list)): ?>
        <p class="wwc-no-products"><?php esc_html_e('No products found.', 'wwc-shop'); ?></p>
    <?php else: ?>
        <div class="wwc-product-grid wwc-grid-<?php echo esc_attr($columns); ?>">
            <?php foreach ($products_list as $product): ?>
                <div class="wwc-product-card" data-product-id="<?php echo esc_attr($product['id']); ?>">
                    <a href="<?php echo esc_url(WWC_Product::get_url($product['slug'])); ?>" class="wwc-product-link">

                        <?php if (WWC_Product::is_on_sale($product)): ?>
                            <span class="wwc-sale-badge">
                                -<?php echo esc_html(WWC_Product::get_discount_percentage($product)); ?>%
                            </span>
                        <?php endif; ?>

                        <div class="wwc-product-image">
                            <img
                                src="<?php echo esc_url(WWC_Product::get_image_url($product)); ?>"
                                alt="<?php echo esc_attr($product['name']); ?>"
                                loading="lazy"
                            >
                        </div>

                        <div class="wwc-product-info">
                            <h3 class="wwc-product-name">
                                <?php echo esc_html(WWC_Product::get_name($product)); ?>
                            </h3>

                            <?php if (!empty($product['average_rating']) && $product['average_rating'] > 0): ?>
                                <div class="wwc-product-rating">
                                    <?php echo WWC_Product::render_stars($product['average_rating']); ?>
                                    <span class="wwc-rating-count">(<?php echo esc_html($product['review_count']); ?>)</span>
                                </div>
                            <?php endif; ?>

                            <div class="wwc-product-badges">
                                <?php echo WWC_Product::render_badges($product); ?>
                            </div>

                            <div class="wwc-product-price">
                                <?php if (WWC_Product::is_on_sale($product)): ?>
                                    <span class="wwc-price-original">
                                        <?php echo esc_html(WWC_Cart::format_price($product['compare_at_price_tnd'])); ?>
                                    </span>
                                <?php endif; ?>
                                <span class="wwc-price-current">
                                    <?php echo esc_html(WWC_Cart::format_price($product['price_tnd'])); ?>
                                </span>
                            </div>

                            <?php if (!empty($product['impact_quantity'])): ?>
                                <div class="wwc-product-impact-preview">
                                    💝 <?php
                                    printf(
                                        esc_html__('%d %s', 'wwc-shop'),
                                        $product['impact_quantity'],
                                        $product['impact_item']
                                    );
                                    ?>
                                </div>
                            <?php endif; ?>
                        </div>
                    </a>

                    <button
                        class="wwc-btn wwc-btn-add-to-cart wwc-quick-add"
                        data-product-id="<?php echo esc_attr($product['id']); ?>"
                        <?php echo empty($product['is_in_stock']) ? 'disabled' : ''; ?>
                    >
                        <?php if (empty($product['is_in_stock'])): ?>
                            <?php esc_html_e('Rupture de stock', 'wwc-shop'); ?>
                        <?php else: ?>
                            <?php esc_html_e('Ajouter au panier', 'wwc-shop'); ?>
                        <?php endif; ?>
                    </button>
                </div>
            <?php endforeach; ?>
        </div>
    <?php endif; ?>
</div>
