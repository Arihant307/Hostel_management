document.addEventListener("DOMContentLoaded", async function() {
    // The server identifies the student from the session cookie.
    try {
        const response = await apiFetch("/auth/profile");
        if (response.status === 401) {
            alert("Login required!");
            window.location.href = "student-login.html";
            return;
        }
        const data = await readJson(response);
        if (data.fullname && data.email) {
            document.getElementById("profile-name").value = data.fullname;
            document.getElementById("profile-email").value = data.email;
        } else {
            alert(data.error || "Failed to load profile.");
        }
    } catch (error) {
        alert("Failed to load profile.");
    }
});

document.getElementById("profile-form").addEventListener("submit", async function(event) {
    event.preventDefault();
    const fullname = document.getElementById("profile-name").value.trim();
    const email = document.getElementById("profile-email").value;
    try {
        const response = await apiFetch("/auth/profile/update", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, fullname })
        });
        const data = await readJson(response);
        if (response.ok) {
            alert(data.message || "Profile updated.");
            localStorage.setItem("userName", fullname);
        } else {
            alert(data.error || data.message || "Failed to update profile.");
            if (response.status === 401) window.location.href = "student-login.html";
        }
    } catch (error) {
        alert("Failed to update profile.");
    }
});
