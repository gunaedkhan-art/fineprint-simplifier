// auth-check.js - Shared authentication validation
async function validateAuthToken() {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
        return { valid: false, reason: 'no_token' };
    }
    
    try {
        const response = await fetch('/api/validate-token', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            return data;
        } else {
            const errorData = await response.json();
            return { valid: false, reason: errorData.reason || 'validation_failed' };
        }
    } catch (error) {
        console.error('Token validation error:', error);
        return { valid: false, reason: 'network_error' };
    }
}

function clearAuthData() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('fineprint_user_id');
    document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
    
    // Clear any temporary analysis data
    const userId = localStorage.getItem('fineprint_user_id');
    if (userId) {
        localStorage.removeItem(`temp_analysis_${userId}`);
    }
}

function showSessionExpiredMessage() {
    // Create modal overlay
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.5); display: flex; align-items: center;
        justify-content: center; z-index: 10000;
    `;
    
    modal.innerHTML = `
        <div style="background: white; padding: 2rem; border-radius: 12px; 
                    max-width: 400px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.2);">
            <h2 style="color: #1e293b; margin-bottom: 1rem;">⏱️ Session Expired</h2>
            <p style="color: #64748b; margin-bottom: 1.5rem;">
                Your session has expired for security. Please sign in again to continue.
            </p>
            <button onclick="window.location.href='/login'" 
                    style="background: #2563eb; color: white; border: none; padding: 0.75rem 2rem;
                           border-radius: 8px; font-size: 1rem; cursor: pointer; font-weight: 600;">
                Sign In
            </button>
        </div>
    `;
    
    document.body.appendChild(modal);
}

async function checkAuthOnPageLoad() {
    const token = localStorage.getItem('access_token');
    
    if (token) {
        const validation = await validateAuthToken();
        
        if (!validation.valid) {
            // Token is expired or invalid
            clearAuthData();
            
            // Only show message if we're not already on login/register pages
            const path = window.location.pathname;
            if (path !== '/login' && path !== '/register' && path !== '/') {
                showSessionExpiredMessage();
            }
        }
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { validateAuthToken, clearAuthData, checkAuthOnPageLoad };
}
