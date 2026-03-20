<?php
/**
 * Product Grid Template
 *
 * Supports filter sidebar and pagination when $show_filters is true.
 *
 * @package WWC_Shop
 */

defined('ABSPATH') || exit;

$columns      = isset($atts['columns']) ? intval($atts['columns']) : 3;
$products_list = $products ?? [];
$show_filters  = $show_filters ?? false;
$total_pages   = $total_pages ?? 1;
$current_page  = $current_page ?? 1;
$categories    = $categories ?? [];

// Helper to build a URL preserving current query params but replacing $key=$val
function wwc_filter_url($key, $val) {
    $query = $_GET;
    if ($val === '') {
        unset($query[$key]);
    } else {
        $query[$key] = $val;
    }
    unset($query['page']); // reset to page 1 on filter change
    return add_query_arg(array_map('urlencode', $query), get_permalink());
}
?>

<div class="wwc-products-wrapper <?php echo $show_filters ? 'wwc-with-filters' : ''; ?>">

    <?php if ($show_filters): ?>
    <!-- Filter Sidebar -->
    <aside class="wwc-filter-sidebar">
        <form id="wwc-filter-form" method="get" action="<?php echo esc_url(get_permalink()); ?>">

            <!-- Search -->
            <div class="wwc-filter-section">
                <h4><?php esc_html_e('Recherche', 'wwc-shop'); ?></h4>
                <input type="text" name="search" class="wwc-filter-search"
                    placeholder="<?php esc_attr_e('Rechercher…', 'wwc-shop'); ?>"
                    value="<?php echo esc_attr($_GET['search'] ?? ''); ?>">
            </div>

            <!-- Category -->
            <?php if (!empty($categories)): ?>
            <div class="wwc-filter-section">
                <h4><?php esc_html_e('Catégorie', 'wwc-shop'); ?></h4>
                <ul class="wwc-filter-list">
                    <li>
                        <a href="<?php echo esc_url(wwc_filter_url('category', '')); ?>"
                           class="<?php echo empty($_GET['category']) ? 'active' : ''; ?>">
                            <?php esc_html_e('Toutes', 'wwc-shop'); ?>
                        </a>
                    </li>
                    <?php foreach ($categories as $cat): ?>
                    <li>
                        <a href="<?php echo esc_url(wwc_filter_url('category', $cat['slug'])); ?>"
                           class="<?php echo (($_GET['category'] ?? '') === $cat['slug']) ? 'active' : ''; ?>">
                            <?php echo esc_html($cat['name']); ?>
                        </a>
                    </li>
                    <?php endforeach; ?>
                </ul>
            </div>
            <?php endif; ?>

            <!-- Price range -->
            <div class="wwc-filter-section">
                <h4><?php esc_html_e('Prix (DT)', 'wwc-shop'); ?></h4>
                <div class="wwc-price-range">
                    <input type="number" name="min_price" placeholder="<?php esc_attr_e('Min', 'wwc-shop'); ?>"
                        value="<?php echo esc_attr($_GET['min_price'] ?? ''); ?>" min="0" step="1">
                    <span>—</span>
                    <input type="number" name="max_price" placeholder="<?php esc_attr_e('Max', 'wwc-shop'); ?>"
                        value="<?php echo esc_attr($_GET['max_price'] ?? ''); ?>" min="0" step="1">
                </div>
            </div>

            <!-- Badges -->
            <div class="wwc-filter-section">
                <h4><?php esc_html_e('Filtres', 'wwc-shop'); ?></h4>
                <label class="wwc-filter-checkbox">
                    <input type="checkbox" name="is_natural" value="true"
                        <?php checked(!empty($_GET['is_natural'])); ?>>
                    <?php esc_html_e('Naturel', 'wwc-shop'); ?>
                </label>
                <label class="wwc-filter-checkbox">
                    <input type="checkbox" name="is_organic" value="true"
                        <?php checked(!empty($_GET['is_organic'])); ?>>
                    <?php esc_html_e('Bio', 'wwc-shop'); ?>
                </label>
                <label class="wwc-filter-checkbox">
                    <input type="checkbox" name="in_stock" value="true"
                        <?php checked(!empty($_GET['in_stock'])); ?>>
                    <?php esc_html_e('En stock seulement', 'wwc-shop'); ?>
                </label>
            </div>

            <!-- Sort -->
            <div class="wwc-filter-section">
                <h4><?php esc_html_e('Trier par', 'wwc-shop'); ?></h4>
                <select name="ordering" class="wwc-filter-sort" onchange="this.form.submit()">
                    <option value="" <?php selected($_GET['ordering'] ?? '', ''); ?>><?php esc_html_e('Par défaut', 'wwc-shop'); ?></option>
                    <option value="price_tnd" <?php selected($_GET['ordering'] ?? '', 'price_tnd'); ?>><?php esc_html_e('Prix croissant', 'wwc-shop'); ?></option>
                    <option value="-price_tnd" <?php selected($_GET['ordering'] ?? '', '-price_tnd'); ?>><?php esc_html_e('Prix décroissant', 'wwc-shop'); ?></option>
                    <option value="-average_rating" <?php selected($_GET['ordering'] ?? '', '-average_rating'); ?>><?php esc_html_e('Mieux notés', 'wwc-shop'); ?></option>
                    <option value="-created_at" <?php selected($_GET['ordering'] ?? '', '-created_at'); ?>><?php esc_html_e('Nouveautés', 'wwc-shop'); ?></option>
                </select>
            </div>

            <button type="submit" class="wwc-btn wwc-btn--primary wwc-filter-apply">
                <?php esc_html_e('Appliquer', 'wwc-shop'); ?>
            </button>

            <?php if (!empty(array_filter($_GET))): ?>
            <a href="<?php echo esc_url(get_permalink()); ?>" class="wwc-filter-clear">
                <?php esc_html_e('Effacer les filtres', 'wwc-shop'); ?>
            </a>
            <?php endif; ?>

        </form>
    </aside>
    <?php endif; ?>

    <!-- Product Grid -->
    <div class="wwc-products-main">

        <?php if ($show_filters && !empty($_GET['search'])): ?>
        <p class="wwc-search-results-label">
            <?php printf(
                esc_html__('%d résultat(s) pour « %s »', 'wwc-shop'),
                $total ?? count($products_list),
                esc_html($_GET['search'])
            ); ?>
        </p>
        <?php endif; ?>

        <?php if (empty($products_list)): ?>
            <p class="wwc-no-products"><?php esc_html_e('Aucun produit trouvé.', 'wwc-shop'); ?></p>
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

            <!-- Pagination -->
            <?php if ($total_pages > 1): ?>
            <nav class="wwc-pagination" aria-label="<?php esc_attr_e('Pagination', 'wwc-shop'); ?>">
                <?php if ($current_page > 1): ?>
                    <a href="<?php echo esc_url(add_query_arg('page', $current_page - 1)); ?>" class="wwc-page-btn">
                        &larr; <?php esc_html_e('Précédent', 'wwc-shop'); ?>
                    </a>
                <?php endif; ?>

                <span class="wwc-page-info">
                    <?php printf(esc_html__('Page %d sur %d', 'wwc-shop'), $current_page, $total_pages); ?>
                </span>

                <?php if ($current_page < $total_pages): ?>
                    <a href="<?php echo esc_url(add_query_arg('page', $current_page + 1)); ?>" class="wwc-page-btn">
                        <?php esc_html_e('Suivant', 'wwc-shop'); ?> &rarr;
                    </a>
                <?php endif; ?>
            </nav>
            <?php endif; ?>

        <?php endif; ?>

    </div><!-- .wwc-products-main -->

</div><!-- .wwc-products-wrapper -->
