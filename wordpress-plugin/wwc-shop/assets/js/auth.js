/**
 * WWC Shop Auth JavaScript
 *
 * Handles login, register, logout, and password reset forms.
 *
 * @package WWC_Shop
 */

(function($) {
    'use strict';

    const WWC_Auth = {

        init: function() {
            this.bindEvents();
        },

        bindEvents: function() {
            $(document).on('submit', '#wwc-login-form',           this.handleLogin.bind(this));
            $(document).on('submit', '#wwc-register-form',        this.handleRegister.bind(this));
            $(document).on('submit', '#wwc-forgot-password-form', this.handleForgotPassword.bind(this));
            $(document).on('submit', '#wwc-reset-password-form',  this.handleResetPassword.bind(this));
            $(document).on('click',  '.wwc-logout-btn',           this.handleLogout.bind(this));

            // Show/hide company field based on customer type
            $(document).on('change', 'input[name="customer_type"]', function() {
                if ($(this).val() === 'business') {
                    $('.wwc-business-field').show();
                } else {
                    $('.wwc-business-field').hide();
                }
            });
        },

        handleLogin: function(e) {
            e.preventDefault();
            const $form = $(e.currentTarget);
            const $btn  = $form.find('#wwc-login-submit');

            const data = this.serializeForm($form, 'wwc_login');
            this.submitForm($btn, data, function(response) {
                this.showMessage($form, response.data.message, 'success');
                setTimeout(function() {
                    window.location.href = response.data.redirect || wwcShop.checkoutUrl;
                }, 600);
            }.bind(this));
        },

        handleRegister: function(e) {
            e.preventDefault();
            const $form = $(e.currentTarget);
            const $btn  = $form.find('#wwc-register-submit');

            const data = this.serializeForm($form, 'wwc_register');
            this.submitForm($btn, data, function(response) {
                this.showMessage($form, response.data.message, 'success');
                setTimeout(function() {
                    window.location.href = response.data.redirect || wwcShop.checkoutUrl;
                }, 600);
            }.bind(this));
        },

        handleForgotPassword: function(e) {
            e.preventDefault();
            const $form = $(e.currentTarget);
            const $btn  = $form.find('#wwc-forgot-submit');

            const data = this.serializeForm($form, 'wwc_password_reset_request');
            this.submitForm($btn, data, function(response) {
                this.showMessage($form, response.data.message, 'success');
                $form.hide();
            }.bind(this));
        },

        handleResetPassword: function(e) {
            e.preventDefault();
            const $form = $(e.currentTarget);
            const $btn  = $form.find('#wwc-reset-submit');

            const data = this.serializeForm($form, 'wwc_password_reset_confirm');
            this.submitForm($btn, data, function(response) {
                this.showMessage($form, response.data.message, 'success');
                setTimeout(function() {
                    window.location.href = response.data.redirect || '/connexion/';
                }, 1200);
            }.bind(this));
        },

        handleLogout: function(e) {
            e.preventDefault();
            $.ajax({
                url: wwcShop.ajaxUrl,
                type: 'POST',
                data: { action: 'wwc_logout', nonce: wwcShop.nonce },
                success: function(response) {
                    if (response.success) {
                        window.location.href = response.data.redirect || '/';
                    }
                }
            });
        },

        /**
         * Serialize a form into a plain object, adding action + nonce.
         */
        serializeForm: function($form, action) {
            const data = { action: action, nonce: wwcShop.nonce };
            $form.serializeArray().forEach(function(field) {
                data[field.name] = field.value;
            });
            return data;
        },

        /**
         * Generic AJAX submit helper.
         */
        submitForm: function($btn, data, onSuccess) {
            const originalText = $btn.text();
            $btn.prop('disabled', true).text('...');

            // Find the closest message container
            const $form = $btn.closest('form');

            $.ajax({
                url: wwcShop.ajaxUrl,
                type: 'POST',
                data: data,
                success: function(response) {
                    if (response.success) {
                        onSuccess(response);
                    } else {
                        const msg = (response.data && response.data.message)
                            ? response.data.message
                            : wwcShop.i18n.error;
                        this.showMessage($form, msg, 'error');
                        $btn.prop('disabled', false).text(originalText);
                    }
                }.bind(this),
                error: function() {
                    this.showMessage($form, wwcShop.i18n.error, 'error');
                    $btn.prop('disabled', false).text(originalText);
                }.bind(this)
            });
        },

        /**
         * Show inline message near the form.
         */
        showMessage: function($form, message, type) {
            // Look for #wwc-auth-message inside the closest .wwc-auth-wrap, fallback to form parent
            const $wrap = $form.closest('.wwc-auth-wrap');
            const $msg  = $wrap.length ? $wrap.find('#wwc-auth-message') : $form.prev('#wwc-auth-message');

            $msg
                .removeClass('wwc-message--success wwc-message--error')
                .addClass('wwc-message--' + type)
                .text(message)
                .show();
        }
    };

    $(document).ready(function() {
        WWC_Auth.init();
    });

    window.WWC_Auth = WWC_Auth;

})(jQuery);
