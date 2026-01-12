// utils.js - Shared utility functions

/**
 * Button glow effect - follows mouse movement
 */
document.addEventListener('mousemove', (e) => {
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
        const rect = btn.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;

        const glow = btn.querySelector('.btn-glow');
        if (glow) {
            glow.style.setProperty('--x', `${x}%`);
            glow.style.setProperty('--y', `${y}%`);
        }
    });
});

/**
 * Update status message with type styling
 * @param {string} elementId - ID of the status element
 * @param {string} message - Message to display
 * @param {string} type - 'info', 'success', or 'error'
 */
function updateStatus(elementId, message, type = 'info') {
    const statusEl = document.getElementById(elementId);
    if (!statusEl) return;

    statusEl.textContent = message;

    if (type === 'success') {
        statusEl.style.background = 'rgba(16, 185, 129, 0.2)';
        statusEl.style.borderColor = '#10b981';
        statusEl.style.color = '#10b981';
    } else if (type === 'error') {
        statusEl.style.background = 'rgba(239, 68, 68, 0.2)';
        statusEl.style.borderColor = '#ef4444';
        statusEl.style.color = '#ef4444';
    } else {
        statusEl.style.background = 'rgba(10, 14, 39, 0.9)';
        statusEl.style.borderColor = 'rgba(255, 255, 255, 0.1)';
        statusEl.style.color = '#a0aec0';
    }
}

/**
 * Show a modal
 * @param {string} modalId - ID of the modal to show
 */
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('show');
    }
}

/**
 * Hide a modal
 * @param {string} modalId - ID of the modal to hide
 */
function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
    }
}

/**
 * Close modals when clicking outside
 */
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('show');
    }
});

/**
 * Enable Enter key to submit on input fields
 */
document.addEventListener('DOMContentLoaded', () => {
    const nameInput = document.getElementById('nameInput');
    if (nameInput) {
        nameInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && typeof registerFace === 'function') {
                registerFace();
            }
        });
    }
});