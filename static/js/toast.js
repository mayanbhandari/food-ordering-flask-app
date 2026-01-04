/**
 * Toast Notification System
 * Provides user feedback for all actions
 */

class ToastNotification {
    constructor() {
        this.container = null;
        this.init();
    }

    init() {
        // Create toast container if it doesn't exist
        if (!document.getElementById('toast-container')) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            this.container.className = 'toast-container';
            this.container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                max-width: 400px;
            `;
            document.body.appendChild(this.container);
        } else {
            this.container = document.getElementById('toast-container');
        }
    }

    show(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        // Toast styles
        const baseStyles = `
            padding: 16px 20px;
            margin-bottom: 10px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            display: flex;
            align-items: center;
            justify-content: space-between;
            min-width: 300px;
            max-width: 400px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            font-weight: 500;
            line-height: 1.4;
            transform: translateX(100%);
            transition: transform 0.3s ease-in-out, opacity 0.3s ease-in-out;
            opacity: 0;
            position: relative;
            overflow: hidden;
        `;

        // Type-specific styles
        const typeStyles = {
            success: `
                background: linear-gradient(135deg, #4CAF50, #45a049);
                color: white;
                border-left: 4px solid #2E7D32;
            `,
            error: `
                background: linear-gradient(135deg, #f44336, #d32f2f);
                color: white;
                border-left: 4px solid #c62828;
            `,
            warning: `
                background: linear-gradient(135deg, #ff9800, #f57c00);
                color: white;
                border-left: 4px solid #ef6c00;
            `,
            info: `
                background: linear-gradient(135deg, #2196F3, #1976D2);
                color: white;
                border-left: 4px solid #1565C0;
            `
        };

        toast.style.cssText = baseStyles + typeStyles[type] || typeStyles.info;

        // Toast content
        const content = document.createElement('div');
        content.style.cssText = `
            display: flex;
            align-items: center;
            flex: 1;
        `;

        // Icon
        const icon = document.createElement('span');
        icon.style.cssText = `
            margin-right: 12px;
            font-size: 18px;
        `;
        
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        icon.textContent = icons[type] || icons.info;

        // Message
        const messageEl = document.createElement('span');
        messageEl.textContent = message;
        messageEl.style.cssText = `
            flex: 1;
        `;

        content.appendChild(icon);
        content.appendChild(messageEl);

        // Close button
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '×';
        closeBtn.style.cssText = `
            background: none;
            border: none;
            color: inherit;
            font-size: 20px;
            font-weight: bold;
            cursor: pointer;
            padding: 0;
            margin-left: 12px;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            transition: background-color 0.2s ease;
        `;
        
        closeBtn.addEventListener('mouseenter', () => {
            closeBtn.style.backgroundColor = 'rgba(255, 255, 255, 0.2)';
        });
        
        closeBtn.addEventListener('mouseleave', () => {
            closeBtn.style.backgroundColor = 'transparent';
        });

        closeBtn.addEventListener('click', () => {
            this.hide(toast);
        });

        toast.appendChild(content);
        toast.appendChild(closeBtn);

        // Add to container
        this.container.appendChild(toast);

        // Animate in
        setTimeout(() => {
            toast.style.transform = 'translateX(0)';
            toast.style.opacity = '1';
        }, 100);

        // Auto hide
        if (duration > 0) {
            setTimeout(() => {
                this.hide(toast);
            }, duration);
        }

        return toast;
    }

    hide(toast) {
        if (toast && toast.parentNode) {
            toast.style.transform = 'translateX(100%)';
            toast.style.opacity = '0';
            
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }
    }

    // Convenience methods
    success(message, duration = 5000) {
        return this.show(message, 'success', duration);
    }

    error(message, duration = 7000) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration = 6000) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration = 5000) {
        return this.show(message, 'info', duration);
    }
}

// Global instance
window.toast = new ToastNotification();


// Form submission feedback
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Processing...';
                
                // Re-enable after 3 seconds (in case of errors)
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.textContent = submitBtn.dataset.originalText || 'Submit';
                }, 3000);
            }
        });
    });
});

