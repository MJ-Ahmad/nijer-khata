/* Learn pages: language (EN / বাংলা / العربية) and theme, shared with the dashboard via localStorage. */
(function () {
  var root = document.documentElement;
  var DIR = { en: "ltr", bn: "ltr", ar: "rtl" };

  function get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function put(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }

  function applyLang(lang) {
    if (!DIR[lang]) lang = "en";
    root.lang = lang;
    root.dir = DIR[lang];
    document.querySelectorAll("[data-en]").forEach(function (el) {
      var v = el.getAttribute("data-" + lang);
      if (v === null) v = el.getAttribute("data-en");
      el.textContent = v;
    });
    document.querySelectorAll("[data-lang]").forEach(function (b) {
      b.setAttribute("aria-pressed", String(b.getAttribute("data-lang") === lang));
    });
    put("khataLang", lang);
  }

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    put("khataTheme", theme);
    var b = document.getElementById("theme");
    if (b) b.textContent = theme === "dark" ? "☀" : "☾";
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-lang]").forEach(function (b) {
      b.addEventListener("click", function () { applyLang(b.getAttribute("data-lang")); });
    });
    var th = document.getElementById("theme");
    if (th) th.addEventListener("click", function () {
      applyTheme(root.getAttribute("data-theme") === "dark" ? "light" : "dark");
    });
    applyLang(get("khataLang") || "en");
    applyTheme(get("khataTheme") || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"));
  });
})();
