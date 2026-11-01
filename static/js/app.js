// All data lives in PostgreSQL. This file only calls the Flask API and draws the result.
const page = document.body.dataset.page;
const $ = (id) => document.getElementById(id);
const money = (n) => "₹" + Number(n).toFixed(0);

// Categories are a display grouping only (the products table has no category column).
const CATEGORIES = {
  "All": null,
  "Dairy & Bread": ["Amul Milk", "Bread", "Eggs"],
  "Fruits & Vegetables": ["Bananas", "Apples", "Potatoes", "Tomatoes", "Onions"],
  "Staples": ["Rice", "Atta", "Cooking Oil", "Sugar", "Tea"],
  "Snacks": ["Maggi", "Biscuits"],
};

let products = [], wishIds = new Set(), category = "All", query = "";

async function api(url, body) {
  const opts = body ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : {};
  const res = await fetch(url, opts);
  const data = await res.json();
  if (!res.ok) { toast(data.error || "Something went wrong"); throw new Error(data.error); }
  return data;
}

function toast(msg) {
  const t = $("toast"); t.textContent = msg; t.classList.add("show");
  clearTimeout(toast.timer); toast.timer = setTimeout(() => t.classList.remove("show"), 1800);
}

async function refreshCounts() {
  const [cart, wish] = await Promise.all([api("/api/cart"), api("/api/wishlist")]);
  $("cartCount").textContent = cart.count;
  $("wishCount").textContent = wish.count;
  wishIds = new Set(wish.items.map((w) => w.product_id));
  return { cart, wish };
}

// ---------- Home page ----------
function productCard(p) {
  return `<article class="card">
    <button class="heart ${wishIds.has(p.product_id) ? "on" : ""}" onclick="toggleWish(${p.product_id})" aria-label="Toggle wishlist">♥</button>
    <img src="${p.image_url}" alt="${p.name}" loading="lazy">
    <h3>${p.name}</h3><div class="pack">${p.quantity}</div>
    <div class="card-foot"><span class="price">${money(p.price)}</span>
    <button class="btn-add" onclick="addToCart(${p.product_id})">Add</button></div></article>`;
}

function renderProducts() {
  const allowed = CATEGORIES[category];
  const list = products.filter((p) => (!allowed || allowed.includes(p.name)) && p.name.toLowerCase().includes(query));
  $("productGrid").innerHTML = list.map(productCard).join("");
  $("empty").hidden = list.length > 0;
}

function renderCategories() {
  $("categories").innerHTML = Object.keys(CATEGORIES)
    .map((c) => `<button class="chip ${c === category ? "active" : ""}" onclick="setCategory('${c}')">${c}</button>`).join("");
}
function setCategory(c) { category = c; renderCategories(); renderProducts(); }

async function addToCart(id) {
  const r = await api("/api/cart/add", { product_id: id });
  toast("✓ " + r.message); refreshCounts();
}

async function toggleWish(id) {
  const adding = !wishIds.has(id);
  await api(adding ? "/api/wishlist/add" : "/api/wishlist/remove", { product_id: id });
  toast(adding ? "♥ Added to wishlist" : "Removed from wishlist");
  await refreshCounts();
  page === "wishlist" ? loadWishlist() : renderProducts();
}

// ---------- Cart page ----------
async function loadCart() {
  const { cart } = await refreshCounts();
  $("cartList").innerHTML = cart.items.length ? cart.items.map((i) => `
    <div class="cart-row">
      <img src="${i.image_url}" alt="${i.name}">
      <div class="info"><strong>${i.name}</strong><div class="pack">${i.pack} · ${money(i.price)}</div></div>
      <div class="stepper"><button onclick="setQty(${i.product_id}, ${i.quantity - 1})" aria-label="Decrease">−</button>
        <span>${i.quantity}</span><button onclick="setQty(${i.product_id}, ${i.quantity + 1})" aria-label="Increase">+</button></div>
      <strong>${money(i.subtotal)}</strong>
      <button class="remove" onclick="removeItem(${i.product_id})">Remove</button>
    </div>`).join("") : `<p class="muted">Your cart is empty. <a href="/" style="color:var(--green);font-weight:700">Browse products</a></p>`;
  $("cartSummary").hidden = !cart.items.length;
  $("subtotal").textContent = money(cart.total);
  $("total").textContent = money(cart.total);
}
async function setQty(id, qty) { await api("/api/cart/update", { product_id: id, quantity: qty }); loadCart(); }
async function removeItem(id) { await api("/api/cart/remove", { product_id: id }); toast("Removed from cart"); loadCart(); }

// ---------- Wishlist page ----------
async function loadWishlist() {
  const { wish } = await refreshCounts();
  $("wishGrid").innerHTML = wish.items.map(productCard).join("");
  $("empty").hidden = wish.items.length > 0;
}

// ---------- Start ----------
(async function init() {
  try {
    if (page === "home") {
      products = await api("/api/products");
      renderCategories(); await refreshCounts(); renderProducts();
      $("search").addEventListener("input", (e) => { query = e.target.value.trim().toLowerCase(); renderProducts(); });
    } else if (page === "cart") loadCart();
    else if (page === "wishlist") loadWishlist();
  } catch (e) { console.error(e); }
})();
// On cart/wishlist pages, pressing Enter in the search box goes back to the home page.
if (page !== "home") $("search").addEventListener("keydown", (e) => { if (e.key === "Enter") location.href = "/"; });
