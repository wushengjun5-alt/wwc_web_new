<?php
/**
 * WWC Shop Impact Helper
 *
 * Helper functions for social impact display
 *
 * @package WWC_Shop
 */

defined('ABSPATH') || exit;

class WWC_Impact {

    /**
     * Format impact number for display
     */
    public static function format_number($number) {
        if ($number >= 1000000) {
            return round($number / 1000000, 1) . 'M';
        }

        if ($number >= 1000) {
            return round($number / 1000, 1) . 'K';
        }

        return number_format($number);
    }

    /**
     * Get impact icon by item type
     */
    public static function get_icon($item_type) {
        $icons = [
            'barres énergétiques' => '🍫',
            'energy bars' => '🍫',
            'repas' => '🍽️',
            'meals' => '🍽️',
            'livres' => '📚',
            'books' => '📚',
            'fournitures' => '✏️',
            'supplies' => '✏️',
            'default' => '💝',
        ];

        $item_lower = strtolower($item_type);

        foreach ($icons as $key => $icon) {
            if (strpos($item_lower, $key) !== false) {
                return $icon;
            }
        }

        return $icons['default'];
    }

    /**
     * Render impact summary card
     */
    public static function render_summary_card($impact_data) {
        if (empty($impact_data)) {
            return '';
        }

        ob_start();
        ?>
        <div class="wwc-impact-summary-card">
            <h3><?php esc_html_e('Votre impact', 'wwc-shop'); ?></h3>

            <div class="wwc-impact-total">
                <span class="wwc-impact-number">
                    <?php echo esc_html(self::format_number($impact_data['total_impact_items'] ?? 0)); ?>
                </span>
                <span class="wwc-impact-label">
                    <?php esc_html_e('items fournis aux étudiants', 'wwc-shop'); ?>
                </span>
            </div>

            <?php if (!empty($impact_data['breakdown'])): ?>
            <div class="wwc-impact-breakdown">
                <h4><?php esc_html_e('Détail', 'wwc-shop'); ?></h4>
                <ul>
                    <?php foreach ($impact_data['breakdown'] as $item => $quantity): ?>
                    <li>
                        <span class="wwc-impact-icon"><?php echo self::get_icon($item); ?></span>
                        <span class="wwc-impact-qty"><?php echo esc_html(self::format_number($quantity)); ?></span>
                        <span class="wwc-impact-item"><?php echo esc_html($item); ?></span>
                    </li>
                    <?php endforeach; ?>
                </ul>
            </div>
            <?php endif; ?>
        </div>
        <?php
        return ob_get_clean();
    }

    /**
     * Render cart impact preview
     */
    public static function render_cart_impact($cart_impact) {
        if (empty($cart_impact)) {
            return '';
        }

        ob_start();
        ?>
        <div class="wwc-cart-impact">
            <div class="wwc-cart-impact-header">
                💝 <?php esc_html_e('Impact de votre commande', 'wwc-shop'); ?>
            </div>
            <div class="wwc-cart-impact-items">
                <?php foreach ($cart_impact as $item => $quantity): ?>
                <div class="wwc-cart-impact-item">
                    <span class="wwc-impact-icon"><?php echo self::get_icon($item); ?></span>
                    <span>
                        <?php
                        printf(
                            /* translators: 1: quantity, 2: item type */
                            esc_html__('%1$d %2$s pour les étudiants', 'wwc-shop'),
                            $quantity,
                            $item
                        );
                        ?>
                    </span>
                </div>
                <?php endforeach; ?>
            </div>
        </div>
        <?php
        return ob_get_clean();
    }

    /**
     * Render impact event card
     */
    public static function render_event_card($event) {
        ob_start();
        ?>
        <div class="wwc-impact-event-card">
            <?php if (!empty($event['photo'])): ?>
            <div class="wwc-event-image">
                <img src="<?php echo esc_url($event['photo']); ?>"
                     alt="<?php echo esc_attr($event['title']); ?>">
            </div>
            <?php endif; ?>

            <div class="wwc-event-content">
                <h4 class="wwc-event-title"><?php echo esc_html($event['title']); ?></h4>

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
                        <?php echo esc_html(self::format_number($event['items_delivered'])); ?>
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
            </div>
        </div>
        <?php
        return ob_get_clean();
    }
}
