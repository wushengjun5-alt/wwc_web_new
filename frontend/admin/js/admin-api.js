/**
 * WWC Admin API Client
 */

const AdminAPI = {
    // Base fetch with error handling
    async fetch(endpoint, options = {}) {
        const url = AdminConfig.apiUrl + endpoint;

        const defaultOptions = {
            headers: AdminConfig.getHeaders()
        };

        const response = await fetch(url, { ...defaultOptions, ...options });

        if (!response.ok) {
            if (response.status === 401 || response.status === 403) {
                AdminConfig.updateApiStatus('error', 'Clé API invalide');
                throw new Error('Authentification requise. Vérifiez votre clé API.');
            }
            const error = await response.json().catch(() => ({}));

            // Parse Django REST Framework validation errors
            let errorMessage = '';
            if (error.detail) {
                errorMessage = error.detail;
            } else if (error.non_field_errors) {
                errorMessage = error.non_field_errors.join(', ');
            } else if (typeof error === 'object') {
                // Field-specific errors
                const fieldErrors = [];
                for (const [field, messages] of Object.entries(error)) {
                    const fieldName = field.replace(/_/g, ' ');
                    const msgList = Array.isArray(messages) ? messages : [messages];
                    fieldErrors.push(`${fieldName}: ${msgList.join(', ')}`);
                }
                errorMessage = fieldErrors.join('\n') || `Erreur ${response.status}`;
            } else {
                errorMessage = `Erreur ${response.status}`;
            }

            throw new Error(errorMessage);
        }

        AdminConfig.updateApiStatus('connected');

        // Handle 204 No Content
        if (response.status === 204) {
            return null;
        }

        return response.json();
    },

    // GET request
    async get(endpoint) {
        return this.fetch(endpoint);
    },

    // POST request
    async post(endpoint, data) {
        return this.fetch(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    // PUT request
    async put(endpoint, data) {
        return this.fetch(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    // PATCH request
    async patch(endpoint, data) {
        return this.fetch(endpoint, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    },

    // DELETE request
    async delete(endpoint) {
        return this.fetch(endpoint, {
            method: 'DELETE'
        });
    },

    // Upload file
    async upload(endpoint, formData) {
        const url = AdminConfig.apiUrl + endpoint;
        const headers = {
            'Authorization': 'Api-Key ' + AdminConfig.getApiKey()
        };

        const response = await fetch(url, {
            method: 'POST',
            headers: headers,
            body: formData
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || 'Erreur upload');
        }

        return response.json();
    },

    // === PRODUCTS ===

    // Get products list
    async getProducts(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = '/admin/products/' + (queryString ? '?' + queryString : '');
        return this.get(endpoint);
    },

    // Get single product
    async getProduct(id) {
        return this.get(`/admin/products/${id}/`);
    },

    // Create product
    async createProduct(data) {
        return this.post('/admin/products/', data);
    },

    // Update product
    async updateProduct(id, data) {
        return this.patch(`/admin/products/${id}/`, data);
    },

    // Delete product
    async deleteProduct(id) {
        return this.delete(`/admin/products/${id}/`);
    },

    // Bulk action on products
    async bulkAction(action, productIds) {
        return this.post('/admin/products/bulk/', {
            action: action,
            product_ids: productIds
        });
    },

    // Duplicate product
    async duplicateProduct(id) {
        return this.post(`/admin/products/${id}/duplicate/`);
    },

    // Upload product image
    async uploadProductImage(productId, file, isPrimary = false) {
        const formData = new FormData();
        formData.append('image', file);
        formData.append('is_primary', isPrimary.toString());
        return this.upload(`/admin/products/${productId}/images/`, formData);
    },

    // Delete product image
    async deleteProductImage(productId, imageId) {
        return this.delete(`/admin/products/${productId}/images/${imageId}/`);
    },

    // Set primary image
    async setPrimaryImage(productId, imageId) {
        return this.patch(`/admin/products/${productId}/images/${imageId}/primary/`, {});
    },

    // === CATEGORIES ===

    async getCategories() {
        return this.get('/admin/categories/');
    },

    // === PRODUCERS ===

    async getProducers() {
        return this.get('/admin/producers/');
    },

    // === STATS ===

    async getStats() {
        return this.get('/admin/stats/');
    },

    // === TEST CONNECTION ===

    async testConnection() {
        try {
            await this.getStats();
            return true;
        } catch (error) {
            console.error('Connection test failed:', error);
            return false;
        }
    }
};
