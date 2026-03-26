<?php
/**
 * WWC Shop - Site Settings Admin
 *
 * WordPress admin page for managing the TND→EUR exchange rate and other
 * site-wide settings stored in the Django DB (SiteSettings model).
 *
 * @package WWC_Shop
 */

defined('ABSPATH') || exit;

class WWC_Site_Settings_Admin {

    public function __construct() {
        add_action('admin_menu',                          [$this, 'add_menu']);
        add_action('admin_post_wwc_save_site_settings',  [$this, 'handle_save']);
    }

    public function add_menu() {
        add_submenu_page(
            'wwc-shop',
            __('Exchange Rate', 'wwc-shop'),
            __('Exchange Rate', 'wwc-shop'),
            'manage_options',
            'wwc-site-settings',
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
        $decoded = json_decode($body, true);

        if ($code >= 200 && $code < 300) {
            return $decoded ?: [];
        }

        return ['error' => is_array($decoded) ? wp_json_encode($decoded) : "HTTP $code"];
    }

    public function render_page() {
        $saved = isset($_GET['wwc_saved']);
        $error = isset($_GET['wwc_error']) ? sanitize_text_field(urldecode($_GET['wwc_error'])) : '';

        $settings = $this->admin_request('/admin/settings/');
        $current_rate = isset($settings['tnd_to_eur_rate']) ? (float) $settings['tnd_to_eur_rate'] : 0.30;
        $updated_at   = $settings['updated_at'] ?? null;
        $api_error    = isset($settings['error']) ? $settings['error'] : '';
        ?>
        <div class="wrap">
            <h1><?php esc_html_e('TND → EUR Exchange Rate', 'wwc-shop'); ?></h1>
            <hr class="wp-header-end">

            <?php if ($saved): ?>
            <div class="notice notice-success is-dismissible"><p><?php esc_html_e('Exchange rate updated successfully.', 'wwc-shop'); ?></p></div>
            <?php endif; ?>

            <?php if ($error): ?>
            <div class="notice notice-error is-dismissible"><p><?php echo esc_html($error); ?></p></div>
            <?php endif; ?>

            <?php if ($api_error): ?>
            <div class="notice notice-warning"><p><strong><?php esc_html_e('Could not load current rate from API:', 'wwc-shop'); ?></strong> <?php echo esc_html($api_error); ?></p></div>
            <?php endif; ?>

            <div style="max-width:560px;background:white;border:1px solid #ddd;border-radius:8px;padding:24px 28px;margin-top:20px;">
                <p style="color:#666;margin-bottom:20px;">
                    <?php esc_html_e('Stripe does not support TND natively. Orders are charged in EUR using this conversion rate. The customer\'s bank handles the final TND conversion on their card statement.', 'wwc-shop'); ?>
                </p>

                <?php if ($updated_at): ?>
                <p style="font-size:12px;color:#999;margin-bottom:20px;">
                    <?php echo esc_html__('Last updated:', 'wwc-shop') . ' ' . esc_html(date_i18n(get_option('date_format') . ' ' . get_option('time_format'), strtotime($updated_at))); ?>
                </p>
                <?php endif; ?>

                <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                    <?php wp_nonce_field('wwc_save_site_settings', 'wwc_nonce'); ?>
                    <input type="hidden" name="action" value="wwc_save_site_settings">

                    <table class="form-table">
                        <tr>
                            <th><label for="tnd_to_eur_rate"><?php esc_html_e('1 TND = X EUR', 'wwc-shop'); ?></label></th>
                            <td>
                                <input type="number" id="tnd_to_eur_rate" name="tnd_to_eur_rate"
                                       class="small-text" step="0.000001" min="0.000001" max="1"
                                       value="<?php echo esc_attr(number_format($current_rate, 6)); ?>"
                                       required>
                                <p class="description">
                                    <?php echo sprintf(
                                        esc_html__('Example: %s means 1 TND = %s EUR. Update this regularly to reflect the real exchange rate.', 'wwc-shop'),
                                        '<code>0.295000</code>',
                                        '0.295'
                                    ); ?>
                                </p>
                            </td>
                        </tr>
                    </table>

                    <?php submit_button(__('Save Exchange Rate', 'wwc-shop')); ?>
                </form>
            </div>
        </div>
        <?php
    }

    public function handle_save() {
        if (!current_user_can('manage_options')) wp_die('Forbidden');
        check_admin_referer('wwc_save_site_settings', 'wwc_nonce');

        $rate = floatval($_POST['tnd_to_eur_rate'] ?? 0.30);
        $result = $this->admin_request('/admin/settings/', 'PUT', ['tnd_to_eur_rate' => $rate]);

        $redirect = admin_url('admin.php?page=wwc-site-settings');
        if (isset($result['error'])) {
            $redirect = add_query_arg('wwc_error', urlencode($result['error']), $redirect);
        } else {
            $redirect = add_query_arg('wwc_saved', '1', $redirect);
        }

        wp_safe_redirect($redirect);
        exit;
    }
}

new WWC_Site_Settings_Admin();
