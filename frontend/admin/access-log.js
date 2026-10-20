// document.addEventListener("DOMContentLoaded", function () {
//     const logList = document.getElementById("log-list");

//     // Example log data (Replace with backend data)
//     const logs = [
//         { user: "John Doe", email: "john@example.com", ip: "192.168.1.1", time: "2025-03-02 14:00" },
//         { user: "Jane Smith", email: "jane@example.com", ip: "192.168.1.2", time: "2025-03-02 15:30" },
//         { user: "Admin", email: "admin@example.com", ip: "192.168.1.3", time: "2025-03-02 16:10" }
//     ];

//     logs.forEach(log => {
//         let row = document.createElement("tr");
//         row.innerHTML = `
//             <td>${log.user}</td>
//             <td>${log.email}</td>
//             <td>${log.ip}</td>
//             <td>${log.time}</td>
//         `;
//         logList.appendChild(row);
//     });
// });


// access-log.js

document.addEventListener("DOMContentLoaded", function () {
    const logList = document.getElementById("log-list");

    // Example log data (Replace with real data from backend)
    const logs = [
        {
            user: "John Doe",
            email: "john@example.com",
            ip: "192.168.1.1",
            time: "2025-04-06 09:23"
        },
        {
            user: "Jane Smith",
            email: "jane@example.com",
            ip: "192.168.1.2",
            time: "2025-04-06 10:45"
        },
        {
            user: "Admin",
            email: "admin@example.com",
            ip: "192.168.1.3",
            time: "2025-04-06 11:10"
        }
    ];

    logs.forEach(log => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${log.user}</td>
            <td>${log.email}</td>
            <td>${log.ip}</td>
            <td>${log.time}</td>
        `;
        logList.appendChild(row);
    });
});