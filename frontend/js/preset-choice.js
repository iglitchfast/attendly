// preset-choice.html — sits between landing.html (semester select) and
// setup.html. Lets the user opt into a class-specific timetable preset,
// or fall through to manual entry (the default/safe path).

async function loadPresets() {
  const container = document.getElementById("preset-options");
  const errorEl = document.getElementById("error-msg");

  try {
    const presets = await getPresets();

    if (presets.length === 0) {
      container.innerHTML = "<p>No presets available yet — use manual entry below.</p>";
      return;
    }

    container.innerHTML = "";
    presets.forEach((preset) => {
      const wrapper = document.createElement("div");
      wrapper.style.marginBottom = "16px";
      wrapper.innerHTML = `
        <button type="button" class="btn-primary preset-btn" data-preset-id="${preset.id}" style="width: 100%;">
          ${preset.label} — use preset timetable
        </button>
        <p style="font-size: 12px; margin-top: 6px;">${preset.warning}</p>
      `;
      wrapper.querySelector(".preset-btn").addEventListener("click", () => handleApplyPreset(preset.id));
      container.appendChild(wrapper);
    });
  } catch (err) {
    errorEl.textContent = err.message || "Failed to load presets";
  }
}

async function handleApplyPreset(presetId) {
  const errorEl = document.getElementById("error-msg");
  errorEl.textContent = "";

  const confirmed = confirm(
    "This will pre-fill subjects and your weekly timetable. Only continue if this preset actually matches your class. You can still edit everything afterward. Continue?"
  );
  if (!confirmed) return;

  try {
    await applyPreset(presetId);
    window.location.href = "setup.html"; // land on setup to review/add baseline numbers
  } catch (err) {
    errorEl.textContent = err.message || "Failed to apply preset";
  }
}

function handleManualEntry() {
  window.location.href = "setup.html";
}

document.addEventListener("DOMContentLoaded", () => {
  loadPresets();
  document.getElementById("manual-btn").addEventListener("click", handleManualEntry);
});