// Handles register/login toggle on login.html

let mode = "login"; // or "register"

function toggleMode() {
  mode = mode === "login" ? "register" : "login";
  document.getElementById("form-title").textContent = mode === "login" ? "Log In" : "Register";
  document.getElementById("submit-btn").textContent = mode === "login" ? "Log In" : "Register";
  document.getElementById("toggle-link").textContent =
    mode === "login" ? "Need an account? Register" : "Already have an account? Log in";
  document.getElementById("error-msg").textContent = "";
}

async function handleSubmit(event) {
  event.preventDefault();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;
  const errorEl = document.getElementById("error-msg");
  errorEl.textContent = "";

  try {
    if (mode === "register") {
      await registerUser(email, password);
      // auto-login right after successful registration
      const tokenData = await loginUser(email, password);
      setToken(tokenData.access_token);
    } else {
      const tokenData = await loginUser(email, password);
      setToken(tokenData.access_token);
    }
    window.location.href = "landing.html";
  } catch (err) {
    errorEl.textContent = err.message || "Something went wrong";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("login-form").addEventListener("submit", handleSubmit);
  document.getElementById("toggle-link").addEventListener("click", (e) => {
    e.preventDefault();
    toggleMode();
  });
});