<?php defined('ABSPATH') || exit;

// uid and token come from the URL query string (Django sends them in the reset link)
$uid   = sanitize_text_field($_GET['uid'] ?? '');
$token = sanitize_text_field($_GET['token'] ?? '');
?>

<div class="wwc-auth-wrap wwc-reset-password-wrap">
    <h2><?php WWC_I18n::e('Réinitialiser le mot de passe'); ?></h2>

    <div id="wwc-auth-message" class="wwc-message" style="display:none;"></div>

    <?php if (empty($uid) || empty($token)) : ?>
        <p class="wwc-error"><?php WWC_I18n::e('Lien de réinitialisation invalide ou expiré.'); ?></p>
        <p><a href="<?php echo esc_url(home_url('/mot-de-passe-oublie/')); ?>"><?php WWC_I18n::e('Demander un nouveau lien'); ?></a></p>
    <?php else : ?>
        <form id="wwc-reset-password-form" class="wwc-auth-form" novalidate>
            <input type="hidden" name="uid" value="<?php echo esc_attr($uid); ?>">
            <input type="hidden" name="token" value="<?php echo esc_attr($token); ?>">

            <div class="wwc-form-row">
                <label for="reset-password"><?php WWC_I18n::e('Nouveau mot de passe'); ?> <span class="required">*</span></label>
                <input type="password" id="reset-password" name="password" autocomplete="new-password" required>
            </div>

            <div class="wwc-form-row">
                <label for="reset-password-confirm"><?php WWC_I18n::e('Confirmer le mot de passe'); ?> <span class="required">*</span></label>
                <input type="password" id="reset-password-confirm" name="password_confirm" autocomplete="new-password" required>
            </div>

            <button type="submit" class="wwc-btn wwc-btn--primary" id="wwc-reset-submit">
                <?php WWC_I18n::e('Réinitialiser le mot de passe'); ?>
            </button>
        </form>
    <?php endif; ?>
</div>
