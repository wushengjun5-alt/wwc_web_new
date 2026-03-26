<?php
/**
 * Order Detail Template
 *
 * @package WWC_Shop
 */

defined('ABSPATH') || exit;

$api   = wwc_shop()->api;
$order = $api->get_order($order_number);

if (is_wp_error($order) || empty($order)) {
    echo '<p class="wwc-error">' . WWC_I18n::t('Commande introuvable.') . '</p>';
    return;
}

$items    = $order['items'] ?? [];
$currency = $order['currency'] ?? 'TND';
$symbol   = $currency === 'EUR' ? '€' : 'DT';

$status_labels = [
    'pending'    => WWC_I18n::t('En attente'),
    'paid'       => WWC_I18n::t('Payée'),
    'processing' => WWC_I18n::t('En traitement'),
    'shipped'    => WWC_I18n::t('Expédiée'),
    'delivered'  => WWC_I18n::t('Livrée'),
    'cancelled'  => WWC_I18n::t('Annulée'),
    'refunded'   => WWC_I18n::t('Remboursée'),
];
$status       = $order['status'] ?? 'pending';
$status_label = $status_labels[$status] ?? $order['status_display'] ?? $status;
?>

<div class="wwc-order-detail">

    <div class="wwc-order-detail-header">
        <div>
            <h2><?php printf(WWC_I18n::t('Commande #%s'), esc_html($order['order_number'])); ?></h2>
            <p class="wwc-order-date">
                <?php printf(
                    WWC_I18n::t('Passée le %s'),
                    esc_html(date_i18n('j F Y', strtotime($order['created_at'])))
                ); ?>
            </p>
        </div>
        <span class="wwc-order-status wwc-status-<?php echo esc_attr($status); ?>">
            <?php echo esc_html($status_label); ?>
        </span>
    </div>

    <!-- Items -->
    <div class="wwc-order-items">
        <h3><?php WWC_I18n::e('Articles'); ?></h3>
        <table class="wwc-order-items-table">
            <thead>
                <tr>
                    <th><?php WWC_I18n::e('Produit'); ?></th>
                    <th><?php WWC_I18n::e('Qté'); ?></th>
                    <th><?php WWC_I18n::e('Prix unitaire'); ?></th>
                    <th><?php WWC_I18n::e('Sous-total'); ?></th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($items as $item): ?>
                <tr>
                    <td>
                        <div class="wwc-order-item-name">
                            <?php echo esc_html($item['product_name'] ?? $item['product']['name'] ?? '—'); ?>
                        </div>
                        <?php if (!empty($item['impact_items'])): ?>
                        <div class="wwc-order-item-impact">
                            💝 <?php echo esc_html($item['impact_items']); ?> items
                        </div>
                        <?php endif; ?>
                    </td>
                    <td><?php echo esc_html($item['quantity']); ?></td>
                    <td><?php echo esc_html($item['unit_price']); ?> <?php echo esc_html($symbol); ?></td>
                    <td><?php echo esc_html($item['subtotal']); ?> <?php echo esc_html($symbol); ?></td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>

    <!-- Totals -->
    <div class="wwc-order-totals">
        <div class="wwc-order-total-row">
            <span><?php WWC_I18n::e('Sous-total'); ?></span>
            <span><?php echo esc_html($order['subtotal']); ?> <?php echo esc_html($symbol); ?></span>
        </div>
        <?php if (!empty($order['shipping_cost']) && $order['shipping_cost'] > 0): ?>
        <div class="wwc-order-total-row">
            <span><?php WWC_I18n::e('Livraison'); ?></span>
            <span><?php echo esc_html($order['shipping_cost']); ?> <?php echo esc_html($symbol); ?></span>
        </div>
        <?php endif; ?>
        <div class="wwc-order-total-row wwc-order-total-final">
            <span><?php WWC_I18n::e('Total'); ?></span>
            <span><?php echo esc_html($order['total']); ?> <?php echo esc_html($symbol); ?></span>
        </div>
    </div>

    <!-- Shipping address -->
    <?php if (!empty($order['shipping_address'])): $addr = $order['shipping_address']; ?>
    <div class="wwc-order-address">
        <h3><?php WWC_I18n::e('Adresse de livraison'); ?></h3>
        <address>
            <?php echo esc_html(trim(($addr['first_name'] ?? '') . ' ' . ($addr['last_name'] ?? ''))); ?><br>
            <?php if (!empty($addr['company'])): echo esc_html($addr['company']) . '<br>'; endif; ?>
            <?php echo esc_html($addr['address_line1'] ?? ''); ?><br>
            <?php if (!empty($addr['address_line2'])): echo esc_html($addr['address_line2']) . '<br>'; endif; ?>
            <?php echo esc_html(trim(($addr['city'] ?? '') . ' ' . ($addr['postal_code'] ?? ''))); ?><br>
            <?php echo esc_html($addr['country'] ?? ''); ?>
        </address>
    </div>
    <?php endif; ?>

    <!-- Tracking -->
    <?php if (!empty($order['tracking_number'])): ?>
    <div class="wwc-order-tracking">
        <h3><?php WWC_I18n::e('Suivi'); ?></h3>
        <p><?php printf(
            WWC_I18n::t('Numéro de suivi : %s'),
            '<strong>' . esc_html($order['tracking_number']) . '</strong>'
        ); ?></p>
    </div>
    <?php endif; ?>

    <!-- Actions -->
    <div class="wwc-order-detail-actions">
        <a href="<?php echo esc_url(home_url('/mon-compte/')); ?>" class="wwc-btn wwc-btn--secondary">
            &larr; <?php WWC_I18n::e('Retour à mon compte'); ?>
        </a>
    </div>

</div>
