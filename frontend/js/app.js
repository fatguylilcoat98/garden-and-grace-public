/*
  Garden & Grace — Public Edition · app.js
  Truth · Safety · We Got Your Back
*/

const API = "";  // same origin

// ── Verse/Content Mode ──────────────────────────────────────
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

function verseParam() { return "verse_mode=" + getVerseMode(); }

function toggleContent(type) {
  const t = getContentToggles();
  t[type] = !t[type];
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
    if (toggle) toggle.classList.toggle("active", t[key]);
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

// ── Hamburger ──────────────────────────────────────────────
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

// ── Shared state ───────────────────────────────────────────
const state = {
  user: null,
  billing: null,
  billing_enabled_known: false,
};

// ── Router ─────────────────────────────────────────────────
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
  if (!isSignedIn()) { goAuth(); return; }
  showScreen("screen-home");
}

function goAuth() {
  showScreen("screen-auth");
}

// ── API helpers (Supabase Bearer token) ────────────────────
async function _authHeader() {
  const token = await getAccessToken();
  return token ? { "Authorization": "Bearer " + token } : {};
}

async function apiPost(path, data, isFormData = false) {
  const headers = await _authHeader();
  if (!isFormData) headers["Content-Type"] = "application/json";

  const sep = path.includes("?") ? "&" : "?";
  const url = API + path + sep + verseParam();
  const response = await fetch(url, {
    method: "POST",
    headers,
    body: isFormData ? data : JSON.stringify(data || {}),
  });

  let json = {};
  try { json = await response.json(); } catch {}

  if (response.status === 402) {
    showPaywall(json.detail || "You've used your free queries for today.");
    refreshBillingStatus();
    throw new Error("LIMIT_REACHED");
  }
  if (response.status === 401) {
    toast("Session expired. Please sign in again.", "error");
    signOut();
    throw new Error("UNAUTHORIZED");
  }
  if (!response.ok) throw new Error(json.detail || "Something went wrong.");

  if (json.quota) {
    state.billing = Object.assign({}, state.billing, json.quota);
    renderQuotaCounter(state.billing);
  }
  return json;
}

async function apiGet(path) {
  const headers = await _authHeader();
  const response = await fetch(API + path, { headers });
  let json = {};
  try { json = await response.json(); } catch {}
  if (response.status === 401) throw new Error("Not signed in.");
  if (!response.ok) throw new Error(json.detail || "Something went wrong.");
  return json;
}

// ── Toast ──────────────────────────────────────────────────
function toast(msg, type) {
  type = type || "success";
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.className = "toast " + type + " show";
  setTimeout(() => el.classList.remove("show"), 3500);
}

// ── Loading helpers ────────────────────────────────────────
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

// ── Date helpers ───────────────────────────────────────────
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

// ── Photo upload helper ────────────────────────────────────
const _uploadBound = {};

function setupPhotoUpload(areaId, inputId, previewId, onFile) {
  const area    = document.getElementById(areaId);
  const input   = document.getElementById(inputId);
  const preview = document.getElementById(previewId);
  if (!area || !input) return;

  if (_uploadBound[inputId]) {
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

// ── Init ───────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", async function() {
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/static/service-worker.js").catch(function() {});
  }

  await authReady();

  if (typeof checkUpgradeReturn === "function") checkUpgradeReturn();

  if (isSignedIn()) {
    initHome();
  } else {
    goAuth();
  }
});

function initHome() {
  showScreen("screen-home");
  var name = (state.user && state.user.name) ? state.user.name : "Friend";
  document.getElementById("home-greeting").textContent = getGreeting() + ", " + name + " 🌿";
  document.getElementById("home-date").textContent = formatDate();

  refreshDailyVerse();
  refreshBillingStatus();
  updateMenuToggles();
}
