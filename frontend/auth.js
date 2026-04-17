/**
 * Circle of the Ninth Gate — auth.js
 *
 * Shared by login.html and comms.html.
 * Handles all interactivity: login submission, token storage,
 * session display, page transitions, and logout.
 *
 * ── Configuration ─────────────────────────────────────────────────────────
 * Set BACKEND_URL to your Railway deployment URL before going live.
 * Example: "https://ninth-gate-production.up.railway.app"
 */

const BACKEND_URL = "https://YOUR-RAILWAY-APP.up.railway.app"; // ← change this
const TOKEN_KEY   = "ng_session_token";
const COMMS_PAGE  = "comms.html";
const LOGIN_PAGE  = "login.html";

// ── Utilities ──────────────────────────────────────────────────────────────

function saveToken(token) {
  sessionStorage.setItem(TOKEN_KEY, token);
}

function loadToken() {
  return sessionStorage.getItem(TOKEN_KEY);
}

function clearToken() {
  sessionStorage.removeItem(TOKEN_KEY);
}

function generateSessionId() {
  return "SX-" + Math.random().toString(36).substring(2, 8).toUpperCase();
}

function currentTimestamp() {
  return new Date().toISOString().replace("T", " ").substring(0, 19) + " UTC";
}

// ── Fade helpers ───────────────────────────────────────────────────────────

function fadeOut(el, duration = 600) {
  return new Promise(resolve => {
    el.style.transition = `opacity ${duration}ms ease`;
    el.style.opacity = "0";
    setTimeout(resolve, duration);
  });
}

function revealMain(el) {
  el.style.display = "block";
  // Trigger reflow so the CSS animation fires
  void el.offsetWidth;
  el.style.animation = "fadeIn 1.2s ease forwards";
}

// ── API calls ──────────────────────────────────────────────────────────────

async function apiAuthenticate(passphrase) {
  const res = await fetch(`${BACKEND_URL}/authenticate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ passphrase }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Authentication failed");
  return data.token;
}

async function apiVerify(token) {
  const res = await fetch(`${BACKEND_URL}/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token }),
  });
  return res.ok;
}

// ── LOGIN PAGE logic ───────────────────────────────────────────────────────
// Runs when login.html loads this script.

if (document.getElementById("passfield")) {

  // If already authenticated, skip straight to comms
  (async () => {
    const existing = loadToken();
    if (existing && await apiVerify(existing)) {
      window.location.replace(COMMS_PAGE);
    }
  })();

  const btn      = document.getElementById("login-btn");
  const input    = document.getElementById("passfield");
  const errorEl  = document.getElementById("login-error");

  async function attemptLogin() {
    const passphrase = input.value.trim();
    if (!passphrase) return;

    btn.disabled = true;
    btn.textContent = "Verifying...";
    errorEl.classList.remove("visible");

    try {
      const token = await apiAuthenticate(passphrase);
      saveToken(token);

      // Fade out the page, then navigate
      await fadeOut(document.querySelector(".wrap"));
      window.location.assign(COMMS_PAGE);

    } catch {
      input.value = "";
      input.focus();
      errorEl.classList.add("visible");
      setTimeout(() => errorEl.classList.remove("visible"), 3000);
      btn.disabled = false;
      btn.textContent = "Authenticate";
    }
  }

  btn.addEventListener("click", attemptLogin);
  input.addEventListener("keydown", e => { if (e.key === "Enter") attemptLogin(); });
}

// ── COMMS PAGE logic ───────────────────────────────────────────────────────
// Runs when comms.html loads this script.

if (document.getElementById("gate")) {

  const gate   = document.getElementById("gate");
  const main   = document.getElementById("main");
  const logoutBtn = document.getElementById("logout-btn");

  // Verify token on load; redirect to login if invalid
  (async () => {
    const token = loadToken();
    const valid = token && await apiVerify(token);

    if (!valid) {
      clearToken();
      window.location.replace(LOGIN_PAGE);
      return;
    }

    // Token is good — hide gate overlay, reveal content
    await fadeOut(gate, 500);
    gate.style.display = "none";

    document.getElementById("session-id").textContent   = generateSessionId();
    document.getElementById("session-time").textContent = currentTimestamp();

    revealMain(main);
  })();

  // Logout
  logoutBtn.addEventListener("click", async () => {
    await fadeOut(main);
    clearToken();
    window.location.assign(LOGIN_PAGE);
  });
}
