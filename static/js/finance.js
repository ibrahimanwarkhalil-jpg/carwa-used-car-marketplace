(function () {
  function digitsOnly(value) {
    return (value || "").replace(/\D/g, "");
  }

  function formatAed(value) {
    return "AED " + Math.max(0, Math.round(value)).toLocaleString();
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

  function updatePreview(form) {
    const preview = form.querySelector("[data-finance-preview]");
    if (!preview) {
      return;
    }

    const budget = Number(digitsOnly(form.elements.budget.value));
    const downPayment = Number(digitsOnly(form.elements.down_payment.value));
    const months = Number(form.elements.tenure_months.value || 0);
    const financeAmount = Math.max(0, budget - downPayment);
    const monthlyTarget = preview.querySelector("[data-finance-monthly]");
    const amountTarget = preview.querySelector("[data-finance-amount]");

    if (!budget || !months || downPayment >= budget) {
      preview.hidden = true;
      return;
    }

    const annualRate = 0.0399;
    const totalPayable = financeAmount * (1 + annualRate * (months / 12));
    amountTarget.textContent = formatAed(financeAmount);
    monthlyTarget.textContent = formatAed(totalPayable / months);
    preview.hidden = false;
  }

  document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector('form[action="/finance"]');
    if (!form) {
      return;
    }

    const phoneInput = form.querySelector("[data-phone-input]");
    if (phoneInput) {
      if (!phoneInput.value) {
        phoneInput.value = "05";
      }
      normalizePhone(phoneInput);
      phoneInput.addEventListener("input", function () {
        normalizePhone(phoneInput);
      });
      phoneInput.addEventListener("keydown", function (event) {
        const allowedKeys = [
          "Backspace",
          "Delete",
          "ArrowLeft",
          "ArrowRight",
          "Tab",
          "Home",
          "End",
        ];
        if (allowedKeys.includes(event.key)) {
          return;
        }
        if (!/^\d$/.test(event.key)) {
          event.preventDefault();
        }
      });
    }

    form.querySelectorAll("[data-digits-only]").forEach(function (input) {
      input.addEventListener("input", function () {
        input.value = digitsOnly(input.value);
        updatePreview(form);
      });
      input.addEventListener("keydown", function (event) {
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
      });
    });

    form.elements.tenure_months.addEventListener("change", function () {
      updatePreview(form);
    });
    updatePreview(form);
  });
})();
