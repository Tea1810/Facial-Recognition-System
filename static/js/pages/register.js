// register.js - Registration screen logic

/**
 * Register a new face
 */
async function registerFace() {
    const nameInput = document.getElementById('nameInput');
    const name = nameInput.value.trim();

    if (!name) {
        updateStatus('registerStatus', 'Please enter your name', 'error');
        nameInput.focus();
        return;
    }

    updateStatus('registerStatus', 'Capturing face...', 'info');

    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name: name })
        });

        const data = await response.json();

        if (data.success) {
            updateStatus('registerStatus', 'Registration successful!', 'success');
            showSuccessModal('Registration Successful!', `Welcome, ${name}! Your face has been registered.`);

            setTimeout(() => {
                nameInput.value = '';
                closeSuccessModal();
                stopVideoFeed('registerVideoFeed');
                navigateToWelcome();
            }, 2500);
        } else {
            updateStatus('registerStatus', data.message, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        updateStatus('registerStatus', 'Connection error. Please try again.', 'error');
    }
}

/**
 * Show success modal with custom title and message
 * @param {string} title - Modal title
 * @param {string} message - Modal message
 */
function showSuccessModal(title, message) {
    const modal = document.getElementById('successModal');
    const titleEl = document.getElementById('successTitle');
    const messageEl = document.getElementById('successMessage');

    if (titleEl) titleEl.textContent = title;
    if (messageEl) messageEl.textContent = message;

    showModal('successModal');
}

/**
 * Close success modal
 */
function closeSuccessModal() {
    hideModal('successModal');
}