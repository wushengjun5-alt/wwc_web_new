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
                <h2><?php WWC_I18n::e('Informations de contact'); ?></h2>

                <div class="wwc-form-row">
                    <div class="wwc-form-field wwc-field-half">
                        <label for="email"><?php WWC_I18n::e('Email'); ?> *</label>
                        <input type="email" id="email" name="email" required
                               value="<?php echo is_user_logged_in() ? esc_attr(wp_get_current_user()->user_email) : ''; ?>">
                    </div>
                    <div class="wwc-form-field wwc-field-half">
                        <label for="phone"><?php WWC_I18n::e('Téléphone'); ?> *</label>
                        <input type="tel" id="phone" name="phone" required placeholder="+216 XX XXX XXX">
                    </div>
                </div>
            </section>

            <!-- Shipping Address -->
            <section class="wwc-checkout-section">
                <h2><?php WWC_I18n::e('Adresse de livraison'); ?></h2>

                <div class="wwc-form-row">
                    <div class="wwc-form-field wwc-field-half">
                        <label for="shipping_first_name"><?php WWC_I18n::e('Prénom'); ?> *</label>
                        <input type="text" id="shipping_first_name" name="shipping_first_name" required>
                    </div>
                    <div class="wwc-form-field wwc-field-half">
                        <label for="shipping_last_name"><?php WWC_I18n::e('Nom'); ?> *</label>
                        <input type="text" id="shipping_last_name" name="shipping_last_name" required>
                    </div>
                </div>

                <div class="wwc-form-field">
                    <label for="shipping_company"><?php WWC_I18n::e('Entreprise'); ?> (<?php WWC_I18n::e('optionnel'); ?>)</label>
                    <input type="text" id="shipping_company" name="shipping_company">
                </div>

                <div class="wwc-form-field">
                    <label for="shipping_address_1"><?php WWC_I18n::e('Adresse'); ?> *</label>
                    <input type="text" id="shipping_address_1" name="shipping_address_1" required>
                </div>

                <div class="wwc-form-field">
                    <label for="shipping_address_2"><?php WWC_I18n::e("Complément d'adresse"); ?></label>
                    <input type="text" id="shipping_address_2" name="shipping_address_2">
                </div>

                <div class="wwc-form-row">
                    <div class="wwc-form-field wwc-field-third">
                        <label for="shipping_postal_code"><?php WWC_I18n::e('Code postal'); ?> *</label>
                        <input type="text" id="shipping_postal_code" name="shipping_postal_code" required>
                    </div>
                    <div class="wwc-form-field wwc-field-third">
                        <label for="shipping_city"><?php WWC_I18n::e('Ville'); ?> *</label>
                        <input type="text" id="shipping_city" name="shipping_city" required>
                    </div>
                    <div class="wwc-form-field wwc-field-third">
                        <label for="shipping_state"><?php WWC_I18n::e('Gouvernorat'); ?></label>
                        <select id="shipping_state" name="shipping_state">
                            <option value=""><?php WWC_I18n::e('Sélectionner'); ?></option>
                            <?php foreach ($states as $code => $name): ?>
                                <option value="<?php echo esc_attr($code); ?>"><?php echo esc_html($name); ?></option>
                            <?php endforeach; ?>
                        </select>
                    </div>
                </div>

                <div class="wwc-form-field">
                    <label for="shipping_country"><?php WWC_I18n::e('Pays'); ?> *</label>
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
                <h2><?php WWC_I18n::e('Méthode de paiement'); ?></h2>

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
                <h2><?php WWC_I18n::e('Notes de commande'); ?></h2>

                <div class="wwc-form-field">
                    <label for="customer_notes"><?php WWC_I18n::e('Instructions spéciales'); ?></label>
                    <textarea id="customer_notes" name="customer_notes" rows="3"
                              placeholder="<?php echo WWC_I18n::attr('Notes sur votre commande, instructions de livraison...'); ?>"></textarea>
                </div>
            </section>

        </div>

        <!-- Order Summary Sidebar -->
        <aside class="wwc-checkout-sidebar">
            <div class="wwc-order-summary">
                <h3><?php WWC_I18n::e('Récapitulatif de commande'); ?></h3>

                <div id="wwc-checkout-items" class="wwc-checkout-items">
                    <!-- Items loaded via AJAX -->
                    <div class="wwc-cart-loading">
                        <span class="wwc-spinner"></span>
                    </div>
                </div>

                <div class="wwc-checkout-totals" data-currency="<?php echo esc_attr($currency); ?>" data-currency-symbol="<?php echo esc_attr($currency_symbol); ?>">
                    <div class="wwc-checkout-row">
                        <span><?php WWC_I18n::e('Sous-total'); ?></span>
                        <span id="wwc-checkout-subtotal">0 <?php echo esc_html($currency_symbol); ?></span>
                    </div>
                    <div class="wwc-checkout-row">
                        <span><?php WWC_I18n::e('Livraison'); ?></span>
                        <span id="wwc-checkout-shipping"><?php WWC_I18n::e('Calculé selon le pays'); ?></span>
                    </div>
                    <div class="wwc-checkout-row wwc-checkout-total">
                        <span><?php WWC_I18n::e('Total'); ?></span>
                        <span id="wwc-checkout-total">0 <?php echo esc_html($currency_symbol); ?></span>
                    </div>
                </div>

                <!-- Impact Summary -->
                <div class="wwc-checkout-impact" id="wwc-checkout-impact">
                    <!-- Impact loaded via AJAX -->
                </div>

                <button type="submit" class="wwc-btn wwc-btn-primary wwc-btn-checkout">
                    <?php WWC_I18n::e('Confirmer la commande'); ?>
                </button>

                <p class="wwc-checkout-secure">
                    🔒 <?php WWC_I18n::e('Paiement sécurisé'); ?>
                </p>
            </div>
        </aside>

    </form>
</div>
