/**
 * WWC Admin Product Edit
 */

let productId = null;
let productData = null;
let isNewProduct = true;

document.addEventListener('DOMContentLoaded', async function() {
    // Get product ID from URL
    const params = AdminConfig.getUrlParams();
    productId = params.get('id');
    isNewProduct = !productId;

    // Check API connection
    const connected = await AdminAPI.testConnection();

    if (!connected && !AdminConfig.getApiKey()) {
        AdminConfig.updateApiStatus('error', 'Clé API requise');
        AdminConfig.showToast('Entrez votre clé API pour continuer', 'warning');
        return;
    }

    // Setup event listeners
    setupEventListeners();

    // Load categories and producers
    await Promise.all([loadCategories(), loadProducers()]);

    // Load product data if editing
    if (productId) {
        await loadProduct();
    } else {
        // New product setup
        document.getElementById('pageTitle').textContent = 'Nouveau Produit';
        document.getElementById('imagesHint').style.display = 'block';
        document.getElementById('uploadArea').style.display = 'none';
    }
});

function setupEventListeners() {
    // Language tabs
    document.querySelectorAll('.lang-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            const lang = this.dataset.lang;
            switchLanguageTab(lang);
        });
    });

    // B2B pricing toggle
    document.getElementById('has_b2b_pricing').addEventListener('change', function() {
        document.getElementById('b2bFields').style.display = this.checked ? 'block' : 'none';
    });

    // SEO section toggle
    document.querySelector('.section-toggle').addEventListener('click', function() {
        const target = document.getElementById(this.dataset.target);
        target.style.display = target.style.display === 'none' ? 'block' : 'none';
        this.classList.toggle('open');
    });

    // Character counts
    document.getElementById('meta_title').addEventListener('input', function() {
        document.getElementById('metaTitleCount').textContent = this.value.length;
    });

    document.getElementById('meta_description').addEventListener('input', function() {
        document.getElementById('metaDescCount').textContent = this.value.length;
    });

    // Impact preview
    ['impact_quantity', 'impact_item', 'impact_school'].forEach(id => {
        document.getElementById(id).addEventListener('input', updateImpactPreview);
    });

    // Form submission
    document.getElementById('productForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        await saveProduct(true);
    });

    // Save draft
    document.getElementById('saveDraftBtn').addEventListener('click', async function() {
        document.getElementById('is_active').value = 'false';
        await saveProduct(false);
    });

    // Image upload
    document.getElementById('selectImagesBtn').addEventListener('click', function() {
        document.getElementById('imageInput').click();
    });

    document.getElementById('imageInput').addEventListener('change', handleImageUpload);

    // Drag and drop
    const uploadArea = document.getElementById('uploadArea');
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', function() {
        this.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        this.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length) {
            uploadImages(files);
        }
    });

    // Preview button
    document.getElementById('previewBtn').addEventListener('click', function() {
        if (productId) {
            window.open(`../product.html?id=${productId}`, '_blank');
        }
    });
}

function switchLanguageTab(lang) {
    document.querySelectorAll('.lang-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.lang-content').forEach(c => c.classList.remove('active'));

    document.querySelector(`.lang-tab[data-lang="${lang}"]`).classList.add('active');
    document.querySelector(`.lang-content[data-lang="${lang}"]`).classList.add('active');
}

async function loadCategories() {
    try {
        const categories = await AdminAPI.getCategories();
        const select = document.getElementById('category');

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

async function loadProducers() {
    try {
        const producers = await AdminAPI.getProducers();
        const select = document.getElementById('producer');

        producers.forEach(prod => {
            const option = document.createElement('option');
            option.value = prod.id;
            option.textContent = prod.name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading producers:', error);
    }
}

async function loadProduct() {
    try {
        productData = await AdminAPI.getProduct(productId);

        document.getElementById('pageTitle').textContent = `Modifier: ${productData.name}`;
        document.getElementById('productId').value = productId;
        document.getElementById('previewBtn').style.display = 'inline-flex';

        // Fill form fields
        fillFormField('name', productData.name);
        fillFormField('description', productData.description);
        fillFormField('short_description', productData.short_description);

        fillFormField('name_en', productData.name_en);
        fillFormField('description_en', productData.description_en);
        fillFormField('short_description_en', productData.short_description_en);

        fillFormField('name_ar', productData.name_ar);
        fillFormField('description_ar', productData.description_ar);
        fillFormField('short_description_ar', productData.short_description_ar);

        fillFormField('price_tnd', productData.price_tnd);
        fillFormField('price_eur', productData.price_eur);
        fillFormField('compare_at_price', productData.compare_at_price);
        fillFormField('cost_price', productData.cost_price);

        if (productData.b2b_price_tnd) {
            document.getElementById('has_b2b_pricing').checked = true;
            document.getElementById('b2bFields').style.display = 'block';
            fillFormField('b2b_price_tnd', productData.b2b_price_tnd);
            fillFormField('b2b_min_quantity', productData.b2b_min_quantity);
        }

        fillFormField('sku', productData.sku);
        fillFormField('stock_quantity', productData.stock_quantity);
        fillFormField('weight', productData.weight);
        document.getElementById('track_inventory').checked = productData.track_inventory !== false;

        fillFormField('category', productData.category);
        fillFormField('producer', productData.producer);

        fillFormField('is_active', productData.is_active ? 'true' : 'false');

        document.getElementById('is_featured').checked = productData.is_featured;
        document.getElementById('is_new').checked = productData.is_new;
        document.getElementById('is_bestseller').checked = productData.is_bestseller;
        document.getElementById('is_eco_friendly').checked = productData.is_eco_friendly;

        fillFormField('impact_quantity', productData.impact_quantity);
        fillFormField('impact_item', productData.impact_item);
        fillFormField('impact_school', productData.impact_school);

        fillFormField('meta_title', productData.meta_title);
        fillFormField('meta_description', productData.meta_description);

        // Update char counts
        document.getElementById('metaTitleCount').textContent = (productData.meta_title || '').length;
        document.getElementById('metaDescCount').textContent = (productData.meta_description || '').length;

        // Show publish info
        document.getElementById('publishInfo').style.display = 'block';
        document.getElementById('createdAt').textContent = AdminConfig.formatDate(productData.created_at);
        document.getElementById('updatedAt').textContent = AdminConfig.formatDate(productData.updated_at);

        // Load images
        renderImages(productData.images || []);

        // Update impact preview
        updateImpactPreview();

    } catch (error) {
        console.error('Error loading product:', error);
        AdminConfig.showToast('Erreur de chargement du produit', 'error');
    }
}

function fillFormField(id, value) {
    const field = document.getElementById(id);
    if (field && value !== null && value !== undefined) {
        field.value = value;
    }
}

function updateImpactPreview() {
    const quantity = document.getElementById('impact_quantity').value;
    const item = document.getElementById('impact_item').value;
    const school = document.getElementById('impact_school').value;

    const previewEl = document.getElementById('impactPreviewText');

    if (quantity && item) {
        let text = `Chaque achat offre ${quantity} ${item}`;
        if (school) {
            text += ` à ${school}`;
        }
        previewEl.textContent = text;
        previewEl.style.fontWeight = '500';
    } else {
        previewEl.textContent = 'Remplissez les champs ci-dessus pour voir l\'aperçu';
        previewEl.style.fontWeight = 'normal';
    }
}

async function saveProduct(publish = true) {
    const saveBtn = document.getElementById('saveBtn');
    const btnText = saveBtn.querySelector('.btn-text');
    const btnLoading = saveBtn.querySelector('.btn-loading');

    btnText.style.display = 'none';
    btnLoading.style.display = 'inline';
    saveBtn.disabled = true;

    try {
        const formData = collectFormData();

        if (publish && document.getElementById('is_active').value === 'true') {
            formData.is_active = true;
        }

        let result;
        if (isNewProduct) {
            result = await AdminAPI.createProduct(formData);
            productId = result.id;
            isNewProduct = false;

            // Update URL without reload
            window.history.replaceState({}, '', `product-edit.html?id=${productId}`);

            // Enable image upload
            document.getElementById('imagesHint').style.display = 'none';
            document.getElementById('uploadArea').style.display = 'block';

            document.getElementById('pageTitle').textContent = `Modifier: ${result.name}`;
            document.getElementById('previewBtn').style.display = 'inline-flex';
        } else {
            result = await AdminAPI.updateProduct(productId, formData);
        }

        AdminConfig.showToast('Produit sauvegardé', 'success');

        // Reload to get updated data
        await loadProduct();

    } catch (error) {
        console.error('Error saving product:', error);
        AdminConfig.showToast(error.message, 'error');
    } finally {
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
        saveBtn.disabled = false;
    }
}

function collectFormData() {
    const data = {
        name: document.getElementById('name').value,
        description: document.getElementById('description').value || null,
        short_description: document.getElementById('short_description').value || null,

        name_en: document.getElementById('name_en').value || null,
        description_en: document.getElementById('description_en').value || null,
        short_description_en: document.getElementById('short_description_en').value || null,

        name_ar: document.getElementById('name_ar').value || null,
        description_ar: document.getElementById('description_ar').value || null,
        short_description_ar: document.getElementById('short_description_ar').value || null,

        price_tnd: parseFloat(document.getElementById('price_tnd').value) || 0,
        price_eur: parseFloat(document.getElementById('price_eur').value) || null,
        compare_at_price: parseFloat(document.getElementById('compare_at_price').value) || null,
        cost_price: parseFloat(document.getElementById('cost_price').value) || null,

        sku: document.getElementById('sku').value || null,
        stock_quantity: parseInt(document.getElementById('stock_quantity').value) || 0,
        weight: parseInt(document.getElementById('weight').value) || null,
        track_inventory: document.getElementById('track_inventory').checked,

        category: parseInt(document.getElementById('category').value) || null,
        producer: parseInt(document.getElementById('producer').value) || null,

        is_active: document.getElementById('is_active').value === 'true',
        is_featured: document.getElementById('is_featured').checked,
        is_new: document.getElementById('is_new').checked,
        is_bestseller: document.getElementById('is_bestseller').checked,
        is_eco_friendly: document.getElementById('is_eco_friendly').checked,

        impact_quantity: parseInt(document.getElementById('impact_quantity').value) || null,
        impact_item: document.getElementById('impact_item').value || null,
        impact_school: document.getElementById('impact_school').value || null,

        meta_title: document.getElementById('meta_title').value || null,
        meta_description: document.getElementById('meta_description').value || null
    };

    if (document.getElementById('has_b2b_pricing').checked) {
        data.b2b_price_tnd = parseFloat(document.getElementById('b2b_price_tnd').value) || null;
        data.b2b_min_quantity = parseInt(document.getElementById('b2b_min_quantity').value) || null;
    }

    return data;
}

// === IMAGES ===

function renderImages(images) {
    const grid = document.getElementById('imagesGrid');

    if (!images.length) {
        grid.innerHTML = '';
        return;
    }

    grid.innerHTML = images.map(img => `
        <div class="image-item ${img.is_primary ? 'primary' : ''}" data-id="${img.id}">
            <img src="${img.image}" alt="">
            <div class="image-actions">
                ${!img.is_primary ? `
                    <button type="button" class="image-set-primary" onclick="setPrimaryImage(${img.id})" title="Définir comme principale">★</button>
                ` : ''}
                <button type="button" class="image-delete" onclick="deleteImage(${img.id})" title="Supprimer">×</button>
            </div>
            ${img.is_primary ? '<div class="primary-badge">Principale</div>' : ''}
        </div>
    `).join('');
}

function handleImageUpload(e) {
    const files = e.target.files;
    if (files.length) {
        uploadImages(files);
    }
}

async function uploadImages(files) {
    if (!productId) {
        AdminConfig.showToast('Sauvegardez le produit d\'abord', 'warning');
        return;
    }

    for (let i = 0; i < files.length; i++) {
        const file = files[i];

        try {
            const result = await AdminAPI.uploadProductImage(productId, file, i === 0 && !productData.images?.length);
            AdminConfig.showToast(`Image téléchargée`, 'success');
        } catch (error) {
            AdminConfig.showToast(`Erreur: ${error.message}`, 'error');
        }
    }

    // Reload product to get updated images
    await loadProduct();
}

async function deleteImage(imageId) {
    if (!confirm('Supprimer cette image ?')) return;

    try {
        await AdminAPI.deleteProductImage(productId, imageId);
        AdminConfig.showToast('Image supprimée', 'success');
        await loadProduct();
    } catch (error) {
        AdminConfig.showToast(error.message, 'error');
    }
}

async function setPrimaryImage(imageId) {
    try {
        await AdminAPI.setPrimaryImage(productId, imageId);
        AdminConfig.showToast('Image principale définie', 'success');
        await loadProduct();
    } catch (error) {
        AdminConfig.showToast(error.message, 'error');
    }
}
