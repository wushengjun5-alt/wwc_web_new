/**
 * WWC Admin - Order Management
 */

let currentPage = 1;
let totalPages = 1;

const STATUS_LABELS = {
    pending:    'En attente',
    paid:       'Payée',
    processing: 'En traitement',
    shipped:    'Expédiée',
    delivered:  'Livrée',
    cancelled:  'Annulée',
    refunded:   'Remboursée',
};

const PAYMENT_LABELS = {
    stripe:           'Carte (Stripe)',
    bank_transfer:    'Virement bancaire',
    cash_on_delivery: 'Paiement à la livraison',
};

document.addEventListener('DOMContentLoaded', async function () {
    const connected = await AdminAPI.testConnection();
    if (!connected && !AdminConfig.getApiKey()) {
        AdminConfig.updateApiStatus('error', 'Clé API requise');
        document.getElementById('ordersBody').innerHTML =
            `<tr><td colspan="8" class="no-products">Entrez votre clé API admin pour accéder aux commandes.</td></tr>`;
        return;
    }

    loadOrders();
    setupEventListeners();
});

function setupEventListeners() {
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', AdminConfig.debounce(() => {
        currentPage = 1;
        loadOrders();
    }, 300));

    document.getElementById('filtersForm').addEventListener('submit', function (e) {
        e.preventDefault();
        currentPage = 1;
        loadOrders();
    });

    document.getElementById('clearFilters').addEventListener('click', function () {
        document.getElementById('searchInput').value = '';
        document.getElementById('statusFilter').value = '';
        currentPage = 1;
        loadOrders();
    });
}

async function loadOrders() {
    const tbody = document.getElementById('ordersBody');
    tbody.innerHTML = `<tr><td colspan="8" class="loading">Chargement...</td></tr>`;

    const params = new URLSearchParams({ page: currentPage, page_size: 20 });
    const search = document.getElementById('searchInput').value.trim();
    const status = document.getElementById('statusFilter').value;
    if (search) params.set('search', search);
    if (status) params.set('status', status);

    try {
        const data = await AdminAPI.get(`/admin/orders/?${params}`);
        const orders = data.results || [];
        const total  = data.count || 0;
        totalPages = Math.ceil(total / 20);

        document.getElementById('orderCount').textContent =
            total > 0 ? `${total} commande${total > 1 ? 's' : ''}` : 'Aucune commande';

        if (orders.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" class="no-products">Aucune commande trouvée.</td></tr>`;
            document.getElementById('pagination').innerHTML = '';
            return;
        }

        tbody.innerHTML = orders.map(o => `
            <tr>
                <td><strong style="font-family:monospace;">${escHtml(o.order_number)}</strong></td>
                <td>
                    <div>${escHtml(o.email)}</div>
                    <div style="font-size:12px;color:var(--admin-text-light);">${escHtml(o.phone || '')}</div>
                </td>
                <td><span class="status-badge status-${o.status}">${STATUS_LABELS[o.status] || o.status}</span></td>
                <td>${AdminConfig.formatPrice(o.total, o.currency)}</td>
                <td style="font-size:13px;">${PAYMENT_LABELS[o.payment_method] || o.payment_method || '—'}</td>
                <td style="font-size:13px;">${escHtml(o.tracking_number || '—')}</td>
                <td style="font-size:13px;">${AdminConfig.formatDate(o.created_at)}</td>
                <td>
                    <button class="btn btn-sm" onclick="openOrder('${escHtml(o.order_number)}')">Voir</button>
                </td>
            </tr>`).join('');

        renderPagination(currentPage, totalPages);
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="8" class="no-products" style="color:var(--admin-danger);">${escHtml(err.message)}</td></tr>`;
    }
}

function renderPagination(page, total) {
    const el = document.getElementById('pagination');
    if (!el || total <= 1) { if (el) el.innerHTML = ''; return; }

    let html = '';
    if (page > 1) html += `<button class="btn btn-sm btn-outline" onclick="goToPage(${page - 1})">← Précédent</button>`;
    html += `<span>Page ${page} sur ${total}</span>`;
    if (page < total) html += `<button class="btn btn-sm btn-outline" onclick="goToPage(${page + 1})">Suivant →</button>`;
    el.innerHTML = html;
}

function goToPage(page) {
    currentPage = page;
    loadOrders();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ── Order Detail Panel ──────────────────────────────────────────

async function openOrder(orderNumber) {
    document.getElementById('panelTitle').textContent = `Commande #${orderNumber}`;
    document.getElementById('panelBody').innerHTML = '<p>Chargement...</p>';
    document.getElementById('panelFooter').innerHTML = '';
    document.getElementById('orderPanel').classList.add('open');
    document.getElementById('panelOverlay').classList.add('open');

    try {
        const order = await AdminAPI.get(`/admin/orders/${orderNumber}/`);
        renderOrderPanel(order);
    } catch (err) {
        document.getElementById('panelBody').innerHTML =
            `<p style="color:red;">${escHtml(err.message)}</p>`;
    }
}

function closePanel() {
    document.getElementById('orderPanel').classList.remove('open');
    document.getElementById('panelOverlay').classList.remove('open');
}

function renderOrderPanel(order) {
    const symbol = order.currency === 'EUR' ? '€' : 'DT';

    const itemsRows = (order.items || []).map(item => `
        <tr>
            <td>${escHtml(item.product_name || '—')}</td>
            <td style="text-align:center;">${item.quantity}</td>
            <td style="text-align:right;">${item.unit_price} ${symbol}</td>
            <td style="text-align:right;font-weight:600;">${item.subtotal} ${symbol}</td>
        </tr>`).join('');

    const addrLines = [
        `${order.shipping_first_name || ''} ${order.shipping_last_name || ''}`.trim(),
        order.shipping_company || '',
        order.shipping_address_1 || '',
        order.shipping_address_2 || '',
        `${order.shipping_postal_code || ''} ${order.shipping_city || ''}`.trim(),
        order.shipping_state || '',
        order.shipping_country || '',
    ].filter(Boolean);
    const addrHtml = addrLines.length
        ? addrLines.map(l => escHtml(l)).join('<br>')
        : '<em style="color:var(--admin-text-light);">Non renseignée</em>';

    const impactEntries = Object.entries(order.impact_summary || {}).filter(([,v]) => v > 0);
    const impactHtml = impactEntries.length
        ? `<div class="detail-section">
            <h4>Impact GreenSchool</h4>
            ${impactEntries.map(([type, qty]) =>
                `<div class="detail-row"><span>${escHtml(type)}</span><strong>${qty} fournis</strong></div>`
            ).join('')}
           </div>`
        : '';

    document.getElementById('panelBody').innerHTML = `
        <!-- Info -->
        <div class="detail-section">
            <h4>Informations</h4>
            <div class="detail-row"><span>Client</span><strong>${escHtml(order.email)}</strong></div>
            <div class="detail-row"><span>Téléphone</span><span>${escHtml(order.phone || '—')}</span></div>
            <div class="detail-row"><span>Commandé le</span><span>${AdminConfig.formatDate(order.created_at)}</span></div>
            ${order.paid_at ? `<div class="detail-row"><span>Payé le</span><span>${AdminConfig.formatDate(order.paid_at)}</span></div>` : ''}
            ${order.shipped_at ? `<div class="detail-row"><span>Expédié le</span><span>${AdminConfig.formatDate(order.shipped_at)}</span></div>` : ''}
            ${order.delivered_at ? `<div class="detail-row"><span>Livré le</span><span>${AdminConfig.formatDate(order.delivered_at)}</span></div>` : ''}
            <div class="detail-row"><span>Paiement</span><span>${PAYMENT_LABELS[order.payment_method] || order.payment_method || '—'}</span></div>
            <div class="detail-row"><span>Devise</span><span>${order.currency}</span></div>
            ${order.customer_notes ? `<div class="detail-row"><span>Notes client</span><span style="font-style:italic;">${escHtml(order.customer_notes)}</span></div>` : ''}
        </div>

        <!-- Items -->
        <div class="detail-section">
            <h4>Articles</h4>
            <table class="items-mini">
                <thead><tr><th>Produit</th><th style="text-align:center;">Qté</th><th style="text-align:right;">Prix</th><th style="text-align:right;">Total</th></tr></thead>
                <tbody>${itemsRows}</tbody>
            </table>
            <div style="margin-top:10px; text-align:right; font-size:14px;">
                <div>Sous-total : <strong>${order.subtotal} ${symbol}</strong></div>
                ${parseFloat(order.shipping_cost) > 0
                    ? `<div>Livraison : <strong>${order.shipping_cost} ${symbol}</strong></div>` : ''}
                ${parseFloat(order.discount_amount) > 0
                    ? `<div style="color:green;">Remise${order.coupon_code ? ` (${escHtml(order.coupon_code)})` : ''} : <strong>-${order.discount_amount} ${symbol}</strong></div>` : ''}
                ${parseFloat(order.tax_amount) > 0
                    ? `<div>Emballage cadeau : <strong>${order.tax_amount} ${symbol}</strong></div>` : ''}
                <div style="font-size:16px; margin-top:6px; border-top:1px solid var(--admin-border); padding-top:6px;">Total : <strong>${order.total} ${symbol}</strong></div>
            </div>
        </div>

        <!-- Address -->
        <div class="detail-section">
            <h4>Adresse de livraison</h4>
            <address style="font-style:normal; font-size:14px; line-height:1.8;">${addrHtml}</address>
        </div>

        ${impactHtml}

        <!-- Update form -->
        <div class="detail-section">
            <h4>Mise à jour</h4>
            <div style="margin-bottom:12px;">
                <label style="font-size:13px;font-weight:600;display:block;margin-bottom:4px;">Statut</label>
                <select id="newStatus" style="width:100%;padding:8px 12px;border:1px solid var(--admin-border);border-radius:6px;font-size:14px;font-family:inherit;">
                    ${Object.entries(STATUS_LABELS).map(([val, label]) =>
                        `<option value="${val}"${order.status === val ? ' selected' : ''}>${label}</option>`
                    ).join('')}
                </select>
            </div>
            <div style="margin-bottom:12px;">
                <label style="font-size:13px;font-weight:600;display:block;margin-bottom:4px;">Numéro de suivi</label>
                <input id="newTracking" type="text" value="${escHtml(order.tracking_number || '')}" placeholder="Ex: TN123456789"
                    style="width:100%;padding:8px 12px;border:1px solid var(--admin-border);border-radius:6px;font-size:14px;font-family:inherit;">
            </div>
        </div>
    `;

    document.getElementById('panelFooter').innerHTML = `
        <button class="btn btn-primary" style="width:100%;" onclick="saveOrderUpdate('${escHtml(order.order_number)}')">
            Enregistrer les modifications
        </button>`;
}

async function saveOrderUpdate(orderNumber) {
    const newStatus   = document.getElementById('newStatus').value;
    const newTracking = document.getElementById('newTracking').value.trim();

    try {
        await AdminAPI.patch(`/admin/orders/${orderNumber}/`, {
            status: newStatus,
            tracking_number: newTracking,
        });
        AdminConfig.showToast('Commande mise à jour avec succès.', 'success');
        closePanel();
        loadOrders();
    } catch (err) {
        AdminConfig.showToast(err.message, 'error');
    }
}

function escHtml(str) {
    return String(str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
