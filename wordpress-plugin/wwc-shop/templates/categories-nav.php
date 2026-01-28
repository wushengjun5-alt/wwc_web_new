<?php
/**
 * Categories Navigation Template
 *
 * Secondary navigation for shop categories
 *
 * @package WWC_Shop
 */

defined('ABSPATH') || exit;

$categories_list = $categories ?? [];
?>

<nav class="wwc-shop-categories">
    <?php foreach ($categories_list as $category): ?>
        <a href="<?php echo esc_url(home_url('/shop/?category=' . $category['slug'])); ?>"
           class="wwc-category-link <?php echo isset($_GET['category']) && $_GET['category'] === $category['slug'] ? 'active' : ''; ?>">
            <?php if (!empty($category['icon'])): ?>
                <span class="wwc-category-icon"><?php echo esc_html($category['icon']); ?></span>
            <?php endif; ?>
            <span class="wwc-category-name"><?php echo esc_html(strtoupper($category['name'])); ?></span>
            <?php if (!empty($category['has_children'])): ?>
                <span class="wwc-category-arrow">▼</span>
            <?php endif; ?>
        </a>
    <?php endforeach; ?>
</nav>
