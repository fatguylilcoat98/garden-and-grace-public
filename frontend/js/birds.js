/*
  Garden & Grace — The Good Neighbor Guard
  Birds & Wildlife Feature: Species identification via Claude Vision
*/

let birdsFile = null;

function initBirds() {
  showScreen("screen-birds");
  resetBirds();
  setupPhotoUpload("birds-upload-area", "birds-input", "birds-preview", (file) => {
    birdsFile = file;
    document.getElementById("birds-analyze-btn").style.display = "flex";
  });
}

function resetBirds() {
  birdsFile = null;
  document.getElementById("birds-upload-area").style.display = "block";
  document.getElementById("birds-preview").style.display = "none";
  document.getElementById("birds-analyze-btn").style.display = "none";
  document.getElementById("birds-reset-btn").style.display = "none";
  document.getElementById("birds-result").classList.remove("visible");
  document.getElementById("birds-verse").classList.remove("visible");
  document.getElementById("birds-input").value = "";
  hideLoading("birds");
}

async function analyzeBirds() {
  if (!birdsFile) return;
  showLoading("birds", "Identifying this creature… 🦅");

  try {
    const form = new FormData();
    form.append("image", birdsFile);
    const data = await apiPost("/features/birds", form, true);
    hideLoading("birds");
    renderBirdsResult(data.result, data.verse);
  } catch (err) {
    hideLoading("birds");
    toast(err.message, "error");
  }
}

function renderBirdsResult(r, verse) {
  document.getElementById("birds-reset-btn").style.display = "flex";
  const eagleSection = r.eagle_connection ? `
    <div class="eagle-highlight">
      <div class="eagle-highlight-label">🦅 Eagle Connection</div>
      <div class="eagle-highlight-text">${r.eagle_connection}</div>
    </div>
  ` : "";

  const funFacts = (r.fun_facts || []).map(f =>
    `<span class="fact-tag">${f}</span>`
  ).join("");

  const card = document.getElementById("birds-result");
  card.innerHTML = `
    <div class="result-name">${r.name || "Unknown Creature"}</div>
    <p class="result-body" style="color:var(--brown); font-size:0.9rem; margin-bottom:10px;">${r.type || ""}</p>
    <p class="result-body">${r.what_it_is || ""}</p>

    ${eagleSection}

    <div class="result-section-label">📍 Where It Lives</div>
    <p class="result-body">${r.where_found || ""}</p>

    <div class="result-section-label">🏡 Home & Nesting</div>
    <p class="result-body">${r.nesting_or_habitat || ""}</p>

    <div class="result-section-label">⏰ Best Time to Spot</div>
    <p class="result-body">${r.best_time_to_spot || ""}</p>

    ${funFacts ? `<div class="result-section-label">✨ Fun Facts</div>
    <div class="fact-tags">${funFacts}</div>` : ""}
  `;
  card.classList.add("visible");

  if (verse) {
    const v = document.getElementById("birds-verse");
    v.innerHTML = `
      <div class="verse-banner-text">"${verse.verse}"</div>
      <div class="verse-banner-ref">— ${verse.ref}</div>
    `;
    v.classList.add("visible");
  }

  document.getElementById("birds-result").scrollIntoView({ behavior: "smooth", block: "start" });
}
