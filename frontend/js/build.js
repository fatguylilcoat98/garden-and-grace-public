/*
  Garden & Grace — The Good Neighbor Guard
  Build It: Photo → materials list + step-by-step build plan + PDF email
*/

let buildFile = null;

function initBuild() {
  showScreen("screen-build");
  resetBuild();
  setupPhotoUpload("build-upload-area", "build-input", "build-preview", (file) => {
    buildFile = file;
    document.getElementById("build-analyze-btn").style.display = "flex";
    document.getElementById("build-email-btn").style.display = "none";
    document.getElementById("build-result").classList.remove("visible");
    document.getElementById("build-verse").classList.remove("visible");
  });
}

function resetBuild() {
  buildFile = null;
  document.getElementById("build-upload-area").style.display = "block";
  document.getElementById("build-preview").style.display = "none";
  document.getElementById("build-analyze-btn").style.display = "none";
  document.getElementById("build-email-btn").style.display = "none";
  document.getElementById("build-result").classList.remove("visible");
  document.getElementById("build-verse").classList.remove("visible");
  hideLoading("build");
}

async function analyzeBuild() {
  if (!buildFile) return;
  showLoading("build", "Building your plan… 🔨");

  try {
    const form = new FormData();
    form.append("image", buildFile);
    const data = await apiPost("/features/build", form, true);
    hideLoading("build");
    renderBuildResult(data.result, data.verse);
    document.getElementById("build-email-btn").style.display = "flex";
  } catch (err) {
    hideLoading("build");
    toast(err.message, "error");
  }
}

async function emailBuildPdf() {
  if (!buildFile) return;
  const btn = document.getElementById("build-email-btn");
  btn.disabled = true;
  btn.textContent = "Sending… 📨";

  try {
    const form = new FormData();
    form.append("image", buildFile);
    const data = await apiPost("/features/build/email", form, true);
    toast(`✅ ${data.message}`, "success");
  } catch (err) {
    toast(err.message, "error");
  } finally {
    btn.disabled = false;
    btn.innerHTML = "📧 Send Build Plan to My Email";
  }
}

function renderBuildResult(r, verse) {
  const tools = (r.tools_needed || []).join("  ·  ");

  const materials = (r.materials || []).map(m =>
    `<li><strong>${m.quantity}</strong> — ${m.item}</li>`
  ).join("");

  const steps = (r.instructions || []).map((s) => {
    const clean = s.replace(/^(step\s*\d+[:.]\s*)/i, "").trim();
    return `<li>${clean}</li>`;
  }).join("");

  const tips = (r.tips || []).map(t => `<li>${t}</li>`).join("");
  const shopping = (r.shopping_list || []).map(s => `<li>${s}</li>`).join("");

  const card = document.getElementById("build-result");
  card.innerHTML = `
    <div class="result-name">🔨 ${r.project_name || "Your Build Plan"}</div>
    <p class="result-body" style="color:var(--brown); font-size:0.9rem; margin-bottom:8px;">
      ${r.skill_level || ""}  ·  ${r.estimated_time || ""}  ·  Est. cost: ${r.estimated_cost || ""}
    </p>
    <p class="result-body">${r.description || ""}</p>

    ${r.dimensions ? `<div style="margin:12px 0; padding:12px 14px; background:#e8f5e8; border-radius:var(--radius-sm); border-left:4px solid var(--forest);">
      <p class="result-body">📐 <strong>Dimensions:</strong> ${r.dimensions}</p>
    </div>` : ""}

    ${tools ? `<div class="result-section-label">🔧 Tools Needed</div>
    <p class="result-body">${tools}</p>` : ""}

    <div class="result-section-label">Materials List</div>
    <ul class="result-list">${materials}</ul>

    <div class="result-section-label">Build Instructions</div>
    <ol class="step-list">${steps}</ol>

    ${tips ? `<div class="result-section-label">✨ Tips</div>
    <ul class="result-list">${tips}</ul>` : ""}

    <div class="result-section-label">🛒 Shopping List</div>
    <ul class="checklist">${shopping}</ul>
  `;
  card.classList.add("visible");

  if (verse) {
    const v = document.getElementById("build-verse");
    v.innerHTML = `
      <div class="verse-banner-text">"${verse.verse}"</div>
      <div class="verse-banner-ref">— ${verse.ref}</div>
    `;
    v.classList.add("visible");
  }

  document.getElementById("build-result").scrollIntoView({ behavior: "smooth", block: "start" });
}
