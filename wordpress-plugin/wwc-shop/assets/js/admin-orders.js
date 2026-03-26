/**
 * WWC Shop Orders Admin JavaScript
 *
 * Handles AJAX update of order status and tracking number.
 *
 * @package WWC_Shop
 */

(function($) {
    'use strict';

    $(document).ready(function() {

        var $form    = $('#wwc-update-order-form');
        var $btn     = $('#wwc-update-order-btn');
        var $notice  = $('#wwc-order-notice');

        if (!$form.length) return;

        $form.on('submit', function(e) {
            e.preventDefault();

            var originalText = $btn.text();
            $btn.prop('disabled', true).text('...');
            $notice.hide().removeClass('success error');

            $.ajax({
                url:  wwcOrders.ajaxUrl,
                type: 'POST',
                data: {
                    action:          'wwc_admin_update_order',
                    nonce:           wwcOrders.nonce,
                    order_number:    $form.find('[name="order_number"]').val(),
                    status:          $form.find('[name="status"]').val(),
                    tracking_number: $form.find('[name="tracking_number"]').val()
                },
                success: function(response) {
                    if (response.success) {
                        $notice
                            .addClass('success')
                            .text(response.data.message || wwcOrders.i18n.updateSuccess)
                            .show();
                    } else {
                        var msg = (response.data && response.data.message)
                            ? response.data.message
                            : wwcOrders.i18n.updateError;
                        $notice.addClass('error').text(msg).show();
                    }
                },
                error: function() {
                    $notice.addClass('error').text(wwcOrders.i18n.updateError).show();
                },
                complete: function() {
                    $btn.prop('disabled', false).text(originalText);
                    $('html, body').animate({ scrollTop: $notice.offset().top - 60 }, 300);
                }
            });
        });

    });

})(jQuery);
