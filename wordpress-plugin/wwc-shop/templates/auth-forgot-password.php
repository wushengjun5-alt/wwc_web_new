<?php defined('ABSPATH') || exit; ?>

<div class="wwc-auth-wrap wwc-forgot-password-wrap">
    <h2><?php WWC_I18n::e('Mot de passe oublié'); ?></h2>
    <p class="wwc-auth-desc"><?php WWC_I18n::e('Entrez votre adresse e-mail et nous vous enverrons un lien pour réinitialiser votre mot de passe.'); ?></p>

    <div id="wwc-auth-message" class="wwc-message" style="display:none;"></div>

    <form id="wwc-forgot-password-form" class="wwc-auth-form" novalidate>
        <div class="wwc-form-row">
            <label for="forgot-email"><?php WWC_I18n::e('Adresse e-mail'); ?> <span class="required">*</span></label>
            <input type="email" id="forgot-email" name="email" autocomplete="email" required>
        </div>

        <button type="submit" class="wwc-btn wwc-btn--primary" id="wwc-forgot-submit">
            <?php WWC_I18n::e('Envoyer le lien'); ?>
        </button>
    </form>

    <p class="wwc-auth-switch">
        <a href="<?php echo esc_url(home_url('/connexion/')); ?>"><?php WWC_I18n::e('Retour à la connexion'); ?></a>
    </p>
</div>
