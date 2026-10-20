// Shared by admin.html and manage-users.html.
// The original "/get-users" endpoint never existed; the backend's admin
// student list (/auth/students) provides the same data.
async function loadUsers() {
    const response = await apiFetch("/auth/students");
    if (response.status === 401 || response.status === 403) {
        alert("Admin login required.");
        window.location.href = "admin-login.html";
        return [];
    }
    const users = await response.json();
    const tableBody = document.querySelector("#user-list tbody");
    if (tableBody) {
        tableBody.innerHTML = users.length ? "" : '<tr><td colspan="4">No users found.</td></tr>';
        users.forEach(user => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${escapeHtml(user.name)}</td>
                <td>${escapeHtml(user.email)}</td>
                <td>${escapeHtml(user.room || "")}</td>
                <td><a href="students.html">Manage</a></td>
            `;
            tableBody.appendChild(row);
        });
    }
    return users;
}

const viewUsersBtn = document.querySelector("#viewUsers");
if (viewUsersBtn) {
    viewUsersBtn.addEventListener("click", async function() {
        const users = await loadUsers();
        console.log(users);
        alert(`${users.length} registered student(s). Open the Students page to manage them.`);
    });
} else {
    document.addEventListener("DOMContentLoaded", loadUsers);
}
