define(['jquery'],
    function ($) {
        'use strict';

        // get currency name
        return {
            getCurrency: function () {
                var currency = 'USD';

                $.ajax({
                    type: 'GET',
                    url: window.location.origin + '/api/v2/currency',
                    contentType: 'application/json',
                    async: false,
                    success: function(data) {
                        currency = data.currency;
                    }
                    // error: function() {
                    //     content.currency = 'USD';
                    // }
                });
                console.log('get_currency');
                console.log(currency);
                return currency;
            }
        };
    }
);
