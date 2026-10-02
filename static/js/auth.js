/**
 * auth.js — JWT token management and authentication utilities.
 * Matches AuthContext.jsx + axiosInstance.js behavior exactly.
 */

const API_BASE = '';  // Same origin

const Auth = {
    getToken() {
        return localStorage.getItem('vc_token');
    },
    getRefreshToken() {
        return localStorage.getItem('vc_refreshToken');
    },
    getUser() {
        try {
            const s = localStorage.getItem('vc_user');
            return s ? JSON.parse(s) : null;
        } catch { return null; }
    },
    isAuthenticated() {
        return !!this.getToken() && !!this.getUser();
    },
    saveAuth(data) {
        localStorage.setItem('vc_token', data.token);
        localStorage.setItem('vc_refreshToken', data.refreshToken);
        const user = {
            userId: data.userId,
            name: data.name,
            phone: data.phone || '',
            role: data.role,
            villageId: data.villageId,
        };
        localStorage.setItem('vc_user', JSON.stringify(user));
    },
    clearAuth() {
        localStorage.removeItem('vc_token');
        localStorage.removeItem('vc_refreshToken');
        localStorage.removeItem('vc_user');
    },
    isAdmin() { return this.getUser()?.role === 'PANCHAYAT_ADMIN'; },
    isFarmer() { return this.getUser()?.role === 'FARMER'; },
    isVillager() { return this.getUser()?.role === 'VILLAGER'; },
};


/**
 * Authenticated fetch wrapper — auto-attaches JWT + handles 401 refresh.
 * Replaces axiosInstance.js interceptor pattern exactly.
 */
async function apiFetch(url, options = {}) {
    const token = Auth.getToken();
    const headers = options.headers || {};

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    // Only set Content-Type to JSON if body is not FormData
    if (options.body && !(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }

    options.headers = headers;

    let response = await fetch(API_BASE + url, options);

    // Handle 401 — try refresh token
    if (response.status === 401 && !options._retried) {
        const refreshToken = Auth.getRefreshToken();
        if (refreshToken) {
            try {
                const refreshResp = await fetch(API_BASE + '/api/auth/refresh-token', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ refreshToken }),
                });

                if (refreshResp.ok) {
                    const data = await refreshResp.json();
                    Auth.saveAuth(data);
                    // Retry original request
                    options._retried = true;
                    options.headers['Authorization'] = `Bearer ${data.token}`;
                    response = await fetch(API_BASE + url, options);
                } else {
                    Auth.clearAuth();
                    window.location.href = '/login/';
                    return;
                }
            } catch {
                Auth.clearAuth();
                window.location.href = '/login/';
                return;
            }
        } else {
            Auth.clearAuth();
            window.location.href = '/login/';
            return;
        }
    }

    return response;
}


/**
 * Logout handler.
 */
async function handleLogout() {
    try {
        await apiFetch('/api/auth/logout', { method: 'POST' });
    } catch { /* ignore */ }
    Auth.clearAuth();
    window.location.href = '/login/';
}
