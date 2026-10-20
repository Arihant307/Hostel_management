document.addEventListener("DOMContentLoaded", function() {
    const tableBody = document.querySelector("#attendance-table tbody");
    // Simulate fetching attendance data (replace with backend call if needed)
    const attendanceRecords = [
        { date: "2024-05-01", status: "Present" },
        { date: "2024-05-02", status: "Absent" },
        { date: "2024-05-03", status: "Present" },
        { date: "2024-05-04", status: "Present" },
        { date: "2024-05-05", status: "Absent" }
    ];
    tableBody.innerHTML = attendanceRecords.map(record =>
        `<tr><td>${record.date}</td><td>${record.status}</td></tr>`
    ).join("");
}); 