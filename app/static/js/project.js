/**
 * ============================================
 * INITIALIZATION
 * ============================================
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('project.js loaded successfully');

    // Attach create project handler
    const createProjectForm = document.getElementById('createProjectForm');
    if (createProjectForm) {
        createProjectForm.addEventListener('submit', handleCreateProjectSubmit);
    }
    // Attach apply project handler
    const applyProjectForm = document.getElementById('apply_project_form');
    if (applyProjectForm) {
        applyProjectForm.addEventListener('submit', handleApplyProjectSubmit);
    }
});

/**
 * ============================================
 * CREATE PROJECT FUNCTIONALITY
 * ============================================
 */

/**
 * Handle create project form submission
 * @param {Event} event - Form submit event
 */
async function handleCreateProjectSubmit(event) {
    event.preventDefault();
    const form = event.target; 
    // Read values using the name attribute
    const name = form.querySelector('[name="name"]').value;
    const description = form.querySelector('[name="description"]').value;
    const sector = form.querySelector('[name="sector"]').value;
    const people_count = form.querySelector('[name="people_count"]').value;
    
    // For multi-select, get all selected values
    const skillsSelect = form.querySelector('[name="skills"]');
    const skills = Array.from(skillsSelect.selectedOptions).map(opt => opt.value);
    
    const other_skill = form.querySelector('[name="other_skill"]')?.value || '';
    try {
        const response = await fetch('/api/create_project', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                name, 
                description, 
                sector, 
                people_count: parseInt(people_count),
                skills,
                other_skill
            })
        });
        const result = await response.json();
        if (result.success) {
            showMessage('Project created successfully! Redirecting...', 'success');
            setTimeout(() => window.location.href = '/', 1000);
        } else {
            showMessage(result.error, 'danger');
        }
    } catch (error) {
        showMessage('An error occurred while creating the project.', 'danger');
    }
}

/**
 * ============================================
 * APPLICATION FUNCTIONALITY
 * ============================================
 */

/**
 * Handle apply project form submission
 * @param {Event} event - Form submit event
 */
async function handleApplyProjectSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const information = form.querySelector('[name="information"]').value;
    const skills = form.querySelector('[name="skills"]').value;
    const other_skill = form.querySelector('[name="other_skill"]')?.value || '';
    const contact_info = form.querySelector('[name="contact_info"]').value;
    try {
        const response = await fetch(`/api/apply/${form.dataset.projectId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ information, skills, other_skill, contact_info })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showMessage('Application submitted successfully!', 'success');
            setTimeout(() => window.location.href = '/', 1000);
        } else {
            showMessage(result.error, 'danger');
        }
    } catch (error) {
        showMessage('An error occurred while submitting the application.', 'danger');
    }
}

/**
 * ============================================
 * VIEW APPLICATION FUNCTIONALITY
 * ============================================
 */

/**
 * Handle apply project form submission
 * @param {Event} event - Form submit event
 */

async function handleViewApplicants(event) {
    event.preventDefault();
    const projectId = event.target.dataset.projectId;
    try {
        const response = await fetch(`/api/project/${projectId}/applicants`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Render applicants list
            const applicantsList = document.getElementById('applicantsList');
            applicantsList.innerHTML = '';
            result.applicants.forEach(applicant => {
                const listItem = document.createElement('li');
                listItem.textContent = `Applicant ID: ${applicant.applicant_id}, Information: ${applicant.information}, Skills: ${applicant.skills}, Contact Info: ${applicant.contact_info}`;
                applicantsList.appendChild(listItem);
            });
        } else {
            showMessage(result.error, 'danger');
        }
    } catch (error) {
        showMessage('An error occurred while fetching the applicants.', 'danger');
    }
}