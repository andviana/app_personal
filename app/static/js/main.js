/**
 * DayLog Global Scripts
 * Handlers for loading overlay, flash messages and global UI patterns.
 */

const showLoading = () => {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.classList.add('active');
};

const hideLoading = () => {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.classList.remove('active');
};

document.addEventListener('DOMContentLoaded', () => {
    // Hide loading if active on load
    hideLoading();

    // Form submission global loading handler
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function (e) {
            // Don't show loading if the form handling is prevented elsewhere
            if (e.defaultPrevented) return;
            
            // Optional: Skip loading for AJAX forms if they handle their own UI
            if (this.getAttribute('data-ajax') === 'true') return;

            showLoading();
            
            // Disable buttons to prevent double submission
            setTimeout(() => {
                const submits = this.querySelectorAll('button[type="submit"], input[type="submit"]');
                submits.forEach(btn => {
                    btn.disabled = true;
                    btn.classList.add('opacity-50', 'cursor-not-allowed');
                });
            }, 0);
        });
    });

    // Handle pageshow (back button cache)
    window.addEventListener('pageshow', (event) => {
        hideLoading();
    });
});

// Toast Helper
const showToast = (message, icon = 'success') => {
    const Toast = Swal.mixin({
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true,
        customClass: {
            popup: 'discord-theme'
        },
        didOpen: (toast) => {
            toast.addEventListener('mouseenter', Swal.stopTimer)
            toast.addEventListener('mouseleave', Swal.resumeTimer)
        }
    });

    Toast.fire({
        icon: icon,
        title: message
    });
};
