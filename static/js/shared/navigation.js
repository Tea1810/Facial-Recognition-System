// navigation.js - Screen navigation management

/**
 * Show a specific screen and hide all others
 * @param {string} screenId - ID of the screen to show
 */
function showScreen(screenId) {
    // Stop all video feeds first
    stopVideoFeed('videoFeed');
    stopVideoFeed('registerVideoFeed');

    // Hide all screens
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });

    // Show the target screen
    const targetScreen = document.getElementById(screenId);
    if (targetScreen) {
        targetScreen.classList.add('active');
    }

    // Start appropriate video feed after a short delay
    setTimeout(() => {
        if (screenId === 'loginScreen') {
            startVideoFeed('videoFeed');
        } else if (screenId === 'registerScreen') {
            startVideoFeed('registerVideoFeed');
        }
    }, 100);
}

/**
 * Navigate to welcome screen
 */
function navigateToWelcome() {
    if (typeof attemptCount !== 'undefined') {
        attemptCount = 0;
        if (typeof updateAttemptCounter === 'function') {
            updateAttemptCounter();
        }
    }
    showScreen('welcomeScreen');
}

/**
 * Navigate to login screen
 */
function navigateToLogin() {
    if (typeof attemptCount !== 'undefined') {
        attemptCount = 0;
        if (typeof updateAttemptCounter === 'function') {
            updateAttemptCounter();
        }
    }
    showScreen('loginScreen');
}

/**
 * Navigate to register screen
 */
function navigateToRegister() {
    showScreen('registerScreen');
}

/**
 * Navigate to home/dashboard screen
 * @param {string} userName - Name of the logged in user
 */
function navigateToHome(userName) {
    const userNameEl = document.getElementById('userName');
    if (userNameEl && userName) {
        userNameEl.textContent = userName;
    }
    showScreen('homeScreen');
}

/**
 * Navigate to register from error modal
 */
function navigateToRegisterFromError() {
    if (typeof closeErrorModal === 'function') {
        closeErrorModal();
    }
    showScreen('registerScreen');
}

/**
 * Logout and return to welcome screen
 */
function logout() {
    if (typeof currentUser !== 'undefined') {
        currentUser = null;
    }
    stopVideoFeed('videoFeed');
    stopVideoFeed('registerVideoFeed');
    showScreen('welcomeScreen');
}