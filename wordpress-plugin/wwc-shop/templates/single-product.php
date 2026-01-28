<?php
/**
 * Single Product Template
 *
 * Matches the UI design from provided screenshots
 *
 * @package WWC_Shop
 */

defined('ABSPATH') || exit;

$images = $product['images'] ?? [];
$primary_image = WWC_Product::get_image_url($product);
?>

<div class="wwc-product-detail">

    <!-- Product Gallery (Left Side) -->
    <div class="wwc-product-gallery">
        <div class="wwc-gallery-main">
            <?php if (WWC_Product::is_on_sale($product)): ?>
                <span class="wwc-sale-badge wwc-sale-badge-large">
                    -<?php echo esc_html(WWC_Product::get_discount_percentage($product)); ?>%
                </span>
            <?php endif; ?>
            <img
                src="<?php echo esc_url($primary_image); ?>"
                alt="<?php echo esc_attr($product['name']); ?>"
                class="wwc-main-image"
                id="wwc-main-image"
            >
        </div>

        <?php if (count($images) > 1): ?>
        <div class="wwc-gallery-thumbnails">
            <?php foreach ($images as $index => $image): ?>
                <button
                    class="wwc-thumbnail <?php echo $index === 0 ? 'active' : ''; ?>"
                    data-image="<?php echo esc_url($image['image']); ?>"
                    type="button"
                >
                    <img
                        src="<?php echo esc_url($image['image']); ?>"
                        alt="<?php echo esc_attr($image['alt_text'] ?? $product['name']); ?>"
                    >
                </button>
            <?php endforeach; ?>
        </div>
        <?php endif; ?>
    </div>

    <!-- Product Info (Right Side) -->
    <div class="wwc-product-info">

        <!-- Product Title -->
        <h1 class="wwc-product-title"><?php echo esc_html(WWC_Product::get_name($product)); ?></h1>

        <!-- Rating -->
        <?php if (!empty($product['review_count']) && $product['review_count'] > 0): ?>
            <div class="wwc-product-rating">
                <?php echo WWC_Product::render_stars($product['average_rating']); ?>
                <span class="wwc-rating-text">
                    <?php echo esc_html($product['average_rating']); ?>/5 -
                    <?php
                    printf(
                        esc_html(_n('%d avis', '%d avis', $product['review_count'], 'wwc-shop')),
                        $product['review_count']
                    );
                    ?>
                </span>
            </div>
        <?php endif; ?>

        <!-- Badges -->
        <div class="wwc-product-badges">
            <?php echo WWC_Product::render_badges($product); ?>
        </div>

        <!-- Description -->
        <div class="wwc-product-description">
            <?php echo wp_kses_post(wpautop(WWC_Product::get_description($product))); ?>
            <?php if (strlen($product['description']) > 300): ?>
                <a href="#" class="wwc-read-more" data-toggle="description">
                    <?php esc_html_e('Lire plus', 'wwc-shop'); ?>
                </a>
            <?php endif; ?>
        </div>

        <!-- Stock Status -->
        <div class="wwc-stock-status">
            <?php echo WWC_Product::render_stock_status($product); ?>
        </div>

        <!-- Quantity Selector and Price -->
        <div class="wwc-product-purchase">
            <div class="wwc-quantity-selector">
                <button class="wwc-qty-btn wwc-qty-minus" type="button">−</button>
                <input
                    type="number"
                    class="wwc-qty-input"
                    id="wwc-product-quantity"
                    value="1"
                    min="1"
                    max="<?php echo esc_attr($product['stock_quantity'] ?? 99); ?>"
                >
                <button class="wwc-qty-btn wwc-qty-plus" type="button">+</button>
            </div>

            <div class="wwc-product-price">
                <?php if (WWC_Product::is_on_sale($product)): ?>
                    <span class="wwc-price-original">
                        <?php echo esc_html(WWC_Cart::format_price($product['compare_at_price_tnd'])); ?>
                    </span>
                <?php endif; ?>
                <span class="wwc-price-amount"><?php echo esc_html(number_format($product['price_tnd'], 0)); ?></span>
                <span class="wwc-price-currency">DT</span>
            </div>
        </div>

        <!-- Impact Badge (Pink Box) -->
        <?php echo WWC_Product::render_impact_badge($product); ?>

        <!-- Add to Cart Button -->
        <button
            class="wwc-btn wwc-btn-primary wwc-add-to-cart"
            data-product-id="<?php echo esc_attr($product['id']); ?>"
            <?php echo empty($product['is_in_stock']) ? 'disabled' : ''; ?>
        >
            <?php if (empty($product['is_in_stock'])): ?>
                <?php esc_html_e('Rupture de stock', 'wwc-shop'); ?>
            <?php else: ?>
                <?php esc_html_e('Ajouter au panier', 'wwc-shop'); ?>
            <?php endif; ?>
        </button>

        <!-- Social Actions -->
        <div class="wwc-product-actions">
            <button class="wwc-btn-icon wwc-share" type="button" title="<?php esc_attr_e('Partager', 'wwc-shop'); ?>">
                <span class="wwc-icon">🔗</span>
            </button>
            <button class="wwc-btn-icon wwc-wishlist" type="button" title="<?php esc_attr_e('Ajouter aux favoris', 'wwc-shop'); ?>" data-product-id="<?php echo esc_attr($product['id']); ?>">
                <span class="wwc-icon">🤍</span>
            </button>
        </div>

        <!-- Accordion Sections -->
        <div class="wwc-product-accordions">

            <?php if (!empty($product['ingredients'])): ?>
            <div class="wwc-accordion">
                <button class="wwc-accordion-header" type="button">
                    <span class="wwc-accordion-icon">🔥</span>
                    <span><?php esc_html_e("Ce qu'il y a dans mon produit", 'wwc-shop'); ?></span>
                    <span class="wwc-accordion-arrow">∨</span>
                </button>
                <div class="wwc-accordion-content">
                    <?php echo wp_kses_post(wpautop($product['ingredients'])); ?>
                </div>
            </div>
            <?php endif; ?>

            <div class="wwc-accordion">
                <button class="wwc-accordion-header" type="button">
                    <span class="wwc-accordion-icon">🎖️</span>
                    <span><?php esc_html_e('Nos engagements', 'wwc-shop'); ?></span>
                    <span class="wwc-accordion-arrow">∨</span>
                </button>
                <div class="wwc-accordion-content">
                    <ul class="wwc-commitments-list">
                        <li>✓ <?php esc_html_e('Produits 100% naturels', 'wwc-shop'); ?></li>
                        <li>✓ <?php esc_html_e('Commerce équitable', 'wwc-shop'); ?></li>
                        <li>✓ <?php esc_html_e('Fabriqués par des producteurs locaux', 'wwc-shop'); ?></li>
                        <li>✓ <?php esc_html_e('Impact social direct', 'wwc-shop'); ?></li>
                    </ul>
                </div>
            </div>

            <?php if (!empty($product['usage'])): ?>
            <div class="wwc-accordion">
                <button class="wwc-accordion-header" type="button">
                    <span class="wwc-accordion-icon">🍃</span>
                    <span><?php esc_html_e('Utilisation', 'wwc-shop'); ?></span>
                    <span class="wwc-accordion-arrow">∨</span>
                </button>
                <div class="wwc-accordion-content">
                    <?php echo wp_kses_post(wpautop($product['usage'])); ?>
                </div>
            </div>
            <?php endif; ?>

            <?php if (!empty($product['producer'])): ?>
            <div class="wwc-accordion">
                <button class="wwc-accordion-header" type="button">
                    <span class="wwc-accordion-icon">👨‍🌾</span>
                    <span><?php esc_html_e('Le producteur', 'wwc-shop'); ?></span>
                    <span class="wwc-accordion-arrow">∨</span>
                </button>
                <div class="wwc-accordion-content">
                    <div class="wwc-producer-card">
                        <?php if (!empty($product['producer']['photo'])): ?>
                            <img src="<?php echo esc_url($product['producer']['photo']); ?>"
                                 alt="<?php echo esc_attr($product['producer']['name']); ?>"
                                 class="wwc-producer-photo">
                        <?php endif; ?>
                        <div class="wwc-producer-info">
                            <h4><?php echo esc_html($product['producer']['name']); ?></h4>
                            <p class="wwc-producer-location">
                                📍 <?php echo esc_html($product['producer']['location']); ?>
                            </p>
                            <?php if (!empty($product['producer']['bio'])): ?>
                                <p class="wwc-producer-bio"><?php echo esc_html($product['producer']['bio']); ?></p>
                            <?php endif; ?>
                        </div>
                    </div>
                </div>
            </div>
            <?php endif; ?>

        </div>

    </div>

</div>

<!-- Related Products Section -->
<?php
$api = wwc_shop()->api;
$related_products = $api->get_related_products($product['slug']);

if (!is_wp_error($related_products) && !empty($related_products)):
?>
<div class="wwc-related-products">
    <h2 class="wwc-section-title"><?php esc_html_e('Complétez ce rituel avec', 'wwc-shop'); ?></h2>

    <div class="wwc-product-grid wwc-grid-4">
        <?php foreach ($related_products as $related): ?>
            <div class="wwc-product-card">
                <a href="<?php echo esc_url(WWC_Product::get_url($related['slug'])); ?>">
                    <div class="wwc-product-image">
                        <img
                            src="<?php echo esc_url(WWC_Product::get_image_url($related)); ?>"
                            alt="<?php echo esc_attr($related['name']); ?>"
                            loading="lazy"
                        >
                    </div>
                    <h3 class="wwc-product-name"><?php echo esc_html($related['name']); ?></h3>
                    <div class="wwc-product-price">
                        <?php echo esc_html(WWC_Cart::format_price($related['price_tnd'])); ?>
                    </div>
                </a>
            </div>
        <?php endforeach; ?>
    </div>
</div>
<?php endif; ?>
