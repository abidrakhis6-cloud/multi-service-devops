// Dark Mode Toggle
document.addEventListener('DOMContentLoaded', function() {
  const themeToggle = document.getElementById('theme-toggle');
  const html = document.documentElement;
  
  // Load saved theme preference
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'dark') {
    html.classList.add('dark-mode');
    if (themeToggle) themeToggle.textContent = '☀️';
  }
  
  // Toggle theme on button click
  if (themeToggle) {
    themeToggle.addEventListener('click', function() {
      html.classList.toggle('dark-mode');
      const isDark = html.classList.contains('dark-mode');
      localStorage.setItem('theme', isDark ? 'dark' : 'light');
      themeToggle.textContent = isDark ? '☀️' : '🌙';
    });
  }
  
  // Cart functionality
  const cartToggle = document.getElementById('cart-toggle');
  const cartSidebar = document.getElementById('cart-sidebar');
  const cartClose = document.getElementById('cart-close');
  
  if (cartToggle) {
    cartToggle.addEventListener('click', function() {
      cartSidebar.classList.toggle('open');
    });
  }
  
  if (cartClose) {
    cartClose.addEventListener('click', function() {
      cartSidebar.classList.remove('open');
    });
  }
  
  // Close cart when clicking outside
  document.addEventListener('click', function(event) {
    if (cartSidebar && cartToggle && 
        !cartSidebar.contains(event.target) && 
        !cartToggle.contains(event.target)) {
      cartSidebar.classList.remove('open');
    }
  });

  updateCartBadge();
  renderCartItems();
});

let cart = {};

function formatPrice(price) {
  return Number(price).toFixed(2).replace('.', ',') + '€';
}

function updateCartBadge() {
  const cartCount = Object.values(cart).reduce((sum, item) => sum + item.quantity, 0);
  const badge = document.getElementById('cart-count');
  if (badge) {
    badge.textContent = cartCount;
  }
}

function addToCart(productId, productName, productPrice) {
  const normalizedPrice = Number(String(productPrice).replace(',', '.'));
  if (!cart[productId]) {
    cart[productId] = { name: productName, price: normalizedPrice, quantity: 0 };
  }
  cart[productId].quantity += 1;
  renderCartItems();
  updateCartBadge();
  
  const cartSidebar = document.getElementById('cart-sidebar');
  if (cartSidebar) {
    cartSidebar.classList.add('open');
  }
}

function removeFromCart(productId) {
  if (!cart[productId]) return;
  cart[productId].quantity -= 1;
  if (cart[productId].quantity <= 0) {
    delete cart[productId];
  }
  renderCartItems();
  updateCartBadge();
}

function renderCartItems() {
  const cartItems = document.getElementById('cart-items');
  if (!cartItems) return;
  cartItems.innerHTML = '';
  let total = 0;

  Object.keys(cart).forEach(key => {
    const item = cart[key];
    const lineTotal = item.price * item.quantity;
    total += lineTotal;

    const newItem = document.createElement('div');
    newItem.className = 'cart-item';
    newItem.innerHTML = `
      <div class="cart-item-row">
        <div>
          <span class="cart-item-name">${item.name}</span>
          <span class="cart-item-quantity">x${item.quantity}</span>
        </div>
        <div>
          <span class="cart-item-price">${formatPrice(lineTotal)}</span>
          <button class="cart-item-remove" onclick="removeFromCart('${key}')">✕</button>
        </div>
      </div>
    `;
    cartItems.appendChild(newItem);
  });

  const totalElement = document.getElementById('cart-total-amount');
  if (totalElement) {
    totalElement.textContent = formatPrice(total);
  }
}

function clearCart() {
  cart = {};
  renderCartItems();
  updateCartBadge();
}

// Map Initialization (for delivery tracking)
function initMap(containerId, latitude, longitude) {
  // This would use Google Maps API
  // For now, this is a placeholder
  const mapContainer = document.getElementById(containerId);
  if (mapContainer) {
    mapContainer.innerHTML = `
      <div style="width: 100%; height: 400px; background: linear-gradient(135deg, #001f3f, #0073b2); 
                  border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white;">
        📍 Map Location: ${latitude}, ${longitude}
      </div>
    `;
  }
}

// Payment method selection
document.addEventListener('DOMContentLoaded', function() {
  const paymentMethods = document.querySelectorAll('.payment-method');
  paymentMethods.forEach(method => {
    method.addEventListener('click', function() {
      paymentMethods.forEach(m => m.classList.remove('selected'));
      this.classList.add('selected');
    });
  });
});

// Send message in chat
function sendMessage(message, sender = 'user') {
  const chatContainer = document.querySelector('.chat-container');
  if (!chatContainer) return;
  
  const messageDiv = document.createElement('div');
  messageDiv.className = `chat-message ${sender}`;
  messageDiv.textContent = message;
  chatContainer.appendChild(messageDiv);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Make voice call
function initiateCall(driverId) {
  alert('Appel initialisé avec le livreur...');
  // This would integrate with a real calling API
}

// Location tracking
function trackLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
      const lat = position.coords.latitude;
      const lng = position.coords.longitude;
      console.log('Current location:', lat, lng);
      return { latitude: lat, longitude: lng };
    });
  }
}

// Active nav button
document.addEventListener('DOMContentLoaded', function() {
  const currentPage = window.location.pathname;
  const navButtons = document.querySelectorAll('.nav-btn');
  
  navButtons.forEach(btn => {
    if (btn.href.includes(currentPage.split('/')[1])) {
      btn.classList.add('active');
    }
  });
});
