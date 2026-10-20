document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.querySelector("form");
    if (loginForm) {
        loginForm.addEventListener("submit", async function (event) {
            event.preventDefault();

            const email = document.querySelector("#email").value.trim();
            const password = document.querySelector("#password").value;

            if (!email || !password) {
                alert("Please fill in all fields.");
                return;
            }

            try {
                const response = await apiFetch("/auth/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ email, password }),
                });

                const result = await readJson(response);
                if (response.ok) {
                    alert("Login successful!");
                    // Send each user to the portal that matches their role.
                    if (result.role === "admin") {
                        localStorage.setItem("token", "admin");
                        window.location.href = "admin-dashboard.html";
                    } else {
                        localStorage.setItem("userEmail", result.email || email);
                        localStorage.setItem("userName", result.name || "Student");
                        localStorage.setItem("studentLoggedIn", "true");
                        window.location.href = "../student/student-dashboard.html";
                    }
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
