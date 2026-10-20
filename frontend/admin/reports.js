document.addEventListener("DOMContentLoaded", async function () {
    const studentReportTable = document.getElementById("student-report");

    if (!(await requireRole("admin", "admin-login.html"))) return;

    function fetchStudentReports() {
        studentReportTable.innerHTML = '<tr><td colspan="4">Loading...</td></tr>';
        apiFetch("/auth/get_student_reports")
            .then(response => {
                if (!response.ok) throw new Error("HTTP " + response.status);
                return response.json();
            })
            .then(data => {
                studentReportTable.innerHTML = "";
                data.forEach(student => {
                    let row = document.createElement("tr");
                    row.innerHTML = `
                        <td>${escapeHtml(student.name)}</td>
                        <td>${escapeHtml(student.email)}</td>
                        <td>${student.room_number ? escapeHtml(student.room_number) : "Not Assigned"}</td>
                        <td>${student.payment_status ? "Paid" : "Pending"}</td>
                    `;
                    studentReportTable.appendChild(row);
                });
                if (data.length === 0) {
                    studentReportTable.innerHTML = '<tr><td colspan="4">No data found.</td></tr>';
                }
            })
            .catch(error => {
                studentReportTable.innerHTML = '<tr><td colspan="4">Error loading data.</td></tr>';
                console.error("Error fetching student reports:", error);
            });
    }

    function fetchRoomOccupancyChart() {
        const chartCanvas = document.getElementById("roomOccupancyChart");
        if (!chartCanvas) return;
        apiFetch("/api/rooms/get_room_occupancy")
            .then(response => {
                if (!response.ok) throw new Error("HTTP " + response.status);
                return response.json();
            })
            .then(data => {
                if (typeof Chart === "undefined") throw new Error("Chart.js failed to load");
                const ctx = chartCanvas.getContext("2d");
                new Chart(ctx, {
                    type: "bar",
                    data: {
                        labels: data.room_types,
                        datasets: [{
                            label: "Occupied Rooms",
                            data: data.occupancy_counts,
                            backgroundColor: "#3498db",
                            borderColor: "#2c3e50",
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { display: false },
                            title: { display: false }
                        },
                        scales: {
                            y: { beginAtZero: true, ticks: { stepSize: 1 } }
                        }
                    }
                });
            })
            .catch(error => {
                const note = document.createElement("div");
                note.style.color = "red";
                note.textContent = "Error loading chart data.";
                chartCanvas.parentElement.appendChild(note);
                console.error("Error fetching room occupancy data:", error);
            });
    }

    fetchStudentReports();
    fetchRoomOccupancyChart();
});
