(function () {
  var c = window.SITE_CONFIG || {};
  var email = (c.email || []).join("@");
  var subject = encodeURIComponent("Website in 24 hours: booking");
  var body = encodeURIComponent(
    "Hi,\n\nI'd like a website for my business.\n\n" +
    "Business name:\nWhat we offer:\nCity / area:\nPhone / WhatsApp:\n\nThanks"
  );
  var bookHref = c.payUrl
    ? c.payUrl
    : (email ? "mailto:" + email + "?subject=" + subject + "&body=" + body : "#pricing");

  document.querySelectorAll("[data-book]").forEach(function (a) {
    a.setAttribute("href", bookHref);
    if (c.payUrl) { a.target = "_blank"; a.rel = "noopener"; }
  });
  document.querySelectorAll("[data-email]").forEach(function (el) {
    el.textContent = email;
    if (el.tagName === "A") el.setAttribute("href", "mailto:" + email);
  });
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
