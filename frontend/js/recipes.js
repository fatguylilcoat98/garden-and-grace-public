/*
  Garden & Grace — Recipe Builder: photo → full recipe + shopping list.
*/

let recipeFile = null;

function initRecipe() {
  showScreen("screen-recipe");
  resetRecipe();
  setupPhotoUpload("recipe-upload-area", "recipe-input", "recipe-preview", (file) => {
    recipeFile = file;
    document.getElementById("recipe-analyze-btn").style.display = "flex";
    document.getElementById("recipe-result").classList.remove("visible");
    document.getElementById("recipe-verse").classList.remove("visible");
  });
}

function resetRecipe() {
  recipeFile = null;
  document.getElementById("recipe-upload-area").style.display = "block";
  document.getElementById("recipe-preview").style.display = "none";
  document.getElementById("recipe-analyze-btn").style.display = "none";
  document.getElementById("recipe-result").classList.remove("visible");
  document.getElementById("recipe-verse").classList.remove("visible");
  document.getElementById("recipe-input").value = "";
  hideLoading("recipe");
}

async function analyzeRecipe() {
  if (!recipeFile) return;
  showLoading("recipe", "Building your recipe… 🍽️");

  try {
    const form = new FormData();
    form.append("image", recipeFile);
    const data = await apiPost("/features/recipe", form, true);
    hideLoading("recipe");
    renderRecipeResult(data.result, data.verse);
  } catch (err) {
    hideLoading("recipe");
    if (err.message !== "LIMIT_REACHED") toast(err.message, "error");
  }
}

function renderRecipeResult(r, verse) {
  const ingredients = (r.ingredients || []).map(i =>
    `<li><strong>${i.amount}</strong> — ${i.item}</li>`
  ).join("");

  const steps = (r.instructions || []).map((s, idx) => {
    const clean = s.replace(/^(step\s*\d+[:.]\s*)/i, "").trim();
    return `<li>${clean}</li>`;
  }).join("");

  const shopping = (r.shopping_list || []).map(s => `<li>${s}</li>`).join("");

  const card = document.getElementById("recipe-result");
  card.innerHTML = `
    <div class="result-name">🍽️ ${r.dish_name || "Your Recipe"}</div>
    <p class="result-body" style="color:var(--brown); font-size:0.9rem;">
      Serves ${r.serves || "—"}  ·  Prep: ${r.prep_time || "—"}  ·  Cook: ${r.cook_time || "—"}
    </p>
    <p class="result-body" style="margin-top:8px;">${r.description || ""}</p>

    ${r.health_note ? `<div style="margin:12px 0; padding:12px 14px; background:#e8f5e8; border-radius:var(--radius-sm); border-left:4px solid var(--forest);">
      <p class="result-body" style="color:var(--forest-dk);">💚 ${r.health_note}</p>
    </div>` : ""}

    <div class="result-section-label">Ingredients</div>
    <ul class="result-list">${ingredients}</ul>

    <div class="result-section-label">Instructions</div>
    <ol class="step-list">${steps}</ol>

    ${r.tips ? `<div style="margin-top:14px; padding:12px 14px; background:var(--cream-dk); border-radius:var(--radius-sm);">
      <p class="result-body">✨ <em>${r.tips}</em></p>
    </div>` : ""}

    <div class="result-section-label">🛒 Shopping List</div>
    <ul class="checklist">${shopping}</ul>
  `;
  card.classList.add("visible");

  if (verse) {
    const v = document.getElementById("recipe-verse");
    v.innerHTML = `
      <div class="verse-banner-text">"${verse.verse}"</div>
      <div class="verse-banner-ref">— ${verse.ref}</div>
    `;
    v.classList.add("visible");
  }

  document.getElementById("recipe-result").scrollIntoView({ behavior: "smooth", block: "start" });
}
