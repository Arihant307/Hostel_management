document.addEventListener("DOMContentLoaded", function () {
    const registerForm = document.querySelector("form");
    if (registerForm) {
        registerForm.addEventListener("submit", async function (event) {
            event.preventDefault();

            const fullname = document.querySelector("#fullname").value.trim();
            const email = document.querySelector("#email").value.trim();
            const password = document.querySelector("#password").value;
            const confirmPassword = document.querySelector("#confirm-password").value;
            const room = document.querySelector("#room").value;

            if (!fullname || !email || !password || !confirmPassword || !room) {
                alert("Please fill in all fields.");
                return;
            }

            if (password !== confirmPassword) {
                alert("Passwords do not match.");
                return;
            }

            if (password.length < 8) {
                alert("Password must be at least 8 characters.");
                return;
            }

            try {
                const response = await apiFetch("/auth/register", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ fullname, email, password, room }),
                });

                const result = await readJson(response);
                if (response.ok) {
                    alert("Registration successful! Please log in.");
                    // New accounts are student accounts, so go to the login page.
                    window.location.href = "login.html";
                } else {
                    alert(result.message || "Registration failed.");
                }
            } catch (error) {
                console.error("Error during registration:", error);
                alert("Could not reach the server. Please try again.");
            }
        });
    }
});
