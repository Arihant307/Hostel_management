document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("student-booking-form");
    if (form) {
        form.addEventListener("submit", function(e) {
            e.preventDefault();
            // Optionally, check if user is logged in
            if (!localStorage.getItem("userEmail")) {
                alert("You must be logged in to book a room.");
                window.location.href = "student-login.html";
                return;
            }
            const roomType = document.getElementById("room-type").value;
            // Simulate booking (replace with backend call if needed)
            alert(`Room of type '${roomType}' booked successfully!`);
            // Optionally, redirect or reset form
            form.reset();
        });
    }
}); 