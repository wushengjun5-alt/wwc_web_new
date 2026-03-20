<?php defined('ABSPATH') || exit;

// uid and token come from the URL query string (Django sends them in the reset link)
$uid   = sanitize_text_field($_GET['uid'] ?? '');
$token = sanitize_text_field($_GET['token'] ?? '');
?>

<div class="wwc-auth-wrap wwc-reset-password-wrap">
    <h2><?php esc_html_e('Réinitialiser le mot de passe', 'wwc-shop'); ?></h2>

    <div id="wwc-auth-message" class="wwc-message" style="display:none;"></div>

    <?php if (empty($uid) || empty($token)) : ?>
        <p class="wwc-error"><?php esc_html_e('Lien de réinitialisation invalide ou expiré.', 'wwc-shop'); ?></p>
        <p><a href="<?php echo esc_url(home_url('/mot-de-passe-oublie/')); ?>"><?php esc_html_e('Demander un nouveau lien', 'wwc-shop'); ?></a></p>
    <?php else : ?>
        <form id="wwc-reset-password-form" class="wwc-auth-form" novalidate>
            <input type="hidden" name="uid" value="<?php echo esc_attr($uid); ?>">
            <input type="hidden" name="token" value="<?php echo esc_attr($token); ?>">

            <div class="wwc-form-row">
                <label for="reset-password"><?php esc_html_e('Nouveau mot de passe', 'wwc-shop'); ?> <span class="required">*</span></label>
                <input type="password" id="reset-password" name="password" autocomplete="new-password" required>
            </div>

            <div class="wwc-form-row">
                <label for="reset-password-confirm"><?php esc_html_e('Confirmer le mot de passe', 'wwc-shop'); ?> <span class="required">*</span></label>
                <input type="password" id="reset-password-confirm" name="password_confirm" autocomplete="new-password" required>
            </div>

            <button type="submit" class="wwc-btn wwc-btn--primary" id="wwc-reset-submit">
                <?php esc_html_e('Réinitialiser le mot de passe', 'wwc-shop'); ?>
            </button>
        </form>
    <?php endif; ?>
</div>
