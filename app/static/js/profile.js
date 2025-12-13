/**
 * ============================================
 * PROFILE PAGE FUNCTIONALITY
 * ============================================
 */

console.log('profile.js loaded');

document.addEventListener('DOMContentLoaded', function() {

    // ==================== PROFILE UPDATE ====================
    const profileForm = document.getElementById('profile-update-form');
    if (profileForm) {
        profileForm.addEventListener('submit', handleProfileUpdate);
    }

    // ==================== AVATAR UPLOAD ====================
    const avatarForm = document.getElementById('avatar-upload-form');
    if (avatarForm) {
        avatarForm.addEventListener('submit', handleAvatarUpload);
    }
    
    // ==================== SKILLS ====================
    const skillForm = document.getElementById('skill-form');
    if (skillForm) {
        skillForm.addEventListener('submit', handleSkillAdd);
    }

    const skillDeleteButtons = document.querySelectorAll('[data-skill-delete]');
    skillDeleteButtons.forEach(btn => {
        btn.addEventListener('click', handleSkillDelete);
    });
});


/**
 * ============================================
 * PROFILE UPDATE HANDLER
 * ============================================
 */
async function handleProfileUpdate(event) {
    event.preventDefault();
    const form = event.target;

    // Read form values
    const username = form.querySelector('[name="username"]').value.trim();
    const email = form.querySelector('[name="email"]').value.trim();
    const contact_info = form.querySelector('[name="contact_info"]').value.trim();
    const bio = form.querySelector('[name="bio"]').value.trim();

    try {
        const response = await fetch('/api/profile/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, contact_info, bio })
        });

        const result = await response.json();

        if (result.success) {
            showMessage('Profile updated successfully!', 'success');

            // Update displayed info without reload
            document.querySelector('.profile-description').textContent = bio || 'No description yet.';
            document.querySelectorAll('p')[0].innerHTML = `<strong>Username:</strong> ${username}`;
            document.querySelectorAll('p')[1].innerHTML = `<strong>Email:</strong> ${email}`;
            document.querySelectorAll('p')[2].innerHTML = `<strong>Contact Info:</strong> ${contact_info || 'Not provided'}`;

            // Exit edit mode
            toggleEditMode();
        } else {
            showMessage(result.message || 'Failed to update profile', 'danger');
        }
    } catch (error) {
        console.error('Profile update error:', error);
        showMessage('An error occurred while updating your profile.', 'danger');
    }
}


/**
 * ============================================
 * AVATAR UPLOAD HANDLER
 * ============================================
 */
async function handleAvatarUpload(event) {
    event.preventDefault();
    const form = event.target;
    const fileInput = form.querySelector('[name="avatar_file"]');
    const file = fileInput.files[0];

    if (!file) {
        showMessage('Please select an image file', 'warning');
        return;
    }

    // Check file type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
    if (!allowedTypes.includes(file.type)) {
        showMessage('Only JPG/PNG/WEBP/GIF allowed', 'danger');
        return;
    }

    try {
        const formData = new FormData();
        formData.append('avatar_file', file);

        const response = await fetch('/api/profile/avatar', {
            method: 'POST',
            body: formData  // Don't set Content-Type header - browser will set it with boundary
        });

        const result = await response.json();

        if (result.success) {
            showMessage('Avatar uploaded successfully!', 'success');

            // Update avatar image
            document.querySelector('.avatar').src = result.avatar_url;

            // Clear file input
            fileInput.value = '';
        } else {
            showMessage(result.message || 'Failed to upload avatar', 'danger');
        }
    } catch (error) {
        console.error('Avatar upload error:', error);
        showMessage('An error occurred while uploading avatar.', 'danger');
    }
}


/**
 * ============================================
 * SKILL ADD HANDLER
 * ============================================
 */
async function handleSkillAdd(event) {
    event.preventDefault();
    const form = event.target;

    const instrument = form.querySelector('[name="instrument"]').value;
    const level = form.querySelector('[name="level"]').value;
    const years = form.querySelector('[name="years"]').value;

    try {
        const response = await fetch('/api/profile/skills', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ instrument, level, years })
        });

        const result = await response.json();

        if (result.success) {
            showMessage(`Added skill: ${instrument}`, 'success');
            setTimeout(() => window.location.reload(), 1000);
        } else {
            showMessage(result.message || 'Failed to add skill', 'danger');
        }
    } catch (error) {
        console.error('Skill add error:', error);
        showMessage('An error occurred while adding skill.', 'danger');
    }
}


/**
 * ============================================
 * SKILL DELETE HANDLER
 * ============================================
 */
async function handleSkillDelete(event) {
    event.preventDefault();
    const button = event.currentTarget;
    const skillId = button.dataset.skillDelete;

    if (!confirm('Remove this skill?')) {
        return;
    }

    try {
        const response = await fetch(`/api/profile/skills/${skillId}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        });

        const result = await response.json();

        if (result.success) {
            showMessage('Skill removed successfully', 'success');

            // Remove skill item from DOM
            const skillItem = button.closest('.skill-item');
            if (skillItem) {
                skillItem.remove();
            }
        } else {
            showMessage(result.message || 'Failed to remove skill', 'danger');
        }
    } catch (error) {
        console.error('Skill delete error:', error);
        showMessage('An error occurred while removing skill.', 'danger');
    }
}


/**
 * ============================================
 * UTILITY: TOGGLE EDIT MODE
 * ============================================
 */
function toggleEditMode() {
    const accountDetails = document.getElementById('account-details');
    const infoEdit = document.getElementById('info-edit');

    if (infoEdit.style.display === 'none' || !infoEdit.style.display) {
        accountDetails.style.display = 'none';
        infoEdit.style.display = 'block';
    } else {
        accountDetails.style.display = 'block';
        infoEdit.style.display = 'none';
    }
}
