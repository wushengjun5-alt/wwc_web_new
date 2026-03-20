<?php defined('ABSPATH') || exit; ?>

<div class="wwc-auth-wrap wwc-forgot-password-wrap">
    <h2><?php esc_html_e('Mot de passe oublié', 'wwc-shop'); ?></h2>
    <p class="wwc-auth-desc"><?php esc_html_e('Entrez votre adresse e-mail et nous vous enverrons un lien pour réinitialiser votre mot de passe.', 'wwc-shop'); ?></p>

    <div id="wwc-auth-message" class="wwc-message" style="display:none;"></div>

    <form id="wwc-forgot-password-form" class="wwc-auth-form" novalidate>
        <div class="wwc-form-row">
            <label for="forgot-email"><?php esc_html_e('Adresse e-mail', 'wwc-shop'); ?> <span class="required">*</span></label>
            <input type="email" id="forgot-email" name="email" autocomplete="email" required>
        </div>

        <button type="submit" class="wwc-btn wwc-btn--primary" id="wwc-forgot-submit">
            <?php esc_html_e('Envoyer le lien', 'wwc-shop'); ?>
        </button>
    </form>

    <p class="wwc-auth-switch">
        <a href="<?php echo esc_url(home_url('/connexion/')); ?>"><?php esc_html_e('Retour à la connexion', 'wwc-shop'); ?></a>
    </p>
</div>
