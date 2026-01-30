/**
 * WWC Shop Products Admin JavaScript
 */

(function($) {
    'use strict';

    // Localized data
    const config = window.wwcAdminProducts || {};

    /**
     * Products List Page
     */
    const ProductsList = {
        init: function() {
            this.bindEvents();
        },

        bindEvents: function() {
            // Select all checkbox
            $('#wwc-select-all').on('change', this.selectAll);

            // Individual checkboxes
            $('.wwc-product-checkbox').on('change', this.updateSelectedCount);

            // Bulk action
            $('#wwc-bulk-apply').on('click', this.applyBulkAction);

            // Delete single product
            $('.wwc-delete-product').on('click', this.deleteProduct);

            // Duplicate product
            $('.wwc-duplicate-product').on('click', this.duplicateProduct);
        },

        selectAll: function() {
            const isChecked = $(this).prop('checked');
            $('.wwc-product-checkbox').prop('checked', isChecked);
            ProductsList.updateSelectedCount();
        },

        updateSelectedCount: function() {
            const count = $('.wwc-product-checkbox:checked').length;
            if (count > 0) {
                $('.wwc-selected-count').text(count + ' ' + (count === 1 ? 'selected' : 'selected'));
            } else {
                $('.wwc-selected-count').text('');
            }
        },

        applyBulkAction: function() {
            const action = $('#wwc-bulk-action').val();
            const productIds = $('.wwc-product-checkbox:checked').map(function() {
                return $(this).val();
            }).get();

            if (!action) {
                alert('Please select an action');
                return;
            }

            if (productIds.length === 0) {
                alert('Please select at least one product');
                return;
            }

            if (action === 'delete' && !confirm(config.i18n.confirmBulkDelete)) {
                return;
            }

            $.ajax({
                url: config.ajaxUrl,
                type: 'POST',
                data: {
                    action: 'wwc_admin_bulk_action',
                    nonce: config.nonce,
                    bulk_action: action,
                    product_ids: productIds
                },
                success: function(response) {
                    if (response.success) {
                        location.reload();
                    } else {
                        alert(response.data.message || config.i18n.error);
                    }
                },
                error: function() {
                    alert(config.i18n.error);
                }
            });
        },

        deleteProduct: function(e) {
            e.preventDefault();

            if (!confirm(config.i18n.confirmDelete)) {
                return;
            }

            const productId = $(this).data('id');
            const $row = $(this).closest('tr');

            $.ajax({
                url: config.ajaxUrl,
                type: 'POST',
                data: {
                    action: 'wwc_admin_delete_product',
                    nonce: config.nonce,
                    product_id: productId
                },
                success: function(response) {
                    if (response.success) {
                        $row.fadeOut(300, function() {
                            $(this).remove();
                        });
                    } else {
                        alert(response.data.message || config.i18n.error);
                    }
                },
                error: function() {
                    alert(config.i18n.error);
                }
            });
        },

        duplicateProduct: function(e) {
            e.preventDefault();

            const productId = $(this).data('id');

            $.ajax({
                url: config.ajaxUrl,
                type: 'POST',
                data: {
                    action: 'wwc_admin_duplicate_product',
                    nonce: config.nonce,
                    product_id: productId
                },
                success: function(response) {
                    if (response.success) {
                        // Redirect to edit the new product
                        window.location.href = config.editUrl + '&id=' + response.data.product.id;
                    } else {
                        alert(response.data.message || config.i18n.error);
                    }
                },
                error: function() {
                    alert(config.i18n.error);
                }
            });
        }
    };

    /**
     * Product Edit Page
     */
    const ProductEdit = {
        init: function() {
            this.bindEvents();
            this.initMediaUploader();
            this.updateImpactPreview();
        },

        bindEvents: function() {
            // Language tabs
            $('.wwc-lang-tab').on('click', this.switchLanguageTab);

            // Form submission
            $('#wwc-product-form').on('submit', this.saveProduct);

            // Impact preview update
            $('#impact_quantity, #impact_item, #impact_school').on('input', this.updateImpactPreview);

            // Image actions
            $(document).on('click', '.wwc-delete-image', this.deleteImage);
            $(document).on('click', '.wwc-set-primary', this.setPrimaryImage);
        },

        switchLanguageTab: function(e) {
            e.preventDefault();

            const lang = $(this).data('lang');

            // Update tabs
            $('.wwc-lang-tab').removeClass('active');
            $(this).addClass('active');

            // Update content
            $('.wwc-lang-content').removeClass('active');
            $(`.wwc-lang-content[data-lang="${lang}"]`).addClass('active');
        },

        saveProduct: function(e) {
            e.preventDefault();

            const $form = $(this);
            const $submitBtn = $('#save-product');
            const $spinner = $form.find('.spinner');

            // Validate required fields
            const name = $form.find('#name').val().trim();
            const category = $form.find('#category').val();
            const priceTnd = $form.find('#price_tnd').val();

            if (!name) {
                alert(config.i18n.frRequired);
                $form.find('#name').focus();
                return;
            }

            if (!category) {
                alert(config.i18n.categoryRequired);
                $form.find('#category').focus();
                return;
            }

            if (!priceTnd) {
                alert(config.i18n.priceRequired);
                $form.find('#price_tnd').focus();
                return;
            }

            // Sync TinyMCE editors
            if (typeof tinyMCE !== 'undefined') {
                tinyMCE.triggerSave();
            }

            // Disable button and show spinner
            $submitBtn.prop('disabled', true).text(config.i18n.saving);
            $spinner.addClass('is-active');

            // Collect form data
            const formData = new FormData($form[0]);
            formData.append('action', 'wwc_admin_save_product');
            formData.append('nonce', config.nonce);

            $.ajax({
                url: config.ajaxUrl,
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function(response) {
                    if (response.success) {
                        // Show success message
                        ProductEdit.showNotice('success', config.i18n.saved);

                        // If new product, redirect to edit page
                        if (!$form.find('[name="product_id"]').val()) {
                            window.location.href = config.editUrl + '&id=' + response.data.product.id;
                        } else {
                            // Update product ID if needed
                            $form.find('[name="product_id"]').val(response.data.product.id);
                        }
                    } else {
                        ProductEdit.showNotice('error', response.data.message || config.i18n.error);

                        // Show field-specific errors
                        if (response.data.errors) {
                            ProductEdit.showFieldErrors(response.data.errors);
                        }
                    }
                },
                error: function() {
                    ProductEdit.showNotice('error', config.i18n.error);
                },
                complete: function() {
                    $submitBtn.prop('disabled', false).text($form.find('[name="product_id"]').val() ? 'Update Product' : 'Create Product');
                    $spinner.removeClass('is-active');
                }
            });
        },

        showNotice: function(type, message) {
            // Remove existing notices
            $('.wwc-notice').remove();

            // Create notice
            const $notice = $('<div class="wwc-notice wwc-notice-' + type + '">' + message + '</div>');
            $('.wp-heading-inline').after($notice);

            // Auto-hide success notices
            if (type === 'success') {
                setTimeout(function() {
                    $notice.fadeOut(300, function() {
                        $(this).remove();
                    });
                }, 3000);
            }

            // Scroll to top
            $('html, body').animate({ scrollTop: 0 }, 300);
        },

        showFieldErrors: function(errors) {
            // Clear previous errors
            $('.wwc-field-error').remove();
            $('.wwc-form-group input, .wwc-form-group select').removeClass('wwc-input-error');

            // Show new errors
            Object.keys(errors).forEach(function(field) {
                const $field = $('[name="product[' + field + ']"]');
                if ($field.length) {
                    $field.addClass('wwc-input-error');
                    $field.after('<span class="wwc-field-error">' + errors[field].join(', ') + '</span>');
                }
            });
        },

        updateImpactPreview: function() {
            const quantity = $('#impact_quantity').val();
            const item = $('#impact_item').val();
            const school = $('#impact_school').val();

            if (quantity && item && school) {
                $('#impact-preview-text').html('💝 ' + quantity + ' ' + item + ' pour ' + school);
            } else {
                $('#impact-preview-text').text('Fill in the fields above to see the impact preview');
            }
        },

        initMediaUploader: function() {
            let mediaUploader;

            $('#upload-images-btn').on('click', function(e) {
                e.preventDefault();

                const productId = $('[name="product_id"]').val();

                if (!productId) {
                    alert('Please save the product first before uploading images.');
                    return;
                }

                // If the uploader exists, reopen it
                if (mediaUploader) {
                    mediaUploader.open();
                    return;
                }

                // Create the media uploader
                mediaUploader = wp.media({
                    title: config.i18n.selectImage,
                    button: {
                        text: config.i18n.useImage
                    },
                    multiple: true
                });

                // When images are selected
                mediaUploader.on('select', function() {
                    const attachments = mediaUploader.state().get('selection').toJSON();

                    attachments.forEach(function(attachment) {
                        ProductEdit.uploadImageToAPI(productId, attachment);
                    });
                });

                mediaUploader.open();
            });
        },

        uploadImageToAPI: function(productId, attachment) {
            // Create a form data with the image
            const formData = new FormData();
            formData.append('action', 'wwc_admin_upload_image');
            formData.append('nonce', config.nonce);
            formData.append('product_id', productId);
            formData.append('alt_text', attachment.alt || attachment.title || '');

            // Fetch the image blob
            fetch(attachment.url)
                .then(response => response.blob())
                .then(blob => {
                    formData.append('image', blob, attachment.filename);

                    $.ajax({
                        url: config.ajaxUrl,
                        type: 'POST',
                        data: formData,
                        processData: false,
                        contentType: false,
                        success: function(response) {
                            if (response.success) {
                                ProductEdit.addImageToGrid(response.data.image);
                            } else {
                                alert(response.data.message || config.i18n.uploadError);
                            }
                        },
                        error: function() {
                            alert(config.i18n.uploadError);
                        }
                    });
                });
        },

        addImageToGrid: function(image) {
            const imageUrl = image.image_url || image.image;
            const isPrimary = image.is_primary ? 'wwc-image-primary' : '';
            const primaryBadge = image.is_primary ? '<span class="wwc-primary-badge">Primary</span>' : '';

            const $imageItem = $(`
                <div class="wwc-image-item ${isPrimary}" data-image-id="${image.id}">
                    <img src="${imageUrl}" alt="">
                    <div class="wwc-image-actions">
                        <button type="button" class="wwc-set-primary" title="Set as primary">★</button>
                        <button type="button" class="wwc-delete-image" title="Delete">×</button>
                    </div>
                    ${primaryBadge}
                </div>
            `);

            $('#product-images').append($imageItem);
        },

        deleteImage: function(e) {
            e.preventDefault();

            const $item = $(this).closest('.wwc-image-item');
            const imageId = $item.data('image-id');
            const productId = $('[name="product_id"]').val();

            $.ajax({
                url: config.ajaxUrl,
                type: 'POST',
                data: {
                    action: 'wwc_admin_delete_image',
                    nonce: config.nonce,
                    product_id: productId,
                    image_id: imageId
                },
                success: function(response) {
                    if (response.success) {
                        $item.fadeOut(300, function() {
                            $(this).remove();
                        });
                    } else {
                        alert(response.data.message || config.i18n.error);
                    }
                },
                error: function() {
                    alert(config.i18n.error);
                }
            });
        },

        setPrimaryImage: function(e) {
            e.preventDefault();

            const $item = $(this).closest('.wwc-image-item');
            const imageId = $item.data('image-id');
            const productId = $('[name="product_id"]').val();

            $.ajax({
                url: config.ajaxUrl,
                type: 'POST',
                data: {
                    action: 'wwc_admin_set_primary_image',
                    nonce: config.nonce,
                    product_id: productId,
                    image_id: imageId
                },
                success: function(response) {
                    if (response.success) {
                        // Update UI
                        $('.wwc-image-item').removeClass('wwc-image-primary');
                        $('.wwc-primary-badge').remove();
                        $item.addClass('wwc-image-primary');
                        $item.append('<span class="wwc-primary-badge">Primary</span>');
                    } else {
                        alert(response.data.message || config.i18n.error);
                    }
                },
                error: function() {
                    alert(config.i18n.error);
                }
            });
        }
    };

    // Initialize on document ready
    $(document).ready(function() {
        // Check which page we're on
        if ($('.wwc-products-admin').length) {
            ProductsList.init();
        }

        if ($('.wwc-product-edit').length) {
            ProductEdit.init();
        }
    });

})(jQuery);
