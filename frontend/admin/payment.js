document.addEventListener("DOMContentLoaded", function () {
    requireRole("admin", "admin-login.html");
});

document.getElementById("payment-form").addEventListener("submit", function(event) {
    event.preventDefault();

    let studentId = document.getElementById("student-id").value.trim();
    let amount = document.getElementById("amount").value;
    let paymentMethod = document.getElementById("payment-method").value;

    if (!studentId || !amount || !paymentMethod) {
        alert("Please fill all fields!");
        return;
    }

    apiFetch("/add_payment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ student_id: studentId, amount: Number(amount), method: paymentMethod })
    })
    .then(response => readJson(response).then(data => ({ ok: response.ok, data })))
    .then(({ ok, data }) => {
        alert(data.message || data.error || (ok ? "Payment recorded." : "Payment failed."));
        if (ok) document.getElementById("payment-form").reset();
    })
    .catch(error => {
        console.error("Error processing payment:", error);
        alert("Could not reach the server. Please try again.");
    });
});
