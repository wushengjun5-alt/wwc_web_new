<?php
/**
 * WWC Shop - Shipping Rates Admin
 *
 * WordPress admin page for managing per-country shipping rates.
 * Reads and writes via the Django admin API (/api/v1/admin/shipping-rates/).
 *
 * @package WWC_Shop
 */

defined('ABSPATH') || exit;

class WWC_Shipping_Admin {

    public function __construct() {
        add_action('admin_menu',            [$this, 'add_menu']);
        add_action('admin_post_wwc_save_shipping_rate',   [$this, 'handle_save']);
        add_action('admin_post_wwc_delete_shipping_rate', [$this, 'handle_delete']);
    }

    public function add_menu() {
        add_submenu_page(
            'wwc-shop',
            __('Shipping Rates', 'wwc-shop'),
            __('Shipping Rates', 'wwc-shop'),
            'manage_options',
            'wwc-shipping-rates',
            [$this, 'render_page']
        );
    }

    /**
     * Perform an admin API request using the stored admin API key.
     */
    private function admin_request($endpoint, $method = 'GET', $data = []) {
        $api_url   = get_option('wwc_api_url', 'https://api.wallahwecan.org');
        $admin_key = get_option('wwc_admin_api_key', '');
        $url       = rtrim($api_url, '/') . '/api/v1' . $endpoint;

        $args = [
            'method'  => $method,
            'timeout' => 15,
            'headers' => [
                'Authorization' => 'Api-Key ' . $admin_key,
                'Content-Type'  => 'application/json',
                'Accept'        => 'application/json',
            ],
        ];

        if (!empty($data)) {
            $args['body'] = wp_json_encode($data);
        }

        $response = wp_remote_request($url, $args);

        if (is_wp_error($response)) {
            return ['error' => $response->get_error_message()];
        }

        $code = wp_remote_retrieve_response_code($response);
        $body = wp_remote_retrieve_body($response);

        if (in_array($code, [200, 201], true)) {
            return json_decode($body, true) ?: [];
        }
        if ($code === 204) {
            return ['deleted' => true];
        }

        $err = json_decode($body, true);
        return ['error' => is_array($err) ? wp_json_encode($err) : "HTTP $code"];
    }

    public function render_page() {
        $notice  = '';
        $action  = isset($_GET['action'])  ? sanitize_text_field($_GET['action'])  : 'list';
        $rate_id = isset($_GET['rate_id']) ? intval($_GET['rate_id'])              : 0;

        if ($action === 'edit' && $rate_id) {
            $rate = $this->admin_request("/admin/shipping-rates/{$rate_id}/");
            if (isset($rate['error'])) {
                $action = 'list';
                $notice = '<div class="notice notice-error"><p>' . esc_html($rate['error']) . '</p></div>';
            }
        }

        $rates_data = $this->admin_request('/admin/shipping-rates/?page_size=100');
        $rates = isset($rates_data['results']) ? $rates_data['results'] : [];
        ?>
        <div class="wrap">
            <h1 class="wp-heading-inline"><?php esc_html_e('Shipping Rates', 'wwc-shop'); ?></h1>
            <?php if ($action === 'list'): ?>
            <a href="<?php echo esc_url(admin_url('admin.php?page=wwc-shipping-rates&action=new')); ?>" class="page-title-action">
                <?php esc_html_e('Add Country', 'wwc-shop'); ?>
            </a>
            <?php endif; ?>
            <hr class="wp-header-end">

            <?php echo $notice; // already escaped above ?>

            <?php if ($action === 'list'): ?>

            <p class="description"><?php esc_html_e('Shipping rates are stored in TND. Free shipping applies when the order subtotal meets or exceeds the threshold.', 'wwc-shop'); ?></p>

            <?php if (empty($rates)): ?>
                <div class="notice notice-warning" style="margin-top:16px;"><p><?php esc_html_e('No shipping rates configured. Add at least one country to enable shipping.', 'wwc-shop'); ?></p></div>
            <?php else: ?>
            <table class="wp-list-table widefat fixed striped" style="margin-top:16px;">
                <thead>
                    <tr>
                        <th><?php esc_html_e('Country', 'wwc-shop'); ?></th>
                        <th><?php esc_html_e('Code', 'wwc-shop'); ?></th>
                        <th><?php esc_html_e('Rate (TND)', 'wwc-shop'); ?></th>
                        <th><?php esc_html_e('Free Shipping From (TND)', 'wwc-shop'); ?></th>
                        <th><?php esc_html_e('Status', 'wwc-shop'); ?></th>
                        <th><?php esc_html_e('Actions', 'wwc-shop'); ?></th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($rates as $r): ?>
                    <tr>
                        <td><strong><?php echo esc_html($r['country_name']); ?></strong></td>
                        <td><code><?php echo esc_html($r['country_code']); ?></code></td>
                        <td><?php echo esc_html(number_format((float) $r['rate_tnd'], 2)); ?> DT</td>
                        <td><?php echo (float) $r['free_threshold_tnd'] > 0 ? esc_html(number_format((float) $r['free_threshold_tnd'], 2)) . ' DT' : '—'; ?></td>
                        <td>
                            <?php if ($r['is_active']): ?>
                                <span style="color:#155724;background:#d4edda;padding:2px 10px;border-radius:30px;font-size:12px;font-weight:600;"><?php esc_html_e('Active', 'wwc-shop'); ?></span>
                            <?php else: ?>
                                <span style="color:#721c24;background:#f8d7da;padding:2px 10px;border-radius:30px;font-size:12px;font-weight:600;"><?php esc_html_e('Inactive', 'wwc-shop'); ?></span>
                            <?php endif; ?>
                        </td>
                        <td>
                            <a href="<?php echo esc_url(admin_url('admin.php?page=wwc-shipping-rates&action=edit&rate_id=' . intval($r['id']))); ?>">
                                <?php esc_html_e('Edit', 'wwc-shop'); ?>
                            </a> |
                            <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>" style="display:inline;" onsubmit="return confirm('<?php echo esc_js(__('Delete this shipping rate?', 'wwc-shop')); ?>')">
                                <?php wp_nonce_field('wwc_delete_shipping_rate_' . intval($r['id']), 'wwc_nonce'); ?>
                                <input type="hidden" name="action"  value="wwc_delete_shipping_rate">
                                <input type="hidden" name="rate_id" value="<?php echo intval($r['id']); ?>">
                                <button type="submit" class="button-link" style="color:#b32d2e;"><?php esc_html_e('Delete', 'wwc-shop'); ?></button>
                            </form>
                        </td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
            <?php endif; ?>

            <?php elseif (in_array($action, ['new', 'edit'], true)): ?>

            <a href="<?php echo esc_url(admin_url('admin.php?page=wwc-shipping-rates')); ?>" style="text-decoration:none;">&larr; <?php esc_html_e('Back to list', 'wwc-shop'); ?></a>

            <h2 style="margin-top:16px;"><?php echo $action === 'edit' ? esc_html__('Edit Shipping Rate', 'wwc-shop') : esc_html__('Add Country', 'wwc-shop'); ?></h2>

            <?php
            $r = ($action === 'edit' && !empty($rate)) ? $rate : [
                'id' => '', 'country_code' => '', 'country_name' => '',
                'rate_tnd' => '0.00', 'free_threshold_tnd' => '0.00', 'is_active' => true,
            ];
            ?>

            <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>" style="max-width:540px;margin-top:20px;">
                <?php wp_nonce_field('wwc_save_shipping_rate', 'wwc_nonce'); ?>
                <input type="hidden" name="action"  value="wwc_save_shipping_rate">
                <input type="hidden" name="rate_id" value="<?php echo intval($r['id'] ?? 0); ?>">

                <table class="form-table">
                    <tr>
                        <th><label for="country_code"><?php esc_html_e('Country Code (2 letters)', 'wwc-shop'); ?> *</label></th>
                        <td>
                            <input type="text" id="country_code" name="country_code" class="small-text"
                                   value="<?php echo esc_attr($r['country_code']); ?>"
                                   maxlength="2" pattern="[A-Za-z]{2}" required
                                   style="text-transform:uppercase;" placeholder="TN">
                        </td>
                    </tr>
                    <tr>
                        <th><label for="country_name"><?php esc_html_e('Country Name', 'wwc-shop'); ?> *</label></th>
                        <td>
                            <input type="text" id="country_name" name="country_name" class="regular-text"
                                   value="<?php echo esc_attr($r['country_name']); ?>"
                                   required placeholder="Tunisie">
                        </td>
                    </tr>
                    <tr>
                        <th><label for="rate_tnd"><?php esc_html_e('Shipping Rate (TND)', 'wwc-shop'); ?></label></th>
                        <td>
                            <input type="number" id="rate_tnd" name="rate_tnd" class="small-text"
                                   value="<?php echo esc_attr($r['rate_tnd']); ?>"
                                   min="0" step="0.01" placeholder="7.00">
                            <p class="description"><?php esc_html_e('Set to 0 for free shipping always.', 'wwc-shop'); ?></p>
                        </td>
                    </tr>
                    <tr>
                        <th><label for="free_threshold_tnd"><?php esc_html_e('Free Shipping Threshold (TND)', 'wwc-shop'); ?></label></th>
                        <td>
                            <input type="number" id="free_threshold_tnd" name="free_threshold_tnd" class="small-text"
                                   value="<?php echo esc_attr($r['free_threshold_tnd']); ?>"
                                   min="0" step="0.01" placeholder="100.00">
                            <p class="description"><?php esc_html_e('Orders above this amount get free shipping. Set to 0 to disable.', 'wwc-shop'); ?></p>
                        </td>
                    </tr>
                    <tr>
                        <th><?php esc_html_e('Active', 'wwc-shop'); ?></th>
                        <td>
                            <input type="checkbox" id="is_active" name="is_active" value="1"
                                   <?php checked(!empty($r['is_active'])); ?>>
                            <label for="is_active"><?php esc_html_e('Enable this shipping destination', 'wwc-shop'); ?></label>
                        </td>
                    </tr>
                </table>

                <?php submit_button($action === 'edit' ? __('Save Changes', 'wwc-shop') : __('Add Country', 'wwc-shop')); ?>
            </form>

            <?php endif; ?>
        </div>
        <?php
    }

    public function handle_save() {
        if (!current_user_can('manage_options')) wp_die('Forbidden');
        check_admin_referer('wwc_save_shipping_rate', 'wwc_nonce');

        $rate_id = intval($_POST['rate_id'] ?? 0);
        $payload = [
            'country_code'       => strtoupper(sanitize_text_field($_POST['country_code'] ?? '')),
            'country_name'       => sanitize_text_field($_POST['country_name'] ?? ''),
            'rate_tnd'           => floatval($_POST['rate_tnd'] ?? 0),
            'free_threshold_tnd' => floatval($_POST['free_threshold_tnd'] ?? 0),
            'is_active'          => !empty($_POST['is_active']),
        ];

        if ($rate_id) {
            $result = $this->admin_request("/admin/shipping-rates/{$rate_id}/", 'PATCH', $payload);
        } else {
            $result = $this->admin_request('/admin/shipping-rates/', 'POST', $payload);
        }

        $redirect = admin_url('admin.php?page=wwc-shipping-rates');
        if (isset($result['error'])) {
            $redirect = add_query_arg('wwc_error', urlencode($result['error']), $redirect);
        } else {
            $redirect = add_query_arg('wwc_saved', '1', $redirect);
        }

        wp_safe_redirect($redirect);
        exit;
    }

    public function handle_delete() {
        if (!current_user_can('manage_options')) wp_die('Forbidden');
        $rate_id = intval($_POST['rate_id'] ?? 0);
        check_admin_referer('wwc_delete_shipping_rate_' . $rate_id, 'wwc_nonce');

        $this->admin_request("/admin/shipping-rates/{$rate_id}/", 'DELETE');

        wp_safe_redirect(add_query_arg('wwc_deleted', '1', admin_url('admin.php?page=wwc-shipping-rates')));
        exit;
    }
}

new WWC_Shipping_Admin();
