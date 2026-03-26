<?php
/**
 * WWC Shop Admin Dashboard
 *
 * @package WWC_Shop
 */

defined('ABSPATH') || exit;

$api = wwc_shop()->api;
$impact_summary = $api->get_impact_summary();
$api_url = get_option('wwc_api_url', 'https://api.wallahwecan.org');
$api_ok  = !is_wp_error($impact_summary);
?>

<div class="wrap">
    <h1><?php esc_html_e('WWC Shop Dashboard', 'wwc-shop'); ?></h1>

    <?php if ($api_ok): ?>
    <div class="notice notice-success inline"><p>✅ <?php printf(esc_html__('API connected: %s', 'wwc-shop'), esc_html($api_url)); ?></p></div>
    <?php else: ?>
    <div class="notice notice-error inline">
        <p>❌ <strong><?php esc_html_e('Cannot reach Django API', 'wwc-shop'); ?></strong></p>
        <p><?php printf(
            esc_html__('Current API URL: %s — %s', 'wwc-shop'),
            '<code>' . esc_html($api_url) . '</code>',
            '<a href="' . esc_url(admin_url('admin.php?page=wwc-shop-settings')) . '">' . esc_html__('Update in Settings', 'wwc-shop') . '</a>'
        ); ?></p>
        <p><em><?php echo esc_html($impact_summary->get_error_message()); ?></em></p>
        <p><?php esc_html_e('If running locally, set the API URL to: http://127.0.0.1:8000', 'wwc-shop'); ?></p>
    </div>
    <?php endif; ?>

    <div class="wwc-admin-dashboard">

        <div class="wwc-admin-card">
            <h2><?php esc_html_e('Quick Links', 'wwc-shop'); ?></h2>
            <ul>
                <li>
                    <a href="<?php echo esc_url(home_url('/shop/')); ?>" target="_blank">
                        <?php esc_html_e('View Shop', 'wwc-shop'); ?> →
                    </a>
                </li>
                <li>
                    <a href="<?php echo esc_url(admin_url('admin.php?page=wwc-shop-settings')); ?>">
                        <?php esc_html_e('Shop Settings', 'wwc-shop'); ?> →
                    </a>
                </li>
                <li>
                    <a href="<?php echo esc_url(get_option('wwc_api_url', 'https://api.wallahwecan.org') . '/admin/'); ?>" target="_blank">
                        <?php esc_html_e('Django Admin', 'wwc-shop'); ?> →
                    </a>
                </li>
            </ul>
        </div>

        <?php if (!is_wp_error($impact_summary)): ?>
        <div class="wwc-admin-card">
            <h2><?php esc_html_e('Impact Summary', 'wwc-shop'); ?></h2>
            <div class="wwc-impact-stats">
                <div class="wwc-stat">
                    <span class="wwc-stat-number">
                        <?php echo esc_html(number_format($impact_summary['total_impact_items'] ?? 0)); ?>
                    </span>
                    <span class="wwc-stat-label"><?php esc_html_e('Total Impact Items', 'wwc-shop'); ?></span>
                </div>
                <div class="wwc-stat">
                    <span class="wwc-stat-number">
                        <?php echo esc_html(number_format($impact_summary['total_orders'] ?? 0)); ?>
                    </span>
                    <span class="wwc-stat-label"><?php esc_html_e('Total Orders', 'wwc-shop'); ?></span>
                </div>
            </div>
        </div>
        <?php endif; ?>

        <div class="wwc-admin-card">
            <h2><?php esc_html_e('Shortcodes', 'wwc-shop'); ?></h2>
            <table class="wp-list-table widefat fixed striped">
                <thead>
                    <tr>
                        <th><?php esc_html_e('Shortcode', 'wwc-shop'); ?></th>
                        <th><?php esc_html_e('Description', 'wwc-shop'); ?></th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><code>[wwc_products]</code></td>
                        <td><?php esc_html_e('Display product grid', 'wwc-shop'); ?></td>
                    </tr>
                    <tr>
                        <td><code>[wwc_products category="soins"]</code></td>
                        <td><?php esc_html_e('Products by category', 'wwc-shop'); ?></td>
                    </tr>
                    <tr>
                        <td><code>[wwc_products featured="true"]</code></td>
                        <td><?php esc_html_e('Featured products only', 'wwc-shop'); ?></td>
                    </tr>
                    <tr>
                        <td><code>[wwc_product slug="roll-on-calme"]</code></td>
                        <td><?php esc_html_e('Single product display', 'wwc-shop'); ?></td>
                    </tr>
                    <tr>
                        <td><code>[wwc_categories]</code></td>
                        <td><?php esc_html_e('Category navigation', 'wwc-shop'); ?></td>
                    </tr>
                    <tr>
                        <td><code>[wwc_cart]</code></td>
                        <td><?php esc_html_e('Cart page content', 'wwc-shop'); ?></td>
                    </tr>
                    <tr>
                        <td><code>[wwc_checkout]</code></td>
                        <td><?php esc_html_e('Checkout page', 'wwc-shop'); ?></td>
                    </tr>
                    <tr>
                        <td><code>[wwc_customer_dashboard]</code></td>
                        <td><?php esc_html_e('Customer dashboard with impact tracking', 'wwc-shop'); ?></td>
                    </tr>
                    <tr>
                        <td><code>[wwc_impact]</code></td>
                        <td><?php esc_html_e('Impact events display', 'wwc-shop'); ?></td>
                    </tr>
                </tbody>
            </table>
        </div>

    </div>
</div>

<style>
.wwc-admin-dashboard {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

.wwc-admin-card {
    background: #fff;
    border: 1px solid #ccd0d4;
    border-radius: 4px;
    padding: 20px;
}

.wwc-admin-card h2 {
    margin-top: 0;
    padding-bottom: 10px;
    border-bottom: 1px solid #eee;
}

.wwc-admin-card ul {
    margin: 0;
    padding: 0;
    list-style: none;
}

.wwc-admin-card li {
    padding: 8px 0;
    border-bottom: 1px solid #f0f0f0;
}

.wwc-admin-card li:last-child {
    border-bottom: none;
}

.wwc-impact-stats {
    display: flex;
    gap: 30px;
}

.wwc-stat {
    text-align: center;
}

.wwc-stat-number {
    display: block;
    font-size: 36px;
    font-weight: 600;
    color: #1e3a5f;
}

.wwc-stat-label {
    display: block;
    color: #666;
    font-size: 14px;
}
</style>
