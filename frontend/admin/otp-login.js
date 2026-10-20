// NOTE: not loaded by any page. The backend has no OTP endpoints (they only
// existed in the unused MySQL prototype and need an SMTP account).
document.getElementById("send-otp-btn").addEventListener("click", function() {
    let email = document.getElementById("email").value.trim();

    apiFetch("/send_otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email })
    })
    .then(response => response.json())
    .then(data => alert(data.message))
    .catch(error => console.error("Error sending OTP:", error));
});

document.getElementById("verify-otp-btn").addEventListener("click", function() {
    let email = document.getElementById("email").value.trim();
    let otp = document.getElementById("otp").value.trim();

    apiFetch("/verify_otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email, otp: otp })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert(data.message);
            window.location.href = "admin-dashboard.html"; // Redirect on success
        }
    })
    .catch(error => console.error("Error verifying OTP:", error));
});
