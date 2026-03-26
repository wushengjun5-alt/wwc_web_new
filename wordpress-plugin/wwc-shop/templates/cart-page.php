<?php
/**
 * Cart Page Template
 *
 * @package WWC_Shop
 */

defined('ABSPATH') || exit;
?>

<div class="wwc-cart-page">
    <h1><?php WWC_I18n::e('Mon Panier'); ?></h1>

    <div class="wwc-cart-page-content" id="wwc-cart-page-content">
        <div class="wwc-cart-loading">
            <span class="wwc-spinner"></span>
            <?php WWC_I18n::e('Chargement...'); ?>
        </div>
    </div>

    <div class="wwc-cart-page-summary" id="wwc-cart-page-summary" style="display: none;">
        <div class="wwc-cart-page-totals">
            <div class="wwc-cart-row">
                <span><?php WWC_I18n::e('Sous-total'); ?></span>
                <span id="wwc-page-subtotal">0 DT</span>
            </div>
            <div class="wwc-cart-row">
                <span><?php WWC_I18n::e('Livraison'); ?></span>
                <span><?php WWC_I18n::e("Calculée à l'étape suivante"); ?></span>
            </div>
        </div>

        <div class="wwc-cart-page-impact" id="wwc-cart-page-impact">
            <!-- Impact loaded via JavaScript -->
        </div>

        <div class="wwc-cart-page-actions">
            <a href="<?php echo esc_url(home_url('/shop/')); ?>" class="wwc-btn wwc-btn-secondary">
                <?php WWC_I18n::e('Continuer vos achats'); ?>
            </a>
            <a href="<?php echo esc_url(home_url('/checkout/')); ?>" class="wwc-btn wwc-btn-primary">
                <?php WWC_I18n::e('Passer la commande'); ?>
            </a>
        </div>
    </div>
</div>

<script>
jQuery(document).ready(function($) {
    function loadCartPage() {
        $.ajax({
            url: wwcShop.ajaxUrl,
            type: 'POST',
            data: {
                action: 'wwc_get_cart',
                nonce: wwcShop.nonce
            },
            success: function(response) {
                if (response.success) {
                    renderCartPage(response.data.cart);
                }
            }
        });
    }

    function renderCartPage(cart) {
        var $content = $('#wwc-cart-page-content');
        var $summary = $('#wwc-cart-page-summary');

        if (!cart || !cart.items || cart.items.length === 0) {
            $content.html(
                '<div class="wwc-cart-empty">' +
                '<div class="wwc-cart-empty-icon">🛒</div>' +
                '<p><?php WWC_I18n::e('Votre panier est vide'); ?></p>' +
                '<a href="<?php echo esc_url(home_url('/shop/')); ?>" class="wwc-btn wwc-btn-primary">' +
                '<?php WWC_I18n::e('Continuer vos achats'); ?></a>' +
                '</div>'
            );
            $summary.hide();
            return;
        }

        var html = '<table class="wwc-cart-table">' +
            '<thead><tr>' +
            '<th><?php WWC_I18n::e('Produit'); ?></th>' +
            '<th><?php WWC_I18n::e('Prix'); ?></th>' +
            '<th><?php WWC_I18n::e('Quantité'); ?></th>' +
            '<th><?php WWC_I18n::e('Total'); ?></th>' +
            '<th></th>' +
            '</tr></thead><tbody>';

        cart.items.forEach(function(item) {
            var image = item.product.primary_image ? item.product.primary_image.image : '';
            html += '<tr data-item-id="' + item.id + '">' +
                '<td class="wwc-cart-product">' +
                '<img src="' + image + '" alt="' + item.product.name + '">' +
                '<span>' + item.product.name + '</span>' +
                '</td>' +
                '<td>' + item.product.price_tnd + ' DT</td>' +
                '<td class="wwc-cart-qty">' +
                '<div class="wwc-quantity-selector">' +
                '<button class="wwc-qty-btn wwc-qty-minus" data-item-id="' + item.id + '">−</button>' +
                '<span class="wwc-cart-item-qty">' + item.quantity + '</span>' +
                '<button class="wwc-qty-btn wwc-qty-plus" data-item-id="' + item.id + '">+</button>' +
                '</div>' +
                '</td>' +
                '<td class="wwc-cart-total">' + item.subtotal + ' DT</td>' +
                '<td><button class="wwc-cart-item-remove" data-item-id="' + item.id + '">🗑️</button></td>' +
                '</tr>';
        });

        html += '</tbody></table>';

        $content.html(html);
        $('#wwc-page-subtotal').text(cart.total + ' DT');

        // Impact summary
        if (cart.total_impact && Object.keys(cart.total_impact).length > 0) {
            var impactHtml = '<div class="wwc-impact-badge">💝 <?php WWC_I18n::e('Votre impact avec cette commande:'); ?><ul>';
            for (var item in cart.total_impact) {
                impactHtml += '<li>' + cart.total_impact[item] + ' ' + item + '</li>';
            }
            impactHtml += '</ul></div>';
            $('#wwc-cart-page-impact').html(impactHtml);
        }

        $summary.show();
    }

    loadCartPage();
});
</script>

<style>
.wwc-cart-page { max-width: 1000px; margin: 0 auto; padding: 40px 20px; }
.wwc-cart-table { width: 100%; border-collapse: collapse; margin-bottom: 30px; }
.wwc-cart-table th, .wwc-cart-table td { padding: 15px; text-align: left; border-bottom: 1px solid #eee; }
.wwc-cart-table th { font-weight: 600; background: #f8f9fa; }
.wwc-cart-product { display: flex; align-items: center; gap: 15px; }
.wwc-cart-product img { width: 80px; height: 80px; object-fit: cover; border-radius: 8px; }
.wwc-cart-page-actions { display: flex; gap: 15px; justify-content: flex-end; margin-top: 20px; }
</style>
