document.getElementById("register-form").addEventListener("submit", async function(event) {
    event.preventDefault();

    let fullname = document.getElementById("fullname").value.trim();
    let email = document.getElementById("email").value.trim();
    let password = document.getElementById("password").value;
    let confirmPassword = document.getElementById("confirm-password").value;
    let room = document.getElementById("room").value;

    if (password !== confirmPassword) {
        alert("Passwords do not match!");
        return;
    }

    if (password.length < 8) {
        alert("Password must be at least 8 characters.");
        return;
    }

    let userData = {
        fullname: fullname,
        email: email,
        password: password,
        room: room
    };

    try {
        const response = await apiFetch("/auth/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(userData)
        });

        const result = await readJson(response);
        if (response.ok) {
            alert("Registration successful! Please log in.");
            window.location.href = "./student-login.html";
        } else {
            alert(result.message || "Registration failed.");
        }
    } catch (error) {
        alert("Could not reach the server. Please try again.");
        console.error(error);
    }
});
