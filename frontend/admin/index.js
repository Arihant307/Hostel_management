document.addEventListener("DOMContentLoaded", function () {
    // Check if user is logged in (Mock Example)
    let isLoggedIn = sessionStorage.getItem("loggedInUser");

    if (isLoggedIn) {
        document.querySelector(".btn-primary").innerText = "Go to Dashboard";
        document.querySelector(".btn-primary").href = "dashboard.html";
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener("click", function (event) {
            event.preventDefault();
            const target = document.querySelector(this.getAttribute("href"));
            target.scrollIntoView({ behavior: "smooth" });
        });
    });
});
