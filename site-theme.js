/* Общая светлая/тёмная тема всех страниц базы знаний. */
(function () {
  "use strict";
  var KEY = "strana-ipoteka-theme";
  if (new URLSearchParams(window.location.search).get("embedded") === "1") {
    document.documentElement.classList.add("embedded-page");
  }
  function stored() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }
  function current() {
    var value = stored();
    return value === "dark" || value === "light" ? value : "light";
  }
  function apply(value) {
    document.documentElement.setAttribute("data-theme", value);
    document.documentElement.style.colorScheme = value;
    document.querySelectorAll(".sw button[data-t]").forEach(function (button) {
      var selected = button.getAttribute("data-t") === value;
      button.setAttribute("aria-pressed", selected ? "true" : "false");
    });
  }
  apply(current());
  document.addEventListener("DOMContentLoaded", function () {
    // Возврат на предыдущую страницу сайта, с безопасным переходом к разделам.
    document.querySelectorAll("[data-site-back]").forEach(function (link) {
      link.addEventListener("click", function (event) {
        var previous = document.referrer;
        if (previous) {
          try {
            var url = new URL(previous);
            if (url.origin === location.origin && history.length > 1) {
              event.preventDefault();
              history.back();
            }
          } catch (err) {}
        }
      });
    });
    apply(current());
    document.querySelectorAll(".sw button[data-t]").forEach(function (button) {
      button.addEventListener("click", function () {
        var next = button.getAttribute("data-t");
        if (next !== "dark" && next !== "light") return;
        try { localStorage.setItem(KEY, next); } catch (e) {}
        apply(next);
      });
    });
  });
  window.addEventListener("storage", function (e) {
    if (e.key === KEY) apply(current());
  });
}());
