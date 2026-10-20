// document.addEventListener("DOMContentLoaded", async function() {
//     const userEmail = localStorage.getItem("userEmail");

//     if (!userEmail) {
//         alert("Please log in first!");
//         window.location.href = "login.html";
//     }

//     // Fetch user details from Flask API
//     const response = await fetch("http://127.0.0.1:5000/user-dashboard", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ email: userEmail })
//     });

//     const data = await response.json();
//     document.querySelector("#dashboard-content").innerHTML = `<h2>Welcome, ${data.name}</h2>`;
// });

// // Logout function
// document.querySelector("#logoutBtn").addEventListener("click", function() {
//     localStorage.removeItem("userEmail");
//     window.location.href = "login.html";
// });
 


// dashboard.js

document.addEventListener("DOMContentLoaded", () => {
    const navLinks = document.querySelectorAll(".nav-links a");
  
    // Highlight current link based on URL
    navLinks.forEach(link => {
      if (link.href === window.location.href) {
        link.classList.add("active-link");
      }
    });
  
    // Add interactive animation to cards
    const cards = document.querySelectorAll(".card");
    cards.forEach(card => {
      card.addEventListener("mouseenter", () => {
        card.classList.add("card-hovered");
      });
      card.addEventListener("mouseleave", () => {
        card.classList.remove("card-hovered");
      });
    });
  
    // Responsive navbar toggle (for future hamburger menu)
    const nav = document.querySelector(".navbar");
    window.addEventListener("scroll", () => {
      if (window.scrollY > 50) {
        nav.classList.add("scrolled");
      } else {
        nav.classList.remove("scrolled");
      }
    });
  });
  