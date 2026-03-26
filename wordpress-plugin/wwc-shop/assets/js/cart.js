/**
 * WWC Shop Cart JavaScript
 *
 * Handles cart operations and AJAX requests
 *
 * @package WWC_Shop
 */

(function($) {
    'use strict';

    const WWC_Cart = {

        // Cache DOM elements
        $sidebar: null,
        $overlay: null,
        $content: null,
        $footer: null,

        /**
         * Initialize cart functionality
         */
        init: function() {
            this.cacheElements();
            this.bindEvents();
            this.loadCart();
        },

        /**
         * Cache DOM elements
         */
        cacheElements: function() {
            this.$sidebar = $('#wwc-cart-sidebar');
            this.$overlay = $('#wwc-cart-overlay');
            this.$content = $('#wwc-cart-content');
            this.$footer = $('#wwc-cart-footer');
        },

        /**
         * Bind event handlers
         */
        bindEvents: function() {
            // Add to cart buttons
            $(document).on('click', '.wwc-add-to-cart, .wwc-quick-add', this.handleAddToCart.bind(this));

            // Checkout form
            $(document).on('submit', '#wwc-checkout-form', this.handleCheckout.bind(this));

            // Cart sidebar toggle
            $(document).on('click', '.wwc-cart-toggle, [data-action="open-cart"]', this.openSidebar.bind(this));
            $(document).on('click', '#wwc-cart-close, #wwc-cart-overlay', this.closeSidebar.bind(this));

            // Cart item quantity
            $(document).on('click', '.wwc-cart-item .wwc-qty-minus', this.handleQuantityMinus.bind(this));
            $(document).on('click', '.wwc-cart-item .wwc-qty-plus', this.handleQuantityPlus.bind(this));

            // Remove item
            $(document).on('click', '.wwc-cart-item-remove', this.handleRemoveItem.bind(this));

            // Escape key closes sidebar
            $(document).on('keydown', function(e) {
                if (e.key === 'Escape' && this.$sidebar.hasClass('open')) {
                    this.closeSidebar();
                }
            }.bind(this));
        },

        /**
         * Load cart data
         */
        loadCart: function() {
            $.ajax({
                url: wwcShop.ajaxUrl,
                type: 'POST',
                data: {
                    action: 'wwc_get_cart',
                    nonce: wwcShop.nonce
                },
                success: function(response) {
                    if (response.success) {
                        this.updateCartDisplay(response.data.cart);
                        this.updateCartCount(response.data.cart_count);
                    }
                }.bind(this)
            });
        },

        /**
         * Handle add to cart
         */
        handleAddToCart: function(e) {
            e.preventDefault();

            const $button = $(e.currentTarget);
            const productId = $button.data('product-id');
            let quantity = 1;

            // Check for quantity input on product detail page
            const $qtyInput = $('#wwc-product-quantity');
            if ($qtyInput.length) {
                quantity = parseInt($qtyInput.val()) || 1;
            }

            // Disable button and show loading
            const originalText = $button.text();
            $button.prop('disabled', true).text('...');

            $.ajax({
                url: wwcShop.ajaxUrl,
                type: 'POST',
                data: {
                    action: 'wwc_add_to_cart',
                    nonce: wwcShop.nonce,
                    product_id: productId,
                    quantity: quantity
                },
                success: function(response) {
                    if (response.success) {
                        this.updateCartDisplay(response.data.cart);
                        this.updateCartCount(response.data.cart_count);
                        this.showNotification(response.data.message, 'success');
                        this.openSidebar();
                    } else {
                        if (response.data && response.data.debug) {
                            console.error('[WWC Cart] Add-to-cart error debug:', response.data.debug);
                        }
                        this.showNotification(response.data.message || wwcShop.i18n.error, 'error');
                    }
                }.bind(this),
                error: function(xhr, status, error) {
                    console.error('[WWC Cart] AJAX error:', status, error, xhr.responseText);
                    this.showNotification(wwcShop.i18n.error, 'error');
                }.bind(this),
                complete: function() {
                    $button.prop('disabled', false).text(originalText);
                }
            });
        },

        /**
         * Handle quantity minus
         */
        handleQuantityMinus: function(e) {
            const $button = $(e.currentTarget);
            const itemId = $button.data('item-id');
            const $qty = $button.siblings('.wwc-cart-item-qty');
            const currentQty = parseInt($qty.text()) || 1;

            if (currentQty > 1) {
                this.updateCartItem(itemId, currentQty - 1);
            } else {
                this.removeCartItem(itemId);
            }
        },

        /**
         * Handle quantity plus
         */
        handleQuantityPlus: function(e) {
            const $button = $(e.currentTarget);
            const itemId = $button.data('item-id');
            const $qty = $button.siblings('.wwc-cart-item-qty');
            const currentQty = parseInt($qty.text()) || 1;

            this.updateCartItem(itemId, currentQty + 1);
        },

        /**
         * Handle remove item
         */
        handleRemoveItem: function(e) {
            const $button = $(e.currentTarget);
            const itemId = $button.data('item-id');

            this.removeCartItem(itemId);
        },

        /**
         * Update cart item quantity
         */
        updateCartItem: function(itemId, quantity) {
            $.ajax({
                url: wwcShop.ajaxUrl,
                type: 'POST',
                data: {
                    action: 'wwc_update_cart',
                    nonce: wwcShop.nonce,
                    item_id: itemId,
                    quantity: quantity
                },
                success: function(response) {
                    if (response.success) {
                        this.updateCartDisplay(response.data.cart);
                        this.updateCartCount(response.data.cart_count);
                    } else {
                        this.showNotification(response.data.message || wwcShop.i18n.error, 'error');
                    }
                }.bind(this)
            });
        },

        /**
         * Remove cart item
         */
        removeCartItem: function(itemId) {
            $.ajax({
                url: wwcShop.ajaxUrl,
                type: 'POST',
                data: {
                    action: 'wwc_remove_from_cart',
                    nonce: wwcShop.nonce,
                    item_id: itemId
                },
                success: function(response) {
                    if (response.success) {
                        this.updateCartDisplay(response.data.cart);
                        this.updateCartCount(response.data.cart_count);
                        this.showNotification(wwcShop.i18n.removedFromCart, 'success');
                    } else {
                        this.showNotification(response.data.message || wwcShop.i18n.error, 'error');
                    }
                }.bind(this)
            });
        },

        /**
         * Handle checkout form submission
         */
        handleCheckout: function(e) {
            e.preventDefault();

            const $form = $(e.currentTarget);
            const $btn = $form.find('.wwc-btn-checkout');
            const originalText = $btn.text();

            // Collect all form fields
            const data = {
                action: 'wwc_checkout',
                nonce: wwcShop.nonce
            };
            $form.serializeArray().forEach(function(field) {
                data[field.name] = field.value;
            });

            $btn.prop('disabled', true).text('...');

            $.ajax({
                url: wwcShop.ajaxUrl,
                type: 'POST',
                data: data,
                success: function(response) {
                    if (response.success) {
                        if (response.data.redirect && response.data.checkout_url) {
                            // Stripe hosted checkout
                            window.location.href = response.data.checkout_url;
                        } else if (response.data.redirect_url) {
                            window.location.href = response.data.redirect_url;
                        }
                    } else {
                        const msg = (response.data && response.data.message)
                            ? response.data.message
                            : wwcShop.i18n.error;
                        this.showNotification(msg, 'error');
                        $btn.prop('disabled', false).text(originalText);
                    }
                }.bind(this),
                error: function() {
                    this.showNotification(wwcShop.i18n.error, 'error');
                    $btn.prop('disabled', false).text(originalText);
                }.bind(this)
            });
        },

        /**
         * Update cart display
         */
        updateCartDisplay: function(cart) {
            if (!cart || !cart.items || cart.items.length === 0) {
                this.showEmptyCart();
                return;
            }

            const template = $('#wwc-cart-item-template').html();
            let itemsHtml = '';

            cart.items.forEach(function(item) {
                let itemHtml = template
                    .replace(/\{\{id\}\}/g, item.id)
                    .replace(/\{\{name\}\}/g, item.product.name)
                    .replace(/\{\{price\}\}/g, item.subtotal + ' DT')
                    .replace(/\{\{quantity\}\}/g, item.quantity)
                    .replace(/\{\{image\}\}/g, item.product.primary_image ?
                        item.product.primary_image.image : '');

                itemsHtml += itemHtml;
            });

            this.$content.html(itemsHtml);

            // Update totals
            $('#wwc-cart-subtotal-amount').text(cart.total + ' DT');

            // Update impact summary
            if (cart.total_impact && Object.keys(cart.total_impact).length > 0) {
                let impactHtml = '<div class="wwc-cart-impact-header">💝 Votre impact</div>';
                for (const [item, qty] of Object.entries(cart.total_impact)) {
                    impactHtml += `<div>${qty} ${item}</div>`;
                }
                $('#wwc-cart-impact-summary').html(impactHtml);
            }

            this.$footer.show();
        },

        /**
         * Show empty cart
         */
        showEmptyCart: function() {
            const template = $('#wwc-cart-empty-template').html();
            this.$content.html(template);
            this.$footer.hide();
        },

        /**
         * Update cart count in header
         */
        updateCartCount: function(count) {
            $('.wwc-cart-count').text(count);

            // Update any cart icons
            if (count > 0) {
                $('.wwc-cart-count').addClass('has-items');
            } else {
                $('.wwc-cart-count').removeClass('has-items');
            }
        },

        /**
         * Open cart sidebar
         */
        openSidebar: function(e) {
            if (e) e.preventDefault();

            this.$sidebar.addClass('open');
            this.$overlay.addClass('open');
            $('body').addClass('wwc-cart-open');
        },

        /**
         * Close cart sidebar
         */
        closeSidebar: function(e) {
            if (e) e.preventDefault();

            this.$sidebar.removeClass('open');
            this.$overlay.removeClass('open');
            $('body').removeClass('wwc-cart-open');
        },

        /**
         * Show notification
         */
        showNotification: function(message, type) {
            const $notification = $('<div class="wwc-notification wwc-notification-' + type + '">')
                .text(message)
                .appendTo('body');

            setTimeout(function() {
                $notification.addClass('show');
            }, 100);

            setTimeout(function() {
                $notification.removeClass('show');
                setTimeout(function() {
                    $notification.remove();
                }, 300);
            }, 3000);
        }
    };

    // Initialize when document is ready
    $(document).ready(function() {
        WWC_Cart.init();
        WWC_LangSwitcher.init();
    });

    // Expose to global scope
    window.WWC_Cart = WWC_Cart;

    // ============================================
    // Language Switcher
    // ============================================

    const WWC_LangSwitcher = {

        init: function() {
            const $switcher = $('#wwc-lang-switcher');
            if (!$switcher.length) return;

            // Set initial RTL state
            this.applyLang(wwcShop.lang || 'fr');

            // Toggle dropdown
            $switcher.on('click', '.wwc-lang-current', function() {
                const $btn = $(this);
                const expanded = $btn.attr('aria-expanded') === 'true';
                $btn.attr('aria-expanded', !expanded);
                $switcher.toggleClass('open');
            });

            // Close on outside click
            $(document).on('click', function(e) {
                if (!$(e.target).closest('#wwc-lang-switcher').length) {
                    $switcher.removeClass('open');
                    $switcher.find('.wwc-lang-current').attr('aria-expanded', 'false');
                }
            });

            // Language option click
            $(document).on('click', '.wwc-lang-option', function() {
                const lang = $(this).data('lang');
                WWC_LangSwitcher.setLang(lang);
            });
        },

        setLang: function(lang) {
            console.log('[WWC Lang] switching to:', lang);

            // Set cookie directly in JS
            var expires = new Date();
            expires.setFullYear(expires.getFullYear() + 1);
            document.cookie = 'wwc_lang=' + encodeURIComponent(lang)
                + '; expires=' + expires.toUTCString()
                + '; path=/; SameSite=Lax';

            console.log('[WWC Lang] cookie set, document.cookie now:', document.cookie);

            // Fire-and-forget AJAX to sync preferred_language on customer profile
            $.post(wwcShop.ajaxUrl, {
                action: 'wwc_set_language',
                nonce: wwcShop.nonce,
                lang: lang
            });

            // Reload — PHP will read the new cookie
            window.location.reload();
        },

        applyLang: function(lang) {
            // Set RTL for Arabic
            if (lang === 'ar') {
                $('html').attr('dir', 'rtl').attr('lang', 'ar');
                $('body').addClass('wwc-rtl');
            } else {
                $('html').removeAttr('dir').attr('lang', lang);
                $('body').removeClass('wwc-rtl');
            }
        }
    };

    window.WWC_LangSwitcher = WWC_LangSwitcher;

    // Debug helper: run this in the browser console to test the API connection:
    // jQuery.post(wwcShop.ajaxUrl, {action:'wwc_debug_api'}).then(r => console.table(r))
    window.wwcDebugApi = function() {
        jQuery.post(wwcShop.ajaxUrl, {action: 'wwc_debug_api'})
            .then(function(r) { console.log('[WWC Debug]', r); console.table(r); })
            .fail(function(x) { console.error('[WWC Debug] AJAX fail:', x.responseText); });
    };

})(jQuery);
