<?php defined('ABSPATH') || exit; ?>

<div class="wwc-auth-wrap wwc-login-wrap">
    <h2><?php WWC_I18n::e('Connexion'); ?></h2>

    <div id="wwc-auth-message" class="wwc-message" style="display:none;"></div>

    <form id="wwc-login-form" class="wwc-auth-form" novalidate>
        <div class="wwc-form-row">
            <label for="login-email"><?php WWC_I18n::e('Adresse e-mail'); ?> <span class="required">*</span></label>
            <input type="email" id="login-email" name="email" autocomplete="email" required>
        </div>

        <div class="wwc-form-row">
            <label for="login-password"><?php WWC_I18n::e('Mot de passe'); ?> <span class="required">*</span></label>
            <input type="password" id="login-password" name="password" autocomplete="current-password" required>
        </div>

        <div class="wwc-form-row wwc-form-row--forgot">
            <a href="<?php echo esc_url(home_url('/mot-de-passe-oublie/')); ?>"><?php WWC_I18n::e('Mot de passe oublié ?'); ?></a>
        </div>

        <button type="submit" class="wwc-btn wwc-btn--primary" id="wwc-login-submit">
            <?php WWC_I18n::e('Se connecter'); ?>
        </button>
    </form>

    <p class="wwc-auth-switch">
        <?php WWC_I18n::e("Pas encore de compte ?"); ?>
        <a href="<?php echo esc_url(home_url('/inscription/')); ?>"><?php WWC_I18n::e('Créer un compte'); ?></a>
    </p>
</div>
