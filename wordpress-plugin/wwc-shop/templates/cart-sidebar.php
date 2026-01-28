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
        <h3><?php esc_html_e('Mon Panier', 'wwc-shop'); ?></h3>
        <button class="wwc-cart-close" id="wwc-cart-close" type="button" aria-label="<?php esc_attr_e('Fermer', 'wwc-shop'); ?>">
            ✕
        </button>
    </div>

    <div class="wwc-cart-content" id="wwc-cart-content">
        <!-- Cart items loaded via AJAX -->
        <div class="wwc-cart-loading">
            <span class="wwc-spinner"></span>
            <?php esc_html_e('Chargement...', 'wwc-shop'); ?>
        </div>
    </div>

    <div class="wwc-cart-footer" id="wwc-cart-footer" style="display: none;">
        <div class="wwc-cart-impact-summary" id="wwc-cart-impact-summary">
            <!-- Impact summary loaded via AJAX -->
        </div>

        <div class="wwc-cart-totals">
            <div class="wwc-cart-subtotal">
                <span><?php esc_html_e('Sous-total', 'wwc-shop'); ?></span>
                <span id="wwc-cart-subtotal-amount">0 DT</span>
            </div>
            <p class="wwc-cart-shipping-note">
                <?php esc_html_e('Frais de livraison calculés à la caisse', 'wwc-shop'); ?>
            </p>
        </div>

        <div class="wwc-cart-actions">
            <a href="<?php echo esc_url(home_url('/cart/')); ?>" class="wwc-btn wwc-btn-secondary">
                <?php esc_html_e('Voir le panier', 'wwc-shop'); ?>
            </a>
            <a href="<?php echo esc_url(home_url('/checkout/')); ?>" class="wwc-btn wwc-btn-primary">
                <?php esc_html_e('Passer la commande', 'wwc-shop'); ?>
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
        <button class="wwc-cart-item-remove" data-item-id="{{id}}" type="button" aria-label="<?php esc_attr_e('Supprimer', 'wwc-shop'); ?>">
            🗑️
        </button>
    </div>
</script>

<!-- Empty Cart Template -->
<script type="text/template" id="wwc-cart-empty-template">
    <div class="wwc-cart-empty">
        <div class="wwc-cart-empty-icon">🛒</div>
        <p><?php esc_html_e('Votre panier est vide', 'wwc-shop'); ?></p>
        <a href="<?php echo esc_url(home_url('/shop/')); ?>" class="wwc-btn wwc-btn-primary">
            <?php esc_html_e('Continuer vos achats', 'wwc-shop'); ?>
        </a>
    </div>
</script>
