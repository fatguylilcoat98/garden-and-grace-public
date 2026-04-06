/*
  Garden & Grace — Public Edition
  Fishing Feature: Deep report + community catches
*/

let _catchPhotoData = "";

function initFishing() {
  showScreen("screen-fishing");
  resetFishing();
  loadCatches();
}

function resetFishing() {
  document.getElementById("fishing-result").classList.remove("visible");
  document.getElementById("fishing-verse").classList.remove("visible");
  document.getElementById("fishing-get-btn").style.display = "flex";
  hideLoading("fishing");
}

async function getFishingReport() {
  showLoading("fishing", "Checking fishing conditions… 🎣");
  document.getElementById("fishing-get-btn").style.display = "none";

  let lat = null, lon = null, locationName = "";

  try {
    const pos = await new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 8000 });
    });
    lat = pos.coords.latitude;
    lon = pos.coords.longitude;
  } catch {
    lat = 38.5816;
    lon = -121.4944;
    locationName = "Sacramento, California";
  }

  try {
    const data = await apiPost("/features/fishing", { lat, lon, location_name: locationName });
    hideLoading("fishing");
    renderFishingResult(data.result, data.verse);
  } catch (err) {
    hideLoading("fishing");
    document.getElementById("fishing-get-btn").style.display = "flex";
    if (err.message !== "LIMIT_REACHED") toast(err.message, "error");
  }
}

function _outlookColor(outlook) {
  const o = (outlook || "").toLowerCase();
  if (o === "strong") return "#2d7a3a";
  if (o === "promising") return "#5a8a3a";
  if (o === "fair") return "#b8860b";
  return "#8b6914"; // slow
}

function renderFishingResult(r, verse) {
  console.log("[Fishing] Raw result:", JSON.stringify(r, null, 2));
  const outlook = r.outlook || "Fair";
  const outlookColor = _outlookColor(outlook);

  // Helper: safely get a displayable string from any value
  function _val(v) {
    if (v === null || v === undefined) return "";
    if (typeof v === "string") return v;
    if (typeof v === "number") return String(v);
    // For objects/arrays, join all string values
    if (Array.isArray(v)) return v.map(_val).join(", ");
    if (typeof v === "object") return Object.values(v).map(_val).filter(Boolean).join(" — ");
    return String(v);
  }

  // Best times
  const times = (r.best_times || []).map(t => {
    if (typeof t === "string") return `<div style="padding:6px 0;border-bottom:1px solid var(--cream-dk);">${t}</div>`;
    return `<div style="display:flex;gap:8px;padding:6px 0;border-bottom:1px solid var(--cream-dk);">
      <span style="font-weight:600;color:var(--green);min-width:90px;">${_val(t.window) || _val(t.time) || ""}</span>
      <span style="color:var(--text-soft);">${_val(t.why) || _val(t.reason) || ""}</span>
    </div>`;
  }).join("");

  // Species
  const speciesRaw = r.active_species || [];
  const species = speciesRaw.map(s => {
    if (typeof s === "string") return `<li>${s}</li>`;
    const name = _val(s.name) || _val(s.species) || _val(s.fish) || Object.values(s).find(v => typeof v === "string") || "Unknown";
    const activity = _val(s.activity) || _val(s.status) || "";
    const note = _val(s.note) || _val(s.tip) || "";
    const actColor = activity.toLowerCase() === "active" ? "var(--green)" :
                     activity.toLowerCase() === "slow" ? "var(--brown-lt)" : "var(--gold-dark, #b8860b)";
    return `<li>
      <strong>${name}</strong>
      ${activity ? `<span style="font-size:0.8rem;color:${actColor};margin-left:6px;">${activity}</span>` : ""}
      ${note ? `<div style="font-size:0.85rem;color:var(--text-soft);margin-top:2px;">${note}</div>` : ""}
    </li>`;
  }).join("") || "<li style='color:var(--text-soft);'>No species data available</li>";

  // Bait & lures
  const baitsRaw = r.bait_and_lures || r.recommended_bait || [];
  const baits = baitsRaw.map(b => {
    if (typeof b === "string") return `<li>${b}</li>`;
    const name = _val(b.name) || _val(b.bait) || _val(b.lure) || Object.values(b).find(v => typeof v === "string") || "Unknown";
    const bestFor = _val(b.best_for) || _val(b.bestFor) || "";
    const tip = _val(b.tip) || _val(b.note) || "";
    return `<li>
      <strong>${name}</strong>
      ${bestFor ? `<span style="font-size:0.8rem;color:var(--text-soft);"> — ${bestFor}</span>` : ""}
      ${tip ? `<div style="font-size:0.85rem;color:var(--text-soft);margin-top:2px;">${tip}</div>` : ""}
    </li>`;
  }).join("") || "<li style='color:var(--text-soft);'>No bait data available</li>";

  // Hot spots
  const hotSpots = (r.hot_spots || []).map(h => {
    if (typeof h === "string") return `<div style="padding:10px 12px;background:var(--cream-dk);border-radius:var(--radius-sm);margin-bottom:8px;font-size:0.9rem;color:var(--text-soft);">📍 ${h}</div>`;
    const area = _val(h.area_type) || _val(h.area) || _val(h.location) || "Suggested area";
    const why = _val(h.why) || _val(h.reason) || "";
    const tip = _val(h.tip) || "";
    return `<div style="padding:10px 12px;background:var(--cream-dk);border-radius:var(--radius-sm);margin-bottom:8px;">
      <div style="font-weight:600;color:var(--text);margin-bottom:4px;">📍 ${area}</div>
      <div style="font-size:0.9rem;color:var(--text-soft);line-height:1.5;">${why}${tip ? " " + tip : ""}</div>
    </div>`;
  }).join("");

  const card = document.getElementById("fishing-result");
  card.innerHTML = `
    <!-- Outlook Banner -->
    <div style="text-align:center;padding:16px;background:${outlookColor}12;border:1px solid ${outlookColor}30;border-radius:var(--radius);margin-bottom:16px;">
      <div style="font-size:1.8rem;font-weight:700;color:${outlookColor};font-family:var(--font-display);letter-spacing:0.04em;">${outlook.toUpperCase()}</div>
      <div style="font-size:0.9rem;color:var(--text-soft);margin-top:4px;">${r.outlook_reason || "Today's outlook"}</div>
    </div>

    <div class="result-name">🎣 Today's Fishing Report</div>

    <div class="result-section-label">Conditions</div>
    <p class="result-body">${r.conditions || ""}</p>

    ${times ? `
    <div class="result-section-label">⏰ Best Times</div>
    <div style="margin-bottom:12px;">${times}</div>
    ` : ""}

    <div class="result-section-label">🐟 Fish Activity</div>
    <ul class="result-list">${species}</ul>

    <div class="result-section-label">🪱 Bait &amp; Lure Ideas</div>
    <ul class="result-list">${baits}</ul>

    ${r.tides_and_current ? `
    <div class="result-section-label">🌊 Tides &amp; Current</div>
    <p class="result-body">${r.tides_and_current}</p>
    ` : ""}

    <div class="result-section-label">🌤 Water &amp; Weather</div>
    <p class="result-body">${r.water_and_weather || r.weather_note || ""}</p>

    ${hotSpots ? `
    <div class="result-section-label">📍 Where I'd Start</div>
    ${hotSpots}
    ` : ""}

    <div class="result-section-label">💡 Next Step</div>
    <p class="result-body">${r.technique_tip || ""}</p>

    ${r.encouragement ? `
    <div style="margin-top:16px;padding:14px;background:var(--cream-dk);border-radius:var(--radius-sm);border-left:4px solid var(--gold);">
      <p class="result-body" style="font-style:italic;color:var(--brown);">${r.encouragement}</p>
    </div>` : ""}
  `;
  card.classList.add("visible");

  if (verse) {
    const v = document.getElementById("fishing-verse");
    v.innerHTML = `
      <div class="verse-banner-text">"${verse.verse}"</div>
      <div class="verse-banner-ref">— ${verse.ref}</div>
    `;
    v.classList.add("visible");
  }

  document.getElementById("fishing-get-btn").style.display = "flex";
  document.getElementById("fishing-result").scrollIntoView({ behavior: "smooth", block: "start" });
}

// ── WHAT DID I CATCH? (ID + Recipe) ──────────────────────────────

let _catchIdFile = null;

function showCatchIdForm() {
  document.getElementById("catch-id-area").style.display = "block";
  document.getElementById("catch-id-area").scrollIntoView({ behavior: "smooth" });
  document.getElementById("catch-id-result").style.display = "none";
  document.getElementById("catch-id-photo-area").style.display = "flex";
  document.getElementById("catch-id-preview").style.display = "none";
  _catchIdFile = null;
}

function handleCatchIdPhoto(input) {
  const file = input.files[0];
  if (!file) return;
  _catchIdFile = file;
  const reader = new FileReader();
  reader.onload = e => {
    document.getElementById("catch-id-preview").src = e.target.result;
    document.getElementById("catch-id-preview").style.display = "block";
    document.getElementById("catch-id-photo-area").style.display = "none";
    // Also set as catch photo data for auto-filling the catch post
    _catchPhotoData = e.target.result;
  };
  reader.readAsDataURL(file);
}

async function identifyCatch() {
  if (!_catchIdFile) { toast("Take a photo of your catch first!", "error"); return; }

  const btn = document.getElementById("catch-id-btn");
  btn.disabled = true;
  btn.textContent = "Identifying… 🐟";

  const formData = new FormData();
  formData.append("image", _catchIdFile);

  try {
    const data = await apiPost("/features/fishing/catch-recipe", formData, true);
    console.log("[Catch ID] Raw result:", JSON.stringify(data.result, null, 2));
    renderCatchIdResult(data.result, data.verse);

    // Auto-fill the catch post form
    if (data.result.fish_name) {
      document.getElementById("catch-fish").value = data.result.fish_name;
    }
    // Set the catch photo preview too
    document.getElementById("catch-preview").src = document.getElementById("catch-id-preview").src;
    document.getElementById("catch-preview").style.display = "block";
    document.getElementById("catch-photo-area").style.display = "none";

  } catch (err) {
    if (err.message !== "LIMIT_REACHED") toast(err.message, "error");
  }
  btn.disabled = false;
  btn.textContent = "What Did I Catch? 🐟";
}

function renderCatchIdResult(r, verse) {
  const ingredients = (r.ingredients || []).map(i => {
    if (typeof i === "string") return `<li>${i}</li>`;
    return `<li><strong>${i.amount || ""}</strong> ${i.item || ""}</li>`;
  }).join("");

  const steps = (r.instructions || []).map(s =>
    `<li style="margin-bottom:8px;">${s}</li>`
  ).join("");

  const tips = (r.cooking_tips || []).map(t => `<li>${t}</li>`).join("");

  const el = document.getElementById("catch-id-result");
  el.innerHTML = `
    <div style="text-align:center;margin-bottom:16px;">
      <div style="font-size:1.4rem;font-weight:700;color:var(--text);font-family:var(--font-display);">🐟 ${r.fish_name || "Your Catch"}</div>
      <div style="font-size:0.9rem;color:var(--text-soft);margin-top:4px;">${r.size_estimate || ""}</div>
    </div>

    <p class="result-body">${r.fish_details || ""}</p>

    <div style="padding:12px;background:var(--cream-dk);border-radius:var(--radius-sm);margin:12px 0;">
      <div style="font-weight:600;color:var(--text);margin-bottom:4px;">Keep or Release?</div>
      <div style="font-size:0.9rem;color:var(--text-soft);">${r.keep_or_release || "Check local regulations."}</div>
    </div>

    <div style="padding:12px;background:var(--cream-dk);border-radius:var(--radius-sm);margin-bottom:16px;">
      <div style="font-weight:600;color:var(--text);margin-bottom:4px;">Taste</div>
      <div style="font-size:0.9rem;color:var(--text-soft);">${r.taste_profile || ""}</div>
    </div>

    <div class="result-section-label">🍽️ ${r.recipe_name || "Recipe"}</div>
    <p class="result-body">${r.recipe_description || ""}</p>

    <div style="display:flex;gap:16px;margin:10px 0 14px;font-size:0.85rem;color:var(--text-soft);">
      ${r.prep_time ? `<span>Prep: ${r.prep_time}</span>` : ""}
      ${r.cook_time ? `<span>Cook: ${r.cook_time}</span>` : ""}
      ${r.serves ? `<span>Serves: ${r.serves}</span>` : ""}
    </div>

    ${ingredients ? `
    <div class="result-section-label">Ingredients</div>
    <ul class="result-list">${ingredients}</ul>
    ` : ""}

    ${steps ? `
    <div class="result-section-label">Instructions</div>
    <ol style="padding-left:20px;margin-bottom:14px;color:var(--text);line-height:1.7;font-size:0.95rem;">${steps}</ol>
    ` : ""}

    ${tips ? `
    <div class="result-section-label">Tips</div>
    <ul class="result-list">${tips}</ul>
    ` : ""}

    ${r.side_suggestions ? `
    <div style="padding:12px;background:var(--cream-dk);border-radius:var(--radius-sm);margin-top:12px;">
      <div style="font-weight:600;color:var(--text);margin-bottom:4px;">Goes great with</div>
      <div style="font-size:0.9rem;color:var(--text-soft);">${r.side_suggestions}</div>
    </div>
    ` : ""}

    <div style="text-align:center;margin-top:16px;">
      <button class="btn-primary" onclick="showCatchForm();document.getElementById('catch-id-area').style.display='none';" style="font-size:0.9rem;padding:10px 20px;">
        📸 Post This Catch
      </button>
    </div>
  `;
  el.style.display = "block";

  if (verse) {
    const v = document.getElementById("fishing-verse");
    v.innerHTML = `
      <div class="verse-banner-text">"${verse.verse}"</div>
      <div class="verse-banner-ref">— ${verse.ref}</div>
    `;
    v.classList.add("visible");
  }

  el.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ── POST A CATCH ─────────────────────────────────────────────────

function showCatchForm() {
  document.getElementById("catch-form-area").style.display = "block";
  document.getElementById("catch-form-area").scrollIntoView({ behavior: "smooth" });
}

function hideCatchForm() {
  document.getElementById("catch-form-area").style.display = "none";
  document.getElementById("catch-fish").value = "";
  document.getElementById("catch-location").value = "";
  document.getElementById("catch-note").value = "";
  document.getElementById("catch-preview").style.display = "none";
  document.getElementById("catch-photo-area").style.display = "flex";
  _catchPhotoData = "";
}

function handleCatchPhoto(input) {
  const file = input.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = e => {
    _catchPhotoData = e.target.result;
    document.getElementById("catch-preview").src = _catchPhotoData;
    document.getElementById("catch-preview").style.display = "block";
    document.getElementById("catch-photo-area").style.display = "none";
  };
  reader.readAsDataURL(file);
}

async function submitCatch() {
  const fish = document.getElementById("catch-fish").value.trim();
  const location = document.getElementById("catch-location").value.trim();
  const note = document.getElementById("catch-note").value.trim();
  const name = state.user?.name || "Anonymous";

  if (!fish) { toast("Please enter the fish type.", "error"); return; }
  if (!location) { toast("Please enter a location.", "error"); return; }

  const btn = document.getElementById("catch-submit-btn");
  btn.disabled = true;
  btn.textContent = "Posting…";

  try {
    await apiPost("/features/catches", {
      fish_type: fish,
      location: location,
      note: note,
      image_data: _catchPhotoData,
      posted_by: name,
    });
    toast("Catch posted! 🎣");
    hideCatchForm();
    loadCatches();
  } catch (err) {
    if (err.message !== "LIMIT_REACHED") toast(err.message, "error");
  }
  btn.disabled = false;
  btn.textContent = "Post Catch 🎣";
}

// ── COMMUNITY CATCHES ────────────────────────────────────────────

async function loadCatches() {
  const container = document.getElementById("catches-list");
  if (!container) return;

  try {
    const data = await apiGet("/features/catches?limit=15");
    const catches = data.catches || [];

    if (catches.length === 0) {
      container.innerHTML = `
        <div style="text-align:center;padding:24px;color:var(--text-soft);font-style:italic;">
          No catches posted yet. Be the first to share one. 🎣
        </div>`;
      return;
    }

    container.innerHTML = catches.map(c => {
      const timeAgo = _timeAgo(c.created_at);
      return `
        <div style="background:var(--white);border-radius:var(--radius-sm);padding:14px;margin-bottom:10px;box-shadow:var(--shadow);">
          ${c.image_data ? `<img src="${c.image_data}" style="width:100%;border-radius:var(--radius-sm);margin-bottom:10px;max-height:200px;object-fit:cover;" alt="Catch photo"/>` : ""}
          <div style="display:flex;justify-content:space-between;align-items:baseline;">
            <div style="font-weight:600;color:var(--text);font-size:1.05rem;">🐟 ${_esc(c.fish_type)}</div>
            <div style="font-size:0.8rem;color:var(--text-soft);">${timeAgo}</div>
          </div>
          <div style="font-size:0.9rem;color:var(--text-soft);margin-top:4px;">📍 ${_esc(c.location)}</div>
          ${c.note ? `<div style="font-size:0.9rem;color:var(--text);margin-top:6px;font-style:italic;">${_esc(c.note)}</div>` : ""}
          <div style="font-size:0.8rem;color:var(--brown-lt);margin-top:6px;">— ${_esc(c.posted_by || "Anonymous")}</div>
        </div>`;
    }).join("");
  } catch {
    container.innerHTML = "";
  }
}

function _timeAgo(dateStr) {
  if (!dateStr) return "";
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return mins + "m ago";
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return hrs + "h ago";
  const days = Math.floor(hrs / 24);
  return days + "d ago";
}

function _esc(str) {
  const d = document.createElement("div");
  d.textContent = str || "";
  return d.innerHTML;
}
