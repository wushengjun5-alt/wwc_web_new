<?php
/**
 * Product Edit Admin Page
 *
 * @package WWC_Shop
 */

defined('ABSPATH') || exit;

$is_new = empty($product);
$categories_list = is_wp_error($categories) ? [] : $categories;
$producers_list = is_wp_error($producers) ? [] : $producers;
$page_title = $is_new ? __('Add New Product', 'wwc-shop') : __('Edit Product', 'wwc-shop');
?>

<div class="wrap wwc-product-edit">
    <h1 class="wp-heading-inline"><?php echo esc_html($page_title); ?></h1>
    <a href="<?php echo esc_url(admin_url('admin.php?page=wwc-products')); ?>" class="page-title-action">
        <?php _e('Back to Products', 'wwc-shop'); ?>
    </a>
    <hr class="wp-header-end">

    <form id="wwc-product-form" class="wwc-product-form">
        <input type="hidden" name="product_id" value="<?php echo esc_attr($product['id'] ?? ''); ?>">

        <div class="wwc-form-layout">
            <!-- Main Content -->
            <div class="wwc-form-main">
                <!-- Basic Info -->
                <div class="wwc-form-section">
                    <h2><?php _e('Basic Information', 'wwc-shop'); ?></h2>

                    <div class="wwc-form-row">
                        <div class="wwc-form-group wwc-form-group-wide">
                            <label for="name">
                                <?php _e('Product Name (French)', 'wwc-shop'); ?>
                                <span class="required">*</span>
                            </label>
                            <input type="text" id="name" name="product[name]"
                                   value="<?php echo esc_attr($product['name'] ?? ''); ?>"
                                   placeholder="<?php esc_attr_e('Enter product name in French', 'wwc-shop'); ?>"
                                   required>
                        </div>
                    </div>

                    <div class="wwc-form-row">
                        <div class="wwc-form-group">
                            <label for="slug"><?php _e('Slug (URL)', 'wwc-shop'); ?></label>
                            <input type="text" id="slug" name="product[slug]"
                                   value="<?php echo esc_attr($product['slug'] ?? ''); ?>"
                                   placeholder="<?php esc_attr_e('auto-generated', 'wwc-shop'); ?>">
                            <p class="description"><?php _e('Leave empty to auto-generate from name', 'wwc-shop'); ?></p>
                        </div>
                        <div class="wwc-form-group">
                            <label for="sku">
                                <?php _e('SKU', 'wwc-shop'); ?>
                                <span class="required">*</span>
                            </label>
                            <input type="text" id="sku" name="product[sku]"
                                   value="<?php echo esc_attr($product['sku'] ?? ''); ?>"
                                   placeholder="<?php esc_attr_e('PROD-XXXXX', 'wwc-shop'); ?>">
                            <p class="description"><?php _e('Unique product identifier', 'wwc-shop'); ?></p>
                        </div>
                    </div>

                    <div class="wwc-form-row">
                        <div class="wwc-form-group wwc-form-group-wide">
                            <label for="short_description"><?php _e('Short Description', 'wwc-shop'); ?></label>
                            <input type="text" id="short_description" name="product[short_description]"
                                   value="<?php echo esc_attr($product['short_description'] ?? ''); ?>"
                                   maxlength="300"
                                   placeholder="<?php esc_attr_e('Brief description for product listings (max 300 chars)', 'wwc-shop'); ?>">
                        </div>
                    </div>
                </div>

                <!-- Descriptions with Language Tabs -->
                <div class="wwc-form-section">
                    <h2><?php _e('Descriptions', 'wwc-shop'); ?></h2>

                    <div class="wwc-lang-tabs">
                        <button type="button" class="wwc-lang-tab active" data-lang="fr">
                            🇫🇷 <?php _e('French', 'wwc-shop'); ?>
                        </button>
                        <button type="button" class="wwc-lang-tab" data-lang="en">
                            🇬🇧 <?php _e('English', 'wwc-shop'); ?>
                        </button>
                        <button type="button" class="wwc-lang-tab" data-lang="ar">
                            🇸🇦 <?php _e('Arabic', 'wwc-shop'); ?>
                        </button>
                    </div>

                    <!-- French -->
                    <div class="wwc-lang-content active" data-lang="fr">
                        <div class="wwc-form-group">
                            <label for="description"><?php _e('Full Description (French)', 'wwc-shop'); ?></label>
                            <?php
                            wp_editor(
                                $product['description'] ?? '',
                                'description',
                                [
                                    'textarea_name' => 'product[description]',
                                    'textarea_rows' => 10,
                                    'media_buttons' => false,
                                    'teeny' => true,
                                    'quicktags' => true,
                                ]
                            );
                            ?>
                        </div>
                        <div class="wwc-form-group">
                            <label for="ingredients"><?php _e('Ingredients (French)', 'wwc-shop'); ?></label>
                            <textarea id="ingredients" name="product[ingredients]" rows="4"><?php echo esc_textarea($product['ingredients'] ?? ''); ?></textarea>
                        </div>
                        <div class="wwc-form-group">
                            <label for="usage"><?php _e('Usage Instructions (French)', 'wwc-shop'); ?></label>
                            <textarea id="usage" name="product[usage]" rows="4"><?php echo esc_textarea($product['usage'] ?? ''); ?></textarea>
                        </div>
                    </div>

                    <!-- English -->
                    <div class="wwc-lang-content" data-lang="en">
                        <div class="wwc-form-group">
                            <label for="name_en"><?php _e('Product Name (English)', 'wwc-shop'); ?></label>
                            <input type="text" id="name_en" name="product[name_en]"
                                   value="<?php echo esc_attr($product['name_en'] ?? ''); ?>">
                        </div>
                        <div class="wwc-form-group">
                            <label for="description_en"><?php _e('Full Description (English)', 'wwc-shop'); ?></label>
                            <?php
                            wp_editor(
                                $product['description_en'] ?? '',
                                'description_en',
                                [
                                    'textarea_name' => 'product[description_en]',
                                    'textarea_rows' => 10,
                                    'media_buttons' => false,
                                    'teeny' => true,
                                    'quicktags' => true,
                                ]
                            );
                            ?>
                        </div>
                        <div class="wwc-form-group">
                            <label for="ingredients_en"><?php _e('Ingredients (English)', 'wwc-shop'); ?></label>
                            <textarea id="ingredients_en" name="product[ingredients_en]" rows="4"><?php echo esc_textarea($product['ingredients_en'] ?? ''); ?></textarea>
                        </div>
                        <div class="wwc-form-group">
                            <label for="usage_en"><?php _e('Usage Instructions (English)', 'wwc-shop'); ?></label>
                            <textarea id="usage_en" name="product[usage_en]" rows="4"><?php echo esc_textarea($product['usage_en'] ?? ''); ?></textarea>
                        </div>
                    </div>

                    <!-- Arabic -->
                    <div class="wwc-lang-content" data-lang="ar">
                        <div class="wwc-form-group">
                            <label for="name_ar"><?php _e('Product Name (Arabic)', 'wwc-shop'); ?></label>
                            <input type="text" id="name_ar" name="product[name_ar]" dir="rtl"
                                   value="<?php echo esc_attr($product['name_ar'] ?? ''); ?>">
                        </div>
                        <div class="wwc-form-group">
                            <label for="description_ar"><?php _e('Full Description (Arabic)', 'wwc-shop'); ?></label>
                            <?php
                            wp_editor(
                                $product['description_ar'] ?? '',
                                'description_ar',
                                [
                                    'textarea_name' => 'product[description_ar]',
                                    'textarea_rows' => 10,
                                    'media_buttons' => false,
                                    'teeny' => true,
                                    'quicktags' => true,
                                ]
                            );
                            ?>
                        </div>
                    </div>
                </div>

                <!-- Images -->
                <div class="wwc-form-section">
                    <h2><?php _e('Images', 'wwc-shop'); ?></h2>

                    <div class="wwc-images-container">
                        <div class="wwc-images-grid" id="product-images">
                            <?php if (!empty($product['images'])): ?>
                                <?php foreach ($product['images'] as $image): ?>
                                <div class="wwc-image-item <?php echo $image['is_primary'] ? 'wwc-image-primary' : ''; ?>"
                                     data-image-id="<?php echo esc_attr($image['id']); ?>">
                                    <img src="<?php echo esc_url($image['image_url'] ?? $image['image']); ?>" alt="">
                                    <div class="wwc-image-actions">
                                        <button type="button" class="wwc-set-primary" title="<?php esc_attr_e('Set as primary', 'wwc-shop'); ?>">★</button>
                                        <button type="button" class="wwc-delete-image" title="<?php esc_attr_e('Delete', 'wwc-shop'); ?>">×</button>
                                    </div>
                                    <?php if ($image['is_primary']): ?>
                                    <span class="wwc-primary-badge"><?php _e('Primary', 'wwc-shop'); ?></span>
                                    <?php endif; ?>
                                </div>
                                <?php endforeach; ?>
                            <?php endif; ?>
                        </div>

                        <div class="wwc-upload-area" id="upload-area">
                            <button type="button" id="upload-images-btn" class="button button-secondary">
                                <?php _e('Add Images', 'wwc-shop'); ?>
                            </button>
                            <p class="description"><?php _e('Click to upload or drag & drop images', 'wwc-shop'); ?></p>
                        </div>
                    </div>
                </div>

                <!-- Impact Section -->
                <div class="wwc-form-section wwc-impact-section">
                    <h2>💝 <?php _e('Social Impact', 'wwc-shop'); ?></h2>
                    <p class="section-description">
                        <?php _e('Define how this purchase supports GreenSchool students.', 'wwc-shop'); ?>
                    </p>

                    <div class="wwc-form-row">
                        <div class="wwc-form-group">
                            <label for="impact_quantity"><?php _e('Impact Quantity', 'wwc-shop'); ?></label>
                            <input type="number" id="impact_quantity" name="product[impact_quantity]"
                                   value="<?php echo esc_attr($product['impact_quantity'] ?? ''); ?>"
                                   min="0" step="1">
                            <p class="description"><?php _e('Number of items provided per purchase', 'wwc-shop'); ?></p>
                        </div>
                        <div class="wwc-form-group">
                            <label for="impact_item"><?php _e('Impact Item (French)', 'wwc-shop'); ?></label>
                            <input type="text" id="impact_item" name="product[impact_item]"
                                   value="<?php echo esc_attr($product['impact_item'] ?? ''); ?>"
                                   placeholder="<?php esc_attr_e('e.g., kits scolaires, repas, livres', 'wwc-shop'); ?>">
                        </div>
                        <div class="wwc-form-group">
                            <label for="impact_item_en"><?php _e('Impact Item (English)', 'wwc-shop'); ?></label>
                            <input type="text" id="impact_item_en" name="product[impact_item_en]"
                                   value="<?php echo esc_attr($product['impact_item_en'] ?? ''); ?>"
                                   placeholder="<?php esc_attr_e('e.g., school kits, meals, books', 'wwc-shop'); ?>">
                        </div>
                    </div>

                    <div class="wwc-form-row">
                        <div class="wwc-form-group wwc-form-group-wide">
                            <label for="impact_school"><?php _e('GreenSchool Name', 'wwc-shop'); ?></label>
                            <input type="text" id="impact_school" name="product[impact_school]"
                                   value="<?php echo esc_attr($product['impact_school'] ?? ''); ?>"
                                   placeholder="<?php esc_attr_e('e.g., GreenSchool Zaghouan', 'wwc-shop'); ?>">
                        </div>
                    </div>

                    <!-- Impact Preview -->
                    <div class="wwc-impact-preview" id="impact-preview">
                        <strong><?php _e('Preview:', 'wwc-shop'); ?></strong>
                        <div class="wwc-impact-preview-text">
                            <span id="impact-preview-text">
                                <?php
                                if (!empty($product['impact_quantity']) && !empty($product['impact_item']) && !empty($product['impact_school'])) {
                                    printf(
                                        __('💝 %d %s for %s', 'wwc-shop'),
                                        $product['impact_quantity'],
                                        $product['impact_item'],
                                        $product['impact_school']
                                    );
                                } else {
                                    _e('Fill in the fields above to see the impact preview', 'wwc-shop');
                                }
                                ?>
                            </span>
                        </div>
                    </div>

                    <div class="wwc-form-row">
                        <div class="wwc-form-group wwc-form-group-wide">
                            <label for="impact_description"><?php _e('Impact Description (French)', 'wwc-shop'); ?></label>
                            <textarea id="impact_description" name="product[impact_description]" rows="2"
                                      placeholder="<?php esc_attr_e('Full impact message shown to customers', 'wwc-shop'); ?>"><?php echo esc_textarea($product['impact_description'] ?? ''); ?></textarea>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Sidebar -->
            <div class="wwc-form-sidebar">
                <!-- Publish Box -->
                <div class="wwc-sidebar-box wwc-publish-box">
                    <h3><?php _e('Publish', 'wwc-shop'); ?></h3>
                    <div class="wwc-publish-content">
                        <div class="wwc-form-group">
                            <label>
                                <input type="checkbox" name="product[is_active]" value="1"
                                    <?php checked(!empty($product['is_active'])); ?>>
                                <?php _e('Published', 'wwc-shop'); ?>
                            </label>
                            <p class="description"><?php _e('Uncheck to save as draft', 'wwc-shop'); ?></p>
                        </div>
                        <div class="wwc-form-group">
                            <label>
                                <input type="checkbox" name="product[is_featured]" value="1"
                                    <?php checked(!empty($product['is_featured'])); ?>>
                                <?php _e('Featured product', 'wwc-shop'); ?>
                            </label>
                        </div>
                    </div>
                    <div class="wwc-publish-actions">
                        <button type="submit" id="save-product" class="button button-primary button-large">
                            <?php echo $is_new ? __('Create Product', 'wwc-shop') : __('Update Product', 'wwc-shop'); ?>
                        </button>
                        <span class="spinner"></span>
                    </div>
                </div>

                <!-- Category -->
                <div class="wwc-sidebar-box">
                    <h3><?php _e('Category', 'wwc-shop'); ?> <span class="required">*</span></h3>
                    <select name="product[category]" id="category" required>
                        <option value=""><?php _e('Select Category', 'wwc-shop'); ?></option>
                        <?php foreach ($categories_list as $cat): ?>
                        <option value="<?php echo esc_attr($cat['id']); ?>"
                            <?php selected(($product['category'] ?? '') == $cat['id']); ?>>
                            <?php echo esc_html($cat['full_name'] ?? $cat['name']); ?>
                        </option>
                        <?php endforeach; ?>
                    </select>
                </div>

                <!-- Producer -->
                <div class="wwc-sidebar-box">
                    <h3><?php _e('Producer', 'wwc-shop'); ?></h3>
                    <select name="product[producer]" id="producer">
                        <option value=""><?php _e('Select Producer', 'wwc-shop'); ?></option>
                        <?php foreach ($producers_list as $prod): ?>
                        <option value="<?php echo esc_attr($prod['id']); ?>"
                            <?php selected(($product['producer'] ?? '') == $prod['id']); ?>>
                            <?php echo esc_html($prod['name']); ?>
                        </option>
                        <?php endforeach; ?>
                    </select>
                </div>

                <!-- Pricing -->
                <div class="wwc-sidebar-box">
                    <h3><?php _e('Pricing', 'wwc-shop'); ?></h3>
                    <div class="wwc-form-group">
                        <label for="price_tnd">
                            <?php _e('Price (TND)', 'wwc-shop'); ?>
                            <span class="required">*</span>
                        </label>
                        <input type="number" id="price_tnd" name="product[price_tnd]"
                               value="<?php echo esc_attr($product['price_tnd'] ?? ''); ?>"
                               step="0.01" min="0" required>
                    </div>
                    <div class="wwc-form-group">
                        <label for="price_eur"><?php _e('Price (EUR)', 'wwc-shop'); ?></label>
                        <input type="number" id="price_eur" name="product[price_eur]"
                               value="<?php echo esc_attr($product['price_eur'] ?? ''); ?>"
                               step="0.01" min="0">
                    </div>
                    <div class="wwc-form-group">
                        <label for="compare_at_price_tnd"><?php _e('Compare at Price (TND)', 'wwc-shop'); ?></label>
                        <input type="number" id="compare_at_price_tnd" name="product[compare_at_price_tnd]"
                               value="<?php echo esc_attr($product['compare_at_price_tnd'] ?? ''); ?>"
                               step="0.01" min="0">
                        <p class="description"><?php _e('Original price for showing discount', 'wwc-shop'); ?></p>
                    </div>

                    <h4><?php _e('B2B Pricing', 'wwc-shop'); ?></h4>
                    <div class="wwc-form-group">
                        <label for="b2b_min_quantity"><?php _e('Min. Quantity for B2B', 'wwc-shop'); ?></label>
                        <input type="number" id="b2b_min_quantity" name="product[b2b_min_quantity]"
                               value="<?php echo esc_attr($product['b2b_min_quantity'] ?? 10); ?>"
                               min="1">
                    </div>
                    <div class="wwc-form-group">
                        <label for="b2b_price_tnd"><?php _e('B2B Price (TND)', 'wwc-shop'); ?></label>
                        <input type="number" id="b2b_price_tnd" name="product[b2b_price_tnd]"
                               value="<?php echo esc_attr($product['b2b_price_tnd'] ?? ''); ?>"
                               step="0.01" min="0">
                    </div>
                </div>

                <!-- Inventory -->
                <div class="wwc-sidebar-box">
                    <h3><?php _e('Inventory', 'wwc-shop'); ?></h3>
                    <div class="wwc-form-group">
                        <label for="stock_quantity"><?php _e('Stock Quantity', 'wwc-shop'); ?></label>
                        <input type="number" id="stock_quantity" name="product[stock_quantity]"
                               value="<?php echo esc_attr($product['stock_quantity'] ?? 0); ?>"
                               min="0">
                    </div>
                    <div class="wwc-form-group">
                        <label>
                            <input type="checkbox" name="product[track_inventory]" value="1"
                                <?php checked($product['track_inventory'] ?? true); ?>>
                            <?php _e('Track inventory', 'wwc-shop'); ?>
                        </label>
                    </div>
                    <div class="wwc-form-group">
                        <label>
                            <input type="checkbox" name="product[allow_backorder]" value="1"
                                <?php checked(!empty($product['allow_backorder'])); ?>>
                            <?php _e('Allow backorders', 'wwc-shop'); ?>
                        </label>
                    </div>
                </div>

                <!-- Badges -->
                <div class="wwc-sidebar-box">
                    <h3><?php _e('Badges', 'wwc-shop'); ?></h3>
                    <div class="wwc-badges-grid">
                        <label class="wwc-badge-option">
                            <input type="checkbox" name="product[is_natural]" value="1"
                                <?php checked(!empty($product['is_natural'])); ?>>
                            <span>🌿 <?php _e('100% Natural', 'wwc-shop'); ?></span>
                        </label>
                        <label class="wwc-badge-option">
                            <input type="checkbox" name="product[is_organic]" value="1"
                                <?php checked(!empty($product['is_organic'])); ?>>
                            <span>🌱 <?php _e('Organic/Bio', 'wwc-shop'); ?></span>
                        </label>
                        <label class="wwc-badge-option">
                            <input type="checkbox" name="product[is_handmade]" value="1"
                                <?php checked(!empty($product['is_handmade'])); ?>>
                            <span>✋ <?php _e('Handmade', 'wwc-shop'); ?></span>
                        </label>
                        <label class="wwc-badge-option">
                            <input type="checkbox" name="product[is_vegan]" value="1"
                                <?php checked(!empty($product['is_vegan'])); ?>>
                            <span>🥗 <?php _e('Vegan', 'wwc-shop'); ?></span>
                        </label>
                        <label class="wwc-badge-option">
                            <input type="checkbox" name="product[is_cruelty_free]" value="1"
                                <?php checked(!empty($product['is_cruelty_free'])); ?>>
                            <span>🐰 <?php _e('Cruelty-Free', 'wwc-shop'); ?></span>
                        </label>
                    </div>
                </div>
            </div>
        </div>
    </form>
</div>
