document.addEventListener("DOMContentLoaded", function () {
  const toggle = document.querySelector("[data-theme-toggle]");
  const label = document.querySelector("[data-theme-label]");
  const icon = document.querySelector("[data-theme-icon]");

  function applyTheme(theme) {
    const isDark = theme === "dark";
    document.documentElement.setAttribute("data-theme", isDark ? "dark" : "light");
    localStorage.setItem("carwa-theme", isDark ? "dark" : "light");

    if (label) {
      label.textContent = isDark ? "Day" : "Dark";
    }
    if (icon) {
      icon.className = isDark ? "fa-solid fa-sun" : "fa-solid fa-moon";
    }
    if (toggle) {
      const actionLabel = isDark ? "Switch to day mode" : "Switch to dark mode";
      toggle.setAttribute("aria-label", actionLabel);
      toggle.setAttribute("title", actionLabel);
      toggle.setAttribute("data-tooltip", actionLabel);
    }
  }

  const savedTheme = localStorage.getItem("carwa-theme") || "light";
  applyTheme(savedTheme);

  if (toggle) {
    toggle.addEventListener("click", function () {
      const currentTheme = document.documentElement.getAttribute("data-theme");
      applyTheme(currentTheme === "dark" ? "light" : "dark");
    });
  }
});
