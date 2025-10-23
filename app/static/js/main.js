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
        const response = await fetch('/logout', {
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
 * Display a message to the user
 * @param {string} text - Message to display
 * @param {string} type - Message type: 'success', 'danger', 'info'
 */
function showMessage(text, type) {
    const container = document.getElementById('message-container');
    
    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = `alert-custom ${type}`;
    messageDiv.innerHTML = `
        <span class="alert-text">${text}</span>
        <button class="alert-close" onclick="this.parentElement.remove();">&times;</button>
    `;
    
    // Clear previous messages
    container.innerHTML = '';
    
    // Add new message
    container.appendChild(messageDiv);
}