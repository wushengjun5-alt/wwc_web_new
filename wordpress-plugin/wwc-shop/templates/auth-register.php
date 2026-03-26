<?php defined('ABSPATH') || exit; ?>

<div class="wwc-auth-wrap wwc-register-wrap">
    <h2><?php WWC_I18n::e('Créer un compte'); ?></h2>

    <div id="wwc-auth-message" class="wwc-message" style="display:none;"></div>

    <form id="wwc-register-form" class="wwc-auth-form" novalidate>
        <div class="wwc-form-row wwc-form-row--half">
            <label for="reg-first-name"><?php WWC_I18n::e('Prénom'); ?> <span class="required">*</span></label>
            <input type="text" id="reg-first-name" name="first_name" autocomplete="given-name" required>
        </div>

        <div class="wwc-form-row wwc-form-row--half">
            <label for="reg-last-name"><?php WWC_I18n::e('Nom'); ?></label>
            <input type="text" id="reg-last-name" name="last_name" autocomplete="family-name">
        </div>

        <div class="wwc-form-row">
            <label for="reg-email"><?php WWC_I18n::e('Adresse e-mail'); ?> <span class="required">*</span></label>
            <input type="email" id="reg-email" name="email" autocomplete="email" required>
        </div>

        <div class="wwc-form-row">
            <label for="reg-password"><?php WWC_I18n::e('Mot de passe'); ?> <span class="required">*</span></label>
            <input type="password" id="reg-password" name="password" autocomplete="new-password" required>
        </div>

        <div class="wwc-form-row">
            <label for="reg-password-confirm"><?php WWC_I18n::e('Confirmer le mot de passe'); ?> <span class="required">*</span></label>
            <input type="password" id="reg-password-confirm" name="password_confirm" autocomplete="new-password" required>
        </div>

        <div class="wwc-form-row">
            <label><?php WWC_I18n::e('Type de compte'); ?></label>
            <label class="wwc-radio-label">
                <input type="radio" name="customer_type" value="individual" checked> <?php WWC_I18n::e('Particulier'); ?>
            </label>
            <label class="wwc-radio-label">
                <input type="radio" name="customer_type" value="business"> <?php WWC_I18n::e('Professionnel'); ?>
            </label>
        </div>

        <div class="wwc-form-row wwc-business-field" style="display:none;">
            <label for="reg-company"><?php WWC_I18n::e('Nom de la société'); ?></label>
            <input type="text" id="reg-company" name="company_name" autocomplete="organization">
        </div>

        <button type="submit" class="wwc-btn wwc-btn--primary" id="wwc-register-submit">
            <?php WWC_I18n::e("S'inscrire"); ?>
        </button>
    </form>

    <p class="wwc-auth-switch">
        <?php WWC_I18n::e('Déjà un compte ?'); ?>
        <a href="<?php echo esc_url(home_url('/connexion/')); ?>"><?php WWC_I18n::e('Se connecter'); ?></a>
    </p>
</div>
