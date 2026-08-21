/*
  Garden & Grace — Auth (Supabase magic link).
  Sign in flow: enter email → Supabase emails a magic link → click link
  returns to the app with an active session.
*/

let _supabase = null;
let _config = null;
let _authReady = null;          // promise resolved once Supabase is ready
let _currentSession = null;

async function loadConfig() {
  if (_config) return _config;
  try {
    const r = await fetch("/config");
    _config = await r.json();
  } catch (e) {
    _config = {};
  }
  return _config;
}

async function initSupabase() {
  if (_supabase) return _supabase;
  const cfg = await loadConfig();
  if (!cfg.supabaseUrl || !cfg.supabaseAnonKey) {
    showAuthConfigError();
    return null;
  }
  if (!window.supabase || !window.supabase.createClient) {
    showAuthConfigError("Supabase JS failed to load. Check your network and refresh.");
    return null;
  }
  _supabase = window.supabase.createClient(cfg.supabaseUrl, cfg.supabaseAnonKey, {
    auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true },
  });
  _supabase.auth.onAuthStateChange((_event, session) => {
    _currentSession = session;
    if (session) {
      state.user = { id: session.user.id, email: session.user.email, name: deriveName(session.user) };
      // Strip the access_token hash Supabase puts in the URL after click-through.
      if (window.location.hash.includes("access_token")) {
        history.replaceState(null, "", window.location.pathname + window.location.search);
      }
      onSignedIn();
    }
  });
  const { data: { session } } = await _supabase.auth.getSession();
  _currentSession = session;
  if (session) {
    state.user = { id: session.user.id, email: session.user.email, name: deriveName(session.user) };
  }
  return _supabase;
}

function deriveName(user) {
  if (!user) return "Friend";
  const meta = user.user_metadata || {};
  return meta.first_name || meta.name || (user.email ? user.email.split("@")[0] : "Friend");
}

function authReady() {
  if (!_authReady) _authReady = initSupabase();
  return _authReady;
}

async function getAccessToken() {
  await authReady();
  if (!_supabase) return null;
  const { data: { session } } = await _supabase.auth.getSession();
  _currentSession = session;
  return session ? session.access_token : null;
}

function isSignedIn() {
  return !!_currentSession;
}

async function sendMagicLink(email) {
  await authReady();
  if (!_supabase) throw new Error("Auth not configured.");
  const redirectTo = window.location.origin + "/";
  const { error } = await _supabase.auth.signInWithOtp({
    email: email.trim().toLowerCase(),
    options: { emailRedirectTo: redirectTo },
  });
  if (error) throw error;
}

async function signOut() {
  if (_supabase) await _supabase.auth.signOut();
  _currentSession = null;
  state.user = null;
  goAuth();
}

function onSignedIn() {
  // Defined in app.js — guarded so this file works in isolation
  if (typeof initHome === "function") initHome();
}

function showAuthConfigError(msg) {
  msg = msg || "Sign-in isn't configured yet. Add SUPABASE_URL and SUPABASE_ANON_KEY on the server.";
  const card = document.getElementById("auth-card-form");
  if (card) {
    card.innerHTML = '<h2>Setup needed</h2><p style="color:#7a6a4a;line-height:1.5;">' + msg + '</p>';
  }
}

async function handleAuthSubmit(e) {
  e.preventDefault();
  const emailInput = document.getElementById("auth-email");
  const email = (emailInput && emailInput.value || "").trim();
  const btn = document.getElementById("auth-submit-btn");
  const status = document.getElementById("auth-status");

  if (!email || !email.includes("@")) {
    if (status) { status.textContent = "Please enter a valid email."; status.style.color = "#a94442"; }
    return;
  }

  btn.disabled = true;
  const originalLabel = btn.textContent;
  btn.textContent = "Sending link…";
  if (status) { status.textContent = ""; status.style.color = ""; }

  try {
    await sendMagicLink(email);
    if (status) {
      status.style.color = "#2d6a4f";
      status.textContent = "Check your inbox — tap the link we just sent to " + email + ".";
    }
    btn.textContent = "Link sent — check your email";
  } catch (err) {
    if (status) {
      status.style.color = "#a94442";
      status.textContent = "Couldn't send link: " + (err.message || err);
    }
    btn.disabled = false;
    btn.textContent = originalLabel;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("auth-form");
  if (form) form.addEventListener("submit", handleAuthSubmit);
  authReady();
});
