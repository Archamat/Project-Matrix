/**
 * ============================================
 * INITIALIZATION
 * ============================================
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('auth.js loaded successfully');
    
    // Attach login handler
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLoginSubmit);
    }
    
    // Attach register handler (when that page exists)
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegisterSubmit);
    }
});


/**
 * ============================================
 * LOGIN FUNCTIONALITY
 * ============================================
 */

/**
 * Handle login form submission
 * @param {Event} event - Form submit event
 */
async function handleLoginSubmit(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showMessage('Login successful! Redirecting...', 'success');
            setTimeout(() => window.location.href = '/', 1000);
        } else {
            showMessage(result.error, 'danger');
        }
    } catch (error) {
        console.error('Login error:', error);
        showMessage('An error occurred. Please try again.', 'danger');
    }
}

/**
 * ============================================
 * REGISTRATION FUNCTIONALITY
 * ============================================
 */

/**
 * Handle register form submission
 * @param {Event} event - Form submit event
 */
async function handleRegisterSubmit(event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const email = document.getElementById('email').value;

    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password, email })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showMessage('Registration successful! You can now log in.', 'success');
            setTimeout(() => window.location.href = '/login', 1000);
        } else {
            showMessage(result.error, 'danger');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showMessage('An error occurred. Please try again.', 'danger');
    }
}