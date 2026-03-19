<?php
/**
 * Checkout Page Template
 *
 * @package WWC_Shop
 */

defined('ABSPATH') || exit;

$currency        = get_option('wwc_default_currency', 'TND');
$currency_symbol = $currency === 'EUR' ? '€' : 'DT';
$countries       = WWC_Checkout::get_shipping_countries();
$payment_methods = WWC_Checkout::get_payment_methods($currency);
$states          = WWC_Checkout::get_tunisia_states();
?>

<div class="wwc-checkout-wrapper">
    <form id="wwc-checkout-form" class="wwc-checkout-form">
        <input type="hidden" name="currency" value="<?php echo esc_attr($currency); ?>">

        <div class="wwc-checkout-main">

            <!-- Contact Information -->
            <section class="wwc-checkout-section">
                <h2><?php esc_html_e('Informations de contact', 'wwc-shop'); ?></h2>

                <div class="wwc-form-row">
                    <div class="wwc-form-field wwc-field-half">
                        <label for="email"><?php esc_html_e('Email', 'wwc-shop'); ?> *</label>
                        <input type="email" id="email" name="email" required
                               value="<?php echo is_user_logged_in() ? esc_attr(wp_get_current_user()->user_email) : ''; ?>">
                    </div>
                    <div class="wwc-form-field wwc-field-half">
                        <label for="phone"><?php esc_html_e('Téléphone', 'wwc-shop'); ?> *</label>
                        <input type="tel" id="phone" name="phone" required placeholder="+216 XX XXX XXX">
                    </div>
                </div>
            </section>

            <!-- Shipping Address -->
            <section class="wwc-checkout-section">
                <h2><?php esc_html_e('Adresse de livraison', 'wwc-shop'); ?></h2>

                <div class="wwc-form-row">
                    <div class="wwc-form-field wwc-field-half">
                        <label for="shipping_first_name"><?php esc_html_e('Prénom', 'wwc-shop'); ?> *</label>
                        <input type="text" id="shipping_first_name" name="shipping_first_name" required>
                    </div>
                    <div class="wwc-form-field wwc-field-half">
                        <label for="shipping_last_name"><?php esc_html_e('Nom', 'wwc-shop'); ?> *</label>
                        <input type="text" id="shipping_last_name" name="shipping_last_name" required>
                    </div>
                </div>

                <div class="wwc-form-field">
                    <label for="shipping_company"><?php esc_html_e('Entreprise', 'wwc-shop'); ?> (<?php esc_html_e('optionnel', 'wwc-shop'); ?>)</label>
                    <input type="text" id="shipping_company" name="shipping_company">
                </div>

                <div class="wwc-form-field">
                    <label for="shipping_address_1"><?php esc_html_e('Adresse', 'wwc-shop'); ?> *</label>
                    <input type="text" id="shipping_address_1" name="shipping_address_1" required>
                </div>

                <div class="wwc-form-field">
                    <label for="shipping_address_2"><?php esc_html_e('Complément d\'adresse', 'wwc-shop'); ?></label>
                    <input type="text" id="shipping_address_2" name="shipping_address_2">
                </div>

                <div class="wwc-form-row">
                    <div class="wwc-form-field wwc-field-third">
                        <label for="shipping_postal_code"><?php esc_html_e('Code postal', 'wwc-shop'); ?> *</label>
                        <input type="text" id="shipping_postal_code" name="shipping_postal_code" required>
                    </div>
                    <div class="wwc-form-field wwc-field-third">
                        <label for="shipping_city"><?php esc_html_e('Ville', 'wwc-shop'); ?> *</label>
                        <input type="text" id="shipping_city" name="shipping_city" required>
                    </div>
                    <div class="wwc-form-field wwc-field-third">
                        <label for="shipping_state"><?php esc_html_e('Gouvernorat', 'wwc-shop'); ?></label>
                        <select id="shipping_state" name="shipping_state">
                            <option value=""><?php esc_html_e('Sélectionner', 'wwc-shop'); ?></option>
                            <?php foreach ($states as $code => $name): ?>
                                <option value="<?php echo esc_attr($code); ?>"><?php echo esc_html($name); ?></option>
                            <?php endforeach; ?>
                        </select>
                    </div>
                </div>

                <div class="wwc-form-field">
                    <label for="shipping_country"><?php esc_html_e('Pays', 'wwc-shop'); ?> *</label>
                    <select id="shipping_country" name="shipping_country" required>
                        <?php foreach ($countries as $code => $name): ?>
                            <option value="<?php echo esc_attr($code); ?>" <?php selected($code, 'TN'); ?>>
                                <?php echo esc_html($name); ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                </div>
            </section>

            <!-- Payment Method -->
            <section class="wwc-checkout-section">
                <h2><?php esc_html_e('Méthode de paiement', 'wwc-shop'); ?></h2>

                <div class="wwc-payment-methods">
                    <?php
                    $first_method = true;
                    foreach ($payment_methods as $method):
                    ?>
                        <label class="wwc-payment-method">
                            <input type="radio" name="payment_method" value="<?php echo esc_attr($method['id']); ?>"
                                   <?php if ($first_method) { echo 'checked'; $first_method = false; } ?>>
                            <span class="wwc-payment-method-content">
                                <span class="wwc-payment-method-title"><?php echo esc_html($method['title']); ?></span>
                                <span class="wwc-payment-method-desc"><?php echo esc_html($method['description']); ?></span>
                            </span>
                        </label>
                    <?php endforeach; ?>
                </div>
            </section>

            <!-- Order Notes -->
            <section class="wwc-checkout-section">
                <h2><?php esc_html_e('Notes de commande', 'wwc-shop'); ?></h2>

                <div class="wwc-form-field">
                    <label for="customer_notes"><?php esc_html_e('Instructions spéciales', 'wwc-shop'); ?></label>
                    <textarea id="customer_notes" name="customer_notes" rows="3"
                              placeholder="<?php esc_attr_e('Notes sur votre commande, instructions de livraison...', 'wwc-shop'); ?>"></textarea>
                </div>
            </section>

        </div>

        <!-- Order Summary Sidebar -->
        <aside class="wwc-checkout-sidebar">
            <div class="wwc-order-summary">
                <h3><?php esc_html_e('Récapitulatif de commande', 'wwc-shop'); ?></h3>

                <div id="wwc-checkout-items" class="wwc-checkout-items">
                    <!-- Items loaded via AJAX -->
                    <div class="wwc-cart-loading">
                        <span class="wwc-spinner"></span>
                    </div>
                </div>

                <div class="wwc-checkout-totals" data-currency="<?php echo esc_attr($currency); ?>" data-currency-symbol="<?php echo esc_attr($currency_symbol); ?>">
                    <div class="wwc-checkout-row">
                        <span><?php esc_html_e('Sous-total', 'wwc-shop'); ?></span>
                        <span id="wwc-checkout-subtotal">0 <?php echo esc_html($currency_symbol); ?></span>
                    </div>
                    <div class="wwc-checkout-row">
                        <span><?php esc_html_e('Livraison', 'wwc-shop'); ?></span>
                        <span id="wwc-checkout-shipping"><?php esc_html_e('Calculé selon le pays', 'wwc-shop'); ?></span>
                    </div>
                    <div class="wwc-checkout-row wwc-checkout-total">
                        <span><?php esc_html_e('Total', 'wwc-shop'); ?></span>
                        <span id="wwc-checkout-total">0 <?php echo esc_html($currency_symbol); ?></span>
                    </div>
                </div>

                <!-- Impact Summary -->
                <div class="wwc-checkout-impact" id="wwc-checkout-impact">
                    <!-- Impact loaded via AJAX -->
                </div>

                <button type="submit" class="wwc-btn wwc-btn-primary wwc-btn-checkout">
                    <?php esc_html_e('Confirmer la commande', 'wwc-shop'); ?>
                </button>

                <p class="wwc-checkout-secure">
                    🔒 <?php esc_html_e('Paiement sécurisé', 'wwc-shop'); ?>
                </p>
            </div>
        </aside>

    </form>
</div>
