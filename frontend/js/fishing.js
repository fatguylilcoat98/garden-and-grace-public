/*
  Garden & Grace — The Good Neighbor Guard
  Fishing Feature: Location-aware conditions report
*/

function initFishing() {
  showScreen("screen-fishing");
  resetFishing();
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

  // Try geolocation
  try {
    const pos = await new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 8000 });
    });
    lat = pos.coords.latitude;
    lon = pos.coords.longitude;
  } catch {
    // Fall back to default (Sacramento area)
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
    toast(err.message, "error");
  }
}

function renderFishingResult(r, verse) {
  const species = (r.active_species || []).map(s =>
    `<li>${s}</li>`
  ).join("");

  const baits = (r.recommended_bait || []).map(b =>
    `<li>${b}</li>`
  ).join("");

  const card = document.getElementById("fishing-result");
  card.innerHTML = `
    <div class="result-name">🎣 Today's Fishing Report</div>

    <div class="result-section-label">Conditions</div>
    <p class="result-body">${r.conditions || ""}</p>

    <div class="result-section-label">⏰ Best Time Today</div>
    <p class="result-body">${r.best_time_today || ""}</p>

    <div class="result-section-label">🐟 Active Fish</div>
    <ul class="result-list">${species}</ul>

    <div class="result-section-label">🪱 Recommended Bait</div>
    <ul class="result-list">${baits}</ul>

    <div class="result-section-label">💡 Technique Tip</div>
    <p class="result-body">${r.technique_tip || ""}</p>

    <div class="result-section-label">🌤 Weather Note</div>
    <p class="result-body">${r.weather_note || ""}</p>

    ${r.encouragement ? `
    <div style="margin-top:16px; padding:14px; background:var(--cream-dk); border-radius:var(--radius-sm); border-left:4px solid var(--gold);">
      <p class="result-body" style="font-style:italic; color:var(--brown);">${r.encouragement}</p>
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

  // Show the "Get New Report" button again
  document.getElementById("fishing-get-btn").style.display = "flex";
  document.getElementById("fishing-result").scrollIntoView({ behavior: "smooth", block: "start" });
}
