let logoutTimer;

function resetTimer() {
    clearTimeout(logoutTimer);
    logoutTimer = setTimeout(() => {
        apiFetch("/auth/logout", { method: "POST" }) // Call Flask Logout API
            .then(() => {
                alert("You have been logged out due to inactivity.");
                window.location.href = "admin-login.html"; // Redirect to login
            })
            .catch(error => console.error("Logout error:", error));
    }, 10 * 60 * 1000); // 10 minutes inactivity logout
}

// Reset timer on user activity
document.addEventListener("mousemove", resetTimer);
document.addEventListener("keypress", resetTimer);

// Start the timer when the page loads
resetTimer();
