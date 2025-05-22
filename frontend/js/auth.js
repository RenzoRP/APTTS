const backendUrl = "http://localhost:8000"; // Replace with backend URL if deployed

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
      role: formData.get("role")
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
      alert("Network error. Try again.");
    }
  });
}

// GOOGLE LOGIN (OAuth2)
window.onload = function () {
  if (window.google) {
    google.accounts.id.initialize({
      client_id: "203635622740-3hddsaakshpi9hvqus79otreqq1qv7p6.apps.googleusercontent.com",
      callback: handleCredentialResponse
    });

    google.accounts.id.renderButton(
      document.getElementById("google-login"),
      { theme: "outline", size: "large" }
    );
  }
};

async function handleCredentialResponse(response) {
  try {
    const res = await fetch(`${backendUrl}/api/auth/google-login/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id_token: response.credential })
    });

    const data = await res.json();
    if (res.ok) {
      localStorage.setItem("token", data.access);
      window.location.href = "dashboard.html";
    } else {
      alert("Google login failed: " + (data.error || "Unknown error"));
    }
  } catch (err) {
    console.error(err);
    alert("Google login error. Try again.");
  }
}