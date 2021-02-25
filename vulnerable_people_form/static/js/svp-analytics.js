window.GOVUK = window.GOVUK || {};

(function (module, cookieSettings, stripPII) {
    "use strict";

    var pagesToTrackPaths = [
        "applying-on-own-behalf",
        "nhs-login",
        "do-you-have-someone-to-go-shopping-for-you",
        "priority-supermarket-deliveries",
        "medical-conditions",
        "basic-care-needs",
        "nhs-letter"
    ];

    function getQueryParam(param) {
        var query = window.location.search.substring(1);
        var params = query.split("&");

        for (var i = 0; i < params.length; i++) {
            var pair = params[i].split("=");
            if(pair[0].toLowerCase() == param){
                return pair[1] === undefined ? '' : decodeURIComponent(pair[1]);
            }
        }
        return "";
    };

    function trackPageValuesOnSubmit(pagesToTrack) {
        var submitButton = document.querySelector('button[type="Submit"]');
        submitButton.addEventListener('click', (event)=>{
            event.preventDefault();

            var form = document.getElementById("svp-form");
            var hasFormSubmitted = false;

            setTimeout(formSubmit, 1000);

            function formSubmit() {
                if (!hasFormSubmitted) {
                    hasFormSubmitted = true;
                    form.submit();
                }
            }

            if(pagesToTrack.indexOf(window.location.pathname.substring(1)) >= 0) {
                var radioButtonLabel = form.querySelector('input[type="radio"]:checked').labels[0].textContent.trim();
                ga("send", "event", "Page interaction", document.title, radioButtonLabel, {
                    hitCallback: function() {
                        formSubmit();
                    },
                });
            }
        });
    }

    function getLinkTrackingData(event){
        var gaData = {};

        if (event.currentTarget.className.indexOf("change-link") !== -1) {
            gaData.action = event.currentTarget.baseURI.indexOf("view-answers") !== -1 ?
                "change link - view answers NHS login user" :
                "change link - check your answers";
        } else {
            gaData.action = event.currentTarget.text;
        }

        gaData.category ="on-page links";
        gaData.link = event.currentTarget.href;

        return gaData;
    }

    function trackLinkClicks() {
        document.querySelectorAll("a").forEach((item) => {
            item.addEventListener("click", (event) => {
                if (event.currentTarget.tagName !== "A"){
                    return;
                }
                event.preventDefault();

                var redirectLocation = event.currentTarget.href;
                var hasRedirected = false;

                setTimeout(redirect, 1000);

                function redirect() {
                    if (!hasRedirected) {
                        hasRedirected = true;
                        document.location = redirectLocation;
                    }
                }

                var linkTrackingData = getLinkTrackingData(event);

                ga("send", "event", linkTrackingData.category, linkTrackingData.action, linkTrackingData.link, {
                    hitCallback: function() {
                        redirect();
                    },
                });
            });
        });
    }

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

                var laValue = getQueryParam('la');
                if (laValue) {
                    ga('send', 'pageview', { 'dimension3':  laValue});
                } else {
                    ga('send', 'pageview');
                }

                trackPageValuesOnSubmit(pagesToTrackPaths);
                trackLinkClicks();
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
