<?php
/**
 * Cart Sidebar Template
 *
 * Slide-out cart panel
 *
 * @package WWC_Shop
 */

defined('ABSPATH') || exit;
?>

<!-- Cart Overlay -->
<div class="wwc-cart-overlay" id="wwc-cart-overlay"></div>

<!-- Cart Sidebar -->
<div class="wwc-cart-sidebar" id="wwc-cart-sidebar">

    <div class="wwc-cart-header">
        <h3><?php WWC_I18n::e('Mon Panier'); ?></h3>
        <button class="wwc-cart-close" id="wwc-cart-close" type="button" aria-label="<?php echo WWC_I18n::attr('Fermer'); ?>">
            ✕
        </button>
    </div>

    <div class="wwc-cart-content" id="wwc-cart-content">
        <!-- Cart items loaded via AJAX -->
        <div class="wwc-cart-loading">
            <span class="wwc-spinner"></span>
            <?php WWC_I18n::e('Chargement...'); ?>
        </div>
    </div>

    <div class="wwc-cart-footer" id="wwc-cart-footer" style="display: none;">
        <div class="wwc-cart-impact-summary" id="wwc-cart-impact-summary">
            <!-- Impact summary loaded via AJAX -->
        </div>

        <div class="wwc-cart-totals">
            <div class="wwc-cart-subtotal">
                <span><?php WWC_I18n::e('Sous-total'); ?></span>
                <span id="wwc-cart-subtotal-amount">0 DT</span>
            </div>
            <p class="wwc-cart-shipping-note">
                <?php WWC_I18n::e('Frais de livraison calculés à la caisse'); ?>
            </p>
        </div>

        <div class="wwc-cart-actions">
            <a href="<?php echo esc_url(home_url('/cart/')); ?>" class="wwc-btn wwc-btn-secondary">
                <?php WWC_I18n::e('Voir le panier'); ?>
            </a>
            <a href="<?php echo esc_url(home_url('/checkout/')); ?>" class="wwc-btn wwc-btn-primary">
                <?php WWC_I18n::e('Passer la commande'); ?>
            </a>
        </div>
    </div>

</div>

<!-- Cart Item Template (for JS) -->
<script type="text/template" id="wwc-cart-item-template">
    <div class="wwc-cart-item" data-item-id="{{id}}">
        <div class="wwc-cart-item-image">
            <img src="{{image}}" alt="{{name}}">
        </div>
        <div class="wwc-cart-item-details">
            <h4 class="wwc-cart-item-name">{{name}}</h4>
            <div class="wwc-cart-item-price">{{price}}</div>
            <div class="wwc-cart-item-quantity">
                <button class="wwc-qty-btn wwc-qty-minus" data-item-id="{{id}}" type="button">−</button>
                <span class="wwc-cart-item-qty">{{quantity}}</span>
                <button class="wwc-qty-btn wwc-qty-plus" data-item-id="{{id}}" type="button">+</button>
            </div>
        </div>
        <button class="wwc-cart-item-remove" data-item-id="{{id}}" type="button" aria-label="<?php echo WWC_I18n::attr('Supprimer'); ?>">
            🗑️
        </button>
    </div>
</script>

<!-- Empty Cart Template -->
<script type="text/template" id="wwc-cart-empty-template">
    <div class="wwc-cart-empty">
        <div class="wwc-cart-empty-icon">🛒</div>
        <p><?php WWC_I18n::e('Votre panier est vide'); ?></p>
        <a href="<?php echo esc_url(home_url('/shop/')); ?>" class="wwc-btn wwc-btn-primary">
            <?php WWC_I18n::e('Continuer vos achats'); ?>
        </a>
    </div>
</script>
