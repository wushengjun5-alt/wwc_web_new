/**
 * WWC Admin Producers Management
 */

let producers = [];
let deleteProducerId = null;

document.addEventListener('DOMContentLoaded', async function() {
    // Check API connection
    const connected = await AdminAPI.testConnection();

    if (!connected && !AdminConfig.getApiKey()) {
        AdminConfig.updateApiStatus('error', 'Clé API requise');
        document.getElementById('producersBody').innerHTML = `
            <tr>
                <td colspan="6" class="no-products">
                    <p>Entrez votre clé API admin pour gérer les producteurs.</p>
                    <p style="margin-top: 10px; color: var(--admin-text-light);">
                        Clé par défaut: <code>wwc-admin-dev-key-change-in-production</code>
                    </p>
                </td>
            </tr>
        `;
        return;
    }

    loadProducers();
});

async function loadProducers() {
    const tbody = document.getElementById('producersBody');
    tbody.innerHTML = '<tr><td colspan="6" class="loading">Chargement...</td></tr>';

    try {
        producers = await AdminAPI.getProducersAdmin();

        if (!producers.length) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="no-products">
                        <p>Aucun producteur.</p>
                        <button class="btn btn-primary" onclick="showAddProducerModal()">Créer un producteur</button>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = producers.map(prod => `
            <tr data-id="${prod.id}">
                <td>
                    ${prod.image
                        ? `<img src="${prod.image}" alt="" class="product-thumb">`
                        : '<div class="no-image">🏭</div>'
                    }
                </td>
                <td><strong>${escapeHtml(prod.name)}</strong></td>
                <td>${escapeHtml(prod.location) || '<span class="text-muted">-</span>'}</td>
                <td style="text-align: center;">${prod.products_count || 0}</td>
                <td>
                    <span class="status-badge status-${prod.is_active ? 'published' : 'draft'}">
                        ${prod.is_active ? 'Actif' : 'Inactif'}
                    </span>
                </td>
                <td>
                    <div class="row-actions">
                        <a href="#" onclick="editProducer(${prod.id}); return false;">Modifier</a>
                        <span>|</span>
                        <a href="#" class="delete" onclick="showDeleteModal(${prod.id}); return false;">Supprimer</a>
                    </div>
                </td>
            </tr>
        `).join('');

    } catch (error) {
        console.error('Error loading producers:', error);
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="loading">Erreur: ${error.message}</td>
            </tr>
        `;
    }
}

function showAddProducerModal() {
    document.getElementById('modalTitle').textContent = 'Nouveau Producteur';
    document.getElementById('producerId').value = '';
    document.getElementById('producerForm').reset();
    document.getElementById('prodActive').value = 'true';
    document.getElementById('producerModal').classList.add('active');
}

function editProducer(id) {
    const prod = producers.find(p => p.id === id);
    if (!prod) return;

    document.getElementById('modalTitle').textContent = 'Modifier le Producteur';
    document.getElementById('producerId').value = prod.id;
    document.getElementById('prodName').value = prod.name || '';
    document.getElementById('prodLocation').value = prod.location || '';
    document.getElementById('prodBio').value = prod.bio || '';
    document.getElementById('prodActive').value = prod.is_active ? 'true' : 'false';

    document.getElementById('producerModal').classList.add('active');
}

function closeProducerModal() {
    document.getElementById('producerModal').classList.remove('active');
}

async function saveProducer(e) {
    e.preventDefault();

    const id = document.getElementById('producerId').value;
    const data = {
        name: document.getElementById('prodName').value,
        location: document.getElementById('prodLocation').value || '',
        bio: document.getElementById('prodBio').value || '',
        is_active: document.getElementById('prodActive').value === 'true'
    };

    try {
        if (id) {
            await AdminAPI.updateProducer(id, data);
            AdminConfig.showToast('Producteur mis à jour', 'success');
        } else {
            await AdminAPI.createProducer(data);
            AdminConfig.showToast('Producteur créé', 'success');
        }

        closeProducerModal();
        loadProducers();
    } catch (error) {
        AdminConfig.showToast(error.message, 'error');
    }
}

function showDeleteModal(id) {
    deleteProducerId = id;
    const prod = producers.find(p => p.id === id);
    const countEl = document.getElementById('deleteProductsCount');
    if (prod && countEl) {
        const count = prod.products_count || 0;
        countEl.textContent = count > 0
            ? `Ce producteur a ${count} produit(s) qui seront supprimés.`
            : 'Ce producteur n\'a aucun produit.';
    }
    document.getElementById('deleteModal').classList.add('active');
}

function closeDeleteModal() {
    deleteProducerId = null;
    document.getElementById('deleteModal').classList.remove('active');
}

async function confirmDelete() {
    if (!deleteProducerId) return;

    try {
        await AdminAPI.deleteProducer(deleteProducerId);
        AdminConfig.showToast('Producteur supprimé', 'success');
        closeDeleteModal();
        loadProducers();
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
window.showAddProducerModal = showAddProducerModal;
window.editProducer = editProducer;
window.closeProducerModal = closeProducerModal;
window.saveProducer = saveProducer;
window.showDeleteModal = showDeleteModal;
window.closeDeleteModal = closeDeleteModal;
window.confirmDelete = confirmDelete;
