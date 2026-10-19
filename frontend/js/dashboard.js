// dashboard.html — subject cards (click to edit baseline) + safe-days-off list.

function clearZeroOnFocus(input) {
  input.addEventListener("focus", () => {
    if (input.value === "0") input.value = "";
  });
  input.addEventListener("blur", () => {
    if (input.value.trim() === "") input.value = "0";
  });
}

async function loadDashboard() {
  const grid = document.getElementById("subject-grid");
  grid.innerHTML = "<p>Loading...</p>";

  try {
    const subjects = await getSubjects();
    if (subjects.length === 0) {
      grid.innerHTML = "<p>No subjects yet. <a href='setup.html'>Add some.</a></p>";
      return;
    }

    grid.innerHTML = "";
    for (const subject of subjects) {
      let prediction;
      try {
        prediction = await getSubjectPrediction(subject.id);
      } catch (_) {
        prediction = {
          conducted: subject.baseline_conducted,
          attended: subject.baseline_attended,
          remaining: 0,
          current_percent: calculatePercentage(subject.baseline_attended, subject.baseline_conducted),
          safe_skips: calculateSafeSkipsSemester(
            subject.baseline_attended,
            subject.baseline_conducted,
            0,
            subject.required_percent
          ),
        };
      }

      const status = getAttendanceStatus(prediction.current_percent, subject.required_percent);

      const card = document.createElement("div");
      card.className = `subject-card ${status}`;
      card.dataset.subjectId = subject.id;
      card.style.cursor = "pointer";
      card.innerHTML = renderViewMode(subject, prediction);

      card.addEventListener("click", (e) => {
        if (card.dataset.editing === "true") return; // ignore clicks while already editing
        enterEditMode(card, subject);
      });

      grid.appendChild(card);
    }
  } catch (err) {
    grid.innerHTML = `<p class="error-text">${err.message || "Failed to load subjects"}</p>`;
  }
}

function renderViewMode(subject, prediction) {
  return `
    <h3>${subject.name}</h3>
    <div class="percent">${prediction.current_percent}%</div>
    <div class="meta">Required: ${subject.required_percent}%</div>
    <div class="meta">${prediction.attended} / ${prediction.conducted} classes attended</div>
    <div class="meta">Safe skips remaining: <strong>${prediction.safe_skips}</strong></div>
    <div class="meta">Classes left this semester: ${prediction.remaining}</div>
    <div class="meta" style="margin-top: 8px; opacity: 0.6;">Click to edit baseline</div>
  `;
}

function enterEditMode(card, subject) {
  card.dataset.editing = "true";
  card.style.cursor = "default";

  card.innerHTML = `
    <h3>${subject.name}</h3>

    <label style="font-size: 12px;">Required attendance %</label>
    <input type="number" class="edit-required" value="${subject.required_percent}" min="1" max="100" />

    <label style="font-size: 12px;">Baseline conducted</label>
    <input type="number" class="edit-conducted" value="${subject.baseline_conducted}" min="0" />

    <label style="font-size: 12px;">Baseline attended</label>
    <input type="number" class="edit-attended" value="${subject.baseline_attended}" min="0" />

    <div style="display: flex; gap: 8px; margin-top: 12px;">
      <button type="button" class="btn-primary save-btn" style="flex: 1;">Save</button>
      <button type="button" class="btn-secondary cancel-btn" style="flex: 1;">Cancel</button>
    </div>
    <div class="error-text edit-error"></div>
  `;

  card.querySelectorAll(".edit-conducted, .edit-attended").forEach(clearZeroOnFocus);

  card.querySelector(".save-btn").addEventListener("click", async (e) => {
    e.stopPropagation();
    const errorEl = card.querySelector(".edit-error");
    const requiredPercent = parseFloat(card.querySelector(".edit-required").value);
    const baselineConducted = parseInt(card.querySelector(".edit-conducted").value, 10);
    const baselineAttended = parseInt(card.querySelector(".edit-attended").value, 10);

    if (baselineAttended > baselineConducted) {
      errorEl.textContent = "Attended can't exceed conducted.";
      return;
    }

    try {
      await updateSubject(subject.id, {
        required_percent: requiredPercent,
        baseline_conducted: baselineConducted,
        baseline_attended: baselineAttended,
      });
      card.dataset.editing = "false";
      loadDashboard(); // reload everyone so predictions stay in sync
    } catch (err) {
      errorEl.textContent = err.message || "Failed to save";
    }
  });

  card.querySelector(".cancel-btn").addEventListener("click", (e) => {
    e.stopPropagation();
    card.dataset.editing = "false";
    card.style.cursor = "pointer";
    loadDashboard();
  });
}

async function loadSafeDaysOff() {
  const list = document.getElementById("safe-days-list");
  list.innerHTML = "<p>Loading...</p>";

  try {
    const data = await getSafeDaysOff();
    const safeDays = data.days.filter((d) => d.safe_to_skip_entirely);

    if (safeDays.length === 0) {
      list.innerHTML = "<p>No fully safe days off found for the rest of the semester.</p>";
      return;
    }

    list.innerHTML = "";
    safeDays.slice(0, 20).forEach((day) => {
      const card = document.createElement("div");
      card.className = "subject-card safe";
      card.innerHTML = `
        <h3>${day.date}</h3>
        <div class="meta">${day.subject_count} class${day.subject_count === 1 ? "" : "es"} scheduled — all safe to skip</div>
      `;
      list.appendChild(card);
    });
  } catch (err) {
    list.innerHTML = `<p class="error-text">${err.message || "Failed to load safe days off"}</p>`;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadDashboard();
  loadSafeDaysOff();
});