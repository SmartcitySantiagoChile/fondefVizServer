"use strict";
$(document).ready(function () {
    function TransferApp() {
        var _self = this;
        var tableId = "barChart";

        this.getTableOpts = function () {

        };

        this.updateTable = function (xData, yData, values, stopInfo) {

        };
    }

    function processData(dataSource, app) {
        console.log(dataSource);

        if (dataSource.status) {
            return;
        }

        app.updateTable(xAxis, yAxis, data, stopInfo);
    }

    // load filters
    (function () {
        loadAvailableDays(Urls["esapi:availableTripDays"]());

        var app = new TransferApp();
        var afterCall = function (data) {
            processData(data, app);
        };
        var opts = {
            urlFilterData: Urls["esapi:transfersData"](),
            afterCallData: afterCall
        };
        new FilterManager(opts);
    })();
});