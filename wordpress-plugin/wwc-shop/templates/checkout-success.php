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
            <h1><?php WWC_I18n::e('Merci pour votre commande !'); ?></h1>
            <p class="wwc-success-order-number">
                <?php
                printf(
                    WWC_I18n::t('Numéro de commande : %s'),
                    '<strong>' . esc_html($order['order_number']) . '</strong>'
                );
                ?>
            </p>
            <p><?php WWC_I18n::e('Un email de confirmation a été envoyé à votre adresse.'); ?></p>
        </div>

        <?php if ($method === 'bank_transfer'): ?>
        <!-- Bank Transfer Instructions -->
        <div class="wwc-bank-transfer-instructions">
            <h2><?php WWC_I18n::e('Instructions de virement bancaire'); ?></h2>
            <p><?php WWC_I18n::e('Votre commande est en attente de paiement. Veuillez effectuer le virement avec les informations suivantes :'); ?></p>

            <div class="wwc-bank-details">
                <div class="wwc-bank-row">
                    <span class="wwc-bank-label"><?php WWC_I18n::e('Bénéficiaire'); ?></span>
                    <span class="wwc-bank-value">Wallah We Can</span>
                </div>
                <div class="wwc-bank-row">
                    <span class="wwc-bank-label"><?php WWC_I18n::e('Banque'); ?></span>
                    <span class="wwc-bank-value">Banque de Tunisie</span>
                </div>
                <div class="wwc-bank-row">
                    <span class="wwc-bank-label">IBAN</span>
                    <span class="wwc-bank-value">TN59 XXXX XXXX XXXX XXXX XXXX</span>
                </div>
                <div class="wwc-bank-row wwc-bank-row--highlight">
                    <span class="wwc-bank-label"><?php WWC_I18n::e('Référence (obligatoire)'); ?></span>
                    <span class="wwc-bank-value"><?php echo esc_html($order['order_number']); ?></span>
                </div>
                <div class="wwc-bank-row wwc-bank-row--highlight">
                    <span class="wwc-bank-label"><?php WWC_I18n::e('Montant'); ?></span>
                    <span class="wwc-bank-value"><?php echo esc_html($order['total']); ?> <?php echo esc_html($order['currency']); ?></span>
                </div>
            </div>

            <p class="wwc-bank-note">
                <?php WWC_I18n::e('Votre commande sera traitée dès réception du virement. Pensez à indiquer le numéro de commande comme référence.'); ?>
            </p>
        </div>
        <?php endif; ?>

        <!-- Order Summary -->
        <div class="wwc-success-order-summary">
            <h2><?php WWC_I18n::e('Récapitulatif'); ?></h2>

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
                <span><?php WWC_I18n::e('Total'); ?></span>
                <span><?php echo esc_html($order['total']); ?> <?php echo esc_html($order['currency']); ?></span>
            </div>
            <?php endif; ?>
        </div>

        <!-- Impact Summary -->
        <?php if (!empty($order['impact_summary'])): ?>
        <div class="wwc-success-impact">
            <h2><?php WWC_I18n::e('Votre impact'); ?></h2>
            <p><?php WWC_I18n::e("Grâce à votre achat, vous contribuez directement à l'initiative GreenSchool :"); ?></p>
            <ul class="wwc-impact-list">
                <?php foreach ($order['impact_summary'] as $item_type => $qty): ?>
                <li>
                    <strong><?php echo esc_html($qty); ?></strong>
                    <?php echo esc_html($item_type); ?>
                    <?php WWC_I18n::e('fourni(e)s à des étudiants'); ?>
                </li>
                <?php endforeach; ?>
            </ul>
        </div>
        <?php endif; ?>

        <div class="wwc-success-actions">
            <a href="<?php echo esc_url(home_url('/shop/')); ?>" class="wwc-btn wwc-btn-primary">
                <?php WWC_I18n::e('Continuer mes achats'); ?>
            </a>
            <?php if (is_user_logged_in()): ?>
            <a href="<?php echo esc_url(home_url('/mon-compte/')); ?>" class="wwc-btn wwc-btn-secondary">
                <?php WWC_I18n::e('Voir mes commandes'); ?>
            </a>
            <?php endif; ?>
        </div>

    <?php else: ?>

        <div class="wwc-success-header">
            <div class="wwc-success-icon">&#10003;</div>
            <h1><?php WWC_I18n::e('Commande confirmée !'); ?></h1>
            <p><?php WWC_I18n::e('Merci pour votre achat. Vous recevrez bientôt un email de confirmation.'); ?></p>
        </div>

        <div class="wwc-success-actions">
            <a href="<?php echo esc_url(home_url('/shop/')); ?>" class="wwc-btn wwc-btn-primary">
                <?php WWC_I18n::e('Continuer mes achats'); ?>
            </a>
        </div>

    <?php endif; ?>

</div>
