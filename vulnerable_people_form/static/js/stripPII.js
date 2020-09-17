window.GOVUK = window.GOVUK || {};

(function (module) {
    "use strict";

    function stripPII(url) {
        function _splitAndRedact(url) {
            var queryString = url.search
                .replace(/^\?/, '')
                .split('&');
            var redactedArray = [];

            for (var i = 0; i < queryString.length; i++) {
                if (queryString[i] !== '') {
                    var paramToRedact = queryString[i].split('=');

                    redactedArray.push(
                        paramToRedact[0] +
                        '=<'+
                        paramToRedact[0].toUpperCase() +
                        '>'
                    );
                }
            }

            return redactedArray.length > 0 ? '?' + redactedArray.join('&') : '';
        }

        try {
            return url.protocol +
                '//' +
                url.host +
                url.pathname +
                _splitAndRedact(url) +
                url.hash;
        } catch (error) {
            console.error(error);
            return '';
        }
    }

    module.stripPII = stripPII;

}(window.GOVUK));
