/**
 * WWC Admin Products List
 */

let currentPage = 1;
let totalPages = 1;
let selectedProducts = new Set();
let deleteProductId = null;
let langCompleteFilter = '';

document.addEventListener('DOMContentLoaded', async function() {
    // Check API connection
    const connected = await AdminAPI.testConnection();

    if (!connected && !AdminConfig.getApiKey()) {
        AdminConfig.updateApiStatus('error', 'Clé API requise');
        document.getElementById('productsBody').innerHTML = `
            <tr>
                <td colspan="11" class="no-products">
                    <p>Entrez votre clé API admin pour accéder aux produits.</p>
                    <p style="margin-top: 10px; color: var(--admin-text-light);">
                        Clé par défaut: <code>wwc-admin-dev-key-change-in-production</code>
                    </p>
                </td>
            </tr>
        `;
        return;
    }

    // Initialize
    loadCategories();
    loadProducts();
    setupEventListeners();

    // Apply URL filters
    applyUrlFilters();
});

function setupEventListeners() {
    // Search with debounce
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', AdminConfig.debounce(() => {
        currentPage = 1;
        loadProducts();
    }, 300));

    // Filter form
    document.getElementById('filtersForm').addEventListener('submit', function(e) {
        e.preventDefault();
        currentPage = 1;
        loadProducts();
    });

    // Clear filters
    document.getElementById('clearFilters').addEventListener('click', function() {
        document.getElementById('searchInput').value = '';
        document.getElementById('statusFilter').value = '';
        document.getElementById('categoryFilter').value = '';
        document.getElementById('stockFilter').value = '';
        currentPage = 1;
        loadProducts();
    });

    // Select all checkbox
    document.getElementById('selectAll').addEventListener('change', function() {
        const checkboxes = document.querySelectorAll('.product-checkbox');
        checkboxes.forEach(cb => {
            cb.checked = this.checked;
            if (this.checked) {
                selectedProducts.add(parseInt(cb.value));
            } else {
                selectedProducts.delete(parseInt(cb.value));
            }
        });
        updateBulkActions();
    });

    // Bulk action
    document.getElementById('applyBulkAction').addEventListener('click', applyBulkAction);

    // Delete modal
    document.getElementById('closeDeleteModal').addEventListener('click', closeDeleteModal);
    document.getElementById('cancelDelete').addEventListener('click', closeDeleteModal);
    document.getElementById('confirmDelete').addEventListener('click', confirmDelete);
    document.querySelector('.modal-overlay').addEventListener('click', closeDeleteModal);
}

function applyUrlFilters() {
    const params = AdminConfig.getUrlParams();

    if (params.get('status')) {
        document.getElementById('statusFilter').value = params.get('status');
    }
    if (params.get('category')) {
        document.getElementById('categoryFilter').value = params.get('category');
    }
    if (params.get('low_stock')) {
        document.getElementById('stockFilter').value = 'low';
    }
    langCompleteFilter = params.get('lang_complete') || '';
}

async function loadCategories() {
    try {
        const categories = await AdminAPI.getCategories();
        const select = document.getElementById('categoryFilter');

        categories.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat.id;
            option.textContent = cat.name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

async function loadProducts() {
    const tbody = document.getElementById('productsBody');
    tbody.innerHTML = '<tr><td colspan="11" class="loading">Chargement...</td></tr>';

    try {
        const params = {
            page: currentPage,
            page_size: 20
        };

        const search = document.getElementById('searchInput').value;
        if (search) params.search = search;

        const status = document.getElementById('statusFilter').value;
        if (status === 'published') params.is_active = true;
        if (status === 'draft') params.is_active = false;

        const category = document.getElementById('categoryFilter').value;
        if (category) params.category = category;

        const stock = document.getElementById('stockFilter').value;
        if (stock === 'low') params.low_stock = 'true';
        if (stock === 'out') params.out_of_stock = 'true';

        if (langCompleteFilter) params.lang_complete = langCompleteFilter;

        const response = await AdminAPI.getProducts(params);
        const products = response.results || response;
        totalPages = Math.ceil((response.count || products.length) / 20);

        if (!products.length) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="11" class="no-products">
                        <p>Aucun produit trouvé.</p>
                        <a href="product-edit.html" class="btn btn-primary">Créer un produit</a>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = products.map(product => renderProductRow(product)).join('');

        // Add event listeners to new checkboxes
        document.querySelectorAll('.product-checkbox').forEach(cb => {
            cb.addEventListener('change', function() {
                if (this.checked) {
                    selectedProducts.add(parseInt(this.value));
                } else {
                    selectedProducts.delete(parseInt(this.value));
                }
                updateBulkActions();
            });
        });

        renderPagination();

    } catch (error) {
        console.error('Error loading products:', error);
        tbody.innerHTML = `
            <tr>
                <td colspan="11" class="loading">Erreur: ${error.message}</td>
            </tr>
        `;
    }
}

function renderProductRow(product) {
    const langCompleteness = product.language_completeness || {};

    return `
        <tr data-id="${product.id}">
            <td>
                <input type="checkbox" class="product-checkbox" value="${product.id}"
                    ${selectedProducts.has(product.id) ? 'checked' : ''}>
            </td>
            <td>
                ${product.primary_image_url
                    ? `<img src="${product.primary_image_url}" alt="" class="product-thumb">`
                    : '<div class="no-image">📦</div>'
                }
            </td>
            <td>
                <div class="product-name-cell">
                    <a href="product-edit.html?id=${product.id}" class="product-name">
                        ${escapeHtml(product.name)}
                    </a>
                    <div class="product-badges">
                        ${product.is_featured ? '<span class="badge badge-featured">⭐ Featured</span>' : ''}
                        ${product.is_new ? '<span class="badge">🆕 New</span>' : ''}
                    </div>
                    <div class="row-actions">
                        <a href="product-edit.html?id=${product.id}">Modifier</a>
                        <span>|</span>
                        <a href="../product.html?id=${product.id}" target="_blank">Voir</a>
                        <span>|</span>
                        <a href="#" onclick="duplicateProduct(${product.id}); return false;">Dupliquer</a>
                        <span>|</span>
                        <a href="#" class="delete" onclick="showDeleteModal(${product.id}); return false;">Supprimer</a>
                    </div>
                </div>
            </td>
            <td><code>${product.sku || '-'}</code></td>
            <td>${product.category_name || '-'}</td>
            <td>${AdminConfig.formatPrice(product.price_tnd)}</td>
            <td class="${getStockClass(product.stock_quantity)}">${product.stock_quantity}</td>
            <td>
                <div class="lang-pills">
                    <span class="lang-pill complete">FR</span>
                    <span class="lang-pill ${langCompleteness.en ? 'complete' : ''}">EN</span>
                    <span class="lang-pill ${langCompleteness.ar ? 'complete' : ''}">AR</span>
                </div>
            </td>
            <td>
                <span class="status-badge status-${product.is_active ? 'published' : 'draft'}">
                    ${product.is_active ? 'Publié' : 'Brouillon'}
                </span>
            </td>
            <td>${AdminConfig.formatDate(product.created_at)}</td>
            <td>
                <a href="product-edit.html?id=${product.id}" class="btn btn-sm btn-outline">✏️</a>
            </td>
        </tr>
    `;
}

function renderPagination() {
    const container = document.getElementById('pagination');

    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }

    let html = '';

    // Previous
    if (currentPage > 1) {
        html += `<a href="#" class="page-link" data-page="${currentPage - 1}">←</a>`;
    }

    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
            html += `<a href="#" class="page-link ${i === currentPage ? 'active' : ''}" data-page="${i}">${i}</a>`;
        } else if (i === currentPage - 3 || i === currentPage + 3) {
            html += '<span class="page-link">...</span>';
        }
    }

    // Next
    if (currentPage < totalPages) {
        html += `<a href="#" class="page-link" data-page="${currentPage + 1}">→</a>`;
    }

    container.innerHTML = html;

    // Add event listeners
    container.querySelectorAll('a.page-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            currentPage = parseInt(this.dataset.page);
            loadProducts();
            window.scrollTo(0, 0);
        });
    });
}

function updateBulkActions() {
    const bulkSection = document.getElementById('bulkActions');
    const countSpan = document.getElementById('selectedCount');

    if (selectedProducts.size > 0) {
        bulkSection.style.display = 'flex';
        countSpan.textContent = `${selectedProducts.size} sélectionné(s)`;
    } else {
        bulkSection.style.display = 'none';
    }
}

async function applyBulkAction() {
    const action = document.getElementById('bulkAction').value;

    if (!action) {
        AdminConfig.showToast('Sélectionnez une action', 'warning');
        return;
    }

    if (selectedProducts.size === 0) {
        AdminConfig.showToast('Sélectionnez des produits', 'warning');
        return;
    }

    if (action === 'delete' && !confirm('Supprimer les produits sélectionnés ?')) {
        return;
    }

    try {
        await AdminAPI.bulkAction(action, Array.from(selectedProducts));
        AdminConfig.showToast('Action effectuée', 'success');
        selectedProducts.clear();
        document.getElementById('selectAll').checked = false;
        updateBulkActions();
        loadProducts();
    } catch (error) {
        AdminConfig.showToast(error.message, 'error');
    }
}

async function duplicateProduct(id) {
    try {
        const newProduct = await AdminAPI.duplicateProduct(id);
        AdminConfig.showToast('Produit dupliqué', 'success');
        window.location.href = `product-edit.html?id=${newProduct.id}`;
    } catch (error) {
        AdminConfig.showToast(error.message, 'error');
    }
}

function showDeleteModal(id) {
    deleteProductId = id;
    document.getElementById('deleteModal').classList.add('active');
}

function closeDeleteModal() {
    deleteProductId = null;
    document.getElementById('deleteModal').classList.remove('active');
}

async function confirmDelete() {
    if (!deleteProductId) return;

    try {
        await AdminAPI.deleteProduct(deleteProductId);
        AdminConfig.showToast('Produit supprimé', 'success');
        closeDeleteModal();
        loadProducts();
    } catch (error) {
        AdminConfig.showToast(error.message, 'error');
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

// Expose functions to global scope for onclick handlers
window.duplicateProduct = duplicateProduct;
window.showDeleteModal = showDeleteModal;
window.closeDeleteModal = closeDeleteModal;
window.confirmDelete = confirmDelete;
