<?php
/**
 * WWC Shop Orders Admin
 *
 * Order management in WordPress admin — lists orders from Django API,
 * lets admins update status and tracking number.
 *
 * @package WWC_Shop
 */

defined('ABSPATH') || exit;

class WWC_Orders_Admin {

    private $api;
    private $admin_api_key;

    public function __construct() {
        $this->admin_api_key = get_option('wwc_admin_api_key', '');

        add_action('admin_menu',             [$this, 'add_menu_pages']);
        add_action('admin_enqueue_scripts',  [$this, 'enqueue_admin_assets']);
        add_action('wp_ajax_wwc_admin_update_order', [$this, 'ajax_update_order']);
    }

    /**
     * Add sub-menu under wwc-shop
     */
    public function add_menu_pages() {
        add_submenu_page(
            'wwc-shop',
            __('Orders', 'wwc-shop'),
            __('Orders', 'wwc-shop'),
            'manage_options',
            'wwc-orders',
            [$this, 'render_orders_page']
        );
    }

    /**
     * Enqueue admin CSS/JS only on our pages
     */
    public function enqueue_admin_assets($hook) {
        if (strpos($hook, 'wwc-orders') === false) return;

        wp_enqueue_style(
            'wwc-orders-admin',
            WWC_SHOP_PLUGIN_URL . 'assets/css/admin-orders.css',
            [],
            WWC_SHOP_VERSION
        );
        wp_enqueue_script(
            'wwc-orders-admin',
            WWC_SHOP_PLUGIN_URL . 'assets/js/admin-orders.js',
            ['jquery'],
            WWC_SHOP_VERSION,
            true
        );
        wp_localize_script('wwc-orders-admin', 'wwcOrders', [
            'ajaxUrl' => admin_url('admin-ajax.php'),
            'nonce'   => wp_create_nonce('wwc-shop-nonce'),
            'i18n'    => [
                'updateSuccess' => __('Commande mise à jour.', 'wwc-shop'),
                'updateError'   => __('Erreur lors de la mise à jour.', 'wwc-shop'),
                'confirm'       => __('Confirmer cette action ?', 'wwc-shop'),
            ],
        ]);
    }

    /**
     * Render orders list or detail page
     */
    public function render_orders_page() {
        $order_number = sanitize_text_field($_GET['order'] ?? '');

        if (!empty($order_number)) {
            $this->render_order_detail($order_number);
        } else {
            $this->render_orders_list();
        }
    }

    // ──────────────────────────────────────────────────────────────
    // Orders List
    // ──────────────────────────────────────────────────────────────

    private function render_orders_list() {
        $page       = max(1, intval($_GET['paged'] ?? 1));
        $status     = sanitize_text_field($_GET['status'] ?? '');
        $search     = sanitize_text_field($_GET['s'] ?? '');
        $page_size  = 20;

        $params = [
            'page'      => $page,
            'page_size' => $page_size,
        ];
        if ($status)  $params['status'] = $status;
        if ($search)  $params['search'] = $search;

        $response = $this->admin_get('admin/orders/', $params);
        $orders      = is_wp_error($response) ? [] : ($response['results'] ?? []);
        $total       = is_wp_error($response) ? 0  : ($response['count']   ?? 0);
        $total_pages = $page_size > 0 ? ceil($total / $page_size) : 1;
        $error_msg   = is_wp_error($response) ? $response->get_error_message() : '';

        $status_labels = [
            ''            => __('Tous les statuts', 'wwc-shop'),
            'pending'     => __('En attente',      'wwc-shop'),
            'paid'        => __('Payée',            'wwc-shop'),
            'processing'  => __('En traitement',   'wwc-shop'),
            'shipped'     => __('Expédiée',         'wwc-shop'),
            'delivered'   => __('Livrée',           'wwc-shop'),
            'cancelled'   => __('Annulée',          'wwc-shop'),
            'refunded'    => __('Remboursée',       'wwc-shop'),
        ];

        $list_url = admin_url('admin.php?page=wwc-orders');
        ?>
        <div class="wrap wwc-orders-admin">
            <h1 class="wp-heading-inline"><?php esc_html_e('Commandes', 'wwc-shop'); ?></h1>
            <hr class="wp-header-end">

            <?php if (!$this->admin_api_key): ?>
            <div class="notice notice-warning">
                <p><strong><?php esc_html_e('Admin API Key non configurée.', 'wwc-shop'); ?></strong>
                <a href="<?php echo esc_url(admin_url('admin.php?page=wwc-shop-settings')); ?>"><?php esc_html_e('Configurer', 'wwc-shop'); ?></a></p>
            </div>
            <?php elseif ($error_msg): ?>
            <div class="notice notice-error"><p><?php echo esc_html($error_msg); ?></p></div>
            <?php endif; ?>

            <!-- Filters bar -->
            <form method="get" action="<?php echo esc_url($list_url); ?>" class="wwc-orders-filter-bar">
                <input type="hidden" name="page" value="wwc-orders">
                <select name="status" onchange="this.form.submit()">
                    <?php foreach ($status_labels as $val => $label): ?>
                    <option value="<?php echo esc_attr($val); ?>" <?php selected($status, $val); ?>>
                        <?php echo esc_html($label); ?>
                    </option>
                    <?php endforeach; ?>
                </select>
                <input type="search" name="s" value="<?php echo esc_attr($search); ?>"
                    placeholder="<?php esc_attr_e('N° commande, email, téléphone…', 'wwc-shop'); ?>"
                    class="wwc-orders-search">
                <button type="submit" class="button"><?php esc_html_e('Filtrer', 'wwc-shop'); ?></button>
                <?php if ($status || $search): ?>
                <a href="<?php echo esc_url($list_url); ?>" class="button"><?php esc_html_e('Effacer', 'wwc-shop'); ?></a>
                <?php endif; ?>
                <span class="wwc-orders-count">
                    <?php printf(esc_html__('%d commande(s)', 'wwc-shop'), $total); ?>
                </span>
            </form>

            <!-- Orders table -->
            <table class="wp-list-table widefat fixed striped wwc-orders-table">
                <thead>
                    <tr>
                        <th><?php esc_html_e('Commande', 'wwc-shop'); ?></th>
                        <th><?php esc_html_e('Client', 'wwc-shop'); ?></th>
                        <th><?php esc_html_e('Date', 'wwc-shop'); ?></th>
                        <th><?php esc_html_e('Statut', 'wwc-shop'); ?></th>
                        <th><?php esc_html_e('Paiement', 'wwc-shop'); ?></th>
                        <th><?php esc_html_e('Total', 'wwc-shop'); ?></th>
                        <th><?php esc_html_e('Articles', 'wwc-shop'); ?></th>
                        <th><?php esc_html_e('Actions', 'wwc-shop'); ?></th>
                    </tr>
                </thead>
                <tbody>
                    <?php if (empty($orders)): ?>
                    <tr><td colspan="8" style="text-align:center;padding:40px;">
                        <?php esc_html_e('Aucune commande trouvée.', 'wwc-shop'); ?>
                    </td></tr>
                    <?php else: foreach ($orders as $o):
                        $status_class = 'wwc-status-' . esc_attr($o['status'] ?? 'pending');
                        $detail_url   = add_query_arg('order', $o['order_number'], $list_url);
                    ?>
                    <tr>
                        <td><a href="<?php echo esc_url($detail_url); ?>" class="row-title">
                            #<?php echo esc_html($o['order_number']); ?>
                        </a></td>
                        <td>
                            <div><?php echo esc_html($o['email']); ?></div>
                            <?php if (!empty($o['phone'])): ?>
                            <div class="wwc-order-meta"><?php echo esc_html($o['phone']); ?></div>
                            <?php endif; ?>
                        </td>
                        <td><?php echo esc_html($this->format_date($o['created_at'])); ?></td>
                        <td><span class="wwc-status-badge <?php echo $status_class; ?>">
                            <?php echo esc_html($status_labels[$o['status']] ?? $o['status']); ?>
                        </span></td>
                        <td><?php echo esc_html($o['payment_method'] === 'stripe' ? 'Stripe' : 'Virement'); ?></td>
                        <td><strong><?php echo esc_html($o['total'] . ' ' . $o['currency']); ?></strong></td>
                        <td><?php echo esc_html($o['item_count']); ?></td>
                        <td><a href="<?php echo esc_url($detail_url); ?>" class="button button-small">
                            <?php esc_html_e('Gérer', 'wwc-shop'); ?>
                        </a></td>
                    </tr>
                    <?php endforeach; endif; ?>
                </tbody>
            </table>

            <!-- Pagination -->
            <?php if ($total_pages > 1): ?>
            <div class="tablenav bottom">
                <div class="tablenav-pages">
                    <?php if ($page > 1): ?>
                    <a class="button" href="<?php echo esc_url(add_query_arg('paged', $page - 1, add_query_arg(['status' => $status, 's' => $search], $list_url))); ?>">
                        &laquo; <?php esc_html_e('Précédent', 'wwc-shop'); ?>
                    </a>
                    <?php endif; ?>
                    <span style="margin:0 10px;">
                        <?php printf(esc_html__('Page %1$d sur %2$d', 'wwc-shop'), $page, $total_pages); ?>
                    </span>
                    <?php if ($page < $total_pages): ?>
                    <a class="button" href="<?php echo esc_url(add_query_arg('paged', $page + 1, add_query_arg(['status' => $status, 's' => $search], $list_url))); ?>">
                        <?php esc_html_e('Suivant', 'wwc-shop'); ?> &raquo;
                    </a>
                    <?php endif; ?>
                </div>
            </div>
            <?php endif; ?>
        </div>
        <?php
    }

    // ──────────────────────────────────────────────────────────────
    // Order Detail / Edit
    // ──────────────────────────────────────────────────────────────

    private function render_order_detail($order_number) {
        $order = $this->admin_get("admin/orders/{$order_number}/");
        $list_url = admin_url('admin.php?page=wwc-orders');

        if (is_wp_error($order)) {
            echo '<div class="wrap"><p class="notice notice-error">' . esc_html($order->get_error_message()) . '</p>';
            echo '<a href="' . esc_url($list_url) . '" class="button">' . esc_html__('← Retour', 'wwc-shop') . '</a></div>';
            return;
        }

        $status_labels = [
            'pending'    => __('En attente',    'wwc-shop'),
            'paid'       => __('Payée',          'wwc-shop'),
            'processing' => __('En traitement', 'wwc-shop'),
            'shipped'    => __('Expédiée',       'wwc-shop'),
            'delivered'  => __('Livrée',         'wwc-shop'),
            'cancelled'  => __('Annulée',        'wwc-shop'),
            'refunded'   => __('Remboursée',     'wwc-shop'),
        ];

        $symbol = $order['currency'] === 'EUR' ? '€' : 'DT';
        $items  = $order['items'] ?? [];
        ?>
        <div class="wrap wwc-orders-admin">
            <h1>
                <a href="<?php echo esc_url($list_url); ?>" style="text-decoration:none;color:#50575e;font-size:14px;">
                    ← <?php esc_html_e('Commandes', 'wwc-shop'); ?>
                </a>
                &nbsp; #<?php echo esc_html($order['order_number']); ?>
                <span class="wwc-status-badge wwc-status-<?php echo esc_attr($order['status']); ?>" style="font-size:14px;margin-left:10px;">
                    <?php echo esc_html($status_labels[$order['status']] ?? $order['status']); ?>
                </span>
            </h1>
            <hr class="wp-header-end">

            <div id="wwc-order-notice" style="display:none;"></div>

            <div class="wwc-order-detail-grid">

                <!-- Left column: items + totals + address -->
                <div>
                    <!-- Items -->
                    <div class="postbox">
                        <div class="postbox-header"><h2><?php esc_html_e('Articles', 'wwc-shop'); ?></h2></div>
                        <div class="inside">
                            <table class="widefat fixed striped">
                                <thead>
                                    <tr>
                                        <th><?php esc_html_e('Produit', 'wwc-shop'); ?></th>
                                        <th style="width:60px;"><?php esc_html_e('Qté', 'wwc-shop'); ?></th>
                                        <th style="width:90px;"><?php esc_html_e('Prix unit.', 'wwc-shop'); ?></th>
                                        <th style="width:90px;"><?php esc_html_e('Sous-total', 'wwc-shop'); ?></th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <?php foreach ($items as $item): ?>
                                    <tr>
                                        <td>
                                            <strong><?php echo esc_html($item['product_name']); ?></strong>
                                            <?php if (!empty($item['impact_quantity']) && !empty($item['impact_item'])): ?>
                                            <div style="font-size:12px;color:#666;">
                                                💝 <?php echo esc_html($item['impact_quantity'] . ' ' . $item['impact_item']); ?>
                                                <?php if (!empty($item['impact_school'])): ?>
                                                    (<?php echo esc_html($item['impact_school']); ?>)
                                                <?php endif; ?>
                                            </div>
                                            <?php endif; ?>
                                        </td>
                                        <td><?php echo esc_html($item['quantity']); ?></td>
                                        <td><?php echo esc_html($item['unit_price'] . ' ' . $symbol); ?></td>
                                        <td><?php echo esc_html($item['subtotal'] . ' ' . $symbol); ?></td>
                                    </tr>
                                    <?php endforeach; ?>
                                </tbody>
                            </table>

                            <!-- Totals -->
                            <table class="wwc-totals-table">
                                <tr><td><?php esc_html_e('Sous-total', 'wwc-shop'); ?></td>
                                    <td><?php echo esc_html($order['subtotal'] . ' ' . $symbol); ?></td></tr>
                                <?php if (floatval($order['shipping_cost'] ?? 0) > 0): ?>
                                <tr><td><?php esc_html_e('Livraison', 'wwc-shop'); ?></td>
                                    <td><?php echo esc_html($order['shipping_cost'] . ' ' . $symbol); ?></td></tr>
                                <?php endif; ?>
                                <?php if (floatval($order['discount_amount'] ?? 0) > 0): ?>
                                <tr><td><?php echo esc_html($order['coupon_code'] ? 'Remise (' . $order['coupon_code'] . ')' : 'Remise'); ?></td>
                                    <td style="color:green;">-<?php echo esc_html($order['discount_amount'] . ' ' . $symbol); ?></td></tr>
                                <?php endif; ?>
                                <?php if (floatval($order['tax_amount'] ?? 0) > 0): ?>
                                <tr><td><?php esc_html_e('Emballage cadeau', 'wwc-shop'); ?></td>
                                    <td><?php echo esc_html($order['tax_amount'] . ' ' . $symbol); ?></td></tr>
                                <?php endif; ?>
                                <tr class="wwc-totals-total">
                                    <td><strong><?php esc_html_e('Total', 'wwc-shop'); ?></strong></td>
                                    <td><strong><?php echo esc_html($order['total'] . ' ' . $symbol); ?></strong></td>
                                </tr>
                            </table>
                        </div>
                    </div>

                    <!-- Shipping address -->
                    <?php if (!empty($order['shipping_address_1'])): ?>
                    <div class="postbox">
                        <div class="postbox-header"><h2><?php esc_html_e('Adresse de livraison', 'wwc-shop'); ?></h2></div>
                        <div class="inside">
                            <address style="font-style:normal;line-height:1.8;">
                                <?php echo esc_html(trim($order['shipping_first_name'] . ' ' . $order['shipping_last_name'])); ?><br>
                                <?php if (!empty($order['shipping_company'])): ?>
                                    <?php echo esc_html($order['shipping_company']); ?><br>
                                <?php endif; ?>
                                <?php echo esc_html($order['shipping_address_1']); ?><br>
                                <?php if (!empty($order['shipping_address_2'])): ?>
                                    <?php echo esc_html($order['shipping_address_2']); ?><br>
                                <?php endif; ?>
                                <?php echo esc_html(trim($order['shipping_postal_code'] . ' ' . $order['shipping_city'])); ?><br>
                                <?php echo esc_html($order['shipping_country']); ?>
                            </address>
                        </div>
                    </div>
                    <?php endif; ?>

                    <!-- Customer notes -->
                    <?php if (!empty($order['customer_notes'])): ?>
                    <div class="postbox">
                        <div class="postbox-header"><h2><?php esc_html_e('Notes du client', 'wwc-shop'); ?></h2></div>
                        <div class="inside"><p><?php echo esc_html($order['customer_notes']); ?></p></div>
                    </div>
                    <?php endif; ?>
                </div>

                <!-- Right column: customer info + status update -->
                <div>

                    <!-- Customer -->
                    <div class="postbox">
                        <div class="postbox-header"><h2><?php esc_html_e('Client', 'wwc-shop'); ?></h2></div>
                        <div class="inside">
                            <p><strong><?php esc_html_e('Email :', 'wwc-shop'); ?></strong> <?php echo esc_html($order['email']); ?></p>
                            <p><strong><?php esc_html_e('Téléphone :', 'wwc-shop'); ?></strong> <?php echo esc_html($order['phone'] ?: '—'); ?></p>
                            <p><strong><?php esc_html_e('Paiement :', 'wwc-shop'); ?></strong>
                                <?php echo esc_html($order['payment_method'] === 'stripe' ? 'Stripe (CB)' : 'Virement bancaire'); ?></p>
                            <?php if (!empty($order['paid_at'])): ?>
                            <p><strong><?php esc_html_e('Payé le :', 'wwc-shop'); ?></strong>
                                <?php echo esc_html($this->format_date($order['paid_at'])); ?></p>
                            <?php endif; ?>
                        </div>
                    </div>

                    <!-- Impact -->
                    <?php if (!empty($order['total_impact_items'])): ?>
                    <div class="postbox">
                        <div class="postbox-header"><h2><?php esc_html_e('Impact', 'wwc-shop'); ?></h2></div>
                        <div class="inside">
                            <p style="font-size:22px;font-weight:700;color:#e04403;margin:0;">
                                <?php echo esc_html($order['total_impact_items']); ?>
                            </p>
                            <p style="color:#666;margin:4px 0 12px;"><?php esc_html_e('items fournis aux étudiants', 'wwc-shop'); ?></p>
                            <?php if (!empty($order['impact_summary'])): ?>
                                <?php foreach ($order['impact_summary'] as $item_type => $qty): ?>
                                <p style="margin:2px 0;">💝 <?php echo esc_html($qty . ' ' . $item_type); ?></p>
                                <?php endforeach; ?>
                            <?php endif; ?>
                        </div>
                    </div>
                    <?php endif; ?>

                    <!-- Update order -->
                    <div class="postbox">
                        <div class="postbox-header"><h2><?php esc_html_e('Mettre à jour la commande', 'wwc-shop'); ?></h2></div>
                        <div class="inside">
                            <form id="wwc-update-order-form">
                                <input type="hidden" name="order_number" value="<?php echo esc_attr($order['order_number']); ?>">

                                <p>
                                    <label for="order-status"><strong><?php esc_html_e('Statut :', 'wwc-shop'); ?></strong></label><br>
                                    <select id="order-status" name="status" style="width:100%;margin-top:4px;">
                                        <?php foreach ($status_labels as $val => $label): ?>
                                        <option value="<?php echo esc_attr($val); ?>"
                                            <?php selected($order['status'], $val); ?>>
                                            <?php echo esc_html($label); ?>
                                        </option>
                                        <?php endforeach; ?>
                                    </select>
                                </p>

                                <p>
                                    <label for="tracking-number"><strong><?php esc_html_e('N° de suivi :', 'wwc-shop'); ?></strong></label><br>
                                    <input type="text" id="tracking-number" name="tracking_number"
                                        value="<?php echo esc_attr($order['tracking_number']); ?>"
                                        placeholder="<?php esc_attr_e('Ex: TN123456789TN', 'wwc-shop'); ?>"
                                        style="width:100%;margin-top:4px;">
                                </p>

                                <?php if (!empty($order['shipped_at'])): ?>
                                <p style="font-size:12px;color:#666;">
                                    <?php esc_html_e('Expédiée le :', 'wwc-shop'); ?>
                                    <?php echo esc_html($this->format_date($order['shipped_at'])); ?>
                                </p>
                                <?php endif; ?>
                                <?php if (!empty($order['delivered_at'])): ?>
                                <p style="font-size:12px;color:#666;">
                                    <?php esc_html_e('Livrée le :', 'wwc-shop'); ?>
                                    <?php echo esc_html($this->format_date($order['delivered_at'])); ?>
                                </p>
                                <?php endif; ?>

                                <button type="submit" class="button button-primary" id="wwc-update-order-btn" style="width:100%;margin-top:8px;">
                                    <?php esc_html_e('Enregistrer les modifications', 'wwc-shop'); ?>
                                </button>
                            </form>
                        </div>
                    </div>

                </div>
            </div>
        </div>
        <?php
    }

    // ──────────────────────────────────────────────────────────────
    // AJAX: update order status + tracking
    // ──────────────────────────────────────────────────────────────

    public function ajax_update_order() {
        check_ajax_referer('wwc-shop-nonce', 'nonce');
        if (!current_user_can('manage_options')) {
            wp_send_json_error(['message' => __('Permission refusée.', 'wwc-shop')]);
        }

        $order_number    = sanitize_text_field($_POST['order_number'] ?? '');
        $new_status      = sanitize_text_field($_POST['status'] ?? '');
        $tracking_number = sanitize_text_field($_POST['tracking_number'] ?? '');

        if (empty($order_number)) {
            wp_send_json_error(['message' => __('N° de commande manquant.', 'wwc-shop')]);
        }

        $payload = [];
        if ($new_status)      $payload['status']          = $new_status;
        if ($tracking_number !== null) $payload['tracking_number'] = $tracking_number;

        $result = $this->admin_patch("admin/orders/{$order_number}/", $payload);

        if (is_wp_error($result)) {
            wp_send_json_error(['message' => $result->get_error_message()]);
        }

        wp_send_json_success([
            'message' => $result['message'] ?? __('Commande mise à jour.', 'wwc-shop'),
            'order'   => $result,
        ]);
    }

    // ──────────────────────────────────────────────────────────────
    // Helpers
    // ──────────────────────────────────────────────────────────────

    /**
     * GET request to admin Django API endpoint
     */
    private function admin_get($endpoint, $params = []) {
        return $this->admin_request('GET', $endpoint, $params);
    }

    /**
     * PATCH request to admin Django API endpoint
     */
    private function admin_patch($endpoint, $data = []) {
        return $this->admin_request('PATCH', $endpoint, $data);
    }

    private function admin_request($method, $endpoint, $data = []) {
        if (empty($this->admin_api_key)) {
            return new WP_Error('no_api_key', __('Admin API Key non configurée.', 'wwc-shop'));
        }

        $api_url = rtrim(get_option('wwc_api_url', 'https://api.wallahwecan.org'), '/');
        $url     = $api_url . '/api/v1/' . ltrim($endpoint, '/');

        $args = [
            'method'  => $method,
            'timeout' => 30,
            'headers' => [
                'Content-Type'  => 'application/json',
                'Accept'        => 'application/json',
                'Authorization' => 'Api-Key ' . $this->admin_api_key,
            ],
        ];

        if ($method === 'GET' && !empty($data)) {
            $url = add_query_arg($data, $url);
        } elseif (!empty($data)) {
            $args['body'] = json_encode($data);
        }

        $response = wp_remote_request($url, $args);

        if (is_wp_error($response)) {
            return $response;
        }

        $status_code = wp_remote_retrieve_response_code($response);
        $body        = wp_remote_retrieve_body($response);
        $decoded     = json_decode($body, true);

        if ($status_code >= 400) {
            $msg = is_array($decoded)
                ? ($decoded['detail'] ?? $decoded['error'] ?? $decoded['message'] ?? "HTTP {$status_code}")
                : "HTTP {$status_code}";
            return new WP_Error('api_error', is_string($msg) ? $msg : json_encode($msg), ['status' => $status_code]);
        }

        return $decoded;
    }

    private function format_date($iso) {
        if (!$iso) return '—';
        $ts = strtotime($iso);
        return $ts ? date_i18n(get_option('date_format') . ' ' . get_option('time_format'), $ts) : $iso;
    }
}

// Initialize
new WWC_Orders_Admin();
