// Utility functions for Prycegas Station

/**
 * Show a toast notification
 * @param {string} type - Type of notification (success, error, info, warning)
 * @param {string} title - Title of the notification
 * @param {string} message - Message content
 */
function showToast(type, title, message) {
    const toast = {
        id: Date.now(),
        type: type,
        title: title,
        message: message
    };
    window.dispatchEvent(new CustomEvent('toast', { detail: toast }));
}

/**
 * Show success toast
 * @param {string} title - Title of the notification
 * @param {string} message - Message content
 */
function showSuccess(title, message) {
    showToast('success', title, message);
}

/**
 * Show error toast
 * @param {string} title - Title of the notification
 * @param {string} message - Message content
 */
function showError(title, message) {
    showToast('error', title, message);
}

/**
 * Show info toast
 * @param {string} title - Title of the notification
 * @param {string} message - Message content
 */
function showInfo(title, message) {
    showToast('info', title, message);
}

/**
 * Show warning toast
 * @param {string} title - Title of the notification
 * @param {string} message - Message content
 */
function showWarning(title, message) {
    showToast('warning', title, message);
}

/**
 * Format currency for display
 * @param {number} amount - Amount to format
 * @param {string} currency - Currency symbol (default: ₱)
 * @returns {string} Formatted currency string
 */
function formatCurrency(amount, currency = '₱') {
    return `${currency}${parseFloat(amount).toLocaleString('en-PH', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    })}`;
}

/**
 * Format date for display
 * @param {string|Date} date - Date to format
 * @returns {string} Formatted date string
 */
function formatDate(date) {
    const d = new Date(date);
    return d.toLocaleDateString('en-PH', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

/**
 * Format datetime for display
 * @param {string|Date} datetime - Datetime to format
 * @returns {string} Formatted datetime string
 */
function formatDateTime(datetime) {
    const d = new Date(datetime);
    return d.toLocaleString('en-PH', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Confirm action with user
 * @param {string} message - Confirmation message
 * @param {Function} callback - Function to call if confirmed
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

/**
 * Handle HTMX errors globally
 */
document.addEventListener('htmx:responseError', function(event) {
    showError('Error', 'An error occurred while processing your request. Please try again.');
});

/**
 * Handle HTMX network errors
 */
document.addEventListener('htmx:sendError', function(event) {
    showError('Network Error', 'Unable to connect to the server. Please check your internet connection.');
});

/**
 * Show loading indicator for HTMX requests
 */
document.addEventListener('htmx:beforeRequest', function(event) {
    const target = event.target;
    if (target.classList.contains('btn-loading')) {
        target.disabled = true;
        target.innerHTML = '<svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>Loading...';
    }
});

/**
 * Hide loading indicator after HTMX requests
 */
document.addEventListener('htmx:afterRequest', function(event) {
    const target = event.target;
    if (target.classList.contains('btn-loading')) {
        target.disabled = false;
        // Restore original button text (should be stored in data attribute)
        const originalText = target.getAttribute('data-original-text');
        if (originalText) {
            target.innerHTML = originalText;
        }
    }
});

// Initialize button loading states
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.btn-loading').forEach(button => {
        button.setAttribute('data-original-text', button.innerHTML);
    });
});