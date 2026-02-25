/**
 * Email Status Checker for Registration
 * Provides real-time feedback on email sending status
 */

class EmailStatusChecker {
    constructor(email, emailType = 'verification') {
        this.email = email;
        this.emailType = emailType;
        this.checkInterval = null;
        this.maxAttempts = 30; // Check for 5 minutes max
        this.attempts = 0;
    }

    async checkStatus() {
        try {
            const response = await fetch(`/accounts/api/check-email-status/?email=${encodeURIComponent(this.email)}&type=${this.emailType}`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error checking email status:', error);
            return { status: 'error', message: error.message };
        }
    }

    updateUI(statusData) {
        const statusElement = document.getElementById('email-status');
        const spinnerElement = document.getElementById('email-status-spinner');
        const messageElement = document.getElementById('email-status-message');

        if (!statusElement) return;

        switch (statusData.status) {
            case 'pending':
                this.showPendingStatus(spinnerElement, messageElement);
                break;
            case 'sent':
                this.showSuccessStatus(statusElement, messageElement);
                this.stopChecking();
                break;
            case 'failed':
                this.showFailedStatus(statusElement, messageElement, statusData.error_message);
                this.stopChecking();
                break;
            case 'not_found':
                this.showNotFoundStatus(statusElement, messageElement);
                this.stopChecking();
                break;
            case 'error':
                this.showErrorStatus(statusElement, messageElement);
                this.stopChecking();
                break;
        }
    }

    showPendingStatus(spinnerElement, messageElement) {
        if (spinnerElement) spinnerElement.style.display = 'inline-block';
        if (messageElement) {
            messageElement.innerHTML = 'Sending verification email... <span class="text-muted">This usually takes 10-30 seconds</span>';
            messageElement.className = 'alert alert-info';
        }
    }

    showSuccessStatus(statusElement, messageElement) {
        if (spinnerElement) spinnerElement.style.display = 'none';
        if (messageElement) {
            messageElement.innerHTML = '<i class="fas fa-check-circle me-2"></i>Verification email sent successfully! Please check your inbox.';
            messageElement.className = 'alert alert-success';
        }
    }

    showFailedStatus(statusElement, messageElement, errorMessage) {
        if (spinnerElement) spinnerElement.style.display = 'none';
        if (messageElement) {
            messageElement.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i>Failed to send verification email. ${errorMessage ? `Error: ${errorMessage}` : 'Please try again or contact support.'}`;
            messageElement.className = 'alert alert-warning';
        }
    }

    showNotFoundStatus(statusElement, messageElement) {
        if (spinnerElement) spinnerElement.style.display = 'none';
        if (messageElement) {
            messageElement.innerHTML = '<i class="fas fa-info-circle me-2"></i>Email status not found. Please try registering again.';
            messageElement.className = 'alert alert-info';
        }
    }

    showErrorStatus(statusElement, messageElement) {
        if (spinnerElement) spinnerElement.style.display = 'none';
        if (messageElement) {
            messageElement.innerHTML = '<i class="fas fa-times-circle me-2"></i>Unable to check email status. Please refresh and try again.';
            messageElement.className = 'alert alert-danger';
        }
    }

    async startChecking() {
        if (this.checkInterval) return; // Already checking

        console.log('Starting email status checks for:', this.email);
        
        // Initial check after 2 seconds
        setTimeout(async () => {
            const status = await this.checkStatus();
            this.updateUI(status);
            
            if (status.status === 'pending') {
                // Continue checking every 3 seconds
                this.checkInterval = setInterval(async () => {
                    this.attempts++;
                    
                    if (this.attempts >= this.maxAttempts) {
                        this.updateUI({ status: 'timeout' });
                        this.stopChecking();
                        return;
                    }
                    
                    const currentStatus = await this.checkStatus();
                    this.updateUI(currentStatus);
                }, 3000);
            }
        }, 2000);
    }

    stopChecking() {
        if (this.checkInterval) {
            clearInterval(this.checkInterval);
            this.checkInterval = null;
        }
    }
}

// Auto-initialize on login page with verification parameters
document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const email = urlParams.get('email');
    const command = urlParams.get('command');
    const isAsync = urlParams.get('async') === 'true';

    // Only show status checker if we have email and it's an async registration
    if (email && command === 'verification' && isAsync) {
        const statusContainer = document.createElement('div');
        statusContainer.id = 'email-status-container';
        statusContainer.className = 'mb-3';
        statusContainer.innerHTML = `
            <div id="email-status" class="email-status-wrapper">
                <div class="d-flex align-items-center">
                    <span id="email-status-spinner" class="spinner-border spinner-border-sm me-2" style="display: none;"></span>
                    <span id="email-status-message" class="email-status-message"></span>
                </div>
            </div>
        `;

        // Insert after alerts or at the top of the form
        const alertsContainer = document.querySelector('.alert-container') || document.querySelector('form');
        if (alertsContainer) {
            alertsContainer.parentNode.insertBefore(statusContainer, alertsContainer);
        }

        // Start checking email status
        const checker = new EmailStatusChecker(email, 'verification');
        checker.startChecking();
    }
});

// CSS for email status
const emailStatusCSS = `
.email-status-wrapper {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 1rem;
}

.email-status-message {
    font-size: 14px;
    line-height: 1.5;
}

.alert {
    margin: 0;
    padding: 8px 12px;
    border-radius: 6px;
    font-weight: 500;
}

.alert-success {
    background-color: #d4edda;
    border-color: #c3e6cb;
    color: #155724;
}

.alert-warning {
    background-color: #fff3cd;
    border-color: #ffeaa7;
    color: #856404;
}

.alert-danger {
    background-color: #f8d7da;
    border-color: #f5c6cb;
    color: #721c24;
}

.alert-info {
    background-color: #d1ecf1;
    border-color: #bee5eb;
    color: #0c5460;
}

.spinner-border-sm {
    width: 1rem;
    height: 1rem;
    border-width: 0.2em;
}
`;

// Inject CSS
const style = document.createElement('style');
style.textContent = emailStatusCSS;
document.head.appendChild(style);
