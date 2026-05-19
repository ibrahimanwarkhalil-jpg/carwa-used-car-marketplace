(function () {
  const storageKey = "carwa-compare";
  const maxCars = 4;

  function readSelection() {
    try {
      const parsed = JSON.parse(localStorage.getItem(storageKey) || "[]");
      return Array.isArray(parsed) ? parsed.map(String).slice(0, maxCars) : [];
    } catch (error) {
      return [];
    }
  }

  function writeSelection(ids) {
    const uniqueIds = [];
    ids.map(String).forEach(function (id) {
      if (id && !uniqueIds.includes(id)) {
        uniqueIds.push(id);
      }
    });
    localStorage.setItem(storageKey, JSON.stringify(uniqueIds.slice(0, maxCars)));
    return uniqueIds.slice(0, maxCars);
  }

  function getUrlSelection() {
    const params = new URLSearchParams(window.location.search);
    const ids = params.getAll("cars");
    ["car1", "car2"].forEach(function (key) {
      const value = params.get(key);
      if (value) {
        ids.push(value);
      }
    });
    return ids.filter(Boolean).slice(0, maxCars);
  }

  function compareUrl(ids) {
    const params = new URLSearchParams();
    ids.forEach(function (id) {
      params.append("cars", id);
    });
    return "/compare" + (ids.length ? "?" + params.toString() : "");
  }

  function createTray() {
    const tray = document.createElement("div");
    tray.className = "compare-tray";
    tray.setAttribute("data-compare-tray", "");
    tray.innerHTML = [
      '<div>',
      '<strong>Compare cars</strong>',
      '<span data-compare-summary>Select 2 to 4 cars</span>',
      '</div>',
      '<div class="compare-tray-actions">',
      '<button type="button" class="btn btn-outline-secondary" data-compare-reset>Clear</button>',
      '<a class="btn btn-dark" data-compare-open href="/compare">Open Compare</a>',
      '</div>',
    ].join("");
    document.body.appendChild(tray);
    return tray;
  }

  function render(selection) {
    const ids = writeSelection(selection);
    const tray = document.querySelector("[data-compare-tray]") || createTray();
    const summary = tray.querySelector("[data-compare-summary]");
    const openLink = tray.querySelector("[data-compare-open]");
    const hasSelection = ids.length > 0;

    tray.classList.toggle("is-visible", hasSelection);
    summary.textContent = ids.length + " selected" + (ids.length < 2 ? " - add one more" : "");
    openLink.href = compareUrl(ids);
    openLink.classList.toggle("disabled", ids.length < 2);
    openLink.setAttribute("aria-disabled", ids.length < 2 ? "true" : "false");

    document.querySelectorAll("[data-compare-add]").forEach(function (button) {
      const carId = String(button.getAttribute("data-car-id"));
      const isSelected = ids.includes(carId);
      button.classList.toggle("active", isSelected);
      button.innerHTML = isSelected
        ? "Selected"
        : "Compare";
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    if (document.body.classList.contains("admin-context")) {
      return;
    }

    const urlSelection = getUrlSelection();
    let selection = urlSelection.length ? writeSelection(urlSelection) : readSelection();

    render(selection);

    document.addEventListener("click", function (event) {
      const addButton = event.target.closest("[data-compare-add]");
      if (addButton) {
        const carId = String(addButton.getAttribute("data-car-id"));
        if (selection.includes(carId)) {
          selection = selection.filter(function (id) {
            return id !== carId;
          });
        } else if (selection.length < maxCars) {
          selection = selection.concat(carId);
        }
        render(selection);
        return;
      }

      const resetButton = event.target.closest("[data-compare-reset], [data-compare-clear]");
      if (resetButton) {
        selection = [];
        render(selection);
      }

      const openLink = event.target.closest("[data-compare-open]");
      if (openLink && selection.length < 2) {
        event.preventDefault();
      }
    });

    document.querySelectorAll("[data-compare-remove]").forEach(function (link) {
      link.addEventListener("click", function () {
        const carId = String(link.getAttribute("data-car-id"));
        selection = selection.filter(function (id) {
          return id !== carId;
        });
        writeSelection(selection);
      });
    });
  });
})();
