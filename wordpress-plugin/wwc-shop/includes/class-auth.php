<?php
/**
 * WWC Shop Auth Handler
 *
 * AJAX handlers for register, login, logout, password reset.
 *
 * @package WWC_Shop
 */

defined('ABSPATH') || exit;

class WWC_Auth {

    private $api;

    public function __construct($api) {
        $this->api = $api;
    }

    /**
     * AJAX: Register
     */
    public function ajax_register() {
        check_ajax_referer('wwc-shop-nonce', 'nonce');

        $data = [
            'email'         => sanitize_email($_POST['email'] ?? ''),
            'password'      => $_POST['password'] ?? '',
            'password_confirm' => $_POST['password_confirm'] ?? '',
            'first_name'    => sanitize_text_field($_POST['first_name'] ?? ''),
            'last_name'     => sanitize_text_field($_POST['last_name'] ?? ''),
            'customer_type' => sanitize_text_field($_POST['customer_type'] ?? 'individual'),
            'company_name'  => sanitize_text_field($_POST['company_name'] ?? ''),
        ];

        if (empty($data['email']) || empty($data['password']) || empty($data['first_name'])) {
            wp_send_json_error(['message' => __('Tous les champs obligatoires doivent être remplis.', 'wwc-shop')]);
        }

        $result = $this->api->register_user($data);

        if (is_wp_error($result)) {
            wp_send_json_error(['message' => $result->get_error_message()]);
        }

        if (isset($result['error'])) {
            wp_send_json_error(['message' => $result['error']]);
        }

        // Store tokens
        if (isset($result['access'])) {
            $this->api->store_tokens($result['access'], $result['refresh'] ?? '');
        }

        wp_send_json_success([
            'message'  => __('Inscription réussie ! Bienvenue.', 'wwc-shop'),
            'user'     => $result['user'] ?? [],
            'redirect' => home_url('/mon-compte/'),
        ]);
    }

    /**
     * AJAX: Login
     */
    public function ajax_login() {
        check_ajax_referer('wwc-shop-nonce', 'nonce');

        $email    = sanitize_email($_POST['email'] ?? '');
        $password = $_POST['password'] ?? '';

        if (empty($email) || empty($password)) {
            wp_send_json_error(['message' => __('Email et mot de passe requis.', 'wwc-shop')]);
        }

        $result = $this->api->login_user($email, $password);

        if (is_wp_error($result)) {
            wp_send_json_error(['message' => $result->get_error_message()]);
        }

        if (isset($result['error'])) {
            wp_send_json_error(['message' => $result['error']]);
        }

        $redirect = sanitize_url($_POST['redirect'] ?? home_url('/mon-compte/'));

        wp_send_json_success([
            'message'  => __('Connexion réussie !', 'wwc-shop'),
            'user'     => $result['user'] ?? [],
            'redirect' => $redirect,
        ]);
    }

    /**
     * AJAX: Logout
     */
    public function ajax_logout() {
        check_ajax_referer('wwc-shop-nonce', 'nonce');
        $this->api->clear_tokens();
        wp_send_json_success(['redirect' => home_url('/')]);
    }

    /**
     * AJAX: Password reset request
     */
    public function ajax_password_reset_request() {
        check_ajax_referer('wwc-shop-nonce', 'nonce');

        $email = sanitize_email($_POST['email'] ?? '');
        if (empty($email)) {
            wp_send_json_error(['message' => __('Email requis.', 'wwc-shop')]);
        }

        $result = $this->api->request_password_reset($email);

        if (is_wp_error($result)) {
            wp_send_json_error(['message' => $result->get_error_message()]);
        }

        wp_send_json_success([
            'message' => $result['message'] ?? __('Si cet email existe, un lien de réinitialisation a été envoyé.', 'wwc-shop'),
        ]);
    }

    /**
     * AJAX: Password reset confirm
     */
    public function ajax_password_reset_confirm() {
        check_ajax_referer('wwc-shop-nonce', 'nonce');

        $result = $this->api->confirm_password_reset(
            sanitize_text_field($_POST['uid'] ?? ''),
            sanitize_text_field($_POST['token'] ?? ''),
            $_POST['password'] ?? '',
            $_POST['password_confirm'] ?? ''
        );

        if (is_wp_error($result)) {
            wp_send_json_error(['message' => $result->get_error_message()]);
        }

        if (isset($result['error'])) {
            wp_send_json_error(['message' => $result['error']]);
        }

        wp_send_json_success([
            'message'  => __('Mot de passe réinitialisé. Vous pouvez vous connecter.', 'wwc-shop'),
            'redirect' => home_url('/connexion/'),
        ]);
    }
}
