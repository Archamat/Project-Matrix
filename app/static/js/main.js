/**
 * ============================================
 * GLOBAL SITE FUNCTIONALITY
 * Loads on every page
 * ============================================
 */

document.addEventListener('DOMContentLoaded', function() {

    // Attach logout handler
const logoutLink = document.querySelector('a[href*="logout"]');
if (logoutLink) {
    logoutLink.addEventListener('click', handleLogoutSubmit);
}
});



/**
 * ============================================
 * LOGOUT FUNCTIONALITY
 * ============================================
 */

/**
 * Handle logout form submission
 * @param {Event} event - Form submit event
 */
async function handleLogoutSubmit(event) {
    event.preventDefault();

    try {
        console.log('Logging out user');
        const response = await fetch('/api/logout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const result = await response.json();

        if (result.success) {
            window.location.href = '/login';
        } else {
            console.error('Logout failed:', result.error);
            alert('Logout failed. Please try again.');
        }
    } catch (error) {
        console.error('Logout error:', error);
        alert('An error occurred during logout.');
    }
}

/**
 * ============================================
 * UTILITY FUNCTIONS
 * ============================================
 */

/**
 * Escape HTML to prevent XSS attacks
 * @param {string} str - String to escape
 * @returns {string} Escaped HTML string
 */
function escapeHTML(str) {
    return str.replace(/[&<>"']/g, function (m) {
        switch (m) {
            case '&': return '&amp;';
            case '<': return '&lt;';
            case '>': return '&gt;';
            case '"': return '&quot;';
            case "'": return '&#39;';
            default: return m;
        }
    });
}

/**
 * Display a message to the user
 * @param {string} text - Message to display
 * @param {string} type - Message type: 'success', 'danger', 'info'
 */
function showMessage(text, type) {
    const container = document.getElementById('message-container');

    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.innerHTML = `
        <span class="alert-text">${escapeHTML(text)}</span>
        <button class="alert-close" type="button">&times;</button>
    `;

    const closeBtn = messageDiv.querySelector('.alert-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            messageDiv.remove();
        });
    }

    // Clear previous messages
    container.innerHTML = '';

    // Add new message
    container.appendChild(messageDiv);
}
