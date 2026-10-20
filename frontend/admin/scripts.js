document.addEventListener("DOMContentLoaded", function() {
    const navLinks = document.querySelectorAll("nav ul li a");
    navLinks.forEach(link => {
        link.addEventListener("mouseover", function() {
            this.style.color = "#ffcc00";
        });
        link.addEventListener("mouseout", function() {
            this.style.color = "white";
        });
    });

    const form = document.querySelector("form");
    if (form) {
        form.addEventListener("submit", function(event) {
            const email = document.querySelector("input[name='email']").value;
            const password = document.querySelector("input[name='password']").value;
            if (!email || !password) {
                alert("Please fill in all fields.");
                event.preventDefault();
            }
        });
    }
});
