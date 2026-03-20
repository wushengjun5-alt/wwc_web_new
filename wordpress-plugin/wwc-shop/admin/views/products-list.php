<?php
/**
 * Products List Admin Page
 *
 * @package WWC_Shop
 */

defined('ABSPATH') || exit;

$products_list = is_wp_error($products) ? [] : ($products['results'] ?? $products);
$total_count = is_wp_error($products) ? 0 : ($products['count'] ?? count($products_list));
$categories_list = is_wp_error($categories) ? [] : $categories;
$stats_data = is_wp_error($stats) ? [] : $stats;
?>

<div class="wrap wwc-products-admin">
    <h1 class="wp-heading-inline"><?php _e('Products', 'wwc-shop'); ?></h1>
    <a href="<?php echo esc_url(admin_url('admin.php?page=wwc-product-edit')); ?>" class="page-title-action">
        <?php _e('Add New', 'wwc-shop'); ?>
    </a>
    <hr class="wp-header-end">

    <?php if (empty($this->admin_api_key)): ?>
    <div class="notice notice-warning">
        <p>
            <strong><?php _e('Admin API Key not configured!', 'wwc-shop'); ?></strong>
            <?php _e('Please configure your Admin API Key in', 'wwc-shop'); ?>
            <a href="<?php echo esc_url(admin_url('admin.php?page=wwc-shop-settings')); ?>"><?php _e('Settings', 'wwc-shop'); ?></a>
            <?php _e('to manage products.', 'wwc-shop'); ?>
        </p>
    </div>
    <?php endif; ?>

    <!-- Stats Cards -->
    <?php if (!empty($stats_data)): ?>
    <div class="wwc-stats-cards">
        <div class="wwc-stat-card">
            <span class="wwc-stat-number"><?php echo esc_html($stats_data['total_products'] ?? 0); ?></span>
            <span class="wwc-stat-label"><?php _e('Total Products', 'wwc-shop'); ?></span>
        </div>
        <div class="wwc-stat-card wwc-stat-published">
            <span class="wwc-stat-number"><?php echo esc_html($stats_data['published_products'] ?? 0); ?></span>
            <span class="wwc-stat-label"><?php _e('Published', 'wwc-shop'); ?></span>
        </div>
        <div class="wwc-stat-card wwc-stat-draft">
            <span class="wwc-stat-number"><?php echo esc_html($stats_data['draft_products'] ?? 0); ?></span>
            <span class="wwc-stat-label"><?php _e('Draft', 'wwc-shop'); ?></span>
        </div>
        <div class="wwc-stat-card wwc-stat-warning">
            <span class="wwc-stat-number"><?php echo esc_html($stats_data['low_stock_products'] ?? 0); ?></span>
            <span class="wwc-stat-label"><?php _e('Low Stock', 'wwc-shop'); ?></span>
        </div>
        <div class="wwc-stat-card">
            <span class="wwc-stat-number"><?php echo esc_html($stats_data['missing_english'] ?? 0); ?></span>
            <span class="wwc-stat-label"><?php _e('Missing EN', 'wwc-shop'); ?></span>
        </div>
        <div class="wwc-stat-card">
            <span class="wwc-stat-number"><?php echo esc_html($stats_data['missing_arabic'] ?? 0); ?></span>
            <span class="wwc-stat-label"><?php _e('Missing AR', 'wwc-shop'); ?></span>
        </div>
    </div>
    <?php endif; ?>

    <!-- Filters -->
    <div class="wwc-filters">
        <form method="get" action="">
            <input type="hidden" name="page" value="wwc-products">

            <div class="wwc-filter-row">
                <!-- Search -->
                <div class="wwc-filter-item">
                    <input type="search" name="s" value="<?php echo esc_attr($search); ?>"
                           placeholder="<?php esc_attr_e('Search products...', 'wwc-shop'); ?>"
                           class="wwc-search-input">
                </div>

                <!-- Status Filter -->
                <div class="wwc-filter-item">
                    <select name="status" class="wwc-filter-select">
                        <option value=""><?php _e('All Status', 'wwc-shop'); ?></option>
                        <option value="published" <?php selected($status, 'published'); ?>><?php _e('Published', 'wwc-shop'); ?></option>
                        <option value="draft" <?php selected($status, 'draft'); ?>><?php _e('Draft', 'wwc-shop'); ?></option>
                    </select>
                </div>

                <!-- Category Filter -->
                <div class="wwc-filter-item">
                    <select name="category" class="wwc-filter-select">
                        <option value=""><?php _e('All Categories', 'wwc-shop'); ?></option>
                        <?php foreach ($categories_list as $cat): ?>
                        <option value="<?php echo esc_attr($cat['id']); ?>" <?php selected($category, $cat['id']); ?>>
                            <?php echo esc_html($cat['name']); ?>
                        </option>
                        <?php endforeach; ?>
                    </select>
                </div>

                <div class="wwc-filter-item">
                    <button type="submit" class="button"><?php _e('Filter', 'wwc-shop'); ?></button>
                    <?php if ($search || $status || $category): ?>
                    <a href="<?php echo esc_url(admin_url('admin.php?page=wwc-products')); ?>" class="button">
                        <?php _e('Clear', 'wwc-shop'); ?>
                    </a>
                    <?php endif; ?>
                </div>
            </div>
        </form>
    </div>

    <!-- Bulk Actions -->
    <div class="wwc-bulk-actions">
        <select id="wwc-bulk-action" class="wwc-bulk-select">
            <option value=""><?php _e('Bulk Actions', 'wwc-shop'); ?></option>
            <option value="publish"><?php _e('Publish', 'wwc-shop'); ?></option>
            <option value="unpublish"><?php _e('Unpublish', 'wwc-shop'); ?></option>
            <option value="delete"><?php _e('Delete', 'wwc-shop'); ?></option>
        </select>
        <button type="button" id="wwc-bulk-apply" class="button"><?php _e('Apply', 'wwc-shop'); ?></button>
        <span class="wwc-selected-count"></span>
    </div>

    <!-- Products Table -->
    <table class="wp-list-table widefat fixed striped wwc-products-table">
        <thead>
            <tr>
                <td class="manage-column column-cb check-column">
                    <input type="checkbox" id="wwc-select-all">
                </td>
                <th class="manage-column column-image"><?php _e('Image', 'wwc-shop'); ?></th>
                <th class="manage-column column-name"><?php _e('Name', 'wwc-shop'); ?></th>
                <th class="manage-column column-sku"><?php _e('SKU', 'wwc-shop'); ?></th>
                <th class="manage-column column-category"><?php _e('Category', 'wwc-shop'); ?></th>
                <th class="manage-column column-price"><?php _e('Price', 'wwc-shop'); ?></th>
                <th class="manage-column column-stock"><?php _e('Stock', 'wwc-shop'); ?></th>
                <th class="manage-column column-langs"><?php _e('Languages', 'wwc-shop'); ?></th>
                <th class="manage-column column-status"><?php _e('Status', 'wwc-shop'); ?></th>
                <th class="manage-column column-date"><?php _e('Date', 'wwc-shop'); ?></th>
            </tr>
        </thead>
        <tbody>
            <?php if (empty($products_list)): ?>
            <tr>
                <td colspan="10" class="wwc-no-items">
                    <?php if (is_wp_error($products)): ?>
                        <p class="wwc-error"><?php echo esc_html($products->get_error_message()); ?></p>
                    <?php else: ?>
                        <p><?php _e('No products found.', 'wwc-shop'); ?></p>
                        <a href="<?php echo esc_url(admin_url('admin.php?page=wwc-product-edit')); ?>" class="button button-primary">
                            <?php _e('Add Your First Product', 'wwc-shop'); ?>
                        </a>
                    <?php endif; ?>
                </td>
            </tr>
            <?php else: ?>
                <?php foreach ($products_list as $product): ?>
                <tr data-product-id="<?php echo esc_attr($product['id']); ?>">
                    <th scope="row" class="check-column">
                        <input type="checkbox" class="wwc-product-checkbox" value="<?php echo esc_attr($product['id']); ?>">
                    </th>
                    <td class="column-image">
                        <?php if (!empty($product['primary_image_url'])): ?>
                        <img src="<?php echo esc_url($product['primary_image_url']); ?>" alt="" class="wwc-product-thumb">
                        <?php else: ?>
                        <span class="wwc-no-image">📦</span>
                        <?php endif; ?>
                    </td>
                    <td class="column-name">
                        <strong>
                            <a href="<?php echo esc_url(admin_url('admin.php?page=wwc-product-edit&id=' . $product['id'])); ?>">
                                <?php echo esc_html($product['name']); ?>
                            </a>
                        </strong>
                        <?php if (!empty($product['is_featured'])): ?>
                        <span class="wwc-badge wwc-badge-featured">★</span>
                        <?php endif; ?>
                        <div class="row-actions">
                            <span class="edit">
                                <a href="<?php echo esc_url(admin_url('admin.php?page=wwc-product-edit&id=' . $product['id'])); ?>">
                                    <?php _e('Edit', 'wwc-shop'); ?>
                                </a> |
                            </span>
                            <span class="duplicate">
                                <a href="#" class="wwc-duplicate-product" data-id="<?php echo esc_attr($product['id']); ?>">
                                    <?php _e('Duplicate', 'wwc-shop'); ?>
                                </a> |
                            </span>
                            <span class="trash">
                                <a href="#" class="wwc-delete-product" data-id="<?php echo esc_attr($product['id']); ?>">
                                    <?php _e('Delete', 'wwc-shop'); ?>
                                </a>
                            </span>
                        </div>
                    </td>
                    <td class="column-sku">
                        <code><?php echo esc_html($product['sku'] ?? '—'); ?></code>
                    </td>
                    <td class="column-category">
                        <?php echo esc_html($product['category_name'] ?? '—'); ?>
                    </td>
                    <td class="column-price">
                        <strong><?php echo esc_html(number_format($product['price_tnd'] ?? 0, 2)); ?> DT</strong>
                        <?php if (!empty($product['price_eur'])): ?>
                        <br><small><?php echo esc_html(number_format($product['price_eur'], 2)); ?> €</small>
                        <?php endif; ?>
                    </td>
                    <td class="column-stock">
                        <?php
                        $stock = $product['stock_quantity'] ?? 0;
                        $stock_class = $stock <= 0 ? 'wwc-stock-out' : ($stock <= 10 ? 'wwc-stock-low' : 'wwc-stock-ok');
                        ?>
                        <span class="<?php echo esc_attr($stock_class); ?>"><?php echo esc_html($stock); ?></span>
                    </td>
                    <td class="column-langs">
                        <?php
                        $langs = $product['language_completeness'] ?? [];
                        ?>
                        <span class="wwc-lang <?php echo !empty($langs['fr']) ? 'wwc-lang-complete' : ''; ?>">FR</span>
                        <span class="wwc-lang <?php echo !empty($langs['en']) ? 'wwc-lang-complete' : ''; ?>">EN</span>
                        <span class="wwc-lang <?php echo !empty($langs['ar']) ? 'wwc-lang-complete' : ''; ?>">AR</span>
                    </td>
                    <td class="column-status">
                        <?php if (!empty($product['is_active'])): ?>
                        <span class="wwc-status wwc-status-published"><?php _e('Published', 'wwc-shop'); ?></span>
                        <?php else: ?>
                        <span class="wwc-status wwc-status-draft"><?php _e('Draft', 'wwc-shop'); ?></span>
                        <?php endif; ?>
                    </td>
                    <td class="column-date">
                        <?php
                        $date = $product['updated_at'] ?? $product['created_at'] ?? '';
                        echo $date ? esc_html(date_i18n(get_option('date_format'), strtotime($date))) : '—';
                        ?>
                    </td>
                </tr>
                <?php endforeach; ?>
            <?php endif; ?>
        </tbody>
    </table>

    <!-- Pagination -->
    <?php if ($total_count > 20): ?>
    <div class="wwc-pagination">
        <?php
        $total_pages = ceil($total_count / 20);
        for ($i = 1; $i <= $total_pages; $i++):
            $active = ($i == $page) ? 'wwc-page-active' : '';
            $url = add_query_arg(['paged' => $i], admin_url('admin.php?page=wwc-products'));
        ?>
        <a href="<?php echo esc_url($url); ?>" class="wwc-page-link <?php echo esc_attr($active); ?>">
            <?php echo esc_html($i); ?>
        </a>
        <?php endfor; ?>
    </div>
    <?php endif; ?>
</div>
