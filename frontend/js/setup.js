// setup.html — shows existing subjects (e.g. from an applied preset) as
// editable baseline rows, plus lets you add more manually either way.

let existingSubjects = [];

function clearZeroOnFocus(input) {
  input.addEventListener("focus", () => {
    if (input.value === "0") input.value = "";
  });
  input.addEventListener("blur", () => {
    if (input.value.trim() === "") input.value = "0";
  });
}

async function loadExistingSubjects() {
  try {
    existingSubjects = await getSubjects();
  } catch (_) {
    existingSubjects = [];
  }
  renderExistingSubjects();
}

function renderExistingSubjects() {
  const container = document.getElementById("existing-subjects");

  if (existingSubjects.length === 0) {
    container.innerHTML = "";
    return;
  }

  container.innerHTML = `<h3>Your Subjects</h3><p>Fill in your current attendance for each — these came from your timetable setup.</p>`;

  existingSubjects.forEach((subject) => {
    const row = document.createElement("div");
    row.className = "subject-row existing-subject-row";
    row.innerHTML = `
      <label>${subject.name}</label>

      <div style="display: flex; gap: 12px;">
        <div style="flex: 1;">
          <label style="font-size: 12px;">Conducted so far</label>
          <input type="number" class="existing-conducted" value="${subject.baseline_conducted}" min="0" />
        </div>
        <div style="flex: 1;">
          <label style="font-size: 12px;">Attended so far</label>
          <input type="number" class="existing-attended" value="${subject.baseline_attended}" min="0" />
        </div>
        <div style="flex: 1;">
          <label style="font-size: 12px;">Required %</label>
          <input type="number" class="existing-required" value="${subject.required_percent}" min="1" max="100" />
        </div>
      </div>
      <hr />
    `;
    row.dataset.subjectId = subject.id;
    container.appendChild(row);
    row.querySelectorAll(".existing-conducted, .existing-attended").forEach(clearZeroOnFocus);
  });

  const saveBtn = document.createElement("button");
  saveBtn.type = "button";
  saveBtn.className = "btn-primary";
  saveBtn.textContent = "Save Attendance & Continue to Timetable";
  saveBtn.style.marginTop = "16px";
  saveBtn.addEventListener("click", handleSaveExisting);
  container.appendChild(saveBtn);

  const errorDiv = document.createElement("div");
  errorDiv.className = "error-text";
  errorDiv.id = "existing-error-msg";
  container.appendChild(errorDiv);
}

async function handleSaveExisting() {
  const errorEl = document.getElementById("existing-error-msg");
  errorEl.textContent = "";
  const baselineDate = document.getElementById("baseline-date").value;

  if (!baselineDate) {
    errorEl.textContent = "Set a baseline date above first.";
    return;
  }

  const rows = document.querySelectorAll(".existing-subject-row");
  try {
    for (const row of rows) {
      const subjectId = parseInt(row.dataset.subjectId, 10);
      const conducted = parseInt(row.querySelector(".existing-conducted").value, 10);
      const attended = parseInt(row.querySelector(".existing-attended").value, 10);
      const required = parseFloat(row.querySelector(".existing-required").value);

      if (attended > conducted) {
        errorEl.textContent = `Attended can't exceed conducted for one of your subjects.`;
        return;
      }

      await updateSubject(subjectId, {
        baseline_conducted: conducted,
        baseline_attended: attended,
        required_percent: required,
        baseline_date: baselineDate,
      });
    }
    window.location.href = "timetable.html";
  } catch (err) {
    errorEl.textContent = err.message || "Something went wrong";
  }
}

// --- Manual add-new-subject flow (still available regardless of preset) ---

let subjectRowCount = 0;

function addSubjectRow() {
  subjectRowCount++;
  const id = subjectRowCount;
  const container = document.getElementById("subject-rows");

  const row = document.createElement("div");
  row.className = "subject-row";
  row.id = `subject-row-${id}`;
  row.innerHTML = `
    <label>Subject name</label>
    <input type="text" class="subj-name" required />

    <label>Required attendance %</label>
    <input type="number" class="subj-required" value="75" min="1" max="100" required />

    <label>Baseline conducted (classes held so far)</label>
    <input type="number" class="subj-baseline-conducted" value="0" min="0" required />

    <label>Baseline attended (classes you attended so far)</label>
    <input type="number" class="subj-baseline-attended" value="0" min="0" required />

    <button type="button" class="btn-secondary remove-row-btn">Remove</button>
    <hr />
  `;
  row.querySelector(".remove-row-btn").addEventListener("click", () => row.remove());
  container.appendChild(row);
  row.querySelectorAll(".subj-baseline-conducted, .subj-baseline-attended").forEach(clearZeroOnFocus);
}

function collectSubjectRows(baselineDate) {
  const rows = document.querySelectorAll("#subject-rows .subject-row");
  const subjects = [];
  rows.forEach((row) => {
    const name = row.querySelector(".subj-name").value.trim();
    if (!name) return; // skip empty rows if user didn't fill this optional add-more section
    subjects.push({
      name,
      required_percent: parseFloat(row.querySelector(".subj-required").value),
      baseline_conducted: parseInt(row.querySelector(".subj-baseline-conducted").value, 10),
      baseline_attended: parseInt(row.querySelector(".subj-baseline-attended").value, 10),
      baseline_date: baselineDate,
    });
  });
  return subjects;
}

async function handleSetupSubmit(event) {
  event.preventDefault();
  const errorEl = document.getElementById("error-msg");
  errorEl.textContent = "";

  const baselineDate = document.getElementById("baseline-date").value;
  const newSubjects = collectSubjectRows(baselineDate);

  if (newSubjects.length === 0 && existingSubjects.length === 0) {
    errorEl.textContent = "Add at least one subject.";
    return;
  }

  try {
    for (const subject of newSubjects) {
      await createSubject(subject);
    }
    window.location.href = "timetable.html";
  } catch (err) {
    errorEl.textContent = err.message || "Something went wrong";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadExistingSubjects();
  addSubjectRow();
  document.getElementById("add-row-btn").addEventListener("click", addSubjectRow);
  document.getElementById("setup-form").addEventListener("submit", handleSetupSubmit);
});