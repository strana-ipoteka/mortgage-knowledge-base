/* Общая светлая/тёмная тема всех страниц базы знаний. */
(function () {
  "use strict";
  var KEY = "strana-ipoteka-theme";
  function stored() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }
  function preferred() {
    return (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) ? "dark" : "light";
  }
  function current() {
    var value = stored();
    return value === "dark" || value === "light" ? value : preferred();
  }
  function apply(value) {
    document.documentElement.setAttribute("data-theme", value);
    document.documentElement.style.colorScheme = value;
    var toggle = document.getElementById("theme");
    if (toggle) {
      toggle.setAttribute("aria-label", value === "dark" ? "Включить светлую тему" : "Включить тёмную тему");
      toggle.setAttribute("aria-pressed", value === "dark" ? "true" : "false");
      toggle.title = value === "dark" ? "Сейчас тёмная тема. Переключить на светлую" : "Сейчас светлая тема. Переключить на тёмную";
      toggle.textContent = value === "dark" ? "☀ Тема" : "◐ Тема";
    }
  }
  apply(current());
  document.addEventListener("DOMContentLoaded", function () {
    apply(current());
    var toggle = document.getElementById("theme");
    if (toggle) toggle.addEventListener("click", function () {
      var next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
      try { localStorage.setItem(KEY, next); } catch (e) {}
      apply(next);
    });
  });
  window.addEventListener("storage", function (e) {
    if (e.key === KEY) apply(current());
  });
  if (window.matchMedia) {
    var mq = window.matchMedia("(prefers-color-scheme: dark)");
    if (mq.addEventListener) mq.addEventListener("change", function () {
      if (!stored()) apply(preferred());
    });
  }
}());
