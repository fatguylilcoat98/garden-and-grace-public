/*
  Garden & Grace — The Good Neighbor Guard
  Garden Feature: Plant identification via Claude Vision
*/

let gardenFile = null;

function initGarden() {
  showScreen("screen-garden");
  resetGarden();
  setupPhotoUpload("garden-upload-area", "garden-input", "garden-preview", (file) => {
    gardenFile = file;
    document.getElementById("garden-analyze-btn").style.display = "flex";
  });
}

function resetGarden() {
  gardenFile = null;
  document.getElementById("garden-upload-area").style.display = "block";
  document.getElementById("garden-preview").style.display = "none";
  document.getElementById("garden-analyze-btn").style.display = "none";
  document.getElementById("garden-reset-btn").style.display = "none";
  document.getElementById("garden-result").classList.remove("visible");
  document.getElementById("garden-verse").classList.remove("visible");
  document.getElementById("garden-input").value = "";
  hideLoading("garden");
}

async function analyzeGarden() {
  if (!gardenFile) return;
  showLoading("garden", "Identifying your plant… 🌿");

  try {
    const form = new FormData();
    form.append("image", gardenFile);
    const data = await apiPost("/features/garden", form, true);
    hideLoading("garden");
    renderGardenResult(data.result, data.verse);
  } catch (err) {
    hideLoading("garden");
    toast(err.message, "error");
  }
}

function renderGardenResult(r, verse) {
  document.getElementById("garden-reset-btn").style.display = "flex";
  const card = document.getElementById("garden-result");
  card.innerHTML = `
    <div class="result-name">🌿 ${r.name || "Unknown Plant"}</div>
    <p class="result-body">${r.what_it_is || ""}</p>

    <div class="result-section-label">How to Care For It</div>
    <p class="result-body">${r.care || ""}</p>

    <div class="result-section-label">💧 Watering</div>
    <p class="result-body">${r.watering || ""}</p>

    <div class="result-section-label">🌱 Planting Tips</div>
    <p class="result-body">${r.planting_tips || ""}</p>

    <div class="result-section-label">🍂 This Season</div>
    <p class="result-body">${r.seasonal_advice || ""}</p>

    ${r.fun_fact ? `<div class="result-section-label">✨ Did You Know?</div>
    <p class="result-body">${r.fun_fact}</p>` : ""}
  `;
  card.classList.add("visible");

  if (verse) {
    const v = document.getElementById("garden-verse");
    v.innerHTML = `
      <div class="verse-banner-text">"${verse.verse}"</div>
      <div class="verse-banner-ref">— ${verse.ref}</div>
    `;
    v.classList.add("visible");
  }

  document.getElementById("garden-result").scrollIntoView({ behavior: "smooth", block: "start" });
}
