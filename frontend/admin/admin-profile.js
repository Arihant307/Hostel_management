document.addEventListener("DOMContentLoaded", function () {
    // Simulated admin data (Replace with backend data)
    const adminData = {
        name: "Admin",
        email: "admin@example.com"
    };

    document.getElementById("admin-name").value = adminData.name;
    document.getElementById("admin-email").value = adminData.email;

    document.getElementById("admin-profile-form").addEventListener("submit", function (event) {
        event.preventDefault();

        let updatedName = document.getElementById("admin-name").value.trim();

        if (!updatedName) {
            alert("Name cannot be empty!");
            return;
        }

        console.log("Admin Profile Updated:", updatedName);
        alert("Profile updated successfully!");
    });
});
