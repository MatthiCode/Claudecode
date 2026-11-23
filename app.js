/* ============================================================
   FREIZ — catalogue, illustrations de gourdes, panier
   ============================================================ */

const FLAVORS = [
  {
    id: "barbe-a-papa", name: "Barbe à papa", line1: "BARBE À", line2: "PAPA",
    tag: "Le goût de la fête foraine, sans le sucre.",
    body: "#f08ccb", dark: "#c4549a", band: "#4b1f3d", ink: "#4b1f3d", fruit: "cotton",
    card: ["#f39ad2", "#b84a8e"],
  },
  {
    id: "miel", name: "Miel", line1: "MIEL", line2: "",
    tag: "Doux, rond, réconfortant à mi-parcours.",
    body: "#f6a823", dark: "#d9800c", band: "#5b2c10", ink: "#5b2c10", fruit: "honey",
    card: ["#f7b13a", "#c9700a"],
  },
  {
    id: "pomme", name: "Pomme", line1: "POMME", line2: "",
    tag: "La classique ultra-fraîche. Notre best-seller.",
    body: "#7fcf54", dark: "#4fa52f", band: "#1d3a12", ink: "#1d3a12", fruit: "apple",
    card: ["#7fcf54", "#357a1c"],
  },
  {
    id: "fraise", name: "Fraise", line1: "FRAISE", line2: "",
    tag: "Fruitée et pétillante, comme un dimanche de juin.",
    body: "#e5291f", dark: "#b5140d", band: "#4a1410", ink: "#4a1410", fruit: "strawberry",
    card: ["#ec3d2f", "#9e1009"],
  },
  {
    id: "speculos", name: "Spéculos", line1: "SPÉCULOS", line2: "",
    tag: "Gourmande et épicée. Le goûter du cycliste.",
    body: "#f5c518", dark: "#d99f0a", band: "#5a2a0e", ink: "#5a2a0e", fruit: "speculoos",
    card: ["#f6cc2c", "#c88a06"],
  },
];

const UNIT_PRICE = 1.99;

const PRODUCTS = {
  "pack-decouverte": { name: "Pack Découverte · 10 gourdes", price: 15.9, flavor: "pomme" },
  "pack-saison": { name: "Pack Saison · 24 gourdes", price: 35.9, flavor: "fraise" },
  "abonnement-club": { name: "Abonnement Club · 12 gourdes/mois", price: 17.9, flavor: "speculos" },
};
FLAVORS.forEach((f) => {
  PRODUCTS[`gourde-${f.id}`] = { name: `Gourde ${f.name}`, price: UNIT_PRICE, flavor: f.id };
});

const FREE_SHIPPING = 25;
const euro = (n) => n.toFixed(2).replace(".", ",") + " €";

/* ---------- Illustration SVG d'une gourde ---------- */
let uid = 0;

function fruitArt(type) {
  switch (type) {
    case "apple":
      return `
        <g transform="translate(84 114)">
          <circle r="27" fill="#8fd649"/>
          <circle r="27" fill="url(#shine)"/>
          <ellipse cx="-9" cy="-10" rx="7" ry="4" fill="#fff" opacity=".55" transform="rotate(-30)"/>
          <path d="M0-25c1-7 3-11 6-13" stroke="#5a3515" stroke-width="3" fill="none" stroke-linecap="round"/>
          <path d="M5-34c8-5 16-2 18 2-7 4-14 3-18-2z" fill="#3e8a1e"/>
          ${Array.from({ length: 9 }, (_, i) => `<circle cx="${-15 + (i * 37) % 30}" cy="${-8 + (i * 13) % 24}" r="1.4" fill="#fff" opacity=".6"/>`).join("")}
        </g>`;
    case "honey":
      return `
        <g transform="translate(84 92)">
          <path d="M-14-30h28l-4 22c0 8-4 12-10 12s-10-4-10-12z" fill="#f2b232"/>
          <g fill="#c77a0f">
            <rect x="-15" y="-34" width="30" height="5" rx="2.5"/>
            <rect x="-16" y="-24" width="32" height="4" rx="2"/>
            <rect x="-15" y="-15" width="30" height="4" rx="2"/>
          </g>
          <path d="M-2 4c0 10 2 20 6 26 4-6 6-16 6-26z" fill="#ffc94a"/>
          <path d="M-20 34c10-6 34-6 44 0 0 10-10 18-22 18s-22-8-22-18z" fill="#ffb81c"/>
          <ellipse cx="-6" cy="36" rx="6" ry="2.5" fill="#fff" opacity=".5"/>
        </g>`;
    case "strawberry":
      return `
        <g transform="translate(86 108) rotate(18)">
          <path d="M-24-12c6-12 42-12 48 0 2 18-12 40-24 44-12-4-26-26-24-44z" fill="#ff3b2e"/>
          <path d="M-24-12c6-12 42-12 48 0" fill="none" stroke="#c4170f" stroke-width="2"/>
          ${Array.from({ length: 14 }, (_, i) => `<ellipse cx="${-15 + (i * 11) % 30}" cy="${-4 + Math.floor(i / 3) * 7}" rx="1.4" ry="2.2" fill="#ffe17a"/>`).join("")}
          <path d="M0-16l-14-8 10 1-8-10 12 7 0-12 5 12 9-8-4 11 12-2-12 9z" fill="#3c9c25"/>
        </g>`;
    case "speculoos":
      return `
        <g transform="translate(84 110) rotate(-14)">
          <rect x="-28" y="-20" width="56" height="40" rx="5" fill="#c06a22"/>
          <rect x="-24" y="-16" width="48" height="32" rx="3" fill="none" stroke="#8a4512" stroke-width="2"/>
          <path d="M-16-6h32M-16 0h32M-16 6h32" stroke="#8a4512" stroke-width="2" stroke-linecap="round"/>
          <circle cx="-30" cy="-6" r="3" fill="#c06a22"/><circle cx="30" cy="6" r="3" fill="#c06a22"/>
          <circle cx="-10" cy="-30" r="3.5" fill="#b05e1c"/><circle cx="14" cy="-34" r="2.2" fill="#b05e1c"/>
        </g>`;
    case "cotton":
      return `
        <g transform="translate(84 96)">
          <rect x="-2" y="10" width="4" height="40" rx="2" fill="#fff" opacity=".9"/>
          <g fill="#ffb3e3">
            <circle cx="-12" cy="-6" r="15"/><circle cx="10" cy="-10" r="17"/>
            <circle cx="0" cy="6" r="15"/><circle cx="-18" cy="10" r="10"/><circle cx="18" cy="8" r="11"/>
          </g>
          <g fill="#ffd4ef" opacity=".85">
            <circle cx="-8" cy="-10" r="8"/><circle cx="12" cy="-14" r="7"/>
          </g>
        </g>`;
    default:
      return "";
  }
}

function pouchSVG(flavor) {
  const f = typeof flavor === "string" ? FLAVORS.find((x) => x.id === flavor) : flavor;
  const id = `p${++uid}`;
  const bodyPath = "M30 34 Q30 26 40 26 H80 Q90 26 90 34 L104 52 Q108 58 108 66 V186 Q108 196 98 196 H22 Q12 196 12 186 V66 Q12 58 16 52 Z";
  const label = f.line2
    ? `<text x="20" y="122" class="pf">${f.line1}</text><text x="20" y="138" class="pf">${f.line2}</text>`
    : `<text x="20" y="${f.line1.length > 6 ? 130 : 132}" class="pf" ${f.line1.length > 6 ? 'font-size="15"' : ""}>${f.line1}</text>`;
  const energiesY = f.line2 ? 149 : 143;
  return `
  <svg class="pouch" viewBox="0 0 120 200" role="img" aria-label="Gourde FREIZ ${f.name}">
    <defs>
      <linearGradient id="${id}g" x1="0" x2="1">
        <stop offset="0" stop-color="${f.dark}"/>
        <stop offset=".35" stop-color="${f.body}"/>
        <stop offset=".7" stop-color="${f.body}"/>
        <stop offset="1" stop-color="${f.dark}"/>
      </linearGradient>
      <radialGradient id="shine" cx=".35" cy=".3" r=".8">
        <stop offset="0" stop-color="#fff" stop-opacity=".35"/>
        <stop offset="1" stop-color="#000" stop-opacity=".12"/>
      </radialGradient>
      <clipPath id="${id}c"><path d="${bodyPath}"/></clipPath>
    </defs>
    <!-- bouchon -->
    <rect x="46" y="2" width="28" height="20" rx="3" fill="#f4f4f2"/>
    <g stroke="#d7d7d2" stroke-width="1.4">
      <line x1="51" y1="5" x2="51" y2="19"/><line x1="56" y1="5" x2="56" y2="19"/><line x1="61" y1="5" x2="61" y2="19"/>
      <line x1="66" y1="5" x2="66" y2="19"/><line x1="70" y1="5" x2="70" y2="19"/>
    </g>
    <rect x="42" y="20" width="36" height="7" rx="2" fill="#e6e6e1"/>
    <!-- corps -->
    <path d="${bodyPath}" fill="url(#${id}g)"/>
    <g clip-path="url(#${id}c)">
      ${fruitArt(f.fruit)}
      <path d="M0 160 Q30 150 60 158 T120 154 V200 H0Z" fill="${f.band}"/>
      <text x="60" y="182" text-anchor="middle" font-family="Inter, sans-serif" font-weight="800" font-size="5.2" letter-spacing=".6" fill="#fff" opacity=".85">SANS SUCRES AJOUTÉS</text>
      <rect x="12" y="26" width="10" height="170" fill="#fff" opacity=".12"/>
    </g>
    <!-- logo -->
    <text x="60" y="76" text-anchor="middle" font-family="Anton, Impact, sans-serif" font-size="27" fill="${f.ink}" transform="skewX(-8) translate(10 0)">FREIZ</text>
    <style>.pf{font-family:"Caveat Brush",cursive;font-size:17px;fill:${f.ink}}</style>
    ${label}
    <text x="20" y="${energiesY}" font-family="Anton, Impact, sans-serif" font-size="7.5" letter-spacing=".4" fill="${f.ink}">ENERGIES</text>
  </svg>`;
}

/* ---------- Rendu ---------- */
function renderHero() {
  const order = ["barbe-a-papa", "miel", "pomme", "fraise", "speculos"];
  document.getElementById("heroFan").innerHTML = order.map((id) => pouchSVG(id)).join("");
  document.getElementById("solutionPouch").innerHTML = pouchSVG("pomme");
}

function renderFlavors() {
  const el = document.getElementById("flavors");
  el.innerHTML = FLAVORS.map((f) => `
    <article class="flavor reveal" style="--c1:${f.card[0]};--c2:${f.card[1]}">
      ${pouchSVG(f)}
      <h3 class="flavor__name">${f.name}</h3>
      <p class="flavor__tag">${f.tag}</p>
      <div class="flavor__price">${euro(UNIT_PRICE)} <small>/ gourde</small></div>
      <button class="btn" data-add="gourde-${f.id}">+ Ajouter</button>
    </article>`).join("");
}

/* ---------- Panier ---------- */
const STORAGE_KEY = "freiz-cart";
let cart = {};
try { cart = JSON.parse(localStorage.getItem(STORAGE_KEY)) || {}; } catch (e) { cart = {}; }

function saveCart() {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(cart)); } catch (e) { /* stockage indisponible */ }
}

function cartTotal() {
  return Object.entries(cart).reduce((s, [id, q]) => s + (PRODUCTS[id] ? PRODUCTS[id].price * q : 0), 0);
}

function renderCart() {
  const items = Object.entries(cart).filter(([id, q]) => PRODUCTS[id] && q > 0);
  const count = items.reduce((s, [, q]) => s + q, 0);
  const total = cartTotal();

  document.getElementById("cartCount").textContent = count;
  document.getElementById("cartTotal").textContent = euro(total);

  const remaining = FREE_SHIPPING - total;
  const pct = Math.min(100, (total / FREE_SHIPPING) * 100);
  document.getElementById("cartShipping").innerHTML = (remaining > 0
    ? `Plus que <strong>${euro(remaining)}</strong> pour la livraison offerte 🚚`
    : `🎉 <strong>Livraison offerte</strong> débloquée !`) + `<div class="cart__bar"><i style="width:${pct}%"></i></div>`;

  const list = document.getElementById("cartItems");
  list.innerHTML = items.length
    ? items.map(([id, q]) => `
      <li class="cart-item">
        ${pouchSVG(PRODUCTS[id].flavor)}
        <div>
          <div class="cart-item__name">${PRODUCTS[id].name}</div>
          <div class="cart-item__price">${euro(PRODUCTS[id].price * q)}</div>
        </div>
        <div class="qty">
          <button data-dec="${id}" aria-label="Retirer un">−</button>
          <span>${q}</span>
          <button data-inc="${id}" aria-label="Ajouter un">+</button>
        </div>
      </li>`).join("")
    : `<li class="cart__empty">Ton panier est vide.<br>Le pack découverte est un bon début 😉</li>`;

  document.getElementById("checkout").disabled = !items.length;
}

function add(id) {
  cart[id] = (cart[id] || 0) + 1;
  saveCart();
  renderCart();
  const badge = document.getElementById("cartCount");
  badge.classList.remove("bump"); void badge.offsetWidth; badge.classList.add("bump");
  toast(`✔ ${PRODUCTS[id].name} ajouté au panier`);
}

function setQty(id, delta) {
  cart[id] = Math.max(0, (cart[id] || 0) + delta);
  if (!cart[id]) delete cart[id];
  saveCart();
  renderCart();
}

const cartEl = document.getElementById("cart");
const overlay = document.getElementById("cartOverlay");
function openCart() { cartEl.classList.add("open"); cartEl.setAttribute("aria-hidden", "false"); overlay.hidden = false; }
function closeCart() { cartEl.classList.remove("open"); cartEl.setAttribute("aria-hidden", "true"); overlay.hidden = true; }

let toastTimer;
function toast(msg) {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove("show"), 2200);
}

document.addEventListener("click", (e) => {
  const addBtn = e.target.closest("[data-add]");
  if (addBtn) { add(addBtn.dataset.add); return; }
  const inc = e.target.closest("[data-inc]");
  if (inc) { setQty(inc.dataset.inc, 1); return; }
  const dec = e.target.closest("[data-dec]");
  if (dec) { setQty(dec.dataset.dec, -1); }
});
document.getElementById("cartOpen").addEventListener("click", openCart);
document.getElementById("cartClose").addEventListener("click", closeCart);
overlay.addEventListener("click", closeCart);
document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeCart(); });
document.getElementById("checkout").addEventListener("click", () => {
  // À brancher sur Shopify / Stripe Checkout / WooCommerce
  toast("Paiement à connecter (Stripe, Shopify…) 🔌");
});

/* ---------- CTA collant mobile + animations ---------- */
const sticky = document.getElementById("stickyCta");
const hero = document.querySelector(".hero");
const packs = document.getElementById("packs");
let heroVisible = true, packsVisible = false;
const updateSticky = () => sticky.classList.toggle("visible", !heroVisible && !packsVisible);
new IntersectionObserver(([e]) => { heroVisible = e.isIntersecting; updateSticky(); }).observe(hero);
new IntersectionObserver(([e]) => { packsVisible = e.isIntersecting; updateSticky(); }, { threshold: 0.2 }).observe(packs);

renderHero();
renderFlavors();
renderCart();

document.querySelectorAll(".pain, .step, .pack, .review, .benefits li").forEach((el) => el.classList.add("reveal"));
const revealObs = new IntersectionObserver((entries) => {
  entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add("in"); revealObs.unobserve(e.target); } });
}, { threshold: 0.15 });
document.querySelectorAll(".reveal").forEach((el) => revealObs.observe(el));
