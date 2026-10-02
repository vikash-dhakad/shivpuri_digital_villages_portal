/**
 * main.js — Common utilities for all authenticated pages.
 * Handles auth guard, sidebar active state, user display, notification bell.
 */

document.addEventListener('DOMContentLoaded', () => {
    // ─── Auth Guard ───────────────────────────────────────────────
    const publicPages = ['/login/', '/register/', '/'];
    const currentPath = window.location.pathname;

    if (!publicPages.includes(currentPath)) {
        if (!Auth.isAuthenticated()) {
            window.location.href = '/login/';
            return;
        }
        initAuthenticatedPage();
    }

    // ─── Active Sidebar Link ──────────────────────────────────────
    const sidebarLinks = document.querySelectorAll('.sidebar-link');
    sidebarLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // ─── Role-based visibility ────────────────────────────────────
    const user = Auth.getUser();
    if (user) {
        // Hide farmer-only items from non-farmers
        if (user.role !== 'FARMER') {
            document.querySelectorAll('.farmer-only').forEach(el => el.style.display = 'none');
        }
        // Hide admin-only items from non-admins
        if (user.role !== 'PANCHAYAT_ADMIN') {
            document.querySelectorAll('.admin-only').forEach(el => el.style.display = 'none');
        }
    }
});


function initAuthenticatedPage() {
    const user = Auth.getUser();
    if (!user) return;

    // Update navbar user display
    const nameEl = document.getElementById('user-display-name');
    const roleEl = document.getElementById('user-role-display');
    if (nameEl) nameEl.textContent = user.name;
    if (roleEl) roleEl.textContent = user.role.replace(/_/g, ' ');

    // Fetch unread notification count
    fetchNotificationCount();
}


async function fetchNotificationCount() {
    try {
        const resp = await apiFetch('/api/notifications/unread-count');
        if (resp.ok) {
            const data = await resp.json();
            const badge = document.getElementById('notif-badge');
            if (badge) {
                if (data.count > 0) {
                    badge.textContent = data.count > 99 ? '99+' : data.count;
                    badge.classList.remove('d-none');
                } else {
                    badge.classList.add('d-none');
                }
            }
        }
    } catch { /* silent */ }
}


/**
 * Show a Bootstrap toast notification.
 */
function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    const id = 'toast-' + Date.now();
    const bgClass = type === 'success' ? 'bg-success' : type === 'danger' ? 'bg-danger' : 'bg-warning';
    const icon = type === 'success' ? 'check-circle' : type === 'danger' ? 'x-circle' : 'exclamation-triangle';

    const html = `
        <div id="${id}" class="toast align-items-center text-bg-dark border-0 mb-2" role="alert">
            <div class="d-flex">
                <div class="toast-body d-flex align-items-center gap-2">
                    <i class="bi bi-${icon}-fill text-${type === 'danger' ? 'danger' : type === 'success' ? 'success' : 'warning'}"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    toastContainer.insertAdjacentHTML('beforeend', html);
    const toast = new bootstrap.Toast(document.getElementById(id), { delay: 4000 });
    toast.show();
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    container.style.marginTop = '70px';
    document.body.appendChild(container);
    return container;
}


/**
 * Format date string for display.
 */
function formatDate(dateStr) {
    if (!dateStr) return '—';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-IN', {
        day: '2-digit', month: 'short', year: 'numeric',
        hour: '2-digit', minute: '2-digit',
    });
}

/**
 * Get status badge HTML.
 */
function statusBadge(status) {
    const cls = `badge-${(status || '').toLowerCase().replace(/_/g, '-')}`;
    return `<span class="badge ${cls} rounded-pill px-3 py-2">${(status || '').replace(/_/g, ' ')}</span>`;
}
