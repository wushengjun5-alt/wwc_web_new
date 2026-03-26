/**
 * WWC Shop Product JavaScript
 *
 * Handles product page interactions
 *
 * @package WWC_Shop
 */

(function($) {
    'use strict';

    const WWC_Product = {

        /**
         * Initialize product functionality
         */
        init: function() {
            this.initQuantitySelector();
            this.initGallery();
            this.initAccordions();
            this.initShare();
            this.initWishlist();
            this.initReviewForm();
        },

        /**
         * Initialize quantity selector
         */
        initQuantitySelector: function() {
            const $container = $('.wwc-product-detail .wwc-quantity-selector');

            if (!$container.length) return;

            const $input = $container.find('.wwc-qty-input');
            const $minus = $container.find('.wwc-qty-minus');
            const $plus = $container.find('.wwc-qty-plus');
            const min = parseInt($input.attr('min')) || 1;
            const max = parseInt($input.attr('max')) || 99;

            $minus.on('click', function() {
                const currentVal = parseInt($input.val()) || 1;
                if (currentVal > min) {
                    $input.val(currentVal - 1);
                }
            });

            $plus.on('click', function() {
                const currentVal = parseInt($input.val()) || 1;
                if (currentVal < max) {
                    $input.val(currentVal + 1);
                }
            });

            // Validate on change
            $input.on('change', function() {
                let val = parseInt($(this).val()) || min;
                val = Math.max(min, Math.min(max, val));
                $(this).val(val);
            });
        },

        /**
         * Initialize image gallery
         */
        initGallery: function() {
            const $mainImage = $('#wwc-main-image');
            const $thumbnails = $('.wwc-thumbnail');

            if (!$mainImage.length || !$thumbnails.length) return;

            $thumbnails.on('click', function() {
                const newSrc = $(this).data('image');

                // Fade effect
                $mainImage.fadeOut(150, function() {
                    $mainImage.attr('src', newSrc).fadeIn(150);
                });

                // Update active state
                $thumbnails.removeClass('active');
                $(this).addClass('active');
            });
        },

        /**
         * Initialize accordions
         */
        initAccordions: function() {
            $('.wwc-accordion-header').on('click', function() {
                const $accordion = $(this).closest('.wwc-accordion');
                const $content = $accordion.find('.wwc-accordion-content');

                // Toggle current
                $accordion.toggleClass('active');

                if ($accordion.hasClass('active')) {
                    $content.css('max-height', $content[0].scrollHeight + 'px');
                } else {
                    $content.css('max-height', 0);
                }
            });
        },

        /**
         * Initialize share functionality
         */
        initShare: function() {
            $('.wwc-share').on('click', function() {
                const url = window.location.href;
                const title = document.title;

                // Check for native share API
                if (navigator.share) {
                    navigator.share({
                        title: title,
                        url: url
                    }).catch(function() {});
                } else {
                    // Fallback: copy to clipboard
                    const tempInput = document.createElement('input');
                    document.body.appendChild(tempInput);
                    tempInput.value = url;
                    tempInput.select();
                    document.execCommand('copy');
                    document.body.removeChild(tempInput);

                    // Show notification
                    if (window.WWC_Cart) {
                        window.WWC_Cart.showNotification('Lien copié!', 'success');
                    }
                }
            });
        },

        /**
         * Initialize wishlist functionality
         */
        initWishlist: function() {
            $(document).on('click', '.wwc-wishlist', function() {
                const $button = $(this);
                const productId = $button.data('product-id');

                if ($button.prop('disabled')) return;
                $button.prop('disabled', true);

                $.ajax({
                    url: wwcShop.ajaxUrl,
                    type: 'POST',
                    data: {
                        action: 'wwc_toggle_wishlist',
                        nonce: wwcShop.nonce,
                        product_id: productId
                    },
                    success: function(response) {
                        if (response.success) {
                            const $icon = $button.find('.wwc-icon');
                            $icon.text(response.data.in_wishlist ? '❤️' : '🤍');
                            if (window.WWC_Cart) {
                                WWC_Cart.showNotification(response.data.message, 'success');
                            }
                        } else {
                            // Not logged in or error
                            if (window.WWC_Cart) {
                                const msg = (response.data && response.data.message)
                                    ? response.data.message
                                    : wwcShop.i18n.error;
                                WWC_Cart.showNotification(msg, 'error');
                            }
                        }
                    },
                    error: function() {
                        if (window.WWC_Cart) {
                            WWC_Cart.showNotification(wwcShop.i18n.error, 'error');
                        }
                    },
                    complete: function() {
                        $button.prop('disabled', false);
                    }
                });
            });
        },

        /**
         * Initialize review form submission
         */
        initReviewForm: function() {
            $(document).on('submit', '#wwc-review-form', function(e) {
                e.preventDefault();
                const $form = $(this);
                const $btn = $form.find('#wwc-review-submit');
                const $msg = $('#wwc-review-message');
                const originalText = $btn.text();

                $btn.prop('disabled', true).text('...');

                $.ajax({
                    url: wwcShop.ajaxUrl,
                    type: 'POST',
                    data: {
                        action: 'wwc_add_review',
                        nonce: wwcShop.nonce,
                        product_slug: $form.data('product-slug'),
                        rating: $form.find('input[name="rating"]:checked').val(),
                        comment: $form.find('textarea[name="comment"]').val()
                    },
                    success: function(response) {
                        if (response.success) {
                            $msg.removeClass('wwc-message--error')
                                .addClass('wwc-message--success')
                                .text(response.data.message).show();
                            $form[0].reset();
                            // Reset star display
                            $form.find('.wwc-star-label').css('color', '#ccc');
                        } else {
                            const msg = (response.data && response.data.message)
                                ? response.data.message : wwcShop.i18n.error;
                            $msg.removeClass('wwc-message--success')
                                .addClass('wwc-message--error')
                                .text(msg).show();
                        }
                    },
                    error: function() {
                        $msg.removeClass('wwc-message--success')
                            .addClass('wwc-message--error')
                            .text(wwcShop.i18n.error).show();
                    },
                    complete: function() {
                        $btn.prop('disabled', false).text(originalText);
                    }
                });
            });

            // Star rating hover/click interaction
            $(document).on('change', '#wwc-review-form input[name="rating"]', function() {
                const val = parseInt($(this).val());
                $(this).closest('form').find('.wwc-star-label').each(function(i) {
                    $(this).css('color', i < val ? '#f4b400' : '#ccc');
                });
            });
        }
    };

    // Initialize when document is ready
    $(document).ready(function() {
        WWC_Product.init();
    });

})(jQuery);
