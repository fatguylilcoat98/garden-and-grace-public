/*
  Garden & Grace — Public Edition
  The Good Neighbor Guard
  Built by Christopher Hughes · Sacramento, CA
  Created with the help of AI collaborators (Claude · GPT · Gemini · Groq)
  Truth · Safety · We Got Your Back
*/

const API = "";  // Same origin

// ── Verse/Content Mode ──────────────────────────────────────
// Each content type can be toggled independently
function getContentToggles() {
  try {
    const saved = localStorage.getItem("gg_content_toggles");
    if (saved) return JSON.parse(saved);
  } catch {}
  return { scripture: true, sayings: false, jokes: false };
}

function saveContentToggles(toggles) {
  localStorage.setItem("gg_content_toggles", JSON.stringify(toggles));
}

function getVerseMode() {
  const t = getContentToggles();
  if (t.scripture) return "scripture";
  if (t.sayings) return "sayings";
  if (t.jokes) return "jokes";
  return "off";
}

function verseParam() {
  return "verse_mode=" + getVerseMode();
}

function toggleContent(type) {
  const t = getContentToggles();
  t[type] = !t[type];
  // Only one can be active at a time (radio-style)
  if (t[type]) {
    if (type !== "scripture") t.scripture = false;
    if (type !== "sayings") t.sayings = false;
    if (type !== "jokes") t.jokes = false;
  }
  saveContentToggles(t);
  updateMenuToggles();
  refreshDailyVerse();
}

function updateMenuToggles() {
  const t = getContentToggles();
  ["scripture", "sayings", "jokes"].forEach(key => {
    const toggle = document.getElementById(`toggle-${key}`);
    if (toggle) {
      toggle.classList.toggle("active", t[key]);
    }
  });
}

function refreshDailyVerse() {
  const mode = getVerseMode();
  apiGet("/features/daily-verse?verse_mode=" + mode).then(verse => {
    const vt = document.getElementById("daily-verse-text");
    const vr = document.getElementById("daily-verse-ref");
    if (vt && vr) {
      if (verse.verse) {
        vt.textContent = '"' + verse.verse + '"';
        vr.textContent = "— " + verse.ref;
        vt.parentElement.style.display = "";
      } else {
        vt.parentElement.style.display = "none";
      }
    }
  }).catch(() => {});
}

// ── Hamburger Menu ──────────────────────────────────────────
function toggleMenu() {
  const menu = document.getElementById("hamburger-panel");
  const overlay = document.getElementById("menu-overlay");
  if (!menu) return;
  const isOpen = menu.classList.contains("open");
  menu.classList.toggle("open", !isOpen);
  overlay.classList.toggle("open", !isOpen);
}

function closeMenu() {
  const menu = document.getElementById("hamburger-panel");
  const overlay = document.getElementById("menu-overlay");
  if (menu) menu.classList.remove("open");
  if (overlay) overlay.classList.remove("open");
}

// ── State ───────────────────────────────────────────────────
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

// ── Router ──────────────────────────────────────────────────
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
  closeMenu();
}

function goHome() {
  if (!state.sessionToken) { goAuth(); return; }
  showScreen("screen-home");
}

function goAuth() {
  clearSession();
  showScreen("screen-auth");
}

// ── API Helper ──────────────────────────────────────────────
async function apiPost(path, data, isFormData = false) {
  const headers = {};
  if (state.sessionToken) headers["Authorization"] = "Bearer " + state.sessionToken;
  if (!isFormData) headers["Content-Type"] = "application/json";

  const sep = path.includes("?") ? "&" : "?";
  const url = API + path + sep + verseParam();
  const response = await fetch(url, {
    method: "POST",
    headers,
    body: isFormData ? data : JSON.stringify(data),
  });

  const json = await response.json();

  if (response.status === 429 || json.status === "limit_reached") {
    const msg = json.message || "Daily limit reached. Please try again tomorrow.";
    showLimitMessage(msg, json.type);
    throw new Error("LIMIT_REACHED");
  }

  if (!response.ok) throw new Error(json.detail || "Something went wrong.");
  return json;
}

async function apiGet(path) {
  const headers = {};
  if (state.sessionToken) headers["Authorization"] = "Bearer " + state.sessionToken;
  const response = await fetch(API + path, { headers });
  const json = await response.json();
  if (!response.ok) throw new Error(json.detail || "Something went wrong.");
  return json;
}

// ── Rate Limit UI ───────────────────────────────────────────
function showLimitMessage(msg, type) {
  document.querySelectorAll(".loading-overlay").forEach(el => el.classList.remove("visible"));
  document.querySelectorAll('[id$="-content"]').forEach(el => el.style.display = "");

  const existing = document.getElementById("limit-overlay");
  if (existing) existing.remove();

  const overlay = document.createElement("div");
  overlay.id = "limit-overlay";
  overlay.style.cssText = "position:fixed;inset:0;z-index:9999;background:rgba(30,40,30,0.95);display:flex;align-items:center;justify-content:center;padding:24px;";
  overlay.innerHTML = '<div style="text-align:center;max-width:360px;">' +
    '<div style="font-size:40px;margin-bottom:16px;">🌿</div>' +
    '<h2 style="font-size:20px;color:#e8dcc8;margin-bottom:12px;font-family:Georgia,serif;">' +
    (type === "daily" ? "Daily limit reached" : "Just a moment") + '</h2>' +
    '<p style="font-size:15px;color:#a09880;line-height:1.7;margin-bottom:24px;">' + msg + '</p>' +
    '<button onclick="document.getElementById(\'limit-overlay\').remove()" ' +
    'style="padding:12px 24px;background:transparent;border:1px solid #5a6a5a;color:#a09880;border-radius:8px;cursor:pointer;font-size:14px;">Go Back</button>' +
    '</div>';
  document.body.appendChild(overlay);
}

// ── Usage Counter ───────────────────────────────────────────
async function updateUsageDisplay() {
  try {
    const usage = await apiGet("/usage");
    const el = document.getElementById("usage-counter");
    if (el) {
      el.textContent = usage.remaining + " of " + usage.daily_limit + " uses remaining today";
      el.style.display = "block";
    }
  } catch(e) { /* silent */ }
}

// ── Toast ───────────────────────────────────────────────────
function toast(msg, type) {
  type = type || "success";
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.className = "toast " + type + " show";
  setTimeout(() => el.classList.remove("show"), 3500);
}

// ── Loading helpers ─────────────────────────────────────────
function showLoading(screenId, msg) {
  msg = msg || "Working on it...";
  var lo = document.getElementById(screenId + "-loading");
  lo.classList.add("visible");
  lo.querySelector(".loading-text").textContent = msg;
  document.getElementById(screenId + "-content").style.display = "none";
}
function hideLoading(screenId) {
  document.getElementById(screenId + "-loading").classList.remove("visible");
  document.getElementById(screenId + "-content").style.display = "";
}

// ── Date helpers ────────────────────────────────────────────
function getGreeting() {
  var h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 17) return "Good afternoon";
  return "Good evening";
}

function formatDate() {
  return new Date().toLocaleDateString("en-US", {
    weekday: "long", month: "long", day: "numeric"
  });
}

// ── Photo upload helper (fixed for re-entry) ────────────────
// Uses a registry to prevent duplicate event listeners
const _uploadBound = {};

function setupPhotoUpload(areaId, inputId, previewId, onFile) {
  const area    = document.getElementById(areaId);
  const input   = document.getElementById(inputId);
  const preview = document.getElementById(previewId);
  if (!area || !input) return;

  // Prevent duplicate binding
  if (_uploadBound[inputId]) {
    // Already bound — just replace the callback
    _uploadBound[inputId].onFile = onFile;
    return;
  }

  var handler = {
    onFile: onFile,
    handleFile: function(file) {
      var reader = new FileReader();
      reader.onload = function(e) {
        preview.src = e.target.result;
        preview.style.display = "block";
        area.style.display = "none";
      };
      reader.readAsDataURL(file);
      if (handler.onFile) handler.onFile(file);
    }
  };

  area.addEventListener("click", function() { input.click(); });
  area.addEventListener("dragover", function(e) { e.preventDefault(); area.classList.add("dragover"); });
  area.addEventListener("dragleave", function() { area.classList.remove("dragover"); });
  area.addEventListener("drop", function(e) {
    e.preventDefault();
    area.classList.remove("dragover");
    if (e.dataTransfer.files[0]) handler.handleFile(e.dataTransfer.files[0]);
  });
  input.addEventListener("change", function() {
    if (input.files[0]) handler.handleFile(input.files[0]);
  });

  _uploadBound[inputId] = handler;
}

// ── Init ────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", function() {
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/static/service-worker.js").catch(function() {});
  }

  if (loadSession()) {
    initHome();
  } else {
    goAuth();
  }
});

function initHome() {
  showScreen("screen-home");
  var name = state.user ? state.user.name : "Friend";
  document.getElementById("home-greeting").textContent = getGreeting() + ", " + name + " 🌿";
  document.getElementById("home-date").textContent = formatDate();

  refreshDailyVerse();
  updateUsageDisplay();
  updateMenuToggles();
}
