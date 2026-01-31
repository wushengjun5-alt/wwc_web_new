/**
 * WWC Admin Categories Management
 */

let categories = [];
let deleteCategoryId = null;

document.addEventListener('DOMContentLoaded', async function() {
    // Check API connection
    const connected = await AdminAPI.testConnection();

    if (!connected && !AdminConfig.getApiKey()) {
        AdminConfig.updateApiStatus('error', 'Clé API requise');
        document.getElementById('categoriesBody').innerHTML = `
            <tr>
                <td colspan="9" class="no-products">
                    <p>Entrez votre clé API admin pour gérer les catégories.</p>
                    <p style="margin-top: 10px; color: var(--admin-text-light);">
                        Clé par défaut: <code>wwc-admin-dev-key-change-in-production</code>
                    </p>
                </td>
            </tr>
        `;
        return;
    }

    loadCategories();
});

async function loadCategories() {
    const tbody = document.getElementById('categoriesBody');
    tbody.innerHTML = '<tr><td colspan="9" class="loading">Chargement...</td></tr>';

    try {
        categories = await AdminAPI.getCategoriesAdmin();

        if (!categories.length) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" class="no-products">
                        <p>Aucune catégorie.</p>
                        <button class="btn btn-primary" onclick="showAddCategoryModal()">Créer une catégorie</button>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = categories.map(cat => `
            <tr data-id="${cat.id}">
                <td style="font-size: 24px; text-align: center;">${cat.icon || '📁'}</td>
                <td><strong>${escapeHtml(cat.name)}</strong></td>
                <td>${escapeHtml(cat.name_en) || '<span class="text-muted">-</span>'}</td>
                <td dir="rtl">${escapeHtml(cat.name_ar) || '<span class="text-muted">-</span>'}</td>
                <td><code>${cat.slug}</code></td>
                <td style="text-align: center;">${cat.order}</td>
                <td style="text-align: center;">${cat.products_count || 0}</td>
                <td style="text-align: center;">
                    ${cat.show_in_menu ? '✅' : '❌'}
                </td>
                <td>
                    <span class="status-badge status-${cat.is_active ? 'published' : 'draft'}">
                        ${cat.is_active ? 'Actif' : 'Inactif'}
                    </span>
                </td>
                <td>
                    <div class="row-actions">
                        <a href="#" onclick="editCategory(${cat.id}); return false;">Modifier</a>
                        <span>|</span>
                        <a href="#" class="delete" onclick="showDeleteModal(${cat.id}); return false;">Supprimer</a>
                    </div>
                </td>
            </tr>
        `).join('');

    } catch (error) {
        console.error('Error loading categories:', error);
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="loading">Erreur: ${error.message}</td>
            </tr>
        `;
    }
}

function showAddCategoryModal() {
    document.getElementById('modalTitle').textContent = 'Nouvelle Catégorie';
    document.getElementById('categoryId').value = '';
    document.getElementById('categoryForm').reset();
    document.getElementById('catActive').value = 'true';
    document.getElementById('catShowInMenu').value = 'true';
    document.getElementById('categoryModal').classList.add('active');
}

function editCategory(id) {
    const cat = categories.find(c => c.id === id);
    if (!cat) return;

    document.getElementById('modalTitle').textContent = 'Modifier la Catégorie';
    document.getElementById('categoryId').value = cat.id;
    document.getElementById('catName').value = cat.name || '';
    document.getElementById('catNameEn').value = cat.name_en || '';
    document.getElementById('catNameAr').value = cat.name_ar || '';
    document.getElementById('catIcon').value = cat.icon || '';
    document.getElementById('catDescription').value = cat.description || '';
    document.getElementById('catOrder').value = cat.order || 0;
    document.getElementById('catActive').value = cat.is_active ? 'true' : 'false';
    document.getElementById('catShowInMenu').value = cat.show_in_menu ? 'true' : 'false';

    document.getElementById('categoryModal').classList.add('active');
}

function closeCategoryModal() {
    document.getElementById('categoryModal').classList.remove('active');
}

async function saveCategory(e) {
    e.preventDefault();

    const id = document.getElementById('categoryId').value;
    const data = {
        name: document.getElementById('catName').value,
        name_en: document.getElementById('catNameEn').value || null,
        name_ar: document.getElementById('catNameAr').value || null,
        icon: document.getElementById('catIcon').value || null,
        description: document.getElementById('catDescription').value || '',
        order: parseInt(document.getElementById('catOrder').value) || 0,
        is_active: document.getElementById('catActive').value === 'true',
        show_in_menu: document.getElementById('catShowInMenu').value === 'true'
    };

    try {
        if (id) {
            await AdminAPI.updateCategory(id, data);
            AdminConfig.showToast('Catégorie mise à jour', 'success');
        } else {
            await AdminAPI.createCategory(data);
            AdminConfig.showToast('Catégorie créée', 'success');
        }

        closeCategoryModal();
        loadCategories();
    } catch (error) {
        AdminConfig.showToast(error.message, 'error');
    }
}

function showDeleteModal(id) {
    deleteCategoryId = id;
    const cat = categories.find(c => c.id === id);
    const countEl = document.getElementById('deleteProductsCount');
    if (cat && countEl) {
        const count = cat.products_count || 0;
        countEl.textContent = count > 0
            ? `Cette catégorie contient ${count} produit(s) qui seront supprimés.`
            : 'Cette catégorie ne contient aucun produit.';
    }
    document.getElementById('deleteModal').classList.add('active');
}

function closeDeleteModal() {
    deleteCategoryId = null;
    document.getElementById('deleteModal').classList.remove('active');
}

async function confirmDelete() {
    if (!deleteCategoryId) return;

    try {
        await AdminAPI.deleteCategory(deleteCategoryId);
        AdminConfig.showToast('Catégorie supprimée', 'success');
        closeDeleteModal();
        loadCategories();
    } catch (error) {
        AdminConfig.showToast(error.message, 'error');
    }
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Expose functions to global scope
window.showAddCategoryModal = showAddCategoryModal;
window.editCategory = editCategory;
window.closeCategoryModal = closeCategoryModal;
window.saveCategory = saveCategory;
window.showDeleteModal = showDeleteModal;
window.closeDeleteModal = closeDeleteModal;
window.confirmDelete = confirmDelete;
