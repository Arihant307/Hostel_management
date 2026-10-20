document.getElementById("forgot-form").addEventListener("submit", function(event) {
    event.preventDefault(); // Prevent form from reloading the page

    let email = document.getElementById("email").value.trim();

    if (!email) {
        alert("Please enter your email address.");
        return;
    }

    // Simulate sending a password reset request
    console.log("Password reset request sent for:", email);
    alert("If your email is registered, you will receive a password reset link.");
    
    // Optionally, redirect to login page after submission
    setTimeout(() => {
        window.location.href = "login.html";
    }, 2000);
});
