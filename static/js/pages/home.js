// home.js - Home/Dashboard screen logic

let currentUser = null;

// The logout function is defined in navigation.js

// You can add dashboard-specific functionality here
// For example:

/**
 * Initialize dashboard with user data
 * @param {string} userName - Name of the logged in user
 */
function initializeDashboard(userName) {
    currentUser = userName;
    console.log(`Dashboard initialized for ${userName}`);

    // You can add more dashboard initialization here
    // For example: load user stats, recent activity, etc.
}

// Add event listeners for action buttons if needed
document.addEventListener('DOMContentLoaded', () => {
    const actionButtons = document.querySelectorAll('.action-btn');

    actionButtons.forEach(button => {
        // Skip the logout button as it has its own handler
        if (button.textContent.includes('Log Out')) return;

        button.addEventListener('click', () => {
            const action = button.querySelector('.action-text').textContent;
            console.log(`Action clicked: ${action}`);

            // Add functionality for other buttons here
            // For example:
            // if (action === 'View Dashboard') { ... }
            // if (action === 'Settings') { ... }
            // if (action === 'Manage Users') { ... }
        });
    });
});