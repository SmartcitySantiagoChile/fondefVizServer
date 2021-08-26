"use strict";
$(document).ready(function() {

  // load filters
  (function (){
    loadAvailableDays(Urls["esapi:availableTripDays"]());
    loadRangeCalendar(Urls["esapi:availableTripDays"](), {});

    let previousCall = function () {
      console.log("before");
    };
    let afterCall = function (data, status) {
      console.log("after");
    };

    let opts = {
      urlFilterData: Urls["esapi:postProductTripsBetweenZones"](),
      previousCallData: previousCall,
      afterCallData: afterCall
    };

    new FilterManager(opts);
  })();
});