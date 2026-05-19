(function () {
  function digitsOnly(value) {
    return (value || "").replace(/\D/g, "");
  }

  function normalizePhone(input) {
    let digits = digitsOnly(input.value);
    if (digits.startsWith("9715")) {
      digits = "0" + digits.slice(3);
    }
    if (!digits.startsWith("05")) {
      digits = "05" + digits.replace(/^0+/, "").replace(/^5?/, "");
    }
    input.value = digits.slice(0, 10);
  }

  function blockNonDigits(event) {
    const allowedKeys = [
      "Backspace",
      "Delete",
      "ArrowLeft",
      "ArrowRight",
      "Tab",
      "Home",
      "End",
    ];
    if (!allowedKeys.includes(event.key) && !/^\d$/.test(event.key)) {
      event.preventDefault();
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-phone-input]").forEach(function (input) {
      if (!input.value) {
        input.value = "05";
      }
      normalizePhone(input);
      input.addEventListener("input", function () {
        normalizePhone(input);
      });
      input.addEventListener("keydown", blockNonDigits);
    });
  });
})();
