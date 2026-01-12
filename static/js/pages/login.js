// login.js - Login screen logic

let attemptCount = 0;
const maxAttempts = 6;

/**
 * Update the attempt counter display
 */
function updateAttemptCounter() {
    const attemptCountEl = document.getElementById('attemptCount');
    if (attemptCountEl) {
        attemptCountEl.textContent = attemptCount;
    }
}

/**
 * Attempt to login with face recognition
 */
async function attemptLogin() {
    if (attemptCount >= maxAttempts) {
        return;
    }

    attemptCount++;
    updateAttemptCounter();
    updateStatus('statusMessage', 'Scanning face...', 'info');

    try {
        const response = await fetch('/recognize');
        const data = await response.json();

        if (data.success) {
            updateStatus('statusMessage', `Welcome back, ${data.name}!`, 'success');

            // Show success and redirect to home
            setTimeout(() => {
                stopVideoFeed('videoFeed');
                navigateToHome(data.name);
            }, 1500);
        } else {
            if (attemptCount >= maxAttempts) {
                updateStatus('statusMessage', 'Maximum attempts reached', 'error');
                setTimeout(() => {
                    stopVideoFeed('videoFeed');
                    showErrorModal();
                }, 1000);
            } else {
                updateStatus('statusMessage', `Face not recognized. Try again. (${attemptCount}/${maxAttempts})`, 'error');
            }
        }
    } catch (error) {
        console.error('Error:', error);
        updateStatus('statusMessage', 'Connection error. Please try again.', 'error');
    }
}

/**
 * Show error modal after max attempts
 */
function showErrorModal() {
    showModal('errorModal');
}

/**
 * Close error modal and reset
 */
function closeErrorModal() {
    hideModal('errorModal');
    attemptCount = 0;
    updateAttemptCounter();
    updateStatus('statusMessage', 'Position your face in the frame', 'info');
}