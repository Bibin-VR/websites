// Single place to wire the site up.
// payUrl / payLinkId are managed by scripts/rotate_pay_link.py and the
// "Keep payment link fresh" GitHub Action. While payUrl is empty, every
// "Book" button opens a pre-filled booking email instead.
window.SITE_CONFIG = {
  payUrl: "https://rzp.io/rzp/5bywbkqy",
  payLinkId: "plink_Tlhfw5WrIcPtqm",
  email: ["bibin.blp", "gmail.com"]
};
