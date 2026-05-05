/*
  Garden & Grace — Billing (Stripe Checkout upgrade flow).
*/

async function refreshBillingStatus() {
  try {
    const status = await apiGet("/billing/status");
    state.billing = status;
    renderQuotaCounter(status);
    return status;
  } catch (e) {
    return null;
  }
}

function renderQuotaCounter(status) {
  const el = document.getElementById("usage-counter");
  if (!el || !status) return;
  if (status.tier === "premium") {
    el.textContent = "✨ Premium · unlimited queries";
  } else {
    const remaining = status.remaining != null ? status.remaining : "—";
    const limit = status.daily_limit != null ? status.daily_limit : "—";
    el.textContent = remaining + " of " + limit + " free queries remaining today";
  }
  el.style.display = "block";
}

async function startUpgrade() {
  if (!state.billing || !state.billing_enabled_known) {
    const cfg = await loadConfig();
    if (!cfg.billingEnabled) {
      toast("Upgrades aren't live yet — check back soon!", "info");
      return;
    }
  }
  try {
    const data = await apiPost("/billing/create-checkout-session", {});
    if (data && data.url) {
      window.location.href = data.url;
    } else {
      toast("Couldn't start checkout. Please try again.", "error");
    }
  } catch (e) {
    if (e.message !== "LIMIT_REACHED") {
      toast(e.message || "Couldn't start checkout.", "error");
    }
  }
}

function showPaywall(message) {
  const existing = document.getElementById("paywall-overlay");
  if (existing) existing.remove();

  const cfg = _config || {};
  const upgradeAvailable = cfg.billingEnabled !== false;

  const overlay = document.createElement("div");
  overlay.id = "paywall-overlay";
  overlay.style.cssText = "position:fixed;inset:0;z-index:9999;background:rgba(30,40,30,0.95);display:flex;align-items:center;justify-content:center;padding:24px;";
  overlay.innerHTML =
    '<div style="text-align:center;max-width:380px;background:#fdf8f0;border-radius:14px;padding:28px 24px;box-shadow:0 8px 32px rgba(0,0,0,.3);">' +
      '<div style="font-size:42px;margin-bottom:12px;">🌿</div>' +
      '<h2 style="font-size:22px;color:#3d6b3f;margin-bottom:10px;font-family:Georgia,serif;">Out of free queries</h2>' +
      '<p style="font-size:15px;color:#5a4a3a;line-height:1.6;margin-bottom:22px;">' +
        (message || "You've used all your free queries today. Upgrade to keep going — unlimited photos, recipes, and reports.") +
      '</p>' +
      (upgradeAvailable
        ? '<button id="paywall-upgrade" style="width:100%;padding:14px;background:#b08a4a;color:#fff;border:none;border-radius:10px;font-size:16px;font-weight:600;cursor:pointer;margin-bottom:10px;">✨ Upgrade for unlimited</button>'
        : '<div style="padding:14px;background:#eee;color:#777;border-radius:10px;font-size:14px;margin-bottom:10px;">Upgrades coming soon.</div>') +
      '<button id="paywall-close" style="width:100%;padding:12px;background:transparent;color:#5a4a3a;border:1px solid #c4b89c;border-radius:10px;font-size:14px;cursor:pointer;">Maybe later</button>' +
    '</div>';
  document.body.appendChild(overlay);
  const upBtn = document.getElementById("paywall-upgrade");
  if (upBtn) upBtn.addEventListener("click", startUpgrade);
  document.getElementById("paywall-close").addEventListener("click", () => overlay.remove());
}

function checkUpgradeReturn() {
  const params = new URLSearchParams(window.location.search);
  if (params.get("upgraded") === "1") {
    toast("✨ Welcome to premium — unlimited queries unlocked!", "success");
    history.replaceState(null, "", window.location.pathname);
    setTimeout(refreshBillingStatus, 1500);
  } else if (params.get("upgrade") === "cancel") {
    toast("Upgrade canceled.", "info");
    history.replaceState(null, "", window.location.pathname);
  }
}
