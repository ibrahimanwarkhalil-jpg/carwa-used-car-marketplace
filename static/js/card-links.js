document.addEventListener("DOMContentLoaded", function () {
  const clickableCards = document.querySelectorAll("[data-card-link]");
  const interactiveSelector = "a, button, input, select, textarea, label, summary";

  clickableCards.forEach(function (card) {
    const destination = card.getAttribute("data-card-link");
    if (!destination) {
      return;
    }

    card.addEventListener("click", function (event) {
      if (event.target.closest(interactiveSelector)) {
        return;
      }
      window.location.href = destination;
    });

    card.addEventListener("keydown", function (event) {
      if (event.target !== card) {
        return;
      }
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        window.location.href = destination;
      }
    });
  });
});
