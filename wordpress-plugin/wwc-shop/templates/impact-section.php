<?php
/**
 * Impact Section Template
 *
 * Displays impact events and global impact summary
 *
 * @package WWC_Shop
 */

defined('ABSPATH') || exit;

$api = wwc_shop()->api;
$impact_events = $api->get_impact_events(['page_size' => $atts['limit'] ?? 5]);
$events_list = is_wp_error($impact_events) ? [] : ($impact_events['results'] ?? $impact_events);
?>

<div class="wwc-impact-section">

    <!-- Global Impact Stats -->
    <?php if (!is_wp_error($impact)): ?>
    <div class="wwc-global-impact">
        <h2><?php esc_html_e('Notre Impact Collectif', 'wwc-shop'); ?></h2>

        <div class="wwc-impact-stat-row">
            <div class="wwc-impact-stat">
                <span class="wwc-stat-icon">💝</span>
                <span class="wwc-stat-number"><?php echo esc_html(number_format($impact['total_impact_items'] ?? 0)); ?></span>
                <span class="wwc-stat-label"><?php esc_html_e('items fournis', 'wwc-shop'); ?></span>
            </div>
            <div class="wwc-impact-stat">
                <span class="wwc-stat-icon">📦</span>
                <span class="wwc-stat-number"><?php echo esc_html(number_format($impact['total_orders'] ?? 0)); ?></span>
                <span class="wwc-stat-label"><?php esc_html_e('commandes solidaires', 'wwc-shop'); ?></span>
            </div>
        </div>
    </div>
    <?php endif; ?>

    <!-- Impact Events -->
    <?php if (!empty($events_list)): ?>
    <div class="wwc-impact-events">
        <h2><?php esc_html_e('Événements Récents', 'wwc-shop'); ?></h2>

        <div class="wwc-events-grid">
            <?php foreach ($events_list as $event): ?>
            <div class="wwc-event-card">
                <?php if (!empty($event['photo'])): ?>
                <div class="wwc-event-image">
                    <img src="<?php echo esc_url($event['photo']); ?>"
                         alt="<?php echo esc_attr($event['title']); ?>"
                         loading="lazy">
                </div>
                <?php endif; ?>

                <div class="wwc-event-content">
                    <h3 class="wwc-event-title"><?php echo esc_html($event['title']); ?></h3>

                    <div class="wwc-event-meta">
                        <span class="wwc-event-date">
                            📅 <?php echo esc_html(date_i18n('j F Y', strtotime($event['date']))); ?>
                        </span>
                        <span class="wwc-event-school">
                            🏫 <?php echo esc_html($event['school']); ?>
                        </span>
                    </div>

                    <div class="wwc-event-impact">
                        <span class="wwc-event-number">
                            <?php echo esc_html(number_format($event['items_delivered'])); ?>
                        </span>
                        <span class="wwc-event-type">
                            <?php echo esc_html($event['item_type']); ?>
                        </span>
                        <?php esc_html_e('distribués', 'wwc-shop'); ?>
                    </div>

                    <?php if (!empty($event['description'])): ?>
                    <p class="wwc-event-description">
                        <?php echo esc_html(wp_trim_words($event['description'], 30)); ?>
                    </p>
                    <?php endif; ?>

                    <?php if (!empty($event['video_url'])): ?>
                    <a href="<?php echo esc_url($event['video_url']); ?>" class="wwc-event-video" target="_blank">
                        🎥 <?php esc_html_e('Voir la vidéo', 'wwc-shop'); ?>
                    </a>
                    <?php endif; ?>
                </div>
            </div>
            <?php endforeach; ?>
        </div>
    </div>
    <?php endif; ?>

    <!-- Call to Action -->
    <div class="wwc-impact-cta">
        <h3><?php esc_html_e('Rejoignez le mouvement', 'wwc-shop'); ?></h3>
        <p><?php esc_html_e('Chaque achat contribue à améliorer la vie des étudiants de GreenSchool.', 'wwc-shop'); ?></p>
        <a href="<?php echo esc_url(home_url('/shop/')); ?>" class="wwc-btn wwc-btn-primary">
            <?php esc_html_e('Découvrir nos produits', 'wwc-shop'); ?>
        </a>
    </div>

</div>

<style>
.wwc-impact-section { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }

.wwc-global-impact { text-align: center; margin-bottom: 60px; padding: 40px; background: linear-gradient(135deg, #f8b4c4 0%, #ffd4e0 100%); border-radius: 16px; }
.wwc-global-impact h2 { margin-top: 0; color: #1e3a5f; }

.wwc-impact-stat-row { display: flex; justify-content: center; gap: 60px; margin-top: 30px; }
.wwc-impact-stat { text-align: center; }
.wwc-stat-icon { display: block; font-size: 48px; margin-bottom: 10px; }
.wwc-stat-number { display: block; font-size: 48px; font-weight: 700; color: #1e3a5f; }
.wwc-stat-label { display: block; font-size: 16px; color: #4a3728; }

.wwc-impact-events h2 { text-align: center; margin-bottom: 30px; }

.wwc-events-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 30px; }

.wwc-event-card { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.08); transition: transform 0.3s, box-shadow 0.3s; }
.wwc-event-card:hover { transform: translateY(-5px); box-shadow: 0 8px 24px rgba(0,0,0,0.12); }

.wwc-event-image { height: 200px; overflow: hidden; }
.wwc-event-image img { width: 100%; height: 100%; object-fit: cover; }

.wwc-event-content { padding: 20px; }
.wwc-event-title { font-size: 18px; margin: 0 0 10px; color: #1e3a5f; }

.wwc-event-meta { display: flex; gap: 15px; font-size: 13px; color: #666; margin-bottom: 15px; }

.wwc-event-impact { background: #f8b4c4; padding: 10px 15px; border-radius: 8px; display: inline-block; }
.wwc-event-number { font-size: 24px; font-weight: 700; color: #1e3a5f; }
.wwc-event-type { color: #4a3728; }

.wwc-event-description { margin: 15px 0; color: #666; font-size: 14px; line-height: 1.5; }

.wwc-event-video { display: inline-block; color: #ff6b35; text-decoration: none; font-weight: 600; }
.wwc-event-video:hover { text-decoration: underline; }

.wwc-impact-cta { text-align: center; margin-top: 60px; padding: 40px; background: #1e3a5f; border-radius: 16px; color: white; }
.wwc-impact-cta h3 { margin-top: 0; font-size: 28px; }
.wwc-impact-cta p { opacity: 0.9; margin-bottom: 20px; }

@media (max-width: 768px) {
    .wwc-impact-stat-row { flex-direction: column; gap: 30px; }
    .wwc-events-grid { grid-template-columns: 1fr; }
}
</style>
