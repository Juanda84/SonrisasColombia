(function () {
  "use strict";

  var WHATSAPP_NUMBER = "570000000000"; // TODO: reemplazar con el número real (57 + celular, sin espacios)

  /* ---------- idioma ---------- */
  var esTexts = {}; // se llena al primer cambio a EN, para poder volver a ES
  var current = "es";
  var toggle = document.getElementById("langToggle");

  function applyLang(lang) {
    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      var key = el.getAttribute("data-i18n");
      if (lang === "en") {
        if (!(key in esTexts)) esTexts[key] = el.textContent;
        if (window.SC_EN && window.SC_EN[key]) el.textContent = window.SC_EN[key];
      } else if (key in esTexts) {
        el.textContent = esTexts[key];
      }
    });
    document.documentElement.lang = lang;
    current = lang;
    if (toggle) {
      toggle.textContent = lang === "es" ? "EN" : "ES";
      toggle.setAttribute("aria-label", lang === "es" ? "Switch to English" : "Cambiar a español");
    }
    try { localStorage.setItem("sc-lang", lang); } catch (e) { /* almacenamiento no disponible */ }
  }

  if (toggle) {
    toggle.addEventListener("click", function () {
      applyLang(current === "es" ? "en" : "es");
    });
  }

  try {
    var saved = localStorage.getItem("sc-lang");
    if (saved === "en") applyLang("en");
  } catch (e) { /* almacenamiento no disponible */ }

  /* ---------- menú móvil ---------- */
  var menuToggle = document.getElementById("menuToggle");
  var nav = document.querySelector(".site-nav");
  if (menuToggle && nav) {
    menuToggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      menuToggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    nav.addEventListener("click", function (e) {
      if (e.target.tagName === "A") {
        nav.classList.remove("open");
        menuToggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  /* ---------- formulario → WhatsApp ---------- */
  var form = document.getElementById("bookingForm");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var data = new FormData(form);
      var name = (data.get("name") || "").toString().trim();
      var from = (data.get("from") || "").toString();
      var interest = (data.get("interest") || "").toString();
      var msg;
      if (current === "en") {
        msg = "Hi! I'm " + name + ", writing from " + from +
          ". I'm interested in: " + interest +
          ". I'd like to book my free virtual consultation.";
      } else {
        msg = "¡Hola! Soy " + name + ", escribo desde " + from +
          ". Me interesa: " + interest +
          ". Quiero agendar mi evaluación virtual gratuita.";
      }
      window.open("https://wa.me/" + WHATSAPP_NUMBER + "?text=" + encodeURIComponent(msg), "_blank", "noopener");
    });
  }
})();
