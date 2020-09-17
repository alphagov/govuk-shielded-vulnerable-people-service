window.GOVUK = window.GOVUK || {};
(function (module, analytics) {
    "use strict";
    var DEFAULT_COOKIE_CONSENT = {
        essential: true,
        settings: false,
        usage: false,
        campaigns: false
    };

    var COOKIE_CATEGORIES = {
        cookies_policy: 'essential',
        seen_cookie_message: 'essential',
        cookie_preferences_set: 'essential',
        cookies_preferences_set: 'essential',
        '_email-alert-frontend_session': 'essential',
        licensing_session: 'essential',
        govuk_contact_referrer: 'essential',
        multivariatetest_cohort_coronavirus_extremely_vulnerable_rate_limit: 'essential',
        dgu_beta_banner_dismissed: 'settings',
        global_bar_seen: 'settings',
        govuk_browser_upgrade_dismisssed: 'settings',
        govuk_not_first_visit: 'settings',
        analytics_next_page_call: 'usage',
        _ga: 'usage',
        _gid: 'usage',
        _gat: 'usage',
        'JS-Detection': 'usage',
        TLSversion: 'usage'
    };


    function CookieSettings() {
        var that = this;
        this.submitSettingsForm = function (event) {
            event.preventDefault();

            var formInputs = event.target.getElementsByTagName("input");
            var options = {};

            for (var i = 0; i < formInputs.length; i++) {
                var input = formInputs[i];
                if (input.checked) {
                    var name = input.name.replace('cookies-', '');
                    var value = input.value === "on";

                    options[name] = value;
                }
            }

            that.showConfirmationMessage();
            that.setConsentCookie(options);
            that.setCookie('cookies_preferences_set', true, {days: 365});
            if (analytics) {
                analytics.start();
            }

            return false;
        };
    }

    CookieSettings.prototype.cookie = function (name, value, options) {
        if (typeof value !== 'undefined') {
            if (value === false || value === null) {
                return this.setCookie(name, '', {days: -1});
            } else {
                // Default expiry date of 30 days
                if (typeof options === 'undefined') {
                    options = {days: 30};
                }
                return this.setCookie(name, value, options);
            }
        } else {
            return this.getCookie(name);
        }
    };

    CookieSettings.prototype.setDefaultConsentCookie = function () {
        this.setConsentCookie(DEFAULT_COOKIE_CONSENT);
    };

    CookieSettings.prototype.getConsentCookie = function () {
        var consentCookie = this.cookie('cookies_policy');
        var consentCookieObj = null;

        if (consentCookie) {
            try {
                consentCookieObj = JSON.parse(consentCookie);
            } catch (err) {
                return null;
            }

            if (typeof consentCookieObj !== 'object' && consentCookieObj !== null) {
                consentCookieObj = JSON.parse(consentCookieObj);
            }
        }

        return consentCookieObj;
    };

    CookieSettings.prototype.setConsentCookie = function (options) {
        var cookieConsent = this.getConsentCookie();

        if (!cookieConsent) {
            cookieConsent = JSON.parse(JSON.stringify(DEFAULT_COOKIE_CONSENT));
        }

        for (var cookieType in options) {
            cookieConsent[cookieType] = options[cookieType];

            // Delete cookies of that type if consent being set to false
            if (!options[cookieType]) {
                for (var cookie in COOKIE_CATEGORIES) {
                    if (COOKIE_CATEGORIES[cookie] === cookieType) {
                        this.deleteCookie(cookie);
                    }
                }
            }
        }

        this.setCookie('cookies_policy', JSON.stringify(cookieConsent), {days: 365});
    };

    CookieSettings.prototype.checkConsentCookieCategory = function (cookieName, cookieCategory) {
        var currentConsentCookie = this.getConsentCookie();

        // If the consent cookie doesn't exist, but the cookie is in our known list, return true
        if (!currentConsentCookie && COOKIE_CATEGORIES[cookieName]) {
            return true;
        }

        currentConsentCookie = this.getConsentCookie();

        // Sometimes currentConsentCookie is malformed in some of the tests, so we need to handle these
        try {
            return currentConsentCookie[cookieCategory];
        } catch (e) {
            console.error(e);
            return false;
        }
    };

    CookieSettings.prototype.checkConsentCookie = function (cookieName, cookieValue) {
        // If we're setting the consent cookie OR deleting a cookie, allow by default
        if (cookieName === 'cookies_policy' || (cookieValue === null || cookieValue === false)) {
            return true;
        }

        // Survey cookies are dynamically generated, so we need to check for these separately
        if (cookieName.match('^govuk_surveySeen') || cookieName.match('^govuk_taken')) {
            return this.checkConsentCookieCategory(cookieName, 'settings');
        }

        if (COOKIE_CATEGORIES[cookieName]) {
            var cookieCategory = COOKIE_CATEGORIES[cookieName];

            return this.checkConsentCookieCategory(cookieName, cookieCategory);
        } else {
            // Deny the cookie if it is not known to us
            return false;
        }
    };

    CookieSettings.prototype.setCookie = function (name, value, options) {
        if (this.checkConsentCookie(name, value)) {
            if (typeof options === 'undefined') {
                options = {};
            }
            var cookieString = name + '=' + value + '; path=/';
            if (options.days) {
                var date = new Date();
                date.setTime(date.getTime() + (options.days * 24 * 60 * 60 * 1000));
                cookieString = cookieString + '; expires=' + date.toGMTString();
            }
            if (document.location.protocol === 'https:') {
                cookieString = cookieString + '; Secure';
            }
            document.cookie = cookieString;
        }
    };

    CookieSettings.prototype.getCookie = function (name) {
        var nameEQ = name + '=';
        var cookies = document.cookie.split(';');
        for (var i = 0, len = cookies.length; i < len; i++) {
            var cookie = cookies[i];
            while (cookie.charAt(0) === ' ') {
                cookie = cookie.substring(1, cookie.length);
            }
            if (cookie.indexOf(nameEQ) === 0) {
                return decodeURIComponent(cookie.substring(nameEQ.length));
            }
        }
        return null;
    };

    CookieSettings.prototype.getCookieCategory = function (cookie) {
        return COOKIE_CATEGORIES[cookie];
    };

    CookieSettings.prototype.deleteCookie = function (cookie) {
        this.cookie(cookie, null);

        if (this.cookie(cookie)) {
            // We need to handle deleting cookies on the domain and the .domain
            document.cookie = cookie + '=;expires=' + new Date() + ';';
            document.cookie = cookie + '=;expires=' + new Date() + ';domain=' + window.location.hostname + ';path=/';
        }
    };

    CookieSettings.prototype.deleteUnconsentedCookies = function () {
        var currentConsent = this.getConsentCookie();

        for (var cookieType in currentConsent) {
            // Delete cookies of that type if consent being set to false
            if (!currentConsent[cookieType]) {
                for (var cookie in COOKIE_CATEGORIES) {
                    if (COOKIE_CATEGORIES[cookie] === cookieType) {
                        this.deleteCookie(cookie);
                    }
                }
            }
        }
    };
    CookieSettings.prototype.init = function () {
        var cookieForm = document.querySelector('form[data-module=cookie-settings]');
        if (cookieForm) {
            cookieForm.addEventListener("submit", this.submitSettingsForm);
            this.setInitialFormValues();
        }
    };
    CookieSettings.prototype.setInitialFormValues = function () {
        if (!this.cookie("cookies_policy")) {
            this.setDefaultConsentCookie();
        }

        var currentConsentCookie = this.cookie('cookies_policy');
        var currentConsentCookieJSON = JSON.parse(currentConsentCookie);

        // We don't need the essential value as this cannot be changed by the user
        delete currentConsentCookieJSON["essential"];
        // We don't need the campaigns/settings values as these aren't required by
        // the service.
        delete currentConsentCookieJSON["campaigns"];
        delete currentConsentCookieJSON["settings"];

        for (var cookieType in currentConsentCookieJSON) {
            var radioButton;
            if (currentConsentCookieJSON[cookieType]) {
                radioButton = document.querySelector('input[name=cookies-' + cookieType + '][value=on]');
            } else {
                radioButton = document.querySelector('input[name=cookies-' + cookieType + '][value=off]');
            }
            radioButton.checked = true;
        }
    };

    CookieSettings.prototype.showConfirmationMessage = function () {
        var confirmationMessage = document.querySelector('.cookie-settings__confirmation');
        document.body.scrollTop = document.documentElement.scrollTop = 0;
        confirmationMessage.style.display = "block";
    };

    module.CookieSettings = new CookieSettings();
}(window.GOVUK, window.GOVUK.Analytics));
