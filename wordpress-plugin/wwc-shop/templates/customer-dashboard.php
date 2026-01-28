<?php
/**
 * Customer Dashboard Template
 *
 * Shows customer account with impact tracking
 *
 * @package WWC_Shop
 */

defined('ABSPATH') || exit;

$api = wwc_shop()->api;
$dashboard_data = $api->get_customer_dashboard();

if (is_wp_error($dashboard_data)) {
    echo '<p class="wwc-error">' . esc_html__('Unable to load dashboard data', 'wwc-shop') . '</p>';
    return;
}

$customer = $dashboard_data['customer'] ?? [];
$recent_orders = $dashboard_data['recent_orders'] ?? [];
$impact_summary = $dashboard_data['impact_summary'] ?? [];
?>

<div class="wwc-dashboard">

    <!-- Welcome Section -->
    <div class="wwc-dashboard-header">
        <h1><?php
            printf(
                esc_html__('Bonjour, %s', 'wwc-shop'),
                esc_html($customer['first_name'] ?? wp_get_current_user()->display_name)
            );
        ?></h1>
        <p><?php esc_html_e('Bienvenue dans votre espace personnel. Suivez votre impact et vos commandes.', 'wwc-shop'); ?></p>
    </div>

    <!-- Impact Summary -->
    <div class="wwc-dashboard-impact">
        <h2>💝 <?php esc_html_e('Votre Impact', 'wwc-shop'); ?></h2>

        <div class="wwc-impact-cards">
            <div class="wwc-impact-card wwc-impact-main">
                <span class="wwc-impact-number">
                    <?php echo esc_html(number_format($impact_summary['total_items'] ?? 0)); ?>
                </span>
                <span class="wwc-impact-label">
                    <?php esc_html_e('items fournis aux étudiants', 'wwc-shop'); ?>
                </span>
            </div>

            <div class="wwc-impact-card">
                <span class="wwc-impact-number">
                    <?php echo esc_html($impact_summary['total_orders'] ?? 0); ?>
                </span>
                <span class="wwc-impact-label">
                    <?php esc_html_e('commandes', 'wwc-shop'); ?>
                </span>
            </div>

            <div class="wwc-impact-card">
                <span class="wwc-impact-number">
                    <?php echo esc_html($impact_summary['total_purchases'] ?? '0'); ?> DT
                </span>
                <span class="wwc-impact-label">
                    <?php esc_html_e('d\'achats', 'wwc-shop'); ?>
                </span>
            </div>
        </div>

        <?php if (!empty($impact_summary['breakdown'])): ?>
        <div class="wwc-impact-breakdown">
            <h3><?php esc_html_e('Détail de votre impact', 'wwc-shop'); ?></h3>
            <ul>
                <?php foreach ($impact_summary['breakdown'] as $item => $quantity): ?>
                <li>
                    <span class="wwc-breakdown-icon"><?php echo WWC_Impact::get_icon($item); ?></span>
                    <span class="wwc-breakdown-qty"><?php echo esc_html(number_format($quantity)); ?></span>
                    <span class="wwc-breakdown-item"><?php echo esc_html($item); ?></span>
                </li>
                <?php endforeach; ?>
            </ul>
        </div>
        <?php endif; ?>
    </div>

    <!-- Recent Orders -->
    <div class="wwc-dashboard-orders">
        <h2><?php esc_html_e('Commandes récentes', 'wwc-shop'); ?></h2>

        <?php if (empty($recent_orders)): ?>
            <p class="wwc-no-orders">
                <?php esc_html_e('Vous n\'avez pas encore passé de commande.', 'wwc-shop'); ?>
                <a href="<?php echo esc_url(home_url('/shop/')); ?>">
                    <?php esc_html_e('Découvrir nos produits', 'wwc-shop'); ?>
                </a>
            </p>
        <?php else: ?>
            <table class="wwc-orders-table">
                <thead>
                    <tr>
                        <th><?php esc_html_e('Commande', 'wwc-shop'); ?></th>
                        <th><?php esc_html_e('Date', 'wwc-shop'); ?></th>
                        <th><?php esc_html_e('Statut', 'wwc-shop'); ?></th>
                        <th><?php esc_html_e('Total', 'wwc-shop'); ?></th>
                        <th><?php esc_html_e('Impact', 'wwc-shop'); ?></th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($recent_orders as $order): ?>
                    <tr>
                        <td>
                            <a href="<?php echo esc_url(home_url('/account/order/' . $order['order_number'] . '/')); ?>">
                                #<?php echo esc_html($order['order_number']); ?>
                            </a>
                        </td>
                        <td><?php echo esc_html(date_i18n('j F Y', strtotime($order['created_at']))); ?></td>
                        <td>
                            <span class="wwc-order-status wwc-status-<?php echo esc_attr($order['status']); ?>">
                                <?php echo esc_html($order['status_display']); ?>
                            </span>
                        </td>
                        <td><?php echo esc_html($order['total'] . ' ' . $order['currency']); ?></td>
                        <td>💝 <?php echo esc_html($order['total_impact_items']); ?> items</td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        <?php endif; ?>
    </div>

    <!-- Account Actions -->
    <div class="wwc-dashboard-actions">
        <a href="<?php echo esc_url(home_url('/shop/')); ?>" class="wwc-btn wwc-btn-primary">
            <?php esc_html_e('Continuer vos achats', 'wwc-shop'); ?>
        </a>
        <a href="<?php echo esc_url(wp_logout_url(home_url())); ?>" class="wwc-btn wwc-btn-secondary">
            <?php esc_html_e('Déconnexion', 'wwc-shop'); ?>
        </a>
    </div>

</div>

<style>
.wwc-dashboard { max-width: 1000px; margin: 0 auto; padding: 40px 20px; }
.wwc-dashboard-header { margin-bottom: 40px; }
.wwc-dashboard-header h1 { margin-bottom: 10px; }
.wwc-dashboard-header p { color: #666; }

.wwc-dashboard-impact { background: linear-gradient(135deg, #f8b4c4 0%, #ffd4e0 100%); padding: 30px; border-radius: 12px; margin-bottom: 40px; }
.wwc-dashboard-impact h2 { margin-top: 0; }

.wwc-impact-cards { display: flex; gap: 20px; margin-bottom: 20px; }
.wwc-impact-card { background: white; padding: 20px; border-radius: 8px; text-align: center; flex: 1; }
.wwc-impact-card.wwc-impact-main { flex: 2; }
.wwc-impact-number { display: block; font-size: 36px; font-weight: 700; color: #1e3a5f; }
.wwc-impact-label { display: block; font-size: 14px; color: #666; }

.wwc-impact-breakdown { background: white; padding: 20px; border-radius: 8px; }
.wwc-impact-breakdown h3 { margin-top: 0; }
.wwc-impact-breakdown ul { list-style: none; padding: 0; margin: 0; }
.wwc-impact-breakdown li { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid #eee; }
.wwc-impact-breakdown li:last-child { border-bottom: none; }
.wwc-breakdown-icon { font-size: 24px; }
.wwc-breakdown-qty { font-weight: 600; min-width: 50px; }

.wwc-orders-table { width: 100%; border-collapse: collapse; }
.wwc-orders-table th, .wwc-orders-table td { padding: 15px; text-align: left; border-bottom: 1px solid #eee; }
.wwc-orders-table th { font-weight: 600; background: #f8f9fa; }

.wwc-order-status { padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.wwc-status-pending { background: #fff3cd; color: #856404; }
.wwc-status-paid { background: #d4edda; color: #155724; }
.wwc-status-processing { background: #cce5ff; color: #004085; }
.wwc-status-shipped { background: #e2d4f0; color: #6f42c1; }
.wwc-status-delivered { background: #d1ecf1; color: #0c5460; }

.wwc-dashboard-actions { display: flex; gap: 15px; margin-top: 40px; }
.wwc-no-orders { text-align: center; padding: 40px; background: #f8f9fa; border-radius: 8px; }

@media (max-width: 768px) {
    .wwc-impact-cards { flex-direction: column; }
}
</style>
