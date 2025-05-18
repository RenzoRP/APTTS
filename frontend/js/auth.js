const backendUrl = "http://localhost:8000"; // Replace with your backend URL if deployed

// LOGIN
const loginForm = document.getElementById("login-form");
if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(loginForm);
    const payload = {
      username: formData.get("username"),
      password: formData.get("password"),
    };

    const errorBox = document.createElement("div");
    errorBox.className = "error-box";
    loginForm.appendChild(errorBox);

    try {
      const response = await fetch(`${backendUrl}/api/auth/login/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (response.ok) {
        localStorage.setItem("token", data.access);
        window.location.href = "dashboard.html";
      } else {
        errorBox.textContent = data.error || "Invalid credentials";
      }
    } catch (error) {
      console.error(error);
      errorBox.textContent = "Server error. Try again later.";
    }
  });
}

// REGISTER
const registerForm = document.getElementById("register-form");
if (registerForm) {
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(registerForm);
    const payload = {
      username: formData.get("username"),
      email: formData.get("email"),
      password: formData.get("password"),
    };
    try {
      const response = await fetch(`${backendUrl}/api/auth/register/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (response.ok) {
        localStorage.setItem("token", data.access);
        window.location.href = "dashboard.html";
      } else {
        alert("Registration failed: " + JSON.stringify(data));
      }
    } catch (error) {
      console.error(error);
    }
  });
}

// GOOGLE LOGIN
const googleBtn = document.getElementById("google-login");
if (googleBtn) {
  googleBtn.addEventListener("click", async () => {
    const email = prompt("Enter your Google email (mocked)"); // replace with OAuth popup flow later
    try {
      const response = await fetch(`${backendUrl}/api/auth/google-login/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      const data = await response.json();
      if (response.ok) {
        localStorage.setItem("token", data.access);
        window.location.href = "dashboard.html";
      } else {
        alert("Google login failed: " + (data.error || "Unknown error"));
      }
    } catch (err) {
      console.error(err);
    }
  });
}