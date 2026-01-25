/**
 * ============================================
 * SEARCH FUNCTIONALITY
 * ============================================
 */

console.log('search.js loaded');

/**
 * Search API client
 */
const SearchAPI = {
    /**
     * Search across all entities (users, projects, skills)
     * @param {string} query - Search query
     * @param {number} limit - Number of results per category
     * @returns {Promise<Object>} Search results
     */
    async searchAll(query, limit = 5) {
        try {
            const params = new URLSearchParams({ q: query, limit: limit });
            const response = await fetch(`/api/search/all?${params}`);
            const data = await response.json();
            
            if (!response.ok || !data.success) {
                throw new Error(data.error || 'Search failed');
            }
            
            return data;
        } catch (error) {
            console.error('Search error:', error);
            throw error;
        }
    },

    /**
     * Search for users only
     * @param {string} query - Search query
     * @param {number} limit - Maximum number of results
     * @param {number} offset - Number of results to skip
     * @returns {Promise<Object>} User search results
     */
    async searchUsers(query, limit = null, offset = 0) {
        try {
            const params = new URLSearchParams({ q: query, offset: offset });
            if (limit) params.append('limit', limit);
            
            const response = await fetch(`/api/search/users?${params}`);
            const data = await response.json();
            
            if (!response.ok || !data.success) {
                throw new Error(data.error || 'User search failed');
            }
            
            return data;
        } catch (error) {
            console.error('User search error:', error);
            throw error;
        }
    },

    /**
     * Search for projects only
     * @param {string} query - Search query
     * @param {number} limit - Maximum number of results
     * @param {number} offset - Number of results to skip
     * @returns {Promise<Object>} Project search results
     */
    async searchProjects(query, limit = null, offset = 0) {
        try {
            const params = new URLSearchParams({ q: query, offset: offset });
            if (limit) params.append('limit', limit);
            
            const response = await fetch(`/api/search/projects?${params}`);
            const data = await response.json();
            
            if (!response.ok || !data.success) {
                throw new Error(data.error || 'Project search failed');
            }
            
            return data;
        } catch (error) {
            console.error('Project search error:', error);
            throw error;
        }
    },

    /**
     * Search for skills only
     * @param {string} query - Search query
     * @param {number} limit - Maximum number of results
     * @param {number} offset - Number of results to skip
     * @returns {Promise<Object>} Skill search results
     */
    async searchSkills(query, limit = null, offset = 0) {
        try {
            const params = new URLSearchParams({ q: query, offset: offset });
            if (limit) params.append('limit', limit);
            
            const response = await fetch(`/api/search/skills?${params}`);
            const data = await response.json();
            
            if (!response.ok || !data.success) {
                throw new Error(data.error || 'Skill search failed');
            }
            
            return data;
        } catch (error) {
            console.error('Skill search error:', error);
            throw error;
        }
    }
};


/**
 * Search UI Handler
 */
class SearchHandler {
    constructor(options = {}) {
        this.searchInput = options.searchInput || document.querySelector('#search-input');
        this.resultsContainer = options.resultsContainer || document.querySelector('#search-results');
        this.debounceDelay = options.debounceDelay || 300;
        this.minQueryLength = options.minQueryLength || 1;
        this.searchTimeout = null;
        
        this.init();
    }

    init() {
        if (!this.searchInput) {
            console.warn('Search input not found');
            return;
        }

        // Debounced search on input
        this.searchInput.addEventListener('input', (e) => {
            this.handleSearch(e.target.value);
        });

        // Handle Enter key
        this.searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.handleSearch(e.target.value, true);
            }
        });
    }

    handleSearch(query, immediate = false) {
        const trimmedQuery = query.trim();
        
        // Clear previous timeout
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }

        // If query is too short, clear results
        if (trimmedQuery.length < this.minQueryLength) {
            this.clearResults();
            return;
        }

        // Execute search
        const searchFn = () => {
            this.performSearch(trimmedQuery);
        };

        if (immediate) {
            searchFn();
        } else {
            this.searchTimeout = setTimeout(searchFn, this.debounceDelay);
        }
    }

    async performSearch(query) {
        try {
            this.showLoading();
            
            const results = await SearchAPI.searchAll(query);
            this.displayResults(results);
        } catch (error) {
            this.showError(error.message);
        }
    }

    showLoading() {
        if (this.resultsContainer) {
            this.resultsContainer.innerHTML = '<div class="search-loading">Searching...</div>';
        }
    }

    displayResults(results) {
        if (!this.resultsContainer) {
            return;
        }

        const { users, projects, skills, counts, query, message } = results;

        if (message) {
            this.resultsContainer.innerHTML = `<div class="search-message">${message}</div>`;
            return;
        }

        let html = '';

        // Users section
        if (users.length > 0 || counts.users > 0) {
            html += this.renderSection('Users', users, counts.users, (user) => `
                <div class="search-result-item">
                    <a href="/profile/${user.username}">
                        <strong>${this.highlightQuery(user.username, query)}</strong>
                        ${user.bio ? `<p>${this.highlightQuery(user.bio.substring(0, 100), query)}</p>` : ''}
                    </a>
                </div>
            `);
        }

        // Projects section
        if (projects.length > 0 || counts.projects > 0) {
            html += this.renderSection('Projects', projects, counts.projects, (project) => `
                <div class="search-result-item">
                    <a href="/project/${project.id}">
                        <strong>${this.highlightQuery(project.name, query)}</strong>
                        ${project.description ? `<p>${this.highlightQuery(project.description.substring(0, 100), query)}</p>` : ''}
                    </a>
                </div>
            `);
        }

        // Skills section
        if (skills.length > 0 || counts.skills > 0) {
            html += this.renderSection('Skills', skills, counts.skills, (skill) => `
                <div class="search-result-item">
                    <span>${this.highlightQuery(skill.name, query)}</span>
                </div>
            `);
        }

        if (!html) {
            html = '<div class="search-message">No results found</div>';
        }

        this.resultsContainer.innerHTML = html;
    }

    renderSection(title, items, totalCount, itemRenderer) {
        const moreCount = totalCount - items.length;
        let html = `
            <div class="search-section">
                <h3>${title} ${totalCount > 0 ? `(${totalCount})` : ''}</h3>
                <div class="search-results-list">
        `;

        items.forEach(item => {
            html += itemRenderer(item);
        });

        if (moreCount > 0) {
            html += `<div class="search-more">+ ${moreCount} more result${moreCount > 1 ? 's' : ''}</div>`;
        }

        html += `
                </div>
            </div>
        `;

        return html;
    }

    highlightQuery(text, query) {
        if (!query || !text) return text;
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }

    showError(message) {
        if (this.resultsContainer) {
            this.resultsContainer.innerHTML = `<div class="search-error">Error: ${message}</div>`;
        }
    }

    clearResults() {
        if (this.resultsContainer) {
            this.resultsContainer.innerHTML = '';
        }
    }
}


/**
 * Initialize search on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    // Auto-initialize if search elements exist
    const searchInput = document.querySelector('#search-input');
    const resultsContainer = document.querySelector('#search-results');
    
    if (searchInput && resultsContainer) {
        window.searchHandler = new SearchHandler({
            searchInput: searchInput,
            resultsContainer: resultsContainer
        });
    }
});


// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SearchAPI, SearchHandler };
}

