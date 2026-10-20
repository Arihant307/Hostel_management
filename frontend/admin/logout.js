// Ends the server session, clears local flags, then returns to the login page.
document.addEventListener("DOMContentLoaded", function () {
    let seconds = 3;
    const countdown = document.getElementById("countdown");
    const timer = setInterval(() => {
        seconds -= 1;
        if (countdown && seconds >= 0) countdown.textContent = seconds;
    }, 1000);

    apiFetch("/auth/logout", { method: "POST" })
        .catch(() => { /* ignore network errors */ })
        .finally(() => {
            try {
                sessionStorage.clear();
                localStorage.clear();
            } catch (e) { /* storage unavailable */ }
            setTimeout(() => {
                clearInterval(timer);
                window.location.href = "admin-login.html";
            }, 3000);
        });
});
