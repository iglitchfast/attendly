// Mirrors backend/attendance_engine.py exactly. Plain functions, no modules,
// used for instant client-side feedback before hitting the API.

function calculatePercentage(attended, conducted) {
  if (conducted <= 0) return 0;
  return Math.round((attended / conducted) * 10000) / 100;
}

function calculateSafeSkips(attended, conducted, requiredPercent) {
  if (requiredPercent <= 0) return 1000000;
  if (conducted <= 0) return 0;

  const maxX = (attended * 100) / requiredPercent - conducted;
  return Math.max(0, Math.floor(maxX));
}

function calculateSafeSkipsSemester(attended, conducted, remaining, requiredPercent) {
  const totalClasses = conducted + remaining;
  if (totalClasses <= 0 || requiredPercent <= 0) return remaining;

  const minAttendedNeeded = Math.ceil((requiredPercent / 100) * totalClasses);
  const mustAttendOfRemaining = Math.max(0, minAttendedNeeded - attended);
  return Math.max(0, remaining - mustAttendOfRemaining);
}

function classesNeededToRecover(attended, conducted, requiredPercent) {
  if (requiredPercent <= 0) return 0;

  const current = calculatePercentage(attended, conducted);
  if (current >= requiredPercent) return 0;

  let n = 0;
  while (true) {
    const projected = calculatePercentage(attended + n, conducted + n);
    if (projected >= requiredPercent) return n;
    n++;
    if (n > 100000) return n;
  }
}

// Used by dashboard.js to pick the .subject-card status class
function getAttendanceStatus(currentPercent, requiredPercent) {
  if (currentPercent >= requiredPercent + 3) return "safe";
  if (currentPercent >= requiredPercent) return "risky";
  return "danger";
}