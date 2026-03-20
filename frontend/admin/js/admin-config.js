/**
 * WWC Admin Configuration
 */

const AdminConfig = {
    // API Base URL - adjust if needed
    apiUrl: window.location.origin + '/api/v1',

    // Storage keys
    storageKeys: {
        apiKey: 'wwc_admin_api_key'
    },

    // Get API Key from localStorage
    getApiKey: function() {
        return localStorage.getItem(this.storageKeys.apiKey) || '';
    },

    // Set API Key in localStorage
    setApiKey: function(key) {
        localStorage.setItem(this.storageKeys.apiKey, key);
    },

    // Get default API headers
    getHeaders: function() {
        const headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };

        const apiKey = this.getApiKey();
        if (apiKey) {
            headers['Authorization'] = 'Api-Key ' + apiKey;
        }

        return headers;
    },

    // Format date
    formatDate: function(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleDateString('fr-FR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    },

    // Format currency
    formatPrice: function(price, currency = 'TND') {
        if (price === null || price === undefined) return '-';
        const formatted = parseFloat(price).toFixed(2);
        return currency === 'TND' ? `${formatted} DT` : `${formatted} €`;
    },

    // Show toast notification
    showToast: function(message, type = 'success') {
        const container = document.getElementById('toastContainer');
        if (!container) {
            // Create container if not exists
            const newContainer = document.createElement('div');
            newContainer.className = 'toast-container';
            newContainer.id = 'toastContainer';
            document.body.appendChild(newContainer);
        }

        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠'
        };

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <span class="toast-icon">${icons[type] || icons.success}</span>
            <span class="toast-message">${message}</span>
            <button class="toast-close" onclick="this.parentElement.remove()">×</button>
        `;

        document.getElementById('toastContainer').appendChild(toast);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 5000);
    },

    // Update API status indicator
    updateApiStatus: function(status, message) {
        const statusEl = document.getElementById('apiStatus');
        if (!statusEl) return;

        const dot = statusEl.querySelector('.status-dot');
        const text = statusEl.querySelector('.status-text');

        dot.className = 'status-dot';
        if (status === 'connected') {
            dot.classList.add('connected');
            text.textContent = 'Connecté';
        } else if (status === 'error') {
            dot.classList.add('error');
            text.textContent = message || 'Erreur';
        } else {
            text.textContent = message || 'Connexion...';
        }
    },

    // Get URL parameters
    getUrlParams: function() {
        return new URLSearchParams(window.location.search);
    },

    // Debounce function
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// Initialize API key input on all pages
document.addEventListener('DOMContentLoaded', function() {
    const apiKeyInput = document.getElementById('apiKey');
    const saveApiKeyBtn = document.getElementById('saveApiKey');

    if (apiKeyInput) {
        apiKeyInput.value = AdminConfig.getApiKey();

        if (saveApiKeyBtn) {
            saveApiKeyBtn.addEventListener('click', function() {
                AdminConfig.setApiKey(apiKeyInput.value);
                AdminConfig.showToast('Clé API sauvegardée', 'success');
                location.reload();
            });
        }
    }

    // Mobile menu toggle
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.querySelector('.sidebar');

    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('open');
        });
    }
});
