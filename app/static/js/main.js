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

/**
 * Global UI Utilities
 */
const AppUI = {
    /**
     * Shows a toast notification style Discord
     */
    toast: (message, icon = 'success') => {
        if (typeof Swal === 'undefined') {
            alert(message);
            return;
        }

        const Toast = Swal.mixin({
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 4000,
            timerProgressBar: true,
            customClass: {
                popup: 'discord-theme rounded-xl border border-white/5 shadow-2xl'
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
    },

    /**
     * Shows a Discord-styled confirmation dialog using SweetAlert2
     */
    confirmAction: ({ title, text, icon = 'warning', confirmText = 'Sim, confirmar', onConfirm }) => {
        if (typeof Swal === 'undefined') {
            if (confirm(text)) onConfirm();
            return;
        }

        Swal.fire({
            title: title,
            text: text,
            icon: icon,
            showCancelButton: true,
            confirmButtonColor: '#da373c',
            cancelButtonColor: '#4e5058',
            confirmButtonText: confirmText,
            cancelButtonText: 'Cancelar',
            reverseButtons: true,
            customClass: {
                popup: 'discord-theme',
                confirmButton: 'rounded-xl px-6 py-3 font-bold',
                cancelButton: 'rounded-xl px-6 py-3 font-bold'
            }
        }).then((result) => {
            if (result.isConfirmed) {
                onConfirm();
            }
        });
    },

    /**
     * Toggle visibility of a modal
     */
    toggleModal: (modalId, show = true) => {
        const modal = document.getElementById(modalId);
        if (!modal) return;
        
        if (show) {
            modal.classList.remove('hidden');
        } else {
            modal.classList.add('hidden');
        }
    }
};

// Global Exposure
window.showToast = AppUI.toast;
window.AppUI = AppUI;

