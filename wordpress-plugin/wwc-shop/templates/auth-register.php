<?php defined('ABSPATH') || exit; ?>

<div class="wwc-auth-wrap wwc-register-wrap">
    <h2><?php esc_html_e('Créer un compte', 'wwc-shop'); ?></h2>

    <div id="wwc-auth-message" class="wwc-message" style="display:none;"></div>

    <form id="wwc-register-form" class="wwc-auth-form" novalidate>
        <div class="wwc-form-row wwc-form-row--half">
            <label for="reg-first-name"><?php esc_html_e('Prénom', 'wwc-shop'); ?> <span class="required">*</span></label>
            <input type="text" id="reg-first-name" name="first_name" autocomplete="given-name" required>
        </div>

        <div class="wwc-form-row wwc-form-row--half">
            <label for="reg-last-name"><?php esc_html_e('Nom', 'wwc-shop'); ?></label>
            <input type="text" id="reg-last-name" name="last_name" autocomplete="family-name">
        </div>

        <div class="wwc-form-row">
            <label for="reg-email"><?php esc_html_e('Adresse e-mail', 'wwc-shop'); ?> <span class="required">*</span></label>
            <input type="email" id="reg-email" name="email" autocomplete="email" required>
        </div>

        <div class="wwc-form-row">
            <label for="reg-password"><?php esc_html_e('Mot de passe', 'wwc-shop'); ?> <span class="required">*</span></label>
            <input type="password" id="reg-password" name="password" autocomplete="new-password" required>
        </div>

        <div class="wwc-form-row">
            <label for="reg-password-confirm"><?php esc_html_e('Confirmer le mot de passe', 'wwc-shop'); ?> <span class="required">*</span></label>
            <input type="password" id="reg-password-confirm" name="password_confirm" autocomplete="new-password" required>
        </div>

        <div class="wwc-form-row">
            <label><?php esc_html_e('Type de compte', 'wwc-shop'); ?></label>
            <label class="wwc-radio-label">
                <input type="radio" name="customer_type" value="individual" checked> <?php esc_html_e('Particulier', 'wwc-shop'); ?>
            </label>
            <label class="wwc-radio-label">
                <input type="radio" name="customer_type" value="business"> <?php esc_html_e('Professionnel', 'wwc-shop'); ?>
            </label>
        </div>

        <div class="wwc-form-row wwc-business-field" style="display:none;">
            <label for="reg-company"><?php esc_html_e('Nom de la société', 'wwc-shop'); ?></label>
            <input type="text" id="reg-company" name="company_name" autocomplete="organization">
        </div>

        <button type="submit" class="wwc-btn wwc-btn--primary" id="wwc-register-submit">
            <?php esc_html_e("S'inscrire", 'wwc-shop'); ?>
        </button>
    </form>

    <p class="wwc-auth-switch">
        <?php esc_html_e('Déjà un compte ?', 'wwc-shop'); ?>
        <a href="<?php echo esc_url(home_url('/connexion/')); ?>"><?php esc_html_e('Se connecter', 'wwc-shop'); ?></a>
    </p>
</div>
