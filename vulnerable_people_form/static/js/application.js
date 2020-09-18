(function (w) {
    "use strict";
    function appInit(gaTrackingId, gaCrossDomainTrackingId) {
        if (w.GOVUKFrontend) {
            w.GOVUKFrontend.initAll();
        }

        w.GOVUK.CookieSettings.init();

        w.GOVUK.Analytics.init(gaTrackingId, gaCrossDomainTrackingId);
        w.GOVUK.Analytics.start();

        w.GOVUK.Modules.CookieBanner.init(document.querySelector('[data-module="cookie-banner"]'));
    }
    w.appInit = appInit;
}(window));
