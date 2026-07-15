document.addEventListener("DOMContentLoaded", function () {
  // AOS init
  if (window.AOS) {
    AOS.init({ duration: 700, once: true, offset: 60 });
  }

  // Navbar scroll state
  const navbar = document.querySelector(".mc-navbar");
  const onScroll = () => {
    if (!navbar) return;
    if (window.scrollY > 30) navbar.classList.add("scrolled");
    else navbar.classList.remove("scrolled");
  };
  window.addEventListener("scroll", onScroll);
  onScroll();

  // Theme toggle (persist in-memory only, no localStorage per policy)
  const toggle = document.getElementById("themeToggle");
  if (toggle) {
    toggle.addEventListener("click", () => {
      const root = document.documentElement;
      const current = root.getAttribute("data-theme");
      const next = current === "light" ? "dark" : "light";
      root.setAttribute("data-theme", next);
      root.setAttribute("data-bs-theme", next);
      const icon = toggle.querySelector("i");
      if (icon) {
        icon.classList.toggle("fa-moon");
        icon.classList.toggle("fa-sun");
      }
    });
  }

  // Gauge needle animation on hero (rotate from -90deg to a data angle)
  const needle = document.querySelector(".gauge-needle");
  if (needle) {
    const angle = needle.getAttribute("data-angle") || "0";
    requestAnimationFrame(() => {
      setTimeout(() => {
        needle.style.transform = `rotate(${angle}deg)`;
      }, 300);
    });
  }

  // Live booking counter tick (cosmetic, demo only)
  const counter = document.getElementById("liveCounter");
  if (counter) {
    let base = parseInt(counter.getAttribute("data-base") || "0", 10);
    setInterval(() => {
      const bump = Math.random() > 0.6 ? 1 : 0;
      if (bump) {
        base += 1;
        counter.textContent = base;
        counter.classList.add("pulse-once");
        setTimeout(() => counter.classList.remove("pulse-once"), 400);
      }
    }, 4000);
  }

  // Booking wizard: time-slot picker (radio-backed buttons)
  document.querySelectorAll(".slot-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const group = btn.closest(".slot-grid");
      group.querySelectorAll(".slot-btn").forEach((b) => b.classList.remove("selected"));
      btn.classList.add("selected");
      const input = document.getElementById(btn.dataset.target);
      if (input) input.checked = true;
    });
  });

  // Mobile nav toggle handled by Bootstrap collapse (no extra JS needed)
});
