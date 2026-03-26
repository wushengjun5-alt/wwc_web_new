<?php
/**
 * WWC Shop Donations Admin
 *
 * Manages donation countries, projects, and donations from WordPress admin.
 *
 * @package WWC_Shop
 */

defined('ABSPATH') || exit;

class WWC_Donations_Admin {

    private $admin_api_key;

    public function __construct() {
        $this->admin_api_key = get_option('wwc_admin_api_key', '');

        add_action('admin_menu',            [$this, 'add_menu_pages']);
        add_action('admin_enqueue_scripts', [$this, 'enqueue_admin_assets']);

        // AJAX handlers
        add_action('wp_ajax_wwc_admin_save_project',    [$this, 'ajax_save_project']);
        add_action('wp_ajax_wwc_admin_delete_project',  [$this, 'ajax_delete_project']);
        add_action('wp_ajax_wwc_admin_update_donation', [$this, 'ajax_update_donation']);
        add_action('wp_ajax_wwc_admin_save_country',    [$this, 'ajax_save_country']);
        add_action('wp_ajax_wwc_admin_delete_country',  [$this, 'ajax_delete_country']);
    }

    // ──────────────────────────────────────────────────────────────
    // Menu
    // ──────────────────────────────────────────────────────────────

    public function add_menu_pages() {
        add_submenu_page(
            'wwc-shop',
            __('Dons', 'wwc-shop'),
            __('Dons', 'wwc-shop'),
            'manage_options',
            'wwc-donations',
            [$this, 'render_donations_page']
        );
        add_submenu_page(
            'wwc-shop',
            __('Projets de dons', 'wwc-shop'),
            __('Projets de dons', 'wwc-shop'),
            'manage_options',
            'wwc-donation-projects',
            [$this, 'render_projects_page']
        );
        add_submenu_page(
            'wwc-shop',
            __('Pays (dons)', 'wwc-shop'),
            __('Pays (dons)', 'wwc-shop'),
            'manage_options',
            'wwc-donation-countries',
            [$this, 'render_countries_page']
        );
    }

    public function enqueue_admin_assets($hook) {
        if (strpos($hook, 'wwc-donation') === false) return;

        wp_enqueue_script(
            'wwc-donations-admin',
            WWC_SHOP_PLUGIN_URL . 'assets/js/admin-donations.js',
            ['jquery'],
            WWC_SHOP_VERSION . '.dbg1',
            true
        );
        wp_localize_script('wwc-donations-admin', 'wwcDonations', [
            'ajaxUrl' => admin_url('admin-ajax.php'),
            'nonce'   => wp_create_nonce('wwc-shop-nonce'),
            'i18n'    => [
                'confirmDelete' => __('Supprimer ? Cette action est irréversible.', 'wwc-shop'),
                'saveSuccess'   => __('Enregistré avec succès.', 'wwc-shop'),
                'deleteSuccess' => __('Supprimé avec succès.', 'wwc-shop'),
                'error'         => __('Une erreur est survenue.', 'wwc-shop'),
            ],
        ]);
    }

    // ──────────────────────────────────────────────────────────────
    // DONATIONS LIST
    // ──────────────────────────────────────────────────────────────

    public function render_donations_page() {
        $page      = max(1, intval($_GET['paged'] ?? 1));
        $status    = sanitize_text_field($_GET['status'] ?? '');
        $project   = intval($_GET['project_id'] ?? 0);
        $page_size = 20;

        $params = ['page' => $page, 'page_size' => $page_size];
        if ($status)  $params['status']     = $status;
        if ($project) $params['project_id'] = $project;

        $response    = $this->admin_get('admin/donations/', $params);
        $donations   = is_wp_error($response) ? [] : ($response['results'] ?? []);
        $total       = is_wp_error($response) ? 0  : ($response['count']   ?? 0);
        $total_pages = $page_size > 0 ? ceil($total / $page_size) : 1;
        $error_msg   = is_wp_error($response) ? $response->get_error_message() : '';

        $status_labels = [
            ''          => __('Tous',       'wwc-shop'),
            'pending'   => __('En attente', 'wwc-shop'),
            'completed' => __('Complété',   'wwc-shop'),
            'failed'    => __('Échoué',     'wwc-shop'),
        ];
        $list_url = admin_url('admin.php?page=wwc-donations');
        ?>
        <div class="wrap wwc-donations-admin">
            <h1 class="wp-heading-inline"><?php esc_html_e('Dons', 'wwc-shop'); ?></h1>
            <hr class="wp-header-end">

            <?php $this->maybe_show_api_key_notice(); ?>
            <?php if ($error_msg): ?>
            <div class="notice notice-error"><p><?php echo esc_html($error_msg); ?></p></div>
            <?php endif; ?>

            <div id="wwc-don-notice" style="display:none;margin:10px 0;"></div>

            <!-- Filters -->
            <form method="get" action="<?php echo esc_url($list_url); ?>" style="margin:12px 0;display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
                <input type="hidden" name="page" value="wwc-donations">
                <select name="status" onchange="this.form.submit()">
                    <?php foreach ($status_labels as $val => $label): ?>
                    <option value="<?php echo esc_attr($val); ?>" <?php selected($status, $val); ?>><?php echo esc_html($label); ?></option>
                    <?php endforeach; ?>
                </select>
                <button type="submit" class="button"><?php esc_html_e('Filtrer', 'wwc-shop'); ?></button>
                <?php if ($status || $project): ?>
                <a href="<?php echo esc_url($list_url); ?>" class="button"><?php esc_html_e('Effacer', 'wwc-shop'); ?></a>
                <?php endif; ?>
                <span style="color:#666;"><?php printf(esc_html__('%d don(s)', 'wwc-shop'), $total); ?></span>
            </form>

            <table class="wp-list-table widefat fixed striped">
                <thead><tr>
                    <th><?php esc_html_e('Réf.', 'wwc-shop'); ?></th>
                    <th><?php esc_html_e('Donateur', 'wwc-shop'); ?></th>
                    <th><?php esc_html_e('Projet', 'wwc-shop'); ?></th>
                    <th><?php esc_html_e('Montant', 'wwc-shop'); ?></th>
                    <th><?php esc_html_e('Méthode', 'wwc-shop'); ?></th>
                    <th><?php esc_html_e('Statut', 'wwc-shop'); ?></th>
                    <th><?php esc_html_e('Date', 'wwc-shop'); ?></th>
                    <th><?php esc_html_e('Actions', 'wwc-shop'); ?></th>
                </tr></thead>
                <tbody>
                <?php if (empty($donations)): ?>
                    <tr><td colspan="8" style="text-align:center;padding:40px;"><?php esc_html_e('Aucun don trouvé.', 'wwc-shop'); ?></td></tr>
                <?php else: foreach ($donations as $d):
                    $ref = 'DON-' . str_pad($d['id'], 6, '0', STR_PAD_LEFT);
                    $donor = $d['is_anonymous'] ? __('Anonyme', 'wwc-shop') : esc_html($d['donor_name'] ?: '—');
                ?>
                    <tr id="don-row-<?php echo esc_attr($d['id']); ?>">
                        <td><strong><?php echo esc_html($ref); ?></strong></td>
                        <td>
                            <?php echo esc_html($donor); ?>
                            <?php if (!empty($d['donor_email']) && !$d['is_anonymous']): ?>
                            <div style="font-size:12px;color:#666;"><?php echo esc_html($d['donor_email']); ?></div>
                            <?php endif; ?>
                        </td>
                        <td><?php echo esc_html($d['project']['title'] ?? '—'); ?></td>
                        <td><strong><?php echo esc_html($d['amount'] . ' ' . $d['currency']); ?></strong></td>
                        <td><?php echo esc_html($d['payment_method'] === 'stripe' ? 'Stripe' : 'Virement'); ?></td>
                        <td>
                            <select class="don-status-select" data-id="<?php echo esc_attr($d['id']); ?>" style="font-size:12px;">
                                <?php foreach (['pending' => __('En attente','wwc-shop'), 'completed' => __('Complété','wwc-shop'), 'failed' => __('Échoué','wwc-shop')] as $val => $lbl): ?>
                                <option value="<?php echo esc_attr($val); ?>" <?php selected($d['status'], $val); ?>><?php echo esc_html($lbl); ?></option>
                                <?php endforeach; ?>
                            </select>
                        </td>
                        <td><?php echo esc_html($this->format_date($d['created_at'])); ?></td>
                        <td>
                            <button type="button" class="button button-small don-save-btn" data-id="<?php echo esc_attr($d['id']); ?>">
                                <?php esc_html_e('Enregistrer', 'wwc-shop'); ?>
                            </button>
                        </td>
                    </tr>
                <?php endforeach; endif; ?>
                </tbody>
            </table>

            <?php $this->render_pagination($page, $total_pages, $list_url, ['status' => $status]); ?>
        </div>
        <?php
    }

    // ──────────────────────────────────────────────────────────────
    // PROJECTS
    // ──────────────────────────────────────────────────────────────

    public function render_projects_page() {
        $action = sanitize_text_field($_GET['action'] ?? '');
        $pk     = intval($_GET['id'] ?? 0);

        if ($action === 'edit' && $pk) {
            $this->render_project_form($pk);
        } elseif ($action === 'new') {
            $this->render_project_form(0);
        } else {
            $this->render_projects_list();
        }
    }

    private function render_projects_list() {
        $page      = max(1, intval($_GET['paged'] ?? 1));
        $page_size = 20;

        $response = $this->admin_get('admin/donations/projects/', ['page' => $page, 'page_size' => $page_size]);
        $projects    = is_wp_error($response) ? [] : ($response['results'] ?? []);
        $total       = is_wp_error($response) ? 0  : ($response['count']   ?? 0);
        $total_pages = $page_size > 0 ? ceil($total / $page_size) : 1;
        $error_msg   = is_wp_error($response) ? $response->get_error_message() : '';

        $list_url = admin_url('admin.php?page=wwc-donation-projects');
        $new_url  = add_query_arg('action', 'new', $list_url);
        ?>
        <div class="wrap wwc-donations-admin">
            <h1 class="wp-heading-inline"><?php esc_html_e('Projets de dons', 'wwc-shop'); ?></h1>
            <a href="<?php echo esc_url($new_url); ?>" class="page-title-action"><?php esc_html_e('+ Ajouter', 'wwc-shop'); ?></a>
            <hr class="wp-header-end">

            <?php $this->maybe_show_api_key_notice(); ?>
            <?php if ($error_msg): ?>
            <div class="notice notice-error"><p><?php echo esc_html($error_msg); ?></p></div>
            <?php endif; ?>

            <div id="wwc-don-notice" style="display:none;margin:10px 0;"></div>

            <p style="color:#666;"><?php printf(esc_html__('%d projet(s)', 'wwc-shop'), $total); ?></p>

            <table class="wp-list-table widefat fixed striped">
                <thead><tr>
                    <th><?php esc_html_e('Titre', 'wwc-shop'); ?></th>
                    <th><?php esc_html_e('Pays', 'wwc-shop'); ?></th>
                    <th><?php esc_html_e('Catégorie', 'wwc-shop'); ?></th>
                    <th><?php esc_html_e('Objectif', 'wwc-shop'); ?></th>
                    <th><?php esc_html_e('Collecté', 'wwc-shop'); ?></th>
                    <th><?php esc_html_e('Dons', 'wwc-shop'); ?></th>
                    <th><?php esc_html_e('Actif', 'wwc-shop'); ?></th>
                    <th><?php esc_html_e('Actions', 'wwc-shop'); ?></th>
                </tr></thead>
                <tbody>
                <?php if (empty($projects)): ?>
                    <tr><td colspan="8" style="text-align:center;padding:40px;"><?php esc_html_e('Aucun projet trouvé.', 'wwc-shop'); ?></td></tr>
                <?php else: foreach ($projects as $p):
                    $edit_url = add_query_arg(['action' => 'edit', 'id' => $p['id']], $list_url);
                ?>
                    <tr id="proj-row-<?php echo esc_attr($p['id']); ?>">
                        <td>
                            <a href="<?php echo esc_url($edit_url); ?>" class="row-title"><strong><?php echo esc_html($p['title']); ?></strong></a>
                            <?php if (!empty($p['is_featured'])): ?><span style="color:#e04403;font-size:11px;margin-left:4px;">★ Mis en avant</span><?php endif; ?>
                        </td>
                        <td><?php echo esc_html($p['country']['name'] ?? ($p['country_name'] ?? '—')); ?></td>
                        <td><?php echo esc_html($p['category'] ?? '—'); ?></td>
                        <td><?php echo esc_html($p['goal_amount'] . ' ' . ($p['currency'] ?? 'TND')); ?></td>
                        <td><?php echo esc_html($p['raised_amount'] ?? '0'); ?> (<?php echo esc_html($p['progress_percent'] ?? '0'); ?>%)</td>
                        <td><?php echo esc_html($p['donor_count'] ?? '0'); ?></td>
                        <td><?php echo $p['is_active'] ? '<span style="color:green;">✓</span>' : '<span style="color:#999;">✗</span>'; ?></td>
                        <td style="display:flex;gap:6px;">
                            <a href="<?php echo esc_url($edit_url); ?>" class="button button-small"><?php esc_html_e('Modifier', 'wwc-shop'); ?></a>
                            <button type="button" class="button button-small proj-delete-btn" data-id="<?php echo esc_attr($p['id']); ?>" style="color:#c00;border-color:#c00;"><?php esc_html_e('Supprimer', 'wwc-shop'); ?></button>
                        </td>
                    </tr>
                <?php endforeach; endif; ?>
                </tbody>
            </table>

            <?php $this->render_pagination($page, $total_pages, $list_url); ?>
        </div>
        <?php
    }

    private function render_project_form($pk) {
        $list_url = admin_url('admin.php?page=wwc-donation-projects');
        $is_new   = ($pk === 0);

        $project = [];
        if (!$is_new) {
            $project = $this->admin_get("admin/donations/projects/{$pk}/");
            if (is_wp_error($project)) {
                echo '<div class="wrap"><div class="notice notice-error"><p>' . esc_html($project->get_error_message()) . '</p></div>';
                echo '<a href="' . esc_url($list_url) . '" class="button">← ' . esc_html__('Retour', 'wwc-shop') . '</a></div>';
                return;
            }
        }

        // Load countries for the select
        $countries_res = $this->admin_get('admin/donations/countries/');
        $countries     = is_wp_error($countries_res) ? [] : ($countries_res['results'] ?? $countries_res ?? []);

        $categories = [
            'food'           => __('Alimentation',      'wwc-shop'),
            'infrastructure' => __('Infrastructure',    'wwc-shop'),
            'sports'         => __('Sports',            'wwc-shop'),
            'education'      => __('Éducation',         'wwc-shop'),
            'health'         => __('Santé',             'wwc-shop'),
            'other'          => __('Autre',             'wwc-shop'),
        ];
        ?>
        <div class="wrap wwc-donations-admin">
            <h1>
                <a href="<?php echo esc_url($list_url); ?>" style="text-decoration:none;color:#50575e;font-size:14px;">← <?php esc_html_e('Projets', 'wwc-shop'); ?></a>
                &nbsp; <?php echo $is_new ? esc_html__('Nouveau projet', 'wwc-shop') : esc_html($project['title'] ?? ''); ?>
            </h1>
            <hr class="wp-header-end">

            <div id="wwc-don-notice" style="display:none;margin:10px 0;"></div>

            <form id="wwc-project-form" data-id="<?php echo esc_attr($pk); ?>" method="post" action="#" onsubmit="return false;">
                <div style="display:grid;grid-template-columns:1fr 300px;gap:20px;margin-top:16px;">

                    <!-- Main column -->
                    <div>
                        <div class="postbox">
                            <div class="postbox-header"><h2><?php esc_html_e('Informations', 'wwc-shop'); ?></h2></div>
                            <div class="inside" style="display:flex;flex-direction:column;gap:14px;">

                                <label><strong><?php esc_html_e('Titre (FR) *', 'wwc-shop'); ?></strong><br>
                                    <input type="text" name="title" value="<?php echo esc_attr($project['title'] ?? ''); ?>" class="large-text" required></label>

                                <label><strong><?php esc_html_e('Titre (EN)', 'wwc-shop'); ?></strong><br>
                                    <input type="text" name="title_en" value="<?php echo esc_attr($project['title_en'] ?? ''); ?>" class="large-text"></label>

                                <label><strong><?php esc_html_e('Description (FR)', 'wwc-shop'); ?></strong><br>
                                    <textarea name="description" rows="4" class="large-text"><?php echo esc_textarea($project['description'] ?? ''); ?></textarea></label>

                                <label><strong><?php esc_html_e('Description (EN)', 'wwc-shop'); ?></strong><br>
                                    <textarea name="description_en" rows="4" class="large-text"><?php echo esc_textarea($project['description_en'] ?? ''); ?></textarea></label>

                                <label><strong><?php esc_html_e('École / Bénéficiaire', 'wwc-shop'); ?></strong><br>
                                    <input type="text" name="school" value="<?php echo esc_attr($project['school'] ?? ''); ?>" class="large-text"></label>

                            </div>
                        </div>
                    </div>

                    <!-- Side column -->
                    <div>
                        <div class="postbox">
                            <div class="postbox-header"><h2><?php esc_html_e('Paramètres', 'wwc-shop'); ?></h2></div>
                            <div class="inside" style="display:flex;flex-direction:column;gap:14px;">

                                <label><strong><?php esc_html_e('Pays *', 'wwc-shop'); ?></strong><br>
                                    <select name="country_id" style="width:100%;" required>
                                        <option value=""><?php esc_html_e('— Choisir —', 'wwc-shop'); ?></option>
                                        <?php foreach ($countries as $c): ?>
                                        <option value="<?php echo esc_attr($c['id']); ?>"
                                            <?php selected($project['country_id'] ?? ($project['country']['id'] ?? ''), $c['id']); ?>>
                                            <?php echo esc_html(($c['flag_emoji'] ?? '') . ' ' . $c['name']); ?>
                                        </option>
                                        <?php endforeach; ?>
                                    </select>
                                </label>

                                <label><strong><?php esc_html_e('Catégorie', 'wwc-shop'); ?></strong><br>
                                    <select name="category" style="width:100%;">
                                        <?php foreach ($categories as $val => $lbl): ?>
                                        <option value="<?php echo esc_attr($val); ?>" <?php selected($project['category'] ?? '', $val); ?>><?php echo esc_html($lbl); ?></option>
                                        <?php endforeach; ?>
                                    </select>
                                </label>

                                <label><strong><?php esc_html_e('Objectif *', 'wwc-shop'); ?></strong><br>
                                    <input type="number" name="goal_amount" value="<?php echo esc_attr($project['goal_amount'] ?? ''); ?>" min="1" step="0.01" style="width:100%;" required></label>

                                <label><strong><?php esc_html_e('Devise', 'wwc-shop'); ?></strong><br>
                                    <select name="currency" style="width:100%;">
                                        <option value="TND" <?php selected($project['currency'] ?? 'TND', 'TND'); ?>>TND (DT)</option>
                                        <option value="EUR" <?php selected($project['currency'] ?? '', 'EUR'); ?>>EUR (€)</option>
                                    </select>
                                </label>

                                <label><strong><?php esc_html_e('Date limite', 'wwc-shop'); ?></strong><br>
                                    <input type="date" name="deadline" value="<?php echo esc_attr($project['deadline'] ?? ''); ?>" style="width:100%;"></label>

                                <label style="display:flex;align-items:center;gap:8px;">
                                    <input type="checkbox" name="is_active" value="1" <?php checked(!empty($project['is_active']) || $is_new); ?>>
                                    <strong><?php esc_html_e('Actif', 'wwc-shop'); ?></strong>
                                </label>

                                <label style="display:flex;align-items:center;gap:8px;">
                                    <input type="checkbox" name="is_featured" value="1" <?php checked(!empty($project['is_featured'])); ?>>
                                    <strong><?php esc_html_e('Mis en avant', 'wwc-shop'); ?></strong>
                                </label>

                                <button type="submit" class="button button-primary" style="width:100%;">
                                    <?php echo $is_new ? esc_html__('Créer le projet', 'wwc-shop') : esc_html__('Enregistrer', 'wwc-shop'); ?>
                                </button>

                                <?php if (!$is_new): ?>
                                <button type="button" class="button proj-delete-btn" data-id="<?php echo esc_attr($pk); ?>" data-redirect="<?php echo esc_url($list_url); ?>" style="width:100%;color:#c00;border-color:#c00;">
                                    <?php esc_html_e('Supprimer ce projet', 'wwc-shop'); ?>
                                </button>
                                <?php endif; ?>
                            </div>
                        </div>
                    </div>

                </div>
            </form>
        </div>
        <?php
    }

    // ──────────────────────────────────────────────────────────────
    // COUNTRIES
    // ──────────────────────────────────────────────────────────────

    public function render_countries_page() {
        $response  = $this->admin_get('admin/donations/countries/');
        $countries = is_wp_error($response) ? [] : ($response['results'] ?? $response ?? []);
        $error_msg = is_wp_error($response) ? $response->get_error_message() : '';
        $list_url  = admin_url('admin.php?page=wwc-donation-countries');
        ?>
        <div class="wrap wwc-donations-admin">
            <h1 class="wp-heading-inline"><?php esc_html_e('Pays (dons)', 'wwc-shop'); ?></h1>
            <hr class="wp-header-end">

            <?php $this->maybe_show_api_key_notice(); ?>
            <?php if ($error_msg): ?>
            <div class="notice notice-error"><p><?php echo esc_html($error_msg); ?></p></div>
            <?php endif; ?>

            <div id="wwc-don-notice" style="display:none;margin:10px 0;"></div>

            <div style="display:grid;grid-template-columns:1fr 340px;gap:24px;margin-top:16px;">

                <!-- Countries list -->
                <div>
                    <table class="wp-list-table widefat fixed striped">
                        <thead><tr>
                            <th><?php esc_html_e('Drapeau', 'wwc-shop'); ?></th>
                            <th><?php esc_html_e('Nom (FR)', 'wwc-shop'); ?></th>
                            <th><?php esc_html_e('Nom (EN)', 'wwc-shop'); ?></th>
                            <th><?php esc_html_e('Slug', 'wwc-shop'); ?></th>
                            <th><?php esc_html_e('Actif', 'wwc-shop'); ?></th>
                            <th><?php esc_html_e('Actions', 'wwc-shop'); ?></th>
                        </tr></thead>
                        <tbody>
                        <?php if (empty($countries)): ?>
                            <tr><td colspan="6" style="text-align:center;padding:30px;"><?php esc_html_e('Aucun pays.', 'wwc-shop'); ?></td></tr>
                        <?php else: foreach ($countries as $c): ?>
                            <tr id="country-row-<?php echo esc_attr($c['id']); ?>">
                                <td style="font-size:24px;"><?php echo esc_html($c['flag_emoji'] ?? ''); ?></td>
                                <td><strong><?php echo esc_html($c['name']); ?></strong></td>
                                <td><?php echo esc_html($c['name_en'] ?? ''); ?></td>
                                <td><code><?php echo esc_html($c['slug']); ?></code></td>
                                <td><?php echo $c['is_active'] ? '<span style="color:green;">✓</span>' : '<span style="color:#999;">✗</span>'; ?></td>
                                <td style="display:flex;gap:6px;">
                                    <button type="button" class="button button-small country-edit-btn"
                                        data-id="<?php echo esc_attr($c['id']); ?>"
                                        data-name="<?php echo esc_attr($c['name']); ?>"
                                        data-name_en="<?php echo esc_attr($c['name_en'] ?? ''); ?>"
                                        data-name_ar="<?php echo esc_attr($c['name_ar'] ?? ''); ?>"
                                        data-slug="<?php echo esc_attr($c['slug']); ?>"
                                        data-flag="<?php echo esc_attr($c['flag_emoji'] ?? ''); ?>"
                                        data-active="<?php echo esc_attr($c['is_active'] ? '1' : '0'); ?>">
                                        <?php esc_html_e('Modifier', 'wwc-shop'); ?>
                                    </button>
                                    <button type="button" class="button button-small country-delete-btn" data-id="<?php echo esc_attr($c['id']); ?>" style="color:#c00;border-color:#c00;">
                                        <?php esc_html_e('Supprimer', 'wwc-shop'); ?>
                                    </button>
                                </td>
                            </tr>
                        <?php endforeach; endif; ?>
                        </tbody>
                    </table>
                </div>

                <!-- Add / Edit form -->
                <div>
                    <div class="postbox">
                        <div class="postbox-header"><h2 id="country-form-title"><?php esc_html_e('Ajouter un pays', 'wwc-shop'); ?></h2></div>
                        <div class="inside">
                            <form id="wwc-country-form" method="post" action="#" onsubmit="return false;" style="display:flex;flex-direction:column;gap:12px;">
                                <input type="hidden" name="country_id" id="country-id" value="0">

                                <label><strong><?php esc_html_e('Nom (FR) *', 'wwc-shop'); ?></strong><br>
                                    <input type="text" name="name" id="country-name" class="large-text" required></label>

                                <label><strong><?php esc_html_e('Nom (EN)', 'wwc-shop'); ?></strong><br>
                                    <input type="text" name="name_en" id="country-name-en" class="large-text"></label>

                                <label><strong><?php esc_html_e('Nom (AR)', 'wwc-shop'); ?></strong><br>
                                    <input type="text" name="name_ar" id="country-name-ar" class="large-text" dir="rtl"></label>

                                <label><strong><?php esc_html_e('Slug *', 'wwc-shop'); ?></strong><br>
                                    <input type="text" name="slug" id="country-slug" class="large-text" required placeholder="ex: tunisie"></label>

                                <label><strong><?php esc_html_e('Emoji drapeau', 'wwc-shop'); ?></strong><br>
                                    <input type="text" name="flag_emoji" id="country-flag" class="large-text" placeholder="🇹🇳"></label>

                                <label style="display:flex;align-items:center;gap:8px;">
                                    <input type="checkbox" name="is_active" id="country-active" value="1" checked>
                                    <strong><?php esc_html_e('Actif', 'wwc-shop'); ?></strong>
                                </label>

                                <div style="display:flex;gap:8px;">
                                    <button type="submit" class="button button-primary" style="flex:1;"><?php esc_html_e('Enregistrer', 'wwc-shop'); ?></button>
                                    <button type="button" id="country-form-reset" class="button" style="display:none;"><?php esc_html_e('Annuler', 'wwc-shop'); ?></button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <?php
    }

    // ──────────────────────────────────────────────────────────────
    // AJAX handlers
    // ──────────────────────────────────────────────────────────────

    public function ajax_update_donation() {
        check_ajax_referer('wwc-shop-nonce', 'nonce');
        if (!current_user_can('manage_options')) wp_send_json_error(['message' => __('Permission refusée.', 'wwc-shop')]);

        $id     = intval($_POST['id'] ?? 0);
        $status = sanitize_text_field($_POST['status'] ?? '');

        if (!$id || !$status) wp_send_json_error(['message' => __('Données manquantes.', 'wwc-shop')]);

        $result = $this->admin_patch("admin/donations/{$id}/", ['status' => $status]);
        if (is_wp_error($result)) wp_send_json_error(['message' => $result->get_error_message()]);

        wp_send_json_success(['message' => __('Don mis à jour.', 'wwc-shop')]);
    }

    public function ajax_save_project() {
        check_ajax_referer('wwc-shop-nonce', 'nonce');
        if (!current_user_can('manage_options')) wp_send_json_error(['message' => __('Permission refusée.', 'wwc-shop')]);

        $id = intval($_POST['id'] ?? 0);

        $fields = ['title', 'title_en', 'description', 'description_en', 'school', 'category', 'currency', 'deadline'];
        $payload = [];
        foreach ($fields as $f) {
            if (isset($_POST[$f])) $payload[$f] = sanitize_text_field($_POST[$f]);
        }
        if (isset($_POST['goal_amount']))  $payload['goal_amount']  = floatval($_POST['goal_amount']);
        if (isset($_POST['country_id']))   $payload['country_id']   = intval($_POST['country_id']);
        $payload['is_active']   = !empty($_POST['is_active']);
        $payload['is_featured'] = !empty($_POST['is_featured']);

        if (empty($payload['title'])) wp_send_json_error(['message' => __('Titre requis.', 'wwc-shop')]);
        if (empty($payload['country_id'])) wp_send_json_error(['message' => __('Pays requis.', 'wwc-shop')]);
        if (empty($payload['goal_amount'])) wp_send_json_error(['message' => __('Objectif requis.', 'wwc-shop')]);

        if ($id) {
            $result = $this->admin_patch("admin/donations/projects/{$id}/", $payload);
        } else {
            $result = $this->admin_post('admin/donations/projects/', $payload);
        }

        if (is_wp_error($result)) wp_send_json_error(['message' => $result->get_error_message()]);

        wp_send_json_success([
            'message' => $id ? __('Projet mis à jour.', 'wwc-shop') : __('Projet créé.', 'wwc-shop'),
            'id'      => $result['id'] ?? $id,
        ]);
    }

    public function ajax_delete_project() {
        check_ajax_referer('wwc-shop-nonce', 'nonce');
        if (!current_user_can('manage_options')) wp_send_json_error(['message' => __('Permission refusée.', 'wwc-shop')]);

        $id = intval($_POST['id'] ?? 0);
        if (!$id) wp_send_json_error(['message' => __('ID manquant.', 'wwc-shop')]);

        $result = $this->admin_delete("admin/donations/projects/{$id}/");
        if (is_wp_error($result)) wp_send_json_error(['message' => $result->get_error_message()]);

        wp_send_json_success(['message' => __('Projet supprimé.', 'wwc-shop')]);
    }

    public function ajax_save_country() {
        check_ajax_referer('wwc-shop-nonce', 'nonce');
        if (!current_user_can('manage_options')) wp_send_json_error(['message' => __('Permission refusée.', 'wwc-shop')]);

        $id = intval($_POST['country_id'] ?? 0);

        $payload = [
            'name'       => sanitize_text_field($_POST['name'] ?? ''),
            'slug'       => sanitize_title($_POST['slug'] ?? ''),
            'name_en'    => sanitize_text_field($_POST['name_en'] ?? ''),
            'name_ar'    => sanitize_text_field($_POST['name_ar'] ?? ''),
            'flag_emoji' => sanitize_text_field($_POST['flag_emoji'] ?? ''),
            'is_active'  => !empty($_POST['is_active']),
        ];

        if (empty($payload['name'])) wp_send_json_error(['message' => __('Nom requis.', 'wwc-shop')]);
        if (empty($payload['slug'])) wp_send_json_error(['message' => __('Slug requis.', 'wwc-shop')]);

        if ($id) {
            $result = $this->admin_patch("admin/donations/countries/{$id}/", $payload);
        } else {
            $result = $this->admin_post('admin/donations/countries/', $payload);
        }

        if (is_wp_error($result)) wp_send_json_error(['message' => $result->get_error_message()]);

        wp_send_json_success([
            'message' => $id ? __('Pays mis à jour.', 'wwc-shop') : __('Pays créé.', 'wwc-shop'),
            'country' => $result,
        ]);
    }

    public function ajax_delete_country() {
        check_ajax_referer('wwc-shop-nonce', 'nonce');
        if (!current_user_can('manage_options')) wp_send_json_error(['message' => __('Permission refusée.', 'wwc-shop')]);

        $id = intval($_POST['id'] ?? 0);
        if (!$id) wp_send_json_error(['message' => __('ID manquant.', 'wwc-shop')]);

        $result = $this->admin_delete("admin/donations/countries/{$id}/");
        if (is_wp_error($result)) wp_send_json_error(['message' => $result->get_error_message()]);

        wp_send_json_success(['message' => __('Pays supprimé.', 'wwc-shop')]);
    }

    // ──────────────────────────────────────────────────────────────
    // Helpers
    // ──────────────────────────────────────────────────────────────

    private function maybe_show_api_key_notice() {
        if (!$this->admin_api_key): ?>
        <div class="notice notice-warning">
            <p><strong><?php esc_html_e('Admin API Key non configurée.', 'wwc-shop'); ?></strong>
            <a href="<?php echo esc_url(admin_url('admin.php?page=wwc-shop-settings')); ?>"><?php esc_html_e('Configurer', 'wwc-shop'); ?></a></p>
        </div>
        <?php endif;
    }

    private function render_pagination($page, $total_pages, $base_url, $extra = []) {
        if ($total_pages <= 1) return;
        ?>
        <div class="tablenav bottom">
            <div class="tablenav-pages">
                <?php if ($page > 1): ?>
                <a class="button" href="<?php echo esc_url(add_query_arg(array_merge($extra, ['paged' => $page - 1]), $base_url)); ?>">
                    &laquo; <?php esc_html_e('Précédent', 'wwc-shop'); ?>
                </a>
                <?php endif; ?>
                <span style="margin:0 10px;"><?php printf(esc_html__('Page %1$d sur %2$d', 'wwc-shop'), $page, $total_pages); ?></span>
                <?php if ($page < $total_pages): ?>
                <a class="button" href="<?php echo esc_url(add_query_arg(array_merge($extra, ['paged' => $page + 1]), $base_url)); ?>">
                    <?php esc_html_e('Suivant', 'wwc-shop'); ?> &raquo;
                </a>
                <?php endif; ?>
            </div>
        </div>
        <?php
    }

    private function admin_get($endpoint, $params = []) {
        return $this->admin_request('GET', $endpoint, $params);
    }

    private function admin_post($endpoint, $data = []) {
        return $this->admin_request('POST', $endpoint, $data);
    }

    private function admin_patch($endpoint, $data = []) {
        return $this->admin_request('PATCH', $endpoint, $data);
    }

    private function admin_delete($endpoint) {
        return $this->admin_request('DELETE', $endpoint);
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

        if (is_wp_error($response)) return $response;

        $status_code = wp_remote_retrieve_response_code($response);
        $body        = wp_remote_retrieve_body($response);

        // 204 No Content (delete success)
        if ($status_code === 204) return ['success' => true];

        $decoded = json_decode($body, true);

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

new WWC_Donations_Admin();
