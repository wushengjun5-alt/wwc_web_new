<?php
/**
 * Checkout Success / Order Confirmation Template
 *
 * Reached after:
 *   - Stripe payment success (?order=WWC-...&session_id=cs_...)
 *   - Bank transfer order placement (?order=WWC-...&method=bank_transfer)
 *
 * @package WWC_Shop
 */

defined('ABSPATH') || exit;

$order_number = isset($_GET['order']) ? sanitize_text_field($_GET['order']) : '';
$method       = isset($_GET['method']) ? sanitize_text_field($_GET['method']) : 'stripe';

$order = null;
if ($order_number) {
    $order = wwc_shop()->api->get_order($order_number);
    if (is_wp_error($order)) {
        $order = null;
    }
}
?>

<div class="wwc-success-wrapper">

    <?php if ($order): ?>

        <div class="wwc-success-header">
            <div class="wwc-success-icon">&#10003;</div>
            <h1><?php esc_html_e('Merci pour votre commande !', 'wwc-shop'); ?></h1>
            <p class="wwc-success-order-number">
                <?php
                printf(
                    esc_html__('Numéro de commande : %s', 'wwc-shop'),
                    '<strong>' . esc_html($order['order_number']) . '</strong>'
                );
                ?>
            </p>
            <p><?php esc_html_e('Un email de confirmation a été envoyé à votre adresse.', 'wwc-shop'); ?></p>
        </div>

        <?php if ($method === 'bank_transfer'): ?>
        <!-- Bank Transfer Instructions -->
        <div class="wwc-bank-transfer-instructions">
            <h2><?php esc_html_e('Instructions de virement bancaire', 'wwc-shop'); ?></h2>
            <p><?php esc_html_e('Votre commande est en attente de paiement. Veuillez effectuer le virement avec les informations suivantes :', 'wwc-shop'); ?></p>

            <div class="wwc-bank-details">
                <div class="wwc-bank-row">
                    <span class="wwc-bank-label"><?php esc_html_e('Bénéficiaire', 'wwc-shop'); ?></span>
                    <span class="wwc-bank-value">Wallah We Can</span>
                </div>
                <div class="wwc-bank-row">
                    <span class="wwc-bank-label"><?php esc_html_e('Banque', 'wwc-shop'); ?></span>
                    <span class="wwc-bank-value">Banque de Tunisie</span>
                </div>
                <div class="wwc-bank-row">
                    <span class="wwc-bank-label">IBAN</span>
                    <span class="wwc-bank-value">TN59 XXXX XXXX XXXX XXXX XXXX</span>
                </div>
                <div class="wwc-bank-row wwc-bank-row--highlight">
                    <span class="wwc-bank-label"><?php esc_html_e('Référence (obligatoire)', 'wwc-shop'); ?></span>
                    <span class="wwc-bank-value"><?php echo esc_html($order['order_number']); ?></span>
                </div>
                <div class="wwc-bank-row wwc-bank-row--highlight">
                    <span class="wwc-bank-label"><?php esc_html_e('Montant', 'wwc-shop'); ?></span>
                    <span class="wwc-bank-value"><?php echo esc_html($order['total']); ?> <?php echo esc_html($order['currency']); ?></span>
                </div>
            </div>

            <p class="wwc-bank-note">
                <?php esc_html_e('Votre commande sera traitée dès réception du virement. Pensez à indiquer le numéro de commande comme référence.', 'wwc-shop'); ?>
            </p>
        </div>
        <?php endif; ?>

        <!-- Order Summary -->
        <div class="wwc-success-order-summary">
            <h2><?php esc_html_e('Récapitulatif', 'wwc-shop'); ?></h2>

            <?php if (!empty($order['items'])): ?>
            <div class="wwc-success-items">
                <?php foreach ($order['items'] as $item): ?>
                <div class="wwc-success-item">
                    <span class="wwc-success-item-name">
                        <?php echo esc_html($item['quantity']); ?>x <?php echo esc_html($item['product_name']); ?>
                    </span>
                    <span class="wwc-success-item-price">
                        <?php echo esc_html($item['subtotal']); ?> <?php echo esc_html($order['currency']); ?>
                    </span>
                </div>
                <?php endforeach; ?>
            </div>
            <div class="wwc-success-total">
                <span><?php esc_html_e('Total', 'wwc-shop'); ?></span>
                <span><?php echo esc_html($order['total']); ?> <?php echo esc_html($order['currency']); ?></span>
            </div>
            <?php endif; ?>
        </div>

        <!-- Impact Summary -->
        <?php if (!empty($order['impact_summary'])): ?>
        <div class="wwc-success-impact">
            <h2><?php esc_html_e('Votre impact', 'wwc-shop'); ?></h2>
            <p><?php esc_html_e('Grâce à votre achat, vous contribuez directement à l\'initiative GreenSchool :', 'wwc-shop'); ?></p>
            <ul class="wwc-impact-list">
                <?php foreach ($order['impact_summary'] as $item_type => $qty): ?>
                <li>
                    <strong><?php echo esc_html($qty); ?></strong>
                    <?php echo esc_html($item_type); ?>
                    <?php esc_html_e('fourni(e)s à des étudiants', 'wwc-shop'); ?>
                </li>
                <?php endforeach; ?>
            </ul>
        </div>
        <?php endif; ?>

        <div class="wwc-success-actions">
            <a href="<?php echo esc_url(home_url('/shop/')); ?>" class="wwc-btn wwc-btn-primary">
                <?php esc_html_e('Continuer mes achats', 'wwc-shop'); ?>
            </a>
            <?php if (is_user_logged_in()): ?>
            <a href="<?php echo esc_url(home_url('/mon-compte/')); ?>" class="wwc-btn wwc-btn-secondary">
                <?php esc_html_e('Voir mes commandes', 'wwc-shop'); ?>
            </a>
            <?php endif; ?>
        </div>

    <?php else: ?>

        <div class="wwc-success-header">
            <div class="wwc-success-icon">&#10003;</div>
            <h1><?php esc_html_e('Commande confirmée !', 'wwc-shop'); ?></h1>
            <p><?php esc_html_e('Merci pour votre achat. Vous recevrez bientôt un email de confirmation.', 'wwc-shop'); ?></p>
        </div>

        <div class="wwc-success-actions">
            <a href="<?php echo esc_url(home_url('/shop/')); ?>" class="wwc-btn wwc-btn-primary">
                <?php esc_html_e('Continuer mes achats', 'wwc-shop'); ?>
            </a>
        </div>

    <?php endif; ?>

</div>
