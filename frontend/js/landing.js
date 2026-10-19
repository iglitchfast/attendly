// landing.html — semester selection. First screen after login.

async function loadSemesters() {
  const container = document.getElementById("semester-options");
  const errorEl = document.getElementById("error-msg");
  container.innerHTML = "<p>Loading...</p>";

  try {
    const semesters = await getSemesters();
    container.innerHTML = "";

    semesters.forEach((sem) => {
      const configured = sem.start && sem.end;

      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "btn-primary";
      btn.style.marginTop = "12px";
      btn.disabled = !configured;
      btn.textContent = configured
        ? `${sem.label} (${sem.start} – ${sem.end})`
        : `${sem.label} — not yet available`;

      btn.addEventListener("click", () => handleSelect(sem.key));
      container.appendChild(btn);
    });
  } catch (err) {
    errorEl.textContent = err.message || "Failed to load semesters";
  }
}

async function handleSelect(semesterKey) {
  const errorEl = document.getElementById("error-msg");
  errorEl.textContent = "";

  try {
    await selectSemester(semesterKey);
    window.location.href = "preset-choice.html";
  } catch (err) {
    errorEl.textContent = err.message || "Failed to select semester";
  }
}

document.addEventListener("DOMContentLoaded", loadSemesters);