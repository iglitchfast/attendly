// today.html — today's specific classes with Can Skip: YES / NO / RISKY

async function loadToday() {
  const list = document.getElementById("today-list");
  list.innerHTML = "<p>Loading...</p>";

  try {
    const data = await getTodayPrediction();
    document.getElementById("today-date").textContent = data.date;

    if (data.classes.length === 0) {
      list.innerHTML = "<p>No classes scheduled today.</p>";
      return;
    }

    list.innerHTML = "";
    data.classes.forEach((cls) => {
      const badgeClass = cls.can_skip.toLowerCase(); // "yes" | "no" | "risky"
      const row = document.createElement("div");
      row.className = "subject-card";
      row.innerHTML = `
        <h3>Period ${cls.period_number} — ${cls.subject_name}</h3>
        <span class="badge ${badgeClass}">Can Skip: ${cls.can_skip}</span>
        <div class="meta">${cls.current_percent}% (need ${cls.required_percent}%) · ${cls.safe_skips} safe skips left</div>
      `;
      list.appendChild(row);
    });
  } catch (err) {
    list.innerHTML = `<p class="error-text">${err.message || "Failed to load today's classes"}</p>`;
  }
}

document.addEventListener("DOMContentLoaded", loadToday);