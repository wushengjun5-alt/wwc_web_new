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
            $('.wwc-wishlist').on('click', function() {
                const $button = $(this);
                const productId = $button.data('product-id');

                // Toggle heart icon
                const $icon = $button.find('.wwc-icon');
                if ($icon.text() === '🤍') {
                    $icon.text('❤️');
                    // TODO: Add to wishlist API call
                } else {
                    $icon.text('🤍');
                    // TODO: Remove from wishlist API call
                }
            });
        }
    };

    // Initialize when document is ready
    $(document).ready(function() {
        WWC_Product.init();
    });

})(jQuery);
