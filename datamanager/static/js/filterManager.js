"use strict";

/**
 * Filter manager to select data
 *
 * opts : dict with options. Options available:
 *        - urlDateFilter: url to get data used in charts
 *        - previousCall: function to take actions previous to ask for data
 *        - afterCall: function to take actions after data. It receives data as first argument
 * */
function filterManager(opts) {

    /* OPTIONS */

    var previousCall = undefined;
    var afterCall = undefined;
    var urlFilterData = opts.urlFilterData;
    var urlRouteData = opts.urlRouteData;
    var singleDatePicker = opts.singleDatePicker || false;

    if (opts.hasOwnProperty("previousCallData")) {
        previousCall = opts.previousCallData;
    }
    if (opts.hasOwnProperty("afterCallData")) {
        afterCall = opts.afterCallData;
    }

    /* VARIABLE DEFINITIONS */

    var $DAY_FILTER = $("#dayFilter");
    var $STOP_FILTER = $("#stopFilter");
    var $DAY_TYPE_FILTER = $("#dayTypeFilter");
    var $PERIOD_FILTER = $("#periodFilter");
    var $MINUTE_PERIOD_FILTER = $("#minutePeriodFilter");
    var $OPERATOR_FILTER = $("#operatorFilter");
    var $USER_ROUTE_FILTER = $("#userRouteFilter");
    var $AUTH_ROUTE_FILTER = $("#authRouteFilter");

    var $BTN_UPDATE_DATA = $("#btnUpdateData");

    /* LABELS */

    var PLACEHOLDER_ALL = "Todos";
    var PLACEHOLDER_USER_ROUTE = "Servicio usuario";
    var PLACEHOLDER_AUTH_ROUTE = "Servicio transantiago";

    /* ENABLE select2 library */

    optionDateRangePicker.singleDatePicker = singleDatePicker;
    $DAY_FILTER.daterangepicker(optionDateRangePicker);
    $DAY_TYPE_FILTER.select2({placeholder: PLACEHOLDER_ALL});
    $PERIOD_FILTER.select2({placeholder: PLACEHOLDER_ALL});
    $MINUTE_PERIOD_FILTER.select2({placeholder: PLACEHOLDER_ALL});
    $OPERATOR_FILTER.select2();
    $USER_ROUTE_FILTER.select2({placeholder: PLACEHOLDER_USER_ROUTE});
    $AUTH_ROUTE_FILTER.select2({placeholder: PLACEHOLDER_AUTH_ROUTE});

    if ($STOP_FILTER.length) {
        $STOP_FILTER.select2({
            ajax: {
                delay: 500, // milliseconds
                url: Urls["profile:getStopList"](),
                dataType: "json",
                data: function (params) {
                    return {
                        term: params.term
                    }
                },
                processResults: function (data, params) {
                    return {
                        results: data.items
                    }
                },
                cache: true
            },
            minimumInputLength: 3,
            language: {
                inputTooShort: function () {
                    return "Ingresar 3 o más caracteres";
                }
            }
        });
    }

    /* BUTTON ACTION */

    var _makeAjaxCall = true;
    $BTN_UPDATE_DATA.click(function () {
        var dayType = $DAY_TYPE_FILTER.val();
        var period = $PERIOD_FILTER.val();
        var minutes = $MINUTE_PERIOD_FILTER.val();

        var params = {
            startDate: $DAY_FILTER.data("daterangepicker").startDate.format(),
            endDate: $DAY_FILTER.data("daterangepicker").endDate.format()
        };
        if ($AUTH_ROUTE_FILTER.length && $AUTH_ROUTE_FILTER.val()) {
            params.authRoute = $AUTH_ROUTE_FILTER.val();
        }
        if (dayType) {
            params.dayType = dayType;
        }
        if (period) {
            params.period = period;
        }
        if (minutes) {
            params.halfHour = minutes;
        }
        if ($STOP_FILTER.length && $STOP_FILTER.val()) {
            params.stopCode = $STOP_FILTER.val()
        }

        if (_makeAjaxCall) {
            _makeAjaxCall = false;
            var loadingIcon = " " + $("<i>").addClass("fa fa-cog fa-spin fa-2x fa-fw")[0].outerHTML;
            var previousMessage = $(this).html();
            var button = $(this).append(loadingIcon);

            // actions defined by user
            if (previousCall) {
                previousCall();
            }

            $.getJSON(urlFilterData, params, function (data) {
                if (afterCall) {
                    afterCall(data);
                }
            }).always(function () {
                _makeAjaxCall = true;
                button.html(previousMessage);
            });
        }
    });

    /* LOGIC TO MANAGE OPERATOR, USER ROUTE AND AUTHORITY ROUTE */
    if ($AUTH_ROUTE_FILTER.length) {
        var processRouteData = function (data) {
            var updateAuthRouteList = function (operatorId, userRouteId) {
                var authRouteList = data.availableRoutes[operatorId][userRouteId];
                authRouteList.sort();
                authRouteList = authRouteList.map(function (el) {
                    return {id: el, text: el};
                });
                $AUTH_ROUTE_FILTER.empty();
                $AUTH_ROUTE_FILTER.select2({data: authRouteList});
            };
            var updateUserRouteList = function (operatorId) {
                var userRouteList = Object.keys(data.availableRoutes[operatorId]);
                userRouteList.sort();
                userRouteList = userRouteList.map(function (el) {
                    return {id: el, text: el};
                });
                $USER_ROUTE_FILTER.empty();
                $USER_ROUTE_FILTER.select2({data: userRouteList});
                // call event to update auth route filter
                var selectedItem = $USER_ROUTE_FILTER.select2("data")[0];
                $USER_ROUTE_FILTER.trigger({type: "select2:select", params: {data: selectedItem}});
            };
            $USER_ROUTE_FILTER.on("select2:select", function (e) {
                var selectedItem = e.params.data;
                var operatorId = $OPERATOR_FILTER.length ? $OPERATOR_FILTER.select2("data")[0].id : Object.keys(data.availableRoutes)[0];
                updateAuthRouteList(operatorId, selectedItem.id);
            });
            // if operator filter is visible
            if ($OPERATOR_FILTER.length) {
                $OPERATOR_FILTER.select2({data: data.operatorDict});
                $OPERATOR_FILTER.on("select2:select", function (e) {
                    var selectedItem = e.params.data;
                    // update user route filter and auth route filter
                    updateUserRouteList(selectedItem.id);
                });
                // call event to update user route filter
                var selectedItem = $OPERATOR_FILTER.select2("data")[0];
                $OPERATOR_FILTER.trigger({type: "select2:select", params: {data: selectedItem}});
            } else {
                var operatorId = Object.keys(data.availableRoutes)[0];
                updateUserRouteList(operatorId)
            }
        };
        $.getJSON(urlRouteData, function (data) {
            processRouteData(data);
        });
    }
}