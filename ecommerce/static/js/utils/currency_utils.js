define(['jquery'],
    function($) {
        'use strict';

        // get currency name
        return {
            getCurrency: function() {
                var currency = 'USD';

                $.ajax({
                    type: 'GET',
                    url: '/api/v2/currency',
                    contentType: 'application/json',
                    async: false,
                    success: function(data) {
                        currency = data.currency;
                    }
                });
                return currency;
            }
        };
    }
);
