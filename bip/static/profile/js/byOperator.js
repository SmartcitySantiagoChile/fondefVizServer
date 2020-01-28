"use strict";
$(document).ready(function () {



    // load filters
    (function () {
        loadAvailableDays(Urls["esapi:availableBipDays"]());
        loadRangeCalendar(Urls["esapi:availableBipDays"](), {});

        var previousCall = function () {
        };
        var afterCall = function (data) {
            console.log(data);
         //   processData(data, app);
          //  app.hideLoadingAnimationCharts();
        };
        var opts = {
            urlFilterData: Urls["esapi:operatorData"](),
            urlRouteData: Urls["esapi:availableProfileRoutes"](),
            previousCallData: previousCall,
            afterCallData: afterCall
        };

        new FilterManager(opts);

        $(window).resize(function () {
        });
        $("#menu_toggle").click(function () {
        });
    })()
});