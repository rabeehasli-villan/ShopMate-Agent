// --- Global State ---
let currentUser = null; 
let activeTab = 'ai';
// Generate a unique session ID for the current browser session
let currentSessionId = 'guest-' + Math.random().toString(36).substring(7);

const elements = {
    authOverlay: document.getElementById('auth-overlay'),
    loginForm: document.getElementById('login-form'),
    signupForm: document.getElementById('signup-form'),
    chatMessages: document.getElementById('chat-messages'),
    userInput: document.getElementById('user-input'),
    chatForm: document.getElementById('chat-input-area'),
    userStatus: document.getElementById('user-status'),
    btnLogout: document.getElementById('btn-logout'),
    btnGuest: document.getElementById('btn-guest'),
    productsList: document.getElementById('products-list'),
    couponsList: document.getElementById('coupons-list'),
    ordersHistory: document.getElementById('order-history')
};

// --- Tab Management ---
function switchTab(tabId) {
    activeTab = tabId;
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    document.getElementById(`tab-${tabId}`).classList.remove('hidden');
    document.querySelectorAll('#top-nav button').forEach(el => el.classList.remove('active'));
    const activeBtn = document.getElementById(`btn-${tabId}`);
    if (activeBtn) activeBtn.classList.add('active');

    if (tabId === 'products') loadProducts();
    if (tabId === 'coupons') loadCoupons();
    if (tabId === 'orders') loadOrders();
}

// --- Auth logic ---
function clearChat() {
    elements.chatMessages.innerHTML = `
        <div class="message system">Welcome! How can I help you today?</div>
    `;
}

function guestMode() {
    currentUser = null;
    clearChat();
    elements.authOverlay.classList.add('hidden');
    updateUI();
}

async function handleLogin() {
    const email = document.getElementById('login-email').value;
    const pass = document.getElementById('login-pass').value;

    const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password: pass })
    });
    const data = await res.json();
    if (data.success) {
        currentUser = data.user;
        clearChat(); // FRESH CHAT FOR NEW LOGIN
        elements.authOverlay.classList.add('hidden');
        updateUI();
        addMessage(`Hello ${currentUser.name}! Glad to see you back.`, 'ai');
    } else {
        alert(data.message || "Login failed.");
    }
}

async function handleSignup() {
    const name = document.getElementById('signup-name').value;
    const email = document.getElementById('signup-email').value;
    const pass = document.getElementById('signup-pass').value;
    const address = document.getElementById('signup-address').value;

    const res = await fetch('/api/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password: pass, address })
    });
    const data = await res.json();
    if (data.success) {
        alert("Success! Account created.");
        showLogin();
    } else {
        alert(data.message);
    }
}

function updateUI() {
    if (currentUser && currentUser.id) {
        elements.userStatus.innerText = `User ID: ${currentUser.id} | ${currentUser.name}`;
        elements.btnLogout.classList.remove('hidden');
        elements.btnGuest.classList.add('hidden');
    } else {
        elements.userStatus.innerText = `Guest Mode Enabled`;
        elements.btnLogout.classList.add('hidden');
        elements.btnGuest.classList.remove('hidden');
    }
    switchTab(activeTab);
}

function logout() {
    currentUser = null;
    clearChat(); // CLEAN START
    updateUI();
    showAuth();
}

// --- Data Fetching ---

async function loadProducts() {
    const res = await fetch('/api/products');
    const products = await res.json();
    elements.productsList.innerHTML = products.map(p => `
        <div class="card">
            <h3>${p.name}</h3>
            <p>${p.description}</p>
            <div class="price">$${p.price.toFixed(2)}</div>
            <button onclick="orderProduct('${p.id}')">Order Now</button>
        </div>
    `).join('');
}

async function loadCoupons() {
    const res = await fetch('/api/coupons');
    const coupons = await res.json();
    elements.couponsList.innerHTML = coupons.map(c => `
        <div class="list-item clickable-coupon" onclick="alert('${c.description}')">
            <span class="coupon-code">${c.code}</span> - ${c.discount}% Discount 
            <span class="status-tag ${c.status === 'Active' ? 'active-green' : 'expired-white'}">
                ${c.status}
            </span>
            <p style="font-size: 0.7rem; color: #444; margin-top: 5px;">View Description</p>
        </div>
    `).join('');
}

async function loadOrders() {
    if (!currentUser) {
        elements.ordersHistory.innerHTML = "<p class='system'>Login to view your history.</p>";
        return;
    }
    const res = await fetch(`/api/orders/${currentUser.id}`);
    const orders = await res.json();
    if (orders.length === 0) {
        elements.ordersHistory.innerHTML = "<p>You haven't placed any orders yet.</p>";
        return;
    }
    elements.ordersHistory.innerHTML = orders.map(o => `
        <div class="list-item order-item">
            <div class="order-info">
                #${o.id.substring(0,6)}... | <strong>${o.product_name}</strong> | Status: ${o.status} | Qty: ${o.quantity}
                <p style="font-size: 0.8rem; color: #555;">To: ${o.delivery_address}</p>
            </div>
            <div class="order-actions">
                <button class="mini" onclick="askAIChat('Show details for order ${o.id}')">Details</button>
                <button class="mini" onclick="askAIChat('Cancel order ${o.id}')">Cancel</button>
                <button class="mini" onclick="askAIChat('Update address for order ${o.id}')">Address</button>
            </div>
        </div>
    `).join('');
}

async function orderProduct(pId) {
    if (!currentUser) {
        alert("Please login first.");
        showAuth();
        return;
    }
    const address = prompt("Confirm delivery address:", currentUser.address);
    if (!address) return;

    const res = await fetch('/api/place_order', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: currentUser.id, product_id: pId, delivery_address: address, quantity: 1 })
    });
    const data = await res.json();
    alert(data.message);
    loadOrders();
}

// --- Messaging Area ---

function addMessage(text, sender = 'ai') {
    const msg = document.createElement('div');
    msg.classList.add('message', sender);
    msg.innerText = text;
    elements.chatMessages.appendChild(msg);
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}

function askAIChat(query) {
    switchTab('ai');
    elements.userInput.value = query;
    elements.chatForm.dispatchEvent(new Event('submit'));
}

elements.chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = elements.userInput.value.trim();
    if (!message) return;

    addMessage(message, 'user');
    elements.userInput.value = '';

    try {
        const payload = { 
            message, 
            user_id: currentUser ? currentUser.id : null,
            session_id: currentSessionId // Ensure guest session separation
        };

        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        
        // Ensure no 'undefined' in cases of missing JSON properties
        const finalResponse = data && data.response ? data.response : "The AI model is currently busy. Please try again.";
        addMessage(finalResponse, 'ai');
        
        if (message.toLowerCase().includes('order') || message.toLowerCase().includes('cancel')) {
            loadOrders();
        }
    } catch (err) {
        addMessage("Connection failed. Check your network.", "system");
    }
});

// UI Overlays
function showSignup() { elements.loginForm.classList.add('hidden'); elements.signupForm.classList.remove('hidden'); }
function showLogin() { elements.signupForm.classList.add('hidden'); elements.loginForm.classList.remove('hidden'); }
function showAuth() { elements.authOverlay.classList.remove('hidden'); }

window.onload = () => showAuth();
