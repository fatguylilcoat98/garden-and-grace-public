/*
  Garden & Grace — Public Edition
  The Good Neighbor Guard
  Built by Christopher Hughes · Sacramento, CA
  Created with the help of AI collaborators (Claude · GPT · Gemini · Groq)
  Truth · Safety · We Got Your Back
  Auth: Name-only welcome — no password for public version
*/

async function handleAuthSubmit(e) {
  e.preventDefault();
  const name = document.getElementById("auth-name").value.trim();
  const btn  = document.getElementById("auth-submit-btn");

  if (!name) { toast("Please enter your name.", "error"); return; }

  const user = { name: name };
  saveSession("local-auth", user);
  btn.disabled = true;
  initHome();
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("auth-form");
  if (form) form.addEventListener("submit", handleAuthSubmit);
});
