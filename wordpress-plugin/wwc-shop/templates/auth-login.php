<?php defined('ABSPATH') || exit; ?>

<div class="wwc-auth-wrap wwc-login-wrap">
    <h2><?php esc_html_e('Connexion', 'wwc-shop'); ?></h2>

    <div id="wwc-auth-message" class="wwc-message" style="display:none;"></div>

    <form id="wwc-login-form" class="wwc-auth-form" novalidate>
        <div class="wwc-form-row">
            <label for="login-email"><?php esc_html_e('Adresse e-mail', 'wwc-shop'); ?> <span class="required">*</span></label>
            <input type="email" id="login-email" name="email" autocomplete="email" required>
        </div>

        <div class="wwc-form-row">
            <label for="login-password"><?php esc_html_e('Mot de passe', 'wwc-shop'); ?> <span class="required">*</span></label>
            <input type="password" id="login-password" name="password" autocomplete="current-password" required>
        </div>

        <div class="wwc-form-row wwc-form-row--forgot">
            <a href="<?php echo esc_url(home_url('/mot-de-passe-oublie/')); ?>"><?php esc_html_e('Mot de passe oublié ?', 'wwc-shop'); ?></a>
        </div>

        <button type="submit" class="wwc-btn wwc-btn--primary" id="wwc-login-submit">
            <?php esc_html_e('Se connecter', 'wwc-shop'); ?>
        </button>
    </form>

    <p class="wwc-auth-switch">
        <?php esc_html_e("Pas encore de compte ?", 'wwc-shop'); ?>
        <a href="<?php echo esc_url(home_url('/inscription/')); ?>"><?php esc_html_e('Créer un compte', 'wwc-shop'); ?></a>
    </p>
</div>
