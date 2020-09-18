window.GOVUK = window.GOVUK || {};

(function (module, cookieSettings, stripPII) {
    "use strict";
    function Analytics() {}
    Analytics.prototype.init = function(gaTrackingId, gaCrossDomainTrackingId) {
        this.gaTrackingId = gaTrackingId;
        this.gaCrossDomainTrackingId = gaCrossDomainTrackingId;
    };
    Analytics.prototype.start = function() {
        // Start analytics only if we have user consent
        var consentCookie = cookieSettings.getConsentCookie();
        if (consentCookie && consentCookie["usage"]) {
            (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
            (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
            m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
            })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

            if (this.gaTrackingId) {
                // /govuk-coronavirus-vulnerable-people-form Google Analytics
                ga('create', this.gaTrackingId, 'auto');
                ga('set', 'allowAdFeatures', false);
                ga('set', 'anonymizeIp', true);
                ga('set', 'location', stripPII(window.location));
                ga('send', 'pageview');
            }

            if (this.gaCrossDomainTrackingId) {
                // Cross Government Domain Google Analytics
                ga('create', this.gaCrossDomainTrackingId, 'auto', 'govuk_shared', {'allowLinker': true});
                ga('govuk_shared.require', 'linker');
                ga('govuk_shared.set', 'anonymizeIp', true);
                ga('govuk_shared.set', 'allowAdFeatures', false);
                ga('govuk_shared.linker:autoLink', ['www.gov.uk']);
                ga('govuk_shared.set', 'location', stripPII(window.location));
                ga('govuk_shared.send', 'pageview');
            }
        }
    };

    module.Analytics = new Analytics();

}(window.GOVUK, window.GOVUK.CookieSettings, window.GOVUK.stripPII));
