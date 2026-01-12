let attemptCount = 0;
const maxAttempts = 6;
let currentUser = null;
let videoFeedActive = false;

// Button glow effect
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

// Camera management functions
function startVideoFeed(elementId) {
    const videoElement = document.getElementById(elementId);
    if (videoElement) {
        // Add timestamp to prevent caching
        videoElement.src = `/video_feed?t=${new Date().getTime()}`;
        videoFeedActive = true;
    }
}

function stopVideoFeed(elementId) {
    const videoElement = document.getElementById(elementId);
    if (videoElement) {
        videoElement.src = '';
        videoFeedActive = false;
    }
    // Tell server to release camera
    fetch('/stop_camera').catch(err => console.log('Camera stop error:', err));
}

// Screen navigation
function showScreen(screenId) {
    // Stop all video feeds first
    stopVideoFeed('videoFeed');
    stopVideoFeed('registerVideoFeed');

    // Hide all screens
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });

    // Show the target screen
    document.getElementById(screenId).classList.add('active');

    // Start appropriate video feed after a short delay
    setTimeout(() => {
        if (screenId === 'loginScreen') {
            startVideoFeed('videoFeed');
        } else if (screenId === 'registerScreen') {
            startVideoFeed('registerVideoFeed');
        }
    }, 100);
}

function backToWelcome() {
    attemptCount = 0;
    updateAttemptCounter();
    stopVideoFeed('videoFeed');
    stopVideoFeed('registerVideoFeed');
    showScreen('welcomeScreen');
}

function startLogin() {
    attemptCount = 0;
    updateAttemptCounter();
    showScreen('loginScreen');
}

function startRegister() {
    showScreen('registerScreen');
}

function updateAttemptCounter() {
    document.getElementById('attemptCount').textContent = attemptCount;
}

function updateStatus(message, type = 'info') {
    const statusEl = document.getElementById('statusMessage');
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

function updateRegisterStatus(message, type = 'info') {
    const statusEl = document.getElementById('registerStatus');
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

// Login attempt
async function attemptLogin() {
    if (attemptCount >= maxAttempts) {
        return;
    }

    attemptCount++;
    updateAttemptCounter();
    updateStatus('Scanning face...', 'info');

    try {
        const response = await fetch('/recognize');
        const data = await response.json();

        if (data.success) {
            updateStatus(`Welcome back, ${data.name}!`, 'success');
            currentUser = data.name;

            // Show success and redirect to home
            setTimeout(() => {
                document.getElementById('userName').textContent = data.name;
                stopVideoFeed('videoFeed');
                showScreen('homeScreen');
            }, 1500);
        } else {
            if (attemptCount >= maxAttempts) {
                updateStatus('Maximum attempts reached', 'error');
                setTimeout(() => {
                    stopVideoFeed('videoFeed');
                    showErrorModal();
                }, 1000);
            } else {
                updateStatus(`Face not recognized. Try again. (${attemptCount}/${maxAttempts})`, 'error');
            }
        }
    } catch (error) {
        console.error('Error:', error);
        updateStatus('Connection error. Please try again.', 'error');
    }
}

// Register face
async function registerFace() {
    const nameInput = document.getElementById('nameInput');
    const name = nameInput.value.trim();

    if (!name) {
        updateRegisterStatus('Please enter your name', 'error');
        nameInput.focus();
        return;
    }

    updateRegisterStatus('Capturing face...', 'info');

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
            updateRegisterStatus('Registration successful!', 'success');
            showSuccessModal('Registration Successful!', `Welcome, ${name}! Your face has been registered.`);

            setTimeout(() => {
                nameInput.value = '';
                closeSuccessModal();
                stopVideoFeed('registerVideoFeed');
                showScreen('welcomeScreen');
            }, 2500);
        } else {
            updateRegisterStatus(data.message, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        updateRegisterStatus('Connection error. Please try again.', 'error');
    }
}

// Error Modal
function showErrorModal() {
    const modal = document.getElementById('errorModal');
    modal.classList.add('show');
}

function closeErrorModal() {
    const modal = document.getElementById('errorModal');
    modal.classList.remove('show');
    attemptCount = 0;
    updateAttemptCounter();
    updateStatus('Position your face in the frame', 'info');
}

function showRegisterFromError() {
    closeErrorModal();
    showScreen('registerScreen');
}

// Success Modal
function showSuccessModal(title, message) {
    const modal = document.getElementById('successModal');
    document.getElementById('successTitle').textContent = title;
    document.getElementById('successMessage').textContent = message;
    modal.classList.add('show');
}

function closeSuccessModal() {
    const modal = document.getElementById('successModal');
    modal.classList.remove('show');
}

// Logout
function logout() {
    currentUser = null;
    stopVideoFeed('videoFeed');
    stopVideoFeed('registerVideoFeed');
    showScreen('welcomeScreen');
}

// Close modals on outside click
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('show');
    }
});

// Allow Enter key to submit
document.addEventListener('DOMContentLoaded', () => {
    const nameInput = document.getElementById('nameInput');
    if (nameInput) {
        nameInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                registerFace();
            }
        });
    }
});