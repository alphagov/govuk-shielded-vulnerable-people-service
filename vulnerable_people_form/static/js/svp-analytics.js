window.GOVUK = window.GOVUK || {};

(function (module, cookieSettings, stripPII) {
    "use strict";

    function getQueryParam(param) {
        var query = window.location.search.substring(1);
        var params = query.split("&");

        for (var i = 0; i < params.length; i++) {
            var pair = params[i].split("=");
            if(pair[0].toLowerCase() == param){
                return pair[1] === undefined ? '' : decodeURIComponent(pair[1]);
            }
        }
        return '';
    };

    function gaSendEvent(eventCategory, eventLabel, eventAction) {
        ga('send', {
            hitType: 'event',
            eventCategory: eventCategory,
            eventAction: eventAction,
            eventLabel: eventLabel
        });
    }

    function trackRadioItemsAnswers(inputSelector,eventCategory, eventLabel) {
        document.querySelectorAll(inputSelector).forEach(item => {
          item.addEventListener('click', event => {
            var action = event.target.value === "1" ? "Yes" : "No";
            gaSendEvent(eventCategory, eventLabel, action);
          })
        })
    }

    function trackChangeAnswerLinks(inputSelector,eventCategory) {
        document.querySelectorAll(inputSelector).forEach(item => {
          item.addEventListener('click', event => {
            var changeLinkAction = event.target.baseURI.indexOf('view-answers')  !== -1 ? 'change link - view answers NHS login user' : 'change link - check your answers';
            gaSendEvent(eventCategory, event.target.href, changeLinkAction);
          })
        })
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

                trackRadioItemsAnswers('input[name="do_you_have_someone_to_go_shopping_for_you"]', 'page interaction', window.location);
                trackChangeAnswerLinks('.change-link', 'on-page links');
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
