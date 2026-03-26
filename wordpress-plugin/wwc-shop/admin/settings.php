<?php
/**
 * WWC Shop Settings Page
 *
 * @package WWC_Shop
 */

defined('ABSPATH') || exit;
?>

<div class="wrap">
    <h1><?php echo esc_html(get_admin_page_title()); ?></h1>

    <form method="post" action="options.php">
        <?php
        settings_fields('wwc_shop_settings');
        do_settings_sections('wwc-shop-settings');
        ?>

        <table class="form-table">
            <tr>
                <th scope="row">
                    <label for="wwc_api_url"><?php esc_html_e('API URL', 'wwc-shop'); ?></label>
                </th>
                <td>
                    <input type="url" id="wwc_api_url" name="wwc_api_url" class="regular-text"
                           value="<?php echo esc_attr(get_option('wwc_api_url', 'https://api.wallahwecan.org')); ?>">
                    <p class="description">
                        <?php esc_html_e('The URL of the Django API backend', 'wwc-shop'); ?>
                    </p>
                </td>
            </tr>

            <tr>
                <th scope="row">
                    <label for="wwc_api_key"><?php esc_html_e('API Key', 'wwc-shop'); ?></label>
                </th>
                <td>
                    <input type="password" id="wwc_api_key" name="wwc_api_key" class="regular-text"
                           value="<?php echo esc_attr(get_option('wwc_api_key', '')); ?>">
                    <p class="description">
                        <?php esc_html_e('API authentication key (if required)', 'wwc-shop'); ?>
                    </p>
                </td>
            </tr>

            <tr>
                <th scope="row">
                    <label for="wwc_admin_api_key"><?php esc_html_e('Admin API Key', 'wwc-shop'); ?></label>
                </th>
                <td>
                    <input type="password" id="wwc_admin_api_key" name="wwc_admin_api_key" class="regular-text"
                           value="<?php echo esc_attr(get_option('wwc_admin_api_key', '')); ?>">
                    <p class="description">
                        <?php esc_html_e('Secret key for admin endpoints (products, shipping rates, settings). Must match ADMIN_API_KEY in Django settings.', 'wwc-shop'); ?>
                    </p>
                </td>
            </tr>

            <tr>
                <th scope="row">
                    <label for="wwc_default_currency"><?php esc_html_e('Default Currency', 'wwc-shop'); ?></label>
                </th>
                <td>
                    <select id="wwc_default_currency" name="wwc_default_currency">
                        <option value="TND" <?php selected(get_option('wwc_default_currency'), 'TND'); ?>>
                            TND (Tunisian Dinar)
                        </option>
                        <option value="EUR" <?php selected(get_option('wwc_default_currency'), 'EUR'); ?>>
                            EUR (Euro)
                        </option>
                    </select>
                </td>
            </tr>
        </table>

        <h2><?php esc_html_e('Stripe Settings', 'wwc-shop'); ?></h2>

        <table class="form-table">
            <tr>
                <th scope="row">
                    <label for="wwc_stripe_public_key"><?php esc_html_e('Stripe Public Key', 'wwc-shop'); ?></label>
                </th>
                <td>
                    <input type="text" id="wwc_stripe_public_key" name="wwc_stripe_public_key" class="regular-text"
                           value="<?php echo esc_attr(get_option('wwc_stripe_public_key', '')); ?>">
                </td>
            </tr>

            <tr>
                <th scope="row">
                    <label for="wwc_stripe_secret_key"><?php esc_html_e('Stripe Secret Key', 'wwc-shop'); ?></label>
                </th>
                <td>
                    <input type="password" id="wwc_stripe_secret_key" name="wwc_stripe_secret_key" class="regular-text"
                           value="<?php echo esc_attr(get_option('wwc_stripe_secret_key', '')); ?>">
                </td>
            </tr>
        </table>

        <?php submit_button(); ?>
    </form>
</div>
