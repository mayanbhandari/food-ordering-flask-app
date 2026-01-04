// Main JavaScript for JustEat

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Add to cart functionality
$(document).on('click', '.add-to-cart', function(e) {
    e.preventDefault();

    const button = $(this);
    const menuItemId = button.data('menu-item-id');

    // Find the input in the same row
    const quantity = parseInt(
        button.closest('.d-flex').find('input[type="number"]').val()
    ) || 1;

    console.log("Menu ID:", menuItemId, "Quantity:", quantity);

    $.ajax({
        url: '/customer/add-to-cart',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            menu_item_id: menuItemId,
            quantity: quantity
        }),
        success: function(response) {
            if (response.success) {
                showToast('success', 'Item added to cart!');
            } else {
                showToast('error', response.message);
            }
        },
        error: function(xhr) {
            let msg = 'Error adding to cart';
            if (xhr.responseJSON && xhr.responseJSON.message) {
                msg = xhr.responseJSON.message;
            }
            showToast('error', msg);
        }
    });
});

    // Update cart item quantity
    $('.update-cart-quantity').on('change', function() {
        const cartItemId = $(this).data('cart-item-id');
        const quantity = parseInt($(this).val());
        
        $.ajax({
            url: '/customer/update-cart',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                cart_item_id: cartItemId,
                quantity: quantity
            }),
            success: function(response) {
                if (response.success) {
                    showToast('success', response.message);
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showToast('error', response.message);
                }
            },
            error: function() {
                showToast('error', 'Error updating cart');
            }
        });
    });

    // Place order
    $('#place-order').on('click', function(e) {
        e.preventDefault();
        
        const button = $(this);
        const cartItems = $('.cart-item').length;
        
        if (cartItems === 0) {
            showToast('error', 'Your cart is empty');
            return;
        }
        const confirmed = confirm('Are you sure you want to place the order?');
        console.log(!confirmed)
        if (!confirmed) {
            return;
        }
        
        // Show loading state
        button.prop('disabled', true);
        button.html('<span class="spinner-border spinner-border-sm me-2"></span>Placing Order...');
        
        $.ajax({
            url: '/customer/place-order',
            method: 'POST',
            success: function(response) {
                if (response.success) {
                    showToast('success', 'Order placed successfully!');
                    setTimeout(() => {
                        window.location.href = '/customer/orders';
                    }, 2000);
                } else {
                    showToast('error', response.message);
                }
            },
            error: function(xhr) {
                    let msg = 'Error placing order';
                    if (xhr.responseJSON && xhr.responseJSON.message) {
                        msg = xhr.responseJSON.message;
                    }
                    showToast('error', msg);
                },
            complete: function() {
                button.prop('disabled', false);
                button.html('<i class="fas fa-check me-2"></i>Place Order');
            }
        });
    });
    // Update order status (for restaurant owners)
    $('.update-order-status').on('click', function(e) {
        e.preventDefault();
        
        const button = $(this);
        const orderId = button.data('order-id');
        const newStatus = button.data('status');
        
        $.ajax({
            url: '/restaurant/order/' + orderId + '/update-status',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                status: newStatus
            }),
            success: function(response) {
                if (response.success) {
                    showToast('success', response.message);
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showToast('error', response.message);
                }
            },
            error: function() {
                showToast('error', 'Error updating order status');
            }
        });
    });

    // Search functionality
    $('#search-form').on('submit', function(e) {
        const searchTerm = $('#search-input').val().trim();
        if (searchTerm.length < 2) {
            e.preventDefault();
            showToast('warning', 'Please enter at least 2 characters to search');
        }
    });

    // Quantity controls
    $('.quantity-btn').on('click', function(e) {
        e.preventDefault();
        const button = $(this);
        const input = button.siblings('input[type="number"]');
        const currentValue = parseInt(input.val());
        const min = parseInt(input.attr('min')) || 1;
        const max = parseInt(input.attr('max')) || 99;
        
        if (button.hasClass('quantity-plus')) {
            if (currentValue < max) {
                input.val(currentValue + 1);
                input.trigger('change'); 
            }
        } else if (button.hasClass('quantity-minus')) {
            if (currentValue > min) {
                input.val(currentValue - 1);
                input.trigger('change'); 
            }
        }
    });

    // cart Quantity controls
    $('.cart-quantity-btn').on('click', function(e) {
        e.preventDefault();
        const button = $(this);
        const input = button.siblings('input[type="number"]');
        const currentValue = parseInt(input.val());
        const min = parseInt(input.attr('min')) || 1;
        const max = parseInt(input.attr('max')) || 99;
        
        
        if (button.hasClass('cart-quantity-plus')) {
            if (currentValue < max) {
                input.val(currentValue + 1);
                input.trigger('change'); 
       

            }
        } else if (button.hasClass('cart-quantity-minus')) {
            if (currentValue > min) {
                input.val(currentValue - 1);
                input.trigger('change'); 
       

            }
        }
    });

    // Form validation
    $('form').on('submit', function(e) {
        const form = $(this);
        let isValid = true;
        
        // Remove previous validation classes
        form.find('.is-invalid').removeClass('is-invalid');
        form.find('.invalid-feedback').remove();
        
        // Check required fields
        form.find('[required]').each(function() {
            const field = $(this);
            if (!field.val().trim()) {
                field.addClass('is-invalid');
                field.after('<div class="invalid-feedback">This field is required.</div>');
                isValid = false;
            }
        });
        
        // Email validation
        form.find('input[type="email"]').each(function() {
            const field = $(this);
            const email = field.val();
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (email && !emailRegex.test(email)) {
                field.addClass('is-invalid');
                field.after('<div class="invalid-feedback">Please enter a valid email address.</div>');
                isValid = false;
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            showToast('error', 'Please fix the errors in the form');
        }
    });
});

// Toast notification function
function showToast(type, message) {
    const toastContainer = $('#toast-container');
    
    if (toastContainer.length === 0) {
        $('body').append('<div id="toast-container" class="toast-container position-fixed top-0 end-0 p-3"></div>');
    }
    
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    $('#toast-container').append(toastHtml);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        $(this).remove();
    });
}

// Update cart count in navigation
function updateCartCount() {
    $.ajax({
        url: '/api/cart-count',
        method: 'GET',
        success: function(response) {
            if (response.success) {
                $('.cart-count').text(response.count);
                if (response.count > 0) {
                    $('.cart-count').show();
                } else {
                    $('.cart-count').hide();
                }
            }
        }
    });
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Debounce function for search
function debounce(func, wait) {
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

// Search with debounce
const debouncedSearch = debounce(function(searchTerm) {
    if (searchTerm.length >= 2) {
        // Implement search functionality here
        console.log('Searching for:', searchTerm);
    }
}, 300);

// Initialize search input
$('#search-input').on('input', function() {
    const searchTerm = $(this).val();
    debouncedSearch(searchTerm);
});

// Smooth scrolling for anchor links
$('a[href^="#"]').on('click', function(e) {
    e.preventDefault();
    const target = $(this.getAttribute('href'));
    if (target.length) {
        $('html, body').animate({
            scrollTop: target.offset().top - 80
        }, 1000);
    }
});

// Lazy loading for images
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });

    document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
    });
}
