document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("admin-login-form");
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
                // role: "admin" makes the server refuse non-admin accounts.
                const response = await apiFetch("/auth/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ email, password, role: "admin" }),
                });

                const result = await readJson(response);
                if (response.ok && result.role === "admin") {
                    // The real session is an HttpOnly cookie set by the server;
                    // this flag is only kept for the existing page logic.
                    localStorage.setItem('token', 'admin');
                    alert("Admin login successful!");
                    window.location.href = "admin-dashboard.html";
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
