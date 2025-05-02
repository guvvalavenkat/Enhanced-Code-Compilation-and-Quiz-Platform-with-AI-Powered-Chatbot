
   document.addEventListener("DOMContentLoaded", function() {
    console.log("Script Loaded");

    let lastScrollY = window.scrollY;
    const navbar = document.querySelector(".navbar");

    // Ensure the navbar is visible when the page loads
    navbar.classList.add("visible");

    window.addEventListener("scroll", () => {
        if (window.scrollY > 50 && window.scrollY > lastScrollY) {
            navbar.classList.add("hidden"); // Hide when scrolling down
        } else {
            navbar.classList.remove("hidden"); // Show when scrolling up
        }
        lastScrollY = window.scrollY;
    });

    // Smooth scrolling for navigation links
    document.querySelectorAll(".nav-links a").forEach(link => {
        link.addEventListener("click", function(event) {
            event.preventDefault();
            let target = document.querySelector(this.getAttribute("href"));
            if (target) {
                window.scrollTo({ top: target.offsetTop - 50, behavior: "smooth" });
            }
        });
    });

    // Section Fade-In on Scroll
    const fadeElements = document.querySelectorAll(".fade-in");

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("visible");
            }
        });
    }, { threshold: 0.3 });

    fadeElements.forEach(el => observer.observe(el));
});

