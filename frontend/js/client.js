// Fetch wrapper + JWT header injection. Plain script, no modules —
// loaded via <script src="js/api.js"> before any page-specific JS.

const API_BASE = "http://localhost:8000";

function getToken() {
  return localStorage.getItem("attendly_token");
}

function setToken(token) {
  localStorage.setItem("attendly_token", token);
}

function clearToken() {
  localStorage.removeItem("attendly_token");
}

async function apiRequest(path, { method = "GET", body = null, auth = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : null,
  });

  if (res.status === 401) {
    clearToken();
    window.location.href = "login.html";
    return null;
  }

  if (!res.ok) {
    let detail = "Request failed";
    try {
      const data = await res.json();
      detail = data.detail || detail;
    } catch (_) {}
    throw new Error(detail);
  }

  if (res.status === 204) return null;
  return res.json();
}

// --- Auth ---
const registerUser = (email, password) =>
  apiRequest("/auth/register", { method: "POST", body: { email, password }, auth: false });

const loginUser = (email, password) =>
  apiRequest("/auth/login", { method: "POST", body: { email, password }, auth: false });

// --- Semester selection ---
const getSemesters = () => apiRequest("/auth/semesters", { auth: false });
const selectSemester = (semester) =>
  apiRequest("/auth/me/semester", { method: "PATCH", body: { semester } });

// --- Subjects ---
const getSubjects = () => apiRequest("/subjects/");
const createSubject = (subject) => apiRequest("/subjects/", { method: "POST", body: subject });
const updateSubject = (id, subject) => apiRequest(`/subjects/${id}`, { method: "PATCH", body: subject });
const deleteSubject = (id) => apiRequest(`/subjects/${id}`, { method: "DELETE" });

// --- Timetable ---
const getTimetable = () => apiRequest("/timetable/");
const setTimetableSlot = (entry) => apiRequest("/timetable/", { method: "POST", body: entry });
const deleteTimetableSlot = (id) => apiRequest(`/timetable/${id}`, { method: "DELETE" });

// --- Working day overrides (ad-hoc Saturdays etc.) ---
const getWorkingDayOverrides = () => apiRequest("/working-days/");
const createWorkingDayOverride = (override) =>
  apiRequest("/working-days/", { method: "POST", body: override });
const deleteWorkingDayOverride = (id) => apiRequest(`/working-days/${id}`, { method: "DELETE" });

// --- Predictions ---
const getTodayPrediction = () => apiRequest("/predictions/today");
const getSubjectPrediction = (id) => apiRequest(`/predictions/subject/${id}`);
const getSafeDaysOff = () => apiRequest("/predictions/safe-days-off");

// --- Timetable presets ---
const getPresets = () => apiRequest("/timetable/presets");
const applyPreset = (presetId) =>
  apiRequest("/timetable/apply-preset", { method: "POST", body: { preset_id: presetId } });