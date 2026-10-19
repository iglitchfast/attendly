// timetable.html — grid UI (Mon-Sat only, Sunday never scheduled) plus
// ad-hoc working-day-override management.

const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]; // Sunday intentionally excluded
const PERIODS_PER_DAY = 6; // adjust if needed

let subjectsCache = [];
let timetableCache = [];
let workingDaysCache = [];

function buildGrid() {
  const grid = document.getElementById("timetable-grid");
  grid.innerHTML = "";
  grid.style.gridTemplateColumns = `80px repeat(${DAYS.length}, 1fr)`;

  grid.appendChild(makeCell(""));
  DAYS.forEach((day) => grid.appendChild(makeCell(day, true)));

  for (let period = 1; period <= PERIODS_PER_DAY; period++) {
    grid.appendChild(makeCell(`P${period}`, true));
    DAYS.forEach((_, dayIndex) => {
      grid.appendChild(makeSelectCell(dayIndex, period));
    });
  }
}

function makeCell(text, bold = false) {
  const div = document.createElement("div");
  div.className = "timetable-cell";
  div.textContent = text;
  if (bold) div.style.fontWeight = "600";
  return div;
}

function makeSelectCell(dayIndex, period) {
  const div = document.createElement("div");
  div.className = "timetable-cell";

  const select = document.createElement("select");
  select.dataset.day = dayIndex;
  select.dataset.period = period;

  const emptyOpt = document.createElement("option");
  emptyOpt.value = "";
  emptyOpt.textContent = "—";
  select.appendChild(emptyOpt);

  subjectsCache.forEach((subj) => {
    const opt = document.createElement("option");
    opt.value = subj.id;
    opt.textContent = subj.name;
    select.appendChild(opt);
  });

  const existing = timetableCache.find(
    (e) => e.day_of_week === dayIndex && e.period_number === period
  );
  if (existing) select.value = existing.subject_id;

  select.addEventListener("change", async () => {
    if (!select.value) return;
    try {
      await setTimetableSlot({
        subject_id: parseInt(select.value, 10),
        day_of_week: dayIndex,
        period_number: period,
      });
    } catch (err) {
      alert(err.message || "Failed to save slot");
    }
  });

  div.appendChild(select);
  return div;
}

// --- Working day overrides ---

function renderWorkingDays() {
  const list = document.getElementById("working-day-list");
  if (workingDaysCache.length === 0) {
    list.innerHTML = "<p>No working-day overrides added yet.</p>";
    return;
  }

  list.innerHTML = "";
  workingDaysCache.forEach((wd) => {
    const row = document.createElement("div");
    row.className = "subject-card";
    row.style.marginBottom = "8px";
    row.innerHTML = `
      <strong>${wd.date}</strong> — follows ${DAYS[wd.follows_day_of_week] || "?"}'s timetable
      ${wd.reason ? `<div class="meta">${wd.reason}</div>` : ""}
      <button type="button" class="btn-secondary remove-wd-btn" style="margin-top: 8px;">Remove</button>
    `;
    row.querySelector(".remove-wd-btn").addEventListener("click", async () => {
      try {
        await deleteWorkingDayOverride(wd.id);
        await loadWorkingDays();
      } catch (err) {
        alert(err.message || "Failed to remove");
      }
    });
    list.appendChild(row);
  });
}

async function loadWorkingDays() {
  workingDaysCache = await getWorkingDayOverrides();
  renderWorkingDays();
}

async function handleAddWorkingDay(event) {
  event.preventDefault();
  const errorEl = document.getElementById("wd-error-msg");
  errorEl.textContent = "";

  const date = document.getElementById("wd-date").value;
  const followsDayOfWeek = parseInt(document.getElementById("wd-follows").value, 10);
  const reason = document.getElementById("wd-reason").value.trim() || null;

  try {
    await createWorkingDayOverride({ date, follows_day_of_week: followsDayOfWeek, reason });
    document.getElementById("working-day-form").reset();
    await loadWorkingDays();
    // Calendar engine re-reads overrides on every prediction call, so
    // no separate recalculation step is needed here — dashboard/today
    // will reflect this automatically next time they're loaded.
  } catch (err) {
    errorEl.textContent = err.message || "Failed to add working day";
  }
}

// --- Init ---

async function loadData() {
  subjectsCache = await getSubjects();
  timetableCache = await getTimetable();
  buildGrid();
  await loadWorkingDays();
}

document.addEventListener("DOMContentLoaded", () => {
  loadData();
  document.getElementById("working-day-form").addEventListener("submit", handleAddWorkingDay);
  document.getElementById("done-btn").addEventListener("click", () => {
    window.location.href = "dashboard.html";
  });
});