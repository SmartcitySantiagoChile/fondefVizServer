"use strict";
$(document).ready(function() {

  // load filters
  (function (){
    loadAvailableDays(Urls["esapi:availableStageDays"]());
    loadRangeCalendar(Urls["esapi:availableStageDays"](), {});

    let previousCall = function () {
      console.log("before");
    };
    let afterCall = function (data, status) {
      console.log("after");
    };

    let opts = {
      urlFilterData: Urls["esapi:stageTransfers"](),
      previousCallData: previousCall,
      afterCallData: afterCall
    };

    new FilterManager(opts);
  })();
});