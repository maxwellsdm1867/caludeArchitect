/* ===================================================================
   Claude Architect Foundations — Theme Toggle & Interactive Components
   =================================================================== */
(function () {
  "use strict";

  /* --- Theme -------------------------------------------------------- */
  var html = document.documentElement;
  var THEMES = ["system", "light", "dark"];
  var ICONS  = { system: "\u2699\uFE0F", light: "\u2600\uFE0F", dark: "\uD83C\uDF19" };
  var stored = localStorage.getItem("caf-theme") || "system";
  applyTheme(stored);

  function applyTheme(theme) {
    html.setAttribute("data-theme", theme);
    localStorage.setItem("caf-theme", theme);
    document.querySelectorAll(".theme-toggle").forEach(function (btn) {
      var icon  = btn.querySelector(".theme-icon");
      var label = btn.querySelector(".theme-label");
      if (icon)  icon.textContent  = ICONS[theme];
      if (label) label.textContent = theme.charAt(0).toUpperCase() + theme.slice(1);
    });
  }

  function cycleTheme() {
    var cur  = localStorage.getItem("caf-theme") || "system";
    var next = THEMES[(THEMES.indexOf(cur) + 1) % THEMES.length];
    applyTheme(next);
  }

  /* --- Wait for DOM ------------------------------------------------- */
  document.addEventListener("DOMContentLoaded", function () {

    /* Theme toggle buttons */
    document.querySelectorAll(".theme-toggle").forEach(function (btn) {
      btn.addEventListener("click", cycleTheme);
    });
    applyTheme(localStorage.getItem("caf-theme") || "system");

    /* --- Copy Buttons for Code Examples ----------------------------- */
    document.querySelectorAll(".code-example").forEach(function (block) {
      var btn = document.createElement("button");
      btn.className = "copy-btn";
      btn.textContent = "Copy";
      btn.setAttribute("aria-label", "Copy code to clipboard");
      block.appendChild(btn);

      btn.addEventListener("click", function () {
        var code = block.querySelector("code");
        if (!code) return;
        navigator.clipboard.writeText(code.textContent).then(function () {
          btn.textContent = "Copied!";
          btn.classList.add("copied");
          setTimeout(function () {
            btn.textContent = "Copy";
            btn.classList.remove("copied");
          }, 2000);
        });
      });
    });

    /* --- Collapsible Sections --------------------------------------- */
    document.querySelectorAll(".collapsible-trigger").forEach(function (trigger) {
      trigger.addEventListener("click", function () {
        var parent = trigger.closest(".collapsible");
        if (parent) parent.classList.toggle("open");
      });
    });

    /* --- Tab Groups ------------------------------------------------- */
    document.querySelectorAll(".tab-group").forEach(function (group) {
      var tabs   = group.querySelectorAll(".tab");
      var panels = group.querySelectorAll(".tab-panel");

      tabs.forEach(function (tab, i) {
        tab.addEventListener("click", function () {
          tabs.forEach(function (t) { t.classList.remove("active"); });
          panels.forEach(function (p) { p.classList.remove("active"); });
          tab.classList.add("active");
          if (panels[i]) panels[i].classList.add("active");
        });
      });

      // Activate first tab by default if none active
      if (!group.querySelector(".tab.active")) {
        if (tabs[0])   tabs[0].classList.add("active");
        if (panels[0]) panels[0].classList.add("active");
      }
    });

    /* --- Inline Quiz ------------------------------------------------ */
    document.querySelectorAll(".quiz-question").forEach(function (q) {
      var options = q.querySelectorAll(".quiz-option");
      var reveal  = q.querySelector(".quiz-reveal");
      var correct = q.getAttribute("data-correct");

      options.forEach(function (opt) {
        opt.addEventListener("click", function () {
          if (q.classList.contains("answered")) return;
          q.classList.add("answered");

          var chosen = opt.getAttribute("data-value");

          options.forEach(function (o) {
            o.style.pointerEvents = "none";
            if (o.getAttribute("data-value") === correct) {
              o.classList.add("correct");
            }
          });

          if (chosen === correct) {
            opt.classList.add("correct");
            if (reveal) reveal.classList.add("show", "correct-reveal");
          } else {
            opt.classList.add("incorrect");
            if (reveal) reveal.classList.add("show", "incorrect-reveal");
          }
        });
      });
    });
  });
})();
