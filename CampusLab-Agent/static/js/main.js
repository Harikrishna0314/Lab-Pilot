// CampusLab Agent Frontend JavaScript

const API_BASE = '/api';

// Helper: Get JWT Token
function getToken() {
    return localStorage.getItem('jwt_token');
}

// Helper: Get Current User Object
function getCurrentUser() {
    const userStr = localStorage.getItem('user_info');
    return userStr ? JSON.parse(userStr) : null;
}

// Helper: Auth Fetch Wrapper
async function authFetch(url, options = {}) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...(options.headers || {})
    };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(url, { ...options, headers });
    if (response.status === 401) {
        // Token expired or invalid
        localStorage.removeItem('jwt_token');
        localStorage.removeItem('user_info');
        if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/register')) {
            window.location.href = '/login';
        }
    }
    return response;
}

// Check Auth state on page load
document.addEventListener('DOMContentLoaded', () => {
    const user = getCurrentUser();
    const navUserElem = document.getElementById('nav-user-info');
    const adminNavElem = document.getElementById('nav-admin-link');

    if (user && navUserElem) {
        navUserElem.innerHTML = `
            <span class="text-secondary me-2"><i class="bi bi-person-circle me-1"></i>${user.name} (${user.role.toUpperCase()})</span>
            <button onclick="logout()" class="btn btn-sm btn-outline-danger">Logout</button>
        `;
    }

    if (user && user.role === 'admin' && adminNavElem) {
        adminNavElem.classList.remove('d-none');
    }
});

// Logout
function logout() {
    localStorage.removeItem('jwt_token');
    localStorage.removeItem('user_info');
    window.location.href = '/login';
}

// Handle Login Form
async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const alertBox = document.getElementById('login-alert');

    try {
        const res = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        if (res.ok) {
            localStorage.setItem('jwt_token', data.token);
            localStorage.setItem('user_info', JSON.stringify(data.user));
            window.location.href = '/dashboard';
        } else {
            alertBox.classList.remove('d-none');
            alertBox.innerText = data.error || 'Login failed';
        }
    } catch (err) {
        alertBox.classList.remove('d-none');
        alertBox.innerText = 'Network error occurred.';
    }
}

// Handle Register Form
async function handleRegister(e) {
    e.preventDefault();
    const name = document.getElementById('reg-name').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const role = document.getElementById('reg-role').value;
    const alertBox = document.getElementById('reg-alert');

    try {
        const res = await fetch(`${API_BASE}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password, role })
        });
        const data = await res.json();
        if (res.ok) {
            localStorage.setItem('jwt_token', data.token);
            localStorage.setItem('user_info', JSON.stringify(data.user));
            window.location.href = '/dashboard';
        } else {
            alertBox.classList.remove('d-none');
            alertBox.innerText = data.error || 'Registration failed';
        }
    } catch (err) {
        alertBox.classList.remove('d-none');
        alertBox.innerText = 'Network error occurred.';
    }
}

// Handle AI Chat
async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message) return;

    const chatBox = document.getElementById('chat-messages');
    
    // Render user message
    chatBox.innerHTML += `
        <div class="chat-message user">
            <div>${escapeHtml(message)}</div>
        </div>
    `;
    input.value = '';
    chatBox.scrollTop = chatBox.scrollHeight;

    // Show typing indicator
    const typingId = `typing-${Date.now()}`;
    chatBox.innerHTML += `
        <div class="chat-message bot" id="${typingId}">
            <span class="spinner-border spinner-border-sm me-2" role="status"></span>CampusLab Assistant is processing...
        </div>
    `;
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const res = await authFetch(`${API_BASE}/chat`, {
            method: 'POST',
            body: JSON.stringify({ message })
        });
        const data = await res.json();
        const typingElem = document.getElementById(typingId);
        
        if (res.ok) {
            typingElem.innerText = data.message;
        } else {
            typingElem.innerText = `❌ Error: ${data.error || 'Failed to parse AI request.'}`;
        }
    } catch (err) {
        const typingElem = document.getElementById(typingId);
        if (typingElem) typingElem.innerText = '❌ Network error communicating with AI server.';
    }
    chatBox.scrollTop = chatBox.scrollHeight;
}

function escapeHtml(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
