/**
 * WWC Admin Dashboard
 */

document.addEventListener('DOMContentLoaded', async function() {
    // Check API connection
    const connected = await AdminAPI.testConnection();

    if (!connected && !AdminConfig.getApiKey()) {
        AdminConfig.updateApiStatus('error', 'Clé API requise');
        document.getElementById('statsGrid').innerHTML = `
            <div class="stat-card" style="grid-column: 1/-1; text-align: center; padding: 40px;">
                <p>Entrez votre clé API admin en haut à droite pour accéder au dashboard.</p>
                <p style="margin-top: 10px; color: var(--admin-text-light);">
                    Clé par défaut en développement: <code>wwc-admin-dev-key-change-in-production</code>
                </p>
            </div>
        `;
        return;
    }

    // Load dashboard data
    loadStats();
    loadRecentProducts();
});

async function loadStats() {
    try {
        const stats = await AdminAPI.getStats();

        document.getElementById('statTotalProducts').textContent = stats.total_products || 0;
        document.getElementById('statPublished').textContent = stats.published_products || 0;
        document.getElementById('statDraft').textContent = stats.draft_products || 0;
        document.getElementById('statLowStock').textContent = stats.low_stock_products || 0;
        document.getElementById('statMissingEn').textContent = stats.missing_english || 0;
        document.getElementById('statMissingAr').textContent = stats.missing_arabic || 0;

    } catch (error) {
        console.error('Error loading stats:', error);
        AdminConfig.showToast('Erreur de chargement des statistiques', 'error');
    }
}

async function loadRecentProducts() {
    const tbody = document.getElementById('recentProducts');

    try {
        const response = await AdminAPI.getProducts({ page_size: 5, ordering: '-created_at' });
        const products = response.results || response;

        if (!products.length) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="no-products">
                        <p>Aucun produit pour le moment.</p>
                        <a href="product-edit.html" class="btn btn-primary">Créer un produit</a>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = products.map(product => `
            <tr>
                <td>
                    ${product.primary_image_url
                        ? `<img src="${product.primary_image_url}" alt="" class="product-thumb">`
                        : '<div class="no-image">📦</div>'
                    }
                </td>
                <td>
                    <a href="product-edit.html?id=${product.id}" class="product-name">${escapeHtml(product.name)}</a>
                </td>
                <td>${product.category_name || '-'}</td>
                <td>${AdminConfig.formatPrice(product.price_tnd)}</td>
                <td class="${getStockClass(product.stock_quantity)}">${product.stock_quantity}</td>
                <td>
                    <span class="status-badge status-${product.is_active ? 'published' : 'draft'}">
                        ${product.is_active ? 'Publié' : 'Brouillon'}
                    </span>
                </td>
                <td>
                    <div class="row-actions">
                        <a href="product-edit.html?id=${product.id}">Modifier</a>
                        <span>|</span>
                        <a href="../product.html?id=${product.id}" target="_blank">Voir</a>
                    </div>
                </td>
            </tr>
        `).join('');

    } catch (error) {
        console.error('Error loading products:', error);
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="loading">Erreur de chargement</td>
            </tr>
        `;
    }
}

function getStockClass(quantity) {
    if (quantity <= 0) return 'stock-out';
    if (quantity < 10) return 'stock-low';
    return 'stock-ok';
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
