document.addEventListener("DOMContentLoaded", async function () {
    const paymentList = document.getElementById("payment-list");

    if (!(await requireRole("admin", "admin-login.html"))) return;

    function fetchPayments() {
        apiFetch("/get_payments")
            .then(response => {
                if (!response.ok) throw new Error("HTTP " + response.status);
                return response.json();
            })
            .then(data => {
                paymentList.innerHTML = "";
                if (data.length === 0) {
                    paymentList.innerHTML = '<tr><td colspan="4">No payments recorded yet.</td></tr>';
                    return;
                }
                data.forEach(payment => {
                    let row = document.createElement("tr");
                    row.innerHTML = `
                        <td>${escapeHtml(payment.student_id)}${payment.student_name ? " - " + escapeHtml(payment.student_name) : ""}</td>
                        <td>$${escapeHtml(payment.amount)}</td>
                        <td>${escapeHtml(payment.method)}</td>
                        <td>${escapeHtml(payment.date)}</td>
                    `;
                    paymentList.appendChild(row);
                });
            })
            .catch(error => {
                paymentList.innerHTML = '<tr><td colspan="4">Failed to load payments.</td></tr>';
                console.error("Error fetching payments:", error);
            });
    }

    fetchPayments();
});
