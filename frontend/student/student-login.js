document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("student-login-form");
    if (form) {
        form.addEventListener("submit", async function(e) {
            e.preventDefault();
            const email = document.getElementById("email").value.trim();
            const password = document.getElementById("password").value;
            if (!email || !password) {
                alert("Please fill in all fields.");
                return;
            }
            try {
                const response = await apiFetch("/auth/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email, password })
                });
                const result = await readJson(response);
                if (response.ok) {
                    // The session itself is an HttpOnly cookie; these values are
                    // only used for display and for the home page link guard.
                    localStorage.setItem("userEmail", result.email || email);
                    localStorage.setItem("userName", result.name || "Student");
                    localStorage.setItem("studentLoggedIn", "true");
                    alert("Login successful!");
                    window.location.href = "./student-dashboard.html";
                } else {
                    alert(result.message || "Login failed.");
                }
            } catch (error) {
                console.error("Error during login:", error);
                alert("Could not reach the server. Please try again.");
            }
        });
    }
});
