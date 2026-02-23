// Utility functions for Prycegas Station

// Toast notification helper
function showToast(type, title, message) {
    const event = new CustomEvent('toast', {
        detail: {
            id: Date.now(),
            type: type, // 'success', 'error', 'info'
            title: title,
            message: message
        }
    });
    window.dispatchEvent(event);
}

// Enhanced form validation helpers
function validateEmail(email) {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
}

function validatePhone(phone) {
    // Philippine phone number validation
    const cleanPhone = phone.replace(/\s/g, '');
    const phoneRegex = /^(\+63|0)[0-9]{10}$/;
    return phoneRegex.test(cleanPhone);
}

function validateUsername(username) {
    if (!username || username.length < 3 || username.length > 30) {
        return { valid: false, message: 'Username must be 3-30 characters long.' };
    }
    
    const usernameRegex = /^[a-zA-Z0-9_]+$/;
    if (!usernameRegex.test(username)) {
        return { valid: false, message: 'Username can only contain letters, numbers, and underscores.' };
    }
    
    return { valid: true, message: 'Username format is valid.' };
}

function validatePassword(password) {
    const errors = [];
    
    if (!password || password.length < 8) {
        errors.push('at least 8 characters');
    }
    
    if (!/[A-Z]/.test(password)) {
        errors.push('one uppercase letter');
    }
    
    if (!/[a-z]/.test(password)) {
        errors.push('one lowercase letter');
    }
    
    if (!/[0-9]/.test(password)) {
        errors.push('one number');
    }
    
    if (errors.length > 0) {
        return { 
            valid: false, 
            message: `Password must contain ${errors.join(', ')}.` 
        };
    }
    
    return { valid: true, message: 'Password strength is good.' };
}

function sanitizeInput(input) {
    // Basic HTML sanitization
    const div = document.createElement('div');
    div.textContent = input;
    return div.innerHTML.trim();
}

function validateRequired(value, fieldName) {
    if (!value || value.trim().length === 0) {
        return { valid: false, message: `${fieldName} is required.` };
    }
    return { valid: true, message: '' };
}

function validateLength(value, min, max, fieldName) {
    if (value && (value.length < min || value.length > max)) {
        return { 
            valid: false, 
            message: `${fieldName} must be between ${min} and ${max} characters.` 
        };
    }
    return { valid: true, message: '' };
}

function validateNumeric(value, min, max, fieldName) {
    const num = parseFloat(value);
    if (isNaN(num)) {
        return { valid: false, message: `${fieldName} must be a valid number.` };
    }
    
    if (min !== undefined && num < min) {
        return { valid: false, message: `${fieldName} must be at least ${min}.` };
    }
    
    if (max !== undefined && num > max) {
        return { valid: false, message: `${fieldName} cannot exceed ${max}.` };
    }
    
    return { valid: true, message: '' };
}

// HTMX error handling
document.addEventListener('htmx:responseError', function (event) {
    showToast('error', 'Request Failed', 'An error occurred while processing your request.');
});

document.addEventListener('htmx:timeout', function (event) {
    showToast('error', 'Request Timeout', 'The request took too long to complete.');
});

// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert-auto-dismiss');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.opacity = '0';
            setTimeout(function () {
                alert.remove();
            }, 300);
        }, 5000);
    });
});

// Order form enhancements
document.addEventListener('DOMContentLoaded', function () {
    // Handle order form submission success
    document.addEventListener('htmx:afterRequest', function (event) {
        if (event.detail.target.id === 'form-messages' && event.detail.xhr.status === 200) {
            try {
                const response = JSON.parse(event.detail.xhr.responseText);
                if (response.success) {
                    showToast('success', 'Order Placed Successfully!', response.message);
                    // Redirect after showing toast
                    if (response.redirect) {
                        setTimeout(() => {
                            window.location.href = response.redirect;
                        }, 2000);
                    }
                } else {
                    showToast('error', 'Order Failed', response.message);
                }
            } catch (e) {
                // Response might be HTML with form errors, let HTMX handle it
                console.log('Form response received');
            }
        }
    });

    // Handle stock checking responses
    document.addEventListener('htmx:afterRequest', function (event) {
        if (event.detail.target.id === 'stock-info') {
            // Stock info updated successfully
            console.log('Stock info updated');
        }
    });
});

// Prevent double form submission
document.addEventListener('DOMContentLoaded', function () {
    const forms = document.querySelectorAll('form');
    forms.forEach(function (form) {
        form.addEventListener('submit', function (event) {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton && !submitButton.disabled) {
                setTimeout(function () {
                    submitButton.disabled = true;
                    submitButton.innerHTML = 'Processing...';
                }, 100);
            }
        });
    });
});

// Dealer Dashboard Utilities
class DealerDashboard {
    constructor() {
        this.refreshInterval = null;
        this.autoRefreshEnabled = false;
        this.init();
    }

    init() {
        // Initialize dashboard functionality
        this.setupAutoRefresh();
    }

    setupAutoRefresh() {
        // Auto-refresh functionality for dashboard
        const refreshToggle = document.querySelector('[x-model="autoRefresh"]');
        if (refreshToggle) {
            this.autoRefreshEnabled = refreshToggle.checked;
        }
    }

    startAutoRefresh(interval = 30000) {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        this.refreshInterval = setInterval(() => {
            this.refreshDashboardData();
        }, interval);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    refreshDashboardData() {
        // Use HTMX to refresh dashboard sections
        if (typeof htmx !== 'undefined') {
            const dashboardStats = document.getElementById('dashboard-stats');
            const recentActivity = document.getElementById('recent-activity');

            if (dashboardStats) {
                htmx.trigger(dashboardStats, 'refresh');
            }
            if (recentActivity) {
                htmx.trigger(recentActivity, 'refresh');
            }
        } else {
            // Fallback to page reload
            window.location.reload();
        }
    }

    // Manual refresh method
    manualRefresh() {
        this.refreshDashboardData();
        showToast('info', 'Dashboard Refreshed', 'Data has been updated');
    }
}

// Initialize dealer dashboard if on dealer pages
document.addEventListener('DOMContentLoaded', function () {
    if (document.querySelector('.dealer-dashboard') || window.location.pathname.includes('/dealer/')) {
        window.dealerDashboard = new DealerDashboard();
    }
});

// Enhanced HTMX error handling for dealer operations
document.addEventListener('htmx:responseError', function (event) {
    const target = event.detail.target;
    
    // Special handling for dealer dashboard refreshes
    if (target && (target.id === 'dashboard-stats' || target.id === 'recent-activity')) {
        showToast('error', 'Dashboard Update Failed', 'Unable to refresh dashboard data. Please try again.');
        // Reset opacity and pointer events
        target.style.opacity = '1';
        target.style.pointerEvents = 'auto';
    } else {
        showToast('error', 'Request Failed', 'An error occurred while processing your request.');
    }
});

// Utility function for formatting currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-PH', {
        style: 'currency',
        currency: 'PHP',
        minimumFractionDigits: 2
    }).format(amount);
}

// Utility function for formatting relative time
function formatRelativeTime(date) {
    const now = new Date();
    const diffInSeconds = Math.floor((now - new Date(date)) / 1000);
    
    if (diffInSeconds < 60) return 'just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
    return `${Math.floor(diffInSeconds / 86400)} days ago`;
}
// Enhanced form validation class with comprehensive security measures
class FormValidator {
    constructor(formElement) {
        this.form = formElement;
        this.errors = {};
        this.isValid = true;
        this.validationRules = {};
        this.securityConfig = {
            maxInputLength: 10000,
            allowedTags: [],
            rateLimitEnabled: true,
            csrfRequired: true
        };
        this.init();
    }

    init() {
        // Verify CSRF token presence
        if (this.securityConfig.csrfRequired && !this.hasValidCSRFToken()) {
            console.error('CSRF token missing or invalid');
            this.showSecurityError('Security token missing. Please refresh the page.');
            return;
        }

        // Add real-time validation to form fields
        const inputs = this.form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            // Add security attributes
            this.addSecurityAttributes(input);
            
            // Real-time validation events
            input.addEventListener('blur', () => this.validateField(input));
            input.addEventListener('input', (e) => this.handleInput(e));
            input.addEventListener('paste', (e) => this.handlePaste(e));
            
            // Security event listeners
            input.addEventListener('keydown', (e) => this.handleKeydown(e));
        });

        // Add form submission validation with security checks
        this.form.addEventListener('submit', (e) => this.validateForm(e));
        
        // Add rate limiting protection
        if (this.securityConfig.rateLimitEnabled) {
            this.setupRateLimiting();
        }
    }

    validateField(field) {
        const fieldName = field.name;
        const value = field.value;
        let validation = { valid: true, message: '' };

        // Clear previous errors
        this.clearFieldError(field);

        // Security validation first
        const securityCheck = this.performSecurityValidation(field, value);
        if (!securityCheck.valid) {
            validation = securityCheck;
        }
        // Required field validation
        else if (field.hasAttribute('required') && !value.trim()) {
            validation = { valid: false, message: `${this.getFieldLabel(field)} is required.` };
        }
        // Email validation with enhanced security
        else if (field.type === 'email' && value && !this.validateEmailSecure(value)) {
            validation = { valid: false, message: 'Please enter a valid email address.' };
        }
        // Phone validation with sanitization
        else if (field.name === 'phone_number' && value && !this.validatePhoneSecure(value)) {
            validation = { valid: false, message: 'Please enter a valid Philippine phone number.' };
        }
        // Username validation with security checks
        else if (field.name === 'username' && value) {
            validation = this.validateUsernameSecure(value);
        }
        // Password validation with strength requirements
        else if (field.name === 'password1' && value) {
            validation = this.validatePasswordSecure(value);
        }
        // Password confirmation with timing attack protection
        else if (field.name === 'password2' && value) {
            const password1 = this.form.querySelector('[name="password1"]');
            if (password1) {
                validation = this.validatePasswordMatch(value, password1.value);
            }
        }
        // Numeric validation with bounds checking
        else if (field.type === 'number' && value) {
            const min = field.getAttribute('min');
            const max = field.getAttribute('max');
            validation = this.validateNumericSecure(value, min ? parseFloat(min) : undefined, 
                                                   max ? parseFloat(max) : undefined, 
                                                   this.getFieldLabel(field));
        }
        // Text area validation with content filtering
        else if (field.tagName === 'TEXTAREA' && value) {
            validation = this.validateTextAreaSecure(field, value);
        }
        // Length validation with security bounds
        else if (value) {
            const minLength = field.getAttribute('minlength');
            const maxLength = field.getAttribute('maxlength');
            if (minLength || maxLength) {
                validation = this.validateLengthSecure(value, 
                                                     minLength ? parseInt(minLength) : 0,
                                                     maxLength ? parseInt(maxLength) : this.securityConfig.maxInputLength,
                                                     this.getFieldLabel(field));
            }
        }

        // Store validation result
        if (!validation.valid) {
            this.showFieldError(field, validation.message);
            this.errors[fieldName] = validation.message;
            this.logValidationEvent(fieldName, 'error', validation.message);
        } else {
            this.showFieldSuccess(field, validation.message);
            delete this.errors[fieldName];
            this.logValidationEvent(fieldName, 'success', '');
        }

        return validation.valid;
    }

    validateForm(event) {
        this.errors = {};
        this.isValid = true;

        // Security pre-checks
        if (!this.performSecurityPreChecks()) {
            event.preventDefault();
            this.showSecurityError('Security validation failed. Please refresh the page and try again.');
            return false;
        }

        // Rate limiting check
        if (this.securityConfig.rateLimitEnabled && !formSubmissionLimiter.canMakeRequest()) {
            event.preventDefault();
            this.showSecurityError('Too many requests. Please wait before submitting again.');
            return false;
        }

        // Validate all fields
        const inputs = this.form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            if (!this.validateField(input)) {
                this.isValid = false;
            }
        });

        // Additional form-level validation
        if (this.isValid) {
            this.isValid = this.performFormLevelValidation();
        }

        // Prevent submission if validation fails
        if (!this.isValid) {
            event.preventDefault();
            this.showFormErrors();
            return false;
        }

        // Final security sanitization before submission
        this.sanitizeFormData();

        return true;
    }

    // Enhanced security validation methods
    performSecurityValidation(field, value) {
        // Check for suspicious patterns
        const suspiciousPatterns = [
            /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
            /javascript:/gi,
            /on\w+\s*=/gi,
            /data:text\/html/gi,
            /vbscript:/gi,
            /<iframe/gi,
            /<object/gi,
            /<embed/gi,
            /expression\s*\(/gi
        ];

        for (const pattern of suspiciousPatterns) {
            if (pattern.test(value)) {
                return { 
                    valid: false, 
                    message: 'Invalid characters detected. Please remove any script or HTML content.' 
                };
            }
        }

        // Check input length
        if (value.length > this.securityConfig.maxInputLength) {
            return { 
                valid: false, 
                message: `Input too long. Maximum ${this.securityConfig.maxInputLength} characters allowed.` 
            };
        }

        // Check for null bytes and control characters
        if (/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/.test(value)) {
            return { 
                valid: false, 
                message: 'Invalid characters detected.' 
            };
        }

        return { valid: true, message: '' };
    }

    validateEmailSecure(email) {
        // Enhanced email validation with security checks
        const sanitizedEmail = this.sanitizeInput(email.toLowerCase().trim());
        
        // Basic format validation
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if (!emailRegex.test(sanitizedEmail)) {
            return false;
        }

        // Check for suspicious patterns in email
        const suspiciousEmailPatterns = [
            /\.\./,  // Double dots
            /^\./, // Starting with dot
            /\.$/, // Ending with dot
            /@.*@/, // Multiple @ symbols
            /[<>]/  // Angle brackets
        ];

        return !suspiciousEmailPatterns.some(pattern => pattern.test(sanitizedEmail));
    }

    validatePhoneSecure(phone) {
        // Sanitize phone number
        const sanitizedPhone = phone.replace(/[^\d+]/g, '');
        
        // Philippine phone number validation
        const phoneRegex = /^(\+63|0)[0-9]{10}$/;
        return phoneRegex.test(sanitizedPhone);
    }

    validateUsernameSecure(username) {
        const sanitizedUsername = this.sanitizeInput(username.trim());
        
        // Length check
        if (sanitizedUsername.length < 3 || sanitizedUsername.length > 30) {
            return { valid: false, message: 'Username must be 3-30 characters long.' };
        }
        
        // Character validation
        const usernameRegex = /^[a-zA-Z0-9_]+$/;
        if (!usernameRegex.test(sanitizedUsername)) {
            return { valid: false, message: 'Username can only contain letters, numbers, and underscores.' };
        }

        // Check for reserved usernames
        const reservedUsernames = ['admin', 'root', 'administrator', 'system', 'api', 'www', 'mail', 'ftp'];
        if (reservedUsernames.includes(sanitizedUsername.toLowerCase())) {
            return { valid: false, message: 'This username is not available.' };
        }
        
        return { valid: true, message: 'Username format is valid.' };
    }

    validatePasswordSecure(password) {
        const errors = [];
        
        if (!password || password.length < 8) {
            errors.push('at least 8 characters');
        }
        
        if (!/[A-Z]/.test(password)) {
            errors.push('one uppercase letter');
        }
        
        if (!/[a-z]/.test(password)) {
            errors.push('one lowercase letter');
        }
        
        if (!/[0-9]/.test(password)) {
            errors.push('one number');
        }

        // Check for common weak passwords
        const commonPasswords = ['password', '12345678', 'qwerty123', 'admin123'];
        if (commonPasswords.includes(password.toLowerCase())) {
            errors.push('a stronger password (avoid common passwords)');
        }

        // Check for sequential characters
        if (/123456|abcdef|qwerty/i.test(password)) {
            errors.push('avoid sequential characters');
        }
        
        if (errors.length > 0) {
            return { 
                valid: false, 
                message: `Password must contain ${errors.join(', ')}.` 
            };
        }
        
        return { valid: true, message: 'Password strength is good.' };
    }

    validatePasswordMatch(password2, password1) {
        // Use constant-time comparison to prevent timing attacks
        if (password1.length !== password2.length) {
            return { valid: false, message: 'Passwords do not match.' };
        }

        let match = true;
        for (let i = 0; i < password1.length; i++) {
            if (password1.charCodeAt(i) !== password2.charCodeAt(i)) {
                match = false;
            }
        }

        return match ? 
            { valid: true, message: 'Passwords match.' } : 
            { valid: false, message: 'Passwords do not match.' };
    }

    validateNumericSecure(value, min, max, fieldName) {
        const num = parseFloat(value);
        
        if (isNaN(num)) {
            return { valid: false, message: `${fieldName} must be a valid number.` };
        }

        // Check for infinity and extreme values
        if (!isFinite(num)) {
            return { valid: false, message: `${fieldName} must be a finite number.` };
        }
        
        if (min !== undefined && num < min) {
            return { valid: false, message: `${fieldName} must be at least ${min}.` };
        }
        
        if (max !== undefined && num > max) {
            return { valid: false, message: `${fieldName} cannot exceed ${max}.` };
        }
        
        return { valid: true, message: '' };
    }

    validateTextAreaSecure(field, value) {
        const sanitizedValue = this.sanitizeInput(value);
        const fieldName = this.getFieldLabel(field);
        
        // Check for minimum length if specified
        const minLength = field.getAttribute('minlength');
        if (minLength && sanitizedValue.length < parseInt(minLength)) {
            return { 
                valid: false, 
                message: `${fieldName} must be at least ${minLength} characters long.` 
            };
        }

        // Check for maximum length
        const maxLength = field.getAttribute('maxlength') || this.securityConfig.maxInputLength;
        if (sanitizedValue.length > parseInt(maxLength)) {
            return { 
                valid: false, 
                message: `${fieldName} cannot exceed ${maxLength} characters.` 
            };
        }

        return { valid: true, message: '' };
    }

    validateLengthSecure(value, min, max, fieldName) {
        const sanitizedValue = this.sanitizeInput(value);
        
        if (sanitizedValue.length < min) {
            return { 
                valid: false, 
                message: `${fieldName} must be at least ${min} characters long.` 
            };
        }
        
        if (sanitizedValue.length > max) {
            return { 
                valid: false, 
                message: `${fieldName} cannot exceed ${max} characters.` 
            };
        }
        
        return { valid: true, message: '' };
    }

    // Security helper methods
    hasValidCSRFToken() {
        const token = this.form.querySelector('[name=csrfmiddlewaretoken]');
        return token && token.value && token.value.length > 0;
    }

    performSecurityPreChecks() {
        // Check CSRF token
        if (this.securityConfig.csrfRequired && !this.hasValidCSRFToken()) {
            return false;
        }

        // Check form integrity
        const requiredFields = this.form.querySelectorAll('[required]');
        for (const field of requiredFields) {
            if (!field.name || field.name.length === 0) {
                return false;
            }
        }

        return true;
    }

    performFormLevelValidation() {
        // Custom form-level validation rules
        const formType = this.form.dataset.formType || this.detectFormType();
        
        switch (formType) {
            case 'registration':
                return this.validateRegistrationForm();
            case 'order':
                return this.validateOrderForm();
            case 'delivery':
                return this.validateDeliveryForm();
            default:
                return true;
        }
    }

    validateRegistrationForm() {
        const password1 = this.form.querySelector('[name="password1"]');
        const password2 = this.form.querySelector('[name="password2"]');
        const email = this.form.querySelector('[name="email"]');
        
        // Additional password security checks
        if (password1 && email && password1.value.toLowerCase().includes(email.value.split('@')[0].toLowerCase())) {
            this.errors['password1'] = 'Password should not contain parts of your email address.';
            return false;
        }

        return true;
    }

    validateOrderForm() {
        const product = this.form.querySelector('[name="product"]');
        const quantity = this.form.querySelector('[name="quantity"]');
        const deliveryType = this.form.querySelector('[name="delivery_type"]:checked');
        const deliveryAddress = this.form.querySelector('[name="delivery_address"]');
        
        // Validate delivery address for delivery orders
        if (deliveryType && deliveryType.value === 'delivery') {
            if (!deliveryAddress || !deliveryAddress.value.trim()) {
                this.errors['delivery_address'] = 'Delivery address is required for delivery orders.';
                return false;
            }
        }

        return true;
    }

    validateDeliveryForm() {
        const quantity = this.form.querySelector('[name="quantity_received"]');
        const costPerUnit = this.form.querySelector('[name="cost_per_unit"]');
        const totalCost = this.form.querySelector('[name="total_cost"]');
        
        // Validate cost calculation
        if (quantity && costPerUnit && totalCost) {
            const expectedTotal = parseFloat(quantity.value) * parseFloat(costPerUnit.value);
            const actualTotal = parseFloat(totalCost.value);
            
            if (Math.abs(expectedTotal - actualTotal) > 0.01) {
                this.errors['total_cost'] = 'Total cost calculation is incorrect.';
                return false;
            }
        }

        return true;
    }

    detectFormType() {
        if (this.form.querySelector('[name="username"]') && this.form.querySelector('[name="password1"]')) {
            return 'registration';
        }
        if (this.form.querySelector('[name="product"]') && this.form.querySelector('[name="quantity"]')) {
            return 'order';
        }
        if (this.form.querySelector('[name="quantity_received"]')) {
            return 'delivery';
        }
        return 'generic';
    }

    sanitizeFormData() {
        const inputs = this.form.querySelectorAll('input, textarea');
        inputs.forEach(input => {
            if (input.type !== 'password' && input.type !== 'hidden') {
                input.value = this.sanitizeInput(input.value);
            }
        });
    }

    sanitizeInput(input) {
        if (typeof input !== 'string') return input;
        
        // Remove HTML tags and dangerous characters
        return input
            .replace(/<[^>]*>/g, '') // Remove HTML tags
            .replace(/[<>'"&]/g, '') // Remove dangerous characters
            .trim();
    }

    addSecurityAttributes(input) {
        // Add security attributes to prevent common attacks
        input.setAttribute('autocomplete', input.getAttribute('autocomplete') || 'off');
        input.setAttribute('spellcheck', 'false');
        
        // Prevent drag and drop for sensitive fields
        if (input.type === 'password' || input.name === 'username') {
            input.addEventListener('dragstart', (e) => e.preventDefault());
            input.addEventListener('drop', (e) => e.preventDefault());
        }
    }

    handleInput(event) {
        const field = event.target;
        
        // Clear field error on input
        this.clearFieldError(field);
        
        // Debounced validation for better performance
        clearTimeout(field.validationTimeout);
        field.validationTimeout = setTimeout(() => {
            this.validateField(field);
        }, 300);
    }

    handlePaste(event) {
        const field = event.target;
        const pastedData = (event.clipboardData || window.clipboardData).getData('text');
        
        // Security check on pasted content
        const securityCheck = this.performSecurityValidation(field, pastedData);
        if (!securityCheck.valid) {
            event.preventDefault();
            this.showFieldError(field, 'Pasted content contains invalid characters.');
            return;
        }

        // Validate after paste
        setTimeout(() => {
            this.validateField(field);
        }, 10);
    }

    handleKeydown(event) {
        const field = event.target;
        
        // Prevent certain key combinations that might be used for attacks
        if (event.ctrlKey && (event.key === 'v' || event.key === 'V')) {
            // Allow paste but validate it
            setTimeout(() => {
                this.validateField(field);
            }, 10);
        }
    }

    setupRateLimiting() {
        let submitAttempts = 0;
        const maxAttempts = 5;
        const resetTime = 60000; // 1 minute
        
        this.form.addEventListener('submit', (event) => {
            submitAttempts++;
            
            if (submitAttempts > maxAttempts) {
                event.preventDefault();
                this.showSecurityError('Too many submission attempts. Please wait before trying again.');
                return false;
            }
            
            // Reset counter after time period
            setTimeout(() => {
                submitAttempts = Math.max(0, submitAttempts - 1);
            }, resetTime);
        });
    }

    logValidationEvent(fieldName, type, message) {
        // Log validation events for security monitoring
        if (console && console.log) {
            console.log(`Validation ${type} for ${fieldName}: ${message}`);
        }
    }

    showFieldError(field, message) {
        field.classList.add('border-red-500', 'focus:border-red-500', 'focus:ring-red-500');
        field.classList.remove('border-green-500', 'focus:border-green-500', 'focus:ring-green-500');
        
        // Remove existing error message
        this.clearFieldError(field);
        
        // Add error message with security icon for security-related errors
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error mt-1 text-sm text-red-600 flex items-center';
        
        if (message.includes('Invalid characters') || message.includes('Security')) {
            errorDiv.innerHTML = `
                <svg class="w-4 h-4 mr-1 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                </svg>
                <span>${message}</span>
            `;
        } else {
            errorDiv.textContent = message;
        }
        
        field.parentNode.appendChild(errorDiv);
    }

    showFieldSuccess(field, message) {
        if (field.value.trim()) {
            field.classList.add('border-green-500', 'focus:border-green-500', 'focus:ring-green-500');
            field.classList.remove('border-red-500', 'focus:border-red-500', 'focus:ring-red-500');
            
            if (message && message !== '') {
                // Remove existing success message
                const existingSuccess = field.parentNode.querySelector('.field-success');
                if (existingSuccess) {
                    existingSuccess.remove();
                }
                
                // Add success message
                const successDiv = document.createElement('div');
                successDiv.className = 'field-success mt-1 text-sm text-green-600';
                successDiv.textContent = message;
                field.parentNode.appendChild(successDiv);
            }
        }
    }

    clearFieldError(field) {
        field.classList.remove('border-red-500', 'focus:border-red-500', 'focus:ring-red-500',
                              'border-green-500', 'focus:border-green-500', 'focus:ring-green-500');
        
        // Remove error and success messages
        const errorMsg = field.parentNode.querySelector('.field-error');
        const successMsg = field.parentNode.querySelector('.field-success');
        if (errorMsg) errorMsg.remove();
        if (successMsg) successMsg.remove();
    }

    showFormErrors() {
        const errorCount = Object.keys(this.errors).length;
        if (errorCount > 0) {
            showToast('error', 'Validation Error', 
                     `Please fix ${errorCount} error${errorCount > 1 ? 's' : ''} before submitting.`);
            
            // Focus on first error field
            const firstErrorField = this.form.querySelector('.border-red-500');
            if (firstErrorField) {
                firstErrorField.focus();
                firstErrorField.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    }

    showSecurityError(message) {
        showToast('error', 'Security Error', message);
        
        // Log security event
        console.warn('Security validation failed:', message);
        
        // Disable form temporarily
        const submitButton = this.form.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = true;
            setTimeout(() => {
                submitButton.disabled = false;
            }, 5000);
        }
    }

    getFieldLabel(field) {
        const label = this.form.querySelector(`label[for="${field.id}"]`);
        if (label) {
            return label.textContent.replace('*', '').trim();
        }
        return field.name.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
}

// CSRF Token helper
function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

// Enhanced AJAX form submission with validation
function submitFormWithValidation(form, options = {}) {
    const validator = new FormValidator(form);
    
    if (!validator.validateForm({ preventDefault: () => {} })) {
        return Promise.reject('Validation failed');
    }

    const formData = new FormData(form);
    const url = options.url || form.action;
    const method = options.method || form.method || 'POST';

    return fetch(url, {
        method: method,
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showToast('success', 'Success', data.message);
            if (options.onSuccess) {
                options.onSuccess(data);
            }
        } else {
            showToast('error', 'Error', data.message);
            if (options.onError) {
                options.onError(data);
            }
        }
        return data;
    })
    .catch(error => {
        console.error('Form submission error:', error);
        showToast('error', 'Error', 'An error occurred while submitting the form.');
        if (options.onError) {
            options.onError(error);
        }
        throw error;
    });
}

// Initialize form validation on page load
document.addEventListener('DOMContentLoaded', function() {
    // Auto-initialize validation for forms with validation class
    const formsToValidate = document.querySelectorAll('form.validate, form[data-validate="true"]');
    formsToValidate.forEach(form => {
        new FormValidator(form);
    });

    // Add validation to registration and login forms
    const authForms = document.querySelectorAll('form[method="post"]');
    authForms.forEach(form => {
        if (form.querySelector('[name="username"]') || form.querySelector('[name="email"]')) {
            new FormValidator(form);
        }
    });
});

// Security helpers
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

function validateCSRFToken() {
    const token = getCSRFToken();
    if (!token) {
        console.warn('CSRF token not found');
        return false;
    }
    return true;
}

// Rate limiting helper
class RateLimiter {
    constructor(maxRequests = 5, timeWindow = 60000) {
        this.maxRequests = maxRequests;
        this.timeWindow = timeWindow;
        this.requests = [];
    }

    canMakeRequest() {
        const now = Date.now();
        this.requests = this.requests.filter(time => now - time < this.timeWindow);
        
        if (this.requests.length >= this.maxRequests) {
            return false;
        }
        
        this.requests.push(now);
        return true;
    }
}

// Global rate limiter for form submissions
const formSubmissionLimiter = new RateLimiter(10, 60000); // 10 requests per minute

// Performance optimization utilities
class PerformanceOptimizer {
    constructor() {
        this.lazyLoadObserver = null;
        this.intersectionObserver = null;
        this.debounceTimers = new Map();
        this.cache = new Map();
        this.init();
    }

    init() {
        this.setupLazyLoading();
        this.setupImageOptimization();
        this.setupConnectionOptimization();
        this.setupCaching();
    }

    // Lazy loading for large datasets using HTMX
    setupLazyLoading() {
        if ('IntersectionObserver' in window) {
            this.lazyLoadObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const element = entry.target;
                        const loadUrl = element.dataset.lazyLoad;
                        
                        if (loadUrl && !element.dataset.loaded) {
                            element.dataset.loaded = 'true';
                            this.loadContent(element, loadUrl);
                            this.lazyLoadObserver.unobserve(element);
                        }
                    }
                });
            }, {
                rootMargin: '100px', // Load content 100px before it comes into view
                threshold: 0.1
            });

            // Observe all lazy load elements
            document.querySelectorAll('[data-lazy-load]').forEach(el => {
                this.lazyLoadObserver.observe(el);
            });
        }
    }

    loadContent(element, url) {
        // Show loading indicator
        element.innerHTML = `
            <div class="flex items-center justify-center py-8">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-prycegas-orange"></div>
                <span class="ml-3 text-gray-600">Loading...</span>
            </div>
        `;

        // Use HTMX to load content
        htmx.ajax('GET', url, {
            target: element,
            swap: 'innerHTML'
        }).catch(error => {
            element.innerHTML = `
                <div class="text-center py-8 text-red-600">
                    <p>Failed to load content. <button onclick="location.reload()" class="text-prycegas-orange underline">Retry</button></p>
                </div>
            `;
        });
    }

    // Image optimization for mobile devices
    setupImageOptimization() {
        const images = document.querySelectorAll('img[data-src]');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        imageObserver.unobserve(img);
                    }
                });
            });

            images.forEach(img => imageObserver.observe(img));
        } else {
            // Fallback for older browsers
            images.forEach(img => {
                img.src = img.dataset.src;
                img.classList.remove('lazy');
            });
        }
    }

    // Connection optimization for rural areas
    setupConnectionOptimization() {
        // Detect connection quality
        if ('connection' in navigator) {
            const connection = navigator.connection;
            
            // Adjust behavior based on connection
            if (connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g') {
                this.enableSlowConnectionMode();
            }

            // Listen for connection changes
            connection.addEventListener('change', () => {
                if (connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g') {
                    this.enableSlowConnectionMode();
                } else {
                    this.disableSlowConnectionMode();
                }
            });
        }

        // Preload critical resources
        this.preloadCriticalResources();
    }

    enableSlowConnectionMode() {
        document.body.classList.add('slow-connection');
        
        // Reduce auto-refresh frequency
        const autoRefreshElements = document.querySelectorAll('[data-auto-refresh]');
        autoRefreshElements.forEach(el => {
            const currentInterval = parseInt(el.dataset.autoRefresh) || 30000;
            el.dataset.autoRefresh = Math.max(currentInterval * 2, 60000); // At least 1 minute
        });

        // Disable non-essential animations
        const style = document.createElement('style');
        style.textContent = `
            .slow-connection * {
                animation-duration: 0.01ms !important;
                animation-delay: 0.01ms !important;
                transition-duration: 0.01ms !important;
                transition-delay: 0.01ms !important;
            }
        `;
        document.head.appendChild(style);

        showToast('info', 'Slow Connection Detected', 'Optimizing for better performance');
    }

    disableSlowConnectionMode() {
        document.body.classList.remove('slow-connection');
        
        // Restore normal auto-refresh frequency
        const autoRefreshElements = document.querySelectorAll('[data-auto-refresh]');
        autoRefreshElements.forEach(el => {
            el.dataset.autoRefresh = '30000'; // Back to 30 seconds
        });
    }

    preloadCriticalResources() {
        // Preload critical CSS and JS
        const criticalResources = [
            '/static/css/custom.css',
            '/static/js/utils.js'
        ];

        criticalResources.forEach(resource => {
            const link = document.createElement('link');
            link.rel = 'prefetch';
            link.href = resource;
            document.head.appendChild(link);
        });
    }

    // Caching for frequently accessed data
    setupCaching() {
        // Cache HTMX responses for frequently accessed endpoints
        document.addEventListener('htmx:beforeRequest', (event) => {
            const url = event.detail.requestConfig.url;
            const method = event.detail.requestConfig.verb;
            
            // Only cache GET requests
            if (method === 'GET') {
                const cacheKey = this.getCacheKey(url);
                const cached = this.cache.get(cacheKey);
                
                if (cached && !this.isCacheExpired(cached)) {
                    event.preventDefault();
                    event.detail.target.innerHTML = cached.content;
                    return;
                }
            }
        });

        document.addEventListener('htmx:afterRequest', (event) => {
            const url = event.detail.requestConfig.url;
            const method = event.detail.requestConfig.verb;
            
            // Cache successful GET responses
            if (method === 'GET' && event.detail.xhr.status === 200) {
                const cacheKey = this.getCacheKey(url);
                const content = event.detail.xhr.responseText;
                
                // Only cache if it's a cacheable endpoint
                if (this.isCacheable(url)) {
                    this.cache.set(cacheKey, {
                        content: content,
                        timestamp: Date.now(),
                        ttl: this.getCacheTTL(url)
                    });
                }
            }
        });
    }

    getCacheKey(url) {
        return btoa(url).replace(/[^a-zA-Z0-9]/g, '');
    }

    isCacheExpired(cached) {
        return Date.now() - cached.timestamp > cached.ttl;
    }

    isCacheable(url) {
        // Cache dashboard stats, inventory data, etc.
        const cacheablePatterns = [
            '/dealer/dashboard/stats/',
            '/dealer/inventory/',
            '/customer/dashboard/',
            '/api/products/'
        ];
        
        return cacheablePatterns.some(pattern => url.includes(pattern));
    }

    getCacheTTL(url) {
        // Different TTL for different types of data
        if (url.includes('dashboard/stats')) return 30000; // 30 seconds
        if (url.includes('inventory')) return 60000; // 1 minute
        if (url.includes('products')) return 300000; // 5 minutes
        return 30000; // Default 30 seconds
    }

    // Debounce utility for search and filters
    debounce(func, delay, key = 'default') {
        if (this.debounceTimers.has(key)) {
            clearTimeout(this.debounceTimers.get(key));
        }

        const timer = setTimeout(func, delay);
        this.debounceTimers.set(key, timer);
    }

    // Clear cache manually
    clearCache() {
        this.cache.clear();
        showToast('info', 'Cache Cleared', 'Data cache has been cleared');
    }

    // Get cache statistics
    getCacheStats() {
        return {
            size: this.cache.size,
            keys: Array.from(this.cache.keys())
        };
    }
}

// Database query optimization helpers
class QueryOptimizer {
    constructor() {
        this.queryCache = new Map();
        this.prefetchQueue = [];
    }

    // Prefetch related data
    prefetchRelatedData(type, id) {
        const prefetchUrls = this.getPrefetchUrls(type, id);
        
        prefetchUrls.forEach(url => {
            if (!this.queryCache.has(url)) {
                this.prefetchQueue.push(url);
            }
        });

        this.processPrefetchQueue();
    }

    getPrefetchUrls(type, id) {
        const urls = [];
        
        switch (type) {
            case 'order':
                urls.push(`/api/orders/${id}/customer/`);
                urls.push(`/api/orders/${id}/product/`);
                break;
            case 'customer':
                urls.push(`/api/customers/${id}/orders/`);
                urls.push(`/api/customers/${id}/profile/`);
                break;
            case 'product':
                urls.push(`/api/products/${id}/stock/`);
                urls.push(`/api/products/${id}/orders/`);
                break;
        }
        
        return urls;
    }

    processPrefetchQueue() {
        if (this.prefetchQueue.length === 0) return;

        const url = this.prefetchQueue.shift();
        
        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            this.queryCache.set(url, {
                data: data,
                timestamp: Date.now(),
                ttl: 300000 // 5 minutes
            });
        })
        .catch(error => {
            console.warn('Prefetch failed for:', url, error);
        })
        .finally(() => {
            // Process next item in queue
            setTimeout(() => this.processPrefetchQueue(), 100);
        });
    }
}

// Mobile optimization utilities
class MobileOptimizer {
    constructor() {
        this.touchStartY = 0;
        this.touchEndY = 0;
        this.init();
    }

    init() {
        this.optimizeForTouch();
        this.setupPullToRefresh();
        this.optimizeScrolling();
        this.setupOfflineSupport();
    }

    optimizeForTouch() {
        // Add touch-friendly classes to interactive elements
        const interactiveElements = document.querySelectorAll('button, a, input, select, textarea');
        
        interactiveElements.forEach(el => {
            if (!el.classList.contains('touch-optimized')) {
                el.classList.add('touch-optimized');
                
                // Ensure minimum touch target size (44px)
                const rect = el.getBoundingClientRect();
                if (rect.height < 44 || rect.width < 44) {
                    el.style.minHeight = '44px';
                    el.style.minWidth = '44px';
                }
            }
        });
    }

    setupPullToRefresh() {
        let startY = 0;
        let currentY = 0;
        let pullDistance = 0;
        const threshold = 100;

        document.addEventListener('touchstart', (e) => {
            if (window.scrollY === 0) {
                startY = e.touches[0].clientY;
            }
        });

        document.addEventListener('touchmove', (e) => {
            if (window.scrollY === 0 && startY > 0) {
                currentY = e.touches[0].clientY;
                pullDistance = currentY - startY;

                if (pullDistance > 0) {
                    e.preventDefault();
                    
                    // Visual feedback
                    const refreshIndicator = document.getElementById('pull-refresh-indicator');
                    if (refreshIndicator) {
                        refreshIndicator.style.transform = `translateY(${Math.min(pullDistance, threshold)}px)`;
                        refreshIndicator.style.opacity = Math.min(pullDistance / threshold, 1);
                    }
                }
            }
        });

        document.addEventListener('touchend', () => {
            if (pullDistance > threshold) {
                this.triggerRefresh();
            }
            
            // Reset
            startY = 0;
            pullDistance = 0;
            const refreshIndicator = document.getElementById('pull-refresh-indicator');
            if (refreshIndicator) {
                refreshIndicator.style.transform = 'translateY(0)';
                refreshIndicator.style.opacity = '0';
            }
        });
    }

    triggerRefresh() {
        // Trigger page refresh or HTMX reload
        if (typeof htmx !== 'undefined') {
            const mainContent = document.querySelector('main');
            if (mainContent) {
                htmx.ajax('GET', window.location.href, {
                    target: mainContent,
                    swap: 'innerHTML'
                });
            }
        } else {
            location.reload();
        }
        
        showToast('info', 'Refreshing', 'Updating content...');
    }

    optimizeScrolling() {
        // Smooth scrolling for better mobile experience
        document.documentElement.style.scrollBehavior = 'smooth';
        
        // Optimize scroll performance
        let ticking = false;
        
        function updateScrollPosition() {
            // Update any scroll-dependent UI elements
            const scrollTop = window.pageYOffset;
            const scrollPercent = scrollTop / (document.body.scrollHeight - window.innerHeight);
            
            // Update scroll indicator if present
            const scrollIndicator = document.querySelector('.scroll-indicator');
            if (scrollIndicator) {
                scrollIndicator.style.width = `${scrollPercent * 100}%`;
            }
            
            ticking = false;
        }
        
        document.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(updateScrollPosition);
                ticking = true;
            }
        });
    }

    setupOfflineSupport() {
        // Basic offline detection
        window.addEventListener('online', () => {
            showToast('success', 'Connection Restored', 'You are back online');
            document.body.classList.remove('offline');
        });

        window.addEventListener('offline', () => {
            showToast('error', 'Connection Lost', 'You are currently offline');
            document.body.classList.add('offline');
        });

        // Initial state
        if (!navigator.onLine) {
            document.body.classList.add('offline');
        }
    }
}

// Initialize performance optimizations
document.addEventListener('DOMContentLoaded', function() {
    window.performanceOptimizer = new PerformanceOptimizer();
    window.queryOptimizer = new QueryOptimizer();
    window.mobileOptimizer = new MobileOptimizer();
    
    // Add performance monitoring
    if ('performance' in window) {
        window.addEventListener('load', () => {
            setTimeout(() => {
                const perfData = performance.getEntriesByType('navigation')[0];
                console.log('Page load time:', perfData.loadEventEnd - perfData.loadEventStart, 'ms');
                
                // Report slow loading to help with optimization
                if (perfData.loadEventEnd - perfData.loadEventStart > 3000) {
                    console.warn('Slow page load detected. Consider optimizing resources.');
                }
            }, 0);
        });
    }
});

// Export utilities for use in other scripts
window.PrycegasUtils = {
    performanceOptimizer: () => window.performanceOptimizer,
    queryOptimizer: () => window.queryOptimizer,
    mobileOptimizer: () => window.mobileOptimizer,
    debounce: (func, delay, key) => window.performanceOptimizer?.debounce(func, delay, key),
    clearCache: () => window.performanceOptimizer?.clearCache(),
    prefetchData: (type, id) => window.queryOptimizer?.prefetchRelatedData(type, id)
};