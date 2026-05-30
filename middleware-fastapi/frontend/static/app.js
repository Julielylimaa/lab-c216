(function () {
  function initSubjectAccordion() {
    document.querySelectorAll(".subject-row").forEach(function (row) {
      var targetId = row.getAttribute("data-target");
      var details = document.getElementById(targetId);
      if (!details) return;

      function toggle() {
        var isOpen = row.getAttribute("aria-expanded") === "true";
        row.setAttribute("aria-expanded", isOpen ? "false" : "true");
        row.classList.toggle("is-open", !isOpen);
        details.hidden = isOpen;
      }

      row.addEventListener("click", toggle);
      row.addEventListener("keydown", function (event) {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          toggle();
        }
      });
    });
  }

  function initCombobox(root) {
    var input = root.querySelector(".combobox-input");
    var hidden = root.querySelector(".combobox-value");
    var list = root.querySelector(".combobox-list");
    var options = Array.from(root.querySelectorAll(".combobox-option"));

    function closeList() {
      list.hidden = true;
      input.setAttribute("aria-expanded", "false");
    }

    function openList() {
      list.hidden = false;
      input.setAttribute("aria-expanded", "true");
    }

    function filterOptions(query) {
      var term = query.trim().toLowerCase();
      var visible = 0;
      options.forEach(function (option) {
        var match = !term || option.getAttribute("data-search").indexOf(term) !== -1;
        option.hidden = !match;
        if (match) visible += 1;
      });
      return visible;
    }

    function selectOption(option) {
      input.value = option.getAttribute("data-label");
      hidden.value = option.getAttribute("data-id");
      closeList();
    }

    input.addEventListener("focus", function () {
      filterOptions(input.value);
      openList();
    });

    input.addEventListener("input", function () {
      hidden.value = "";
      var visible = filterOptions(input.value);
      if (visible > 0) openList();
      else closeList();
    });

    options.forEach(function (option) {
      option.addEventListener("mousedown", function (event) {
        event.preventDefault();
        selectOption(option);
      });
    });

    document.addEventListener("click", function (event) {
      if (!root.contains(event.target)) closeList();
    });

    input.addEventListener("keydown", function (event) {
      if (event.key === "Escape") closeList();
    });

    var form = root.closest("form");
    if (form) {
      form.addEventListener("submit", function (event) {
        if (!hidden.value) {
          event.preventDefault();
          input.focus();
        }
      });
    }
  }

  function initComboboxes() {
    document.querySelectorAll("[data-combobox]").forEach(initCombobox);
  }

  document.addEventListener("DOMContentLoaded", function () {
    initSubjectAccordion();
    initComboboxes();
  });
})();
