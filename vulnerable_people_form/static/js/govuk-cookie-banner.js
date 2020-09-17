window.GOVUK = window.GOVUK || {};
window.GOVUK.Modules = window.GOVUK.Modules || {};

(function (modules, analytics, cookieSettings) {
  "use strict";
  function CookieBanner() {
    var that = this;
    this.hideCookieMessage = function (event) {
      that.cookieBannerOuterElement.style.display = "none";
      cookieSettings.cookie("cookies_preferences_set", "true", { days: 365 });
      if (event.target) {
        event.preventDefault();
      }
    };
    this.setCookieConsent = function () {
      cookieSettings.setConsentCookie({"usage": true});
      that.showConfirmationMessage();
      cookieSettings.cookie("cookies_preferences_set", "true", { days: 365 });
      if (analytics) {
        analytics.start();
      }
      if (window.GOVUK.globalBarInit) {
        window.GOVUK.globalBarInit.init();
      }
    };
  }
  CookieBanner.prototype.init = function(cookieBannerOuterElement) {
    this.cookieBannerOuterElement = cookieBannerOuterElement;
    this.cookieBannerConfirmationMessage = this.cookieBannerOuterElement
      ? this.cookieBannerOuterElement.querySelector(".cookie-banner__confirmation")
      : undefined;
    if (this.cookieBannerOuterElement) {
      this.setupCookieMessage();
    }
  };
  CookieBanner.prototype.setupCookieMessage = function () {
    var hideLinks = this.cookieBannerOuterElement.querySelectorAll("button[data-hide-cookie-banner]");
    if (hideLinks && hideLinks.length) {
      for (var i = 0; i < hideLinks.length; i++) {
        hideLinks[i].addEventListener("click", this.hideCookieMessage);
      }
    }
    var acceptCookiesLink = this.cookieBannerOuterElement.querySelector("button[data-accept-cookies]");
    if (acceptCookiesLink) {
      acceptCookiesLink.addEventListener("click", this.setCookieConsent);
    }
    this.showCookieMessage();
  };
  CookieBanner.prototype.showCookieMessage = function () {
    // Show the cookie banner if not in the cookie settings page or in an iframe
    if (!this.isInCookiesPage() && !this.isInIframe()) {
      var shouldHaveCookieMessage = (this.cookieBannerOuterElement && cookieSettings.cookie("cookies_preferences_set") !== "true");
      if (shouldHaveCookieMessage) {
        this.cookieBannerOuterElement.style.display = "block"; // Set the default consent cookie if it isn't already present
        if (!cookieSettings.cookie("cookies_policy")) {
          cookieSettings.setDefaultConsentCookie();
        }
        cookieSettings.deleteUnconsentedCookies();
      } else {
        this.cookieBannerOuterElement.style.display = "none";
      }
    } else {
      this.cookieBannerOuterElement.style.display = "none";
    }
  };
  CookieBanner.prototype.showConfirmationMessage = function () {
    this.$cookieBannerMainContent = document.querySelector(".cookie-banner__wrapper");
    if (this.$cookieBannerMainContent) {
      this.$cookieBannerMainContent.style.display = "none";
    }
    if (this.cookieBannerConfirmationMessage) {
      this.cookieBannerConfirmationMessage.style.display = "block";
      this.cookieBannerConfirmationMessage.focus();
    }
  };
  CookieBanner.prototype.isInCookiesPage = function () {
    return window.location.pathname === "/cookies";
  };
  CookieBanner.prototype.isInIframe = function () {
    return window.parent && window.location !== window.parent.location;
  };

  modules.CookieBanner = new CookieBanner();
}(window.GOVUK.Modules, window.GOVUK.Analytics, window.GOVUK.CookieSettings));