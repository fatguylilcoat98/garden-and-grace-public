/*
  Garden & Grace — Public Edition
  The Good Neighbor Guard
  Built by Christopher Hughes · Sacramento, CA
  Created with the help of AI collaborators (Claude · GPT · Gemini · Groq)
  Truth · Safety · We Got Your Back
*/

const API = "";  // Same origin

// ── State ────────────────────────────────────────────────────────
const state = {
  user: null,
  sessionToken: null,
};

function loadSession() {
  const token = localStorage.getItem("gg_session");
  const user  = localStorage.getItem("gg_user");
  if (token && user) {
    state.sessionToken = token;
    state.user = JSON.parse(user);
    return true;
  }
  return false;
}

function saveSession(token, user) {
  state.sessionToken = token;
  state.user = user;
  localStorage.setItem("gg_session", token);
  localStorage.setItem("gg_user", JSON.stringify(user));
}

function clearSession() {
  state.sessionToken = null;
  state.user = null;
  localStorage.removeItem("gg_session");
  localStorage.removeItem("gg_user");
}

// ── Router ───────────────────────────────────────────────────────
function showScreen(id) {
  document.querySelectorAll(".screen").forEach(s => {
    s.classList.remove("active");
    s.style.display = "none";
  });
  const screen = document.getElementById(id);
  if (screen) {
    screen.style.display = "";
    screen.classList.add("active");
  }
  window.scrollTo(0, 0);
}

function goHome() {
  if (!state.sessionToken) { goAuth(); return; }
  showScreen("screen-home");
}

function goAuth() {
  clearSession();
  showScreen("screen-auth");
}

// ── API Helper (with rate limit detection) ───────────────────────
async function apiPost(path, data, isFormData = false) {
  const headers = {};
  if (state.sessionToken) headers["Authorization"] = `Bearer ${state.sessionToken}`;
  if (!isFormData) headers["Content-Type"] = "application/json";

  const response = await fetch(API + path, {
    method: "POST",
    headers,
    body: isFormData ? data : JSON.stringify(data),
  });

  const json = await response.json();

  // Rate limit detection
  if (response.status === 429 || json.status === "limit_reached") {
    const msg = json.message || "Daily limit reached for now. Please try again tomorrow.";
    showLimitMessage(msg, json.type);
    throw new Error("LIMIT_REACHED");
  }

  if (!response.ok) throw new Error(json.detail || "Something went wrong.");
  return json;
}

async function apiGet(path) {
  const headers = {};
  if (state.sessionToken) headers["Authorization"] = `Bearer ${state.sessionToken}`;
  const response = await fetch(API + path, { headers });
  const json = await response.json();
  if (!response.ok) throw new Error(json.detail || "Something went wrong.");
  return json;
}

// ── Rate Limit UI ────────────────────────────────────────────────
function showLimitMessage(msg, type) {
  // Hide any loading states
  document.querySelectorAll(".loading-overlay").forEach(el => el.classList.remove("visible"));
  document.querySelectorAll('[id$="-content"]').forEach(el => el.style.display = "");

  const existing = document.getElementById("limit-overlay");
  if (existing) existing.remove();

  const overlay = document.createElement("div");
  overlay.id = "limit-overlay";
  overlay.style.cssText = `
    position:fixed;inset:0;z-index:9999;
    background:rgba(30,40,30,0.95);
    display:flex;align-items:center;justify-content:center;
    padding:24px;
  `;
  overlay.innerHTML = `
    <div style="text-align:center;max-width:360px;">
      <div style="font-size:40px;margin-bottom:16px;">🌿</div>
      <h2 style="font-size:20px;color:#e8dcc8;margin-bottom:12px;font-family:Georgia,serif;">
        ${type === 'daily' ? 'Daily limit reached for now' : 'Just a moment'}
      </h2>
      <p style="font-size:15px;color:#a09880;line-height:1.7;margin-bottom:24px;">
        ${msg}
      </p>
      ${type === 'daily' ? `
        <p style="font-size:13px;color:#7a7060;margin-bottom:20px;">
          Want more? Support Garden & Grace for unlimited access.
        </p>
        <a href="mailto:thegoodneighborguard@gmail.com?subject=Garden%20and%20Grace%20Access"
           style="display:inline-block;padding:12px 28px;background:#5a7a5a;color:#fff;
                  border-radius:8px;text-decoration:none;font-weight:600;font-size:14px;
                  margin-bottom:12px;">
          Request Access
        </a><br>
      ` : ''}
      <button onclick="document.getElementById('limit-overlay').remove()"
              style="margin-top:8px;padding:10px 24px;background:transparent;
                     border:1px solid #5a6a5a;color:#a09880;border-radius:8px;
                     cursor:pointer;font-size:14px;">
        Go Back
      </button>
    </div>
  `;
  document.body.appendChild(overlay);
}

// ── Usage Counter ────────────────────────────────────────────────
async function updateUsageDisplay() {
  try {
    const usage = await apiGet("/usage");
    const el = document.getElementById("usage-counter");
    if (el) {
      el.textContent = `${usage.remaining} of ${usage.daily_limit} uses remaining today`;
      el.style.display = "block";
    }
  } catch(e) { /* silent */ }
}

// ── Toast ─────────────────────────────────────────────────────────
function toast(msg, type = "success") {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.className = `toast ${type} show`;
  setTimeout(() => el.classList.remove("show"), 3500);
}

// ── Loading helpers ───────────────────────────────────────────────
function showLoading(screenId, msg = "Working on it…") {
  document.getElementById(`${screenId}-loading`).classList.add("visible");
  document.getElementById(`${screenId}-loading`).querySelector(".loading-text").textContent = msg;
  document.getElementById(`${screenId}-content`).style.display = "none";
}
function hideLoading(screenId) {
  document.getElementById(`${screenId}-loading`).classList.remove("visible");
  document.getElementById(`${screenId}-content`).style.display = "";
}

// ── Date helpers ──────────────────────────────────────────────────
function getGreeting() {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 17) return "Good afternoon";
  return "Good evening";
}

function formatDate() {
  return new Date().toLocaleDateString("en-US", {
    weekday: "long", month: "long", day: "numeric"
  });
}

// ── Photo upload helper ───────────────────────────────────────────
function setupPhotoUpload(areaId, inputId, previewId, onFile) {
  const area    = document.getElementById(areaId);
  const input   = document.getElementById(inputId);
  const preview = document.getElementById(previewId);

  area.addEventListener("click", () => input.click());
  area.addEventListener("dragover", e => { e.preventDefault(); area.classList.add("dragover"); });
  area.addEventListener("dragleave", () => area.classList.remove("dragover"));
  area.addEventListener("drop", e => {
    e.preventDefault();
    area.classList.remove("dragover");
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  });
  input.addEventListener("change", () => {
    if (input.files[0]) handleFile(input.files[0]);
  });

  function handleFile(file) {
    const reader = new FileReader();
    reader.onload = e => {
      preview.src = e.target.result;
      preview.style.display = "block";
      area.style.display = "none";
    };
    reader.readAsDataURL(file);
    if (onFile) onFile(file);
  }
}

// ── Init ──────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/static/service-worker.js").catch(() => {});
  }

  if (loadSession()) {
    initHome();
  } else {
    goAuth();
  }
});

function initHome() {
  showScreen("screen-home");
  const name = state.user?.name || "Friend";
  document.getElementById("home-greeting").textContent = `${getGreeting()}, ${name} 🌿`;
  document.getElementById("home-date").textContent = formatDate();

  // Load daily verse
  apiGet("/features/daily-verse").then(verse => {
    document.getElementById("daily-verse-text").textContent = `"${verse.verse}"`;
    document.getElementById("daily-verse-ref").textContent = `— ${verse.ref}`;
  }).catch(() => {});

  // Show usage counter
  updateUsageDisplay();
}
