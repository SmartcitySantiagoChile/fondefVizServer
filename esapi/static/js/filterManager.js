"use strict";

/**
 * Filter manager to select data
 *
 * opts : dict with options. Options available:
 *        - urlDateFilter: url to get data used in charts
 *        - previousCall: function to take actions previous to ask for data
 *        - afterCall: function to take actions after data. It receives data as first argument
 * */
function FilterManager(opts) {

    /* OPTIONS */
    var previousCall = undefined;
    var afterCall = undefined;
    var urlFilterData = opts.urlFilterData;
    var urlRouteData = opts.urlRouteData;
    var singleDatePicker = opts.singleDatePicker || false;
    /* function that return additional params to send to server */
    var dataUrlParams = opts.dataUrlParams || function () {
        return {};
    };

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
    var $HOUR_RANGE_FILTER = $("#hourRangeFilter");
    var $BOARDING_PERIOD_FILTER = $("#boardingPeriodFilter");
    var $METRIC_FILTER = $("#metricFilter");

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
    $AUTH_ROUTE_FILTER.select2({placeholder: PLACEHOLDER_AUTH_ROUTE});
    $USER_ROUTE_FILTER.select2({placeholder: PLACEHOLDER_USER_ROUTE, allowClear: Boolean($AUTH_ROUTE_FILTER.length)});
    $BOARDING_PERIOD_FILTER.select2({placeholder: PLACEHOLDER_ALL});
    $METRIC_FILTER.select2({placeholder: PLACEHOLDER_ALL});

    if ($STOP_FILTER.length) {
        $STOP_FILTER.select2({
            ajax: {
                delay: 500, // milliseconds
                url: Urls["esapi:matchedStopData"](),
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
        var hourPeriodFrom = $HOUR_RANGE_FILTER.data("from");
        var hourPeriodTo = $HOUR_RANGE_FILTER.data("to");
        var userRoute = $USER_ROUTE_FILTER.val();
        var authRoute = $AUTH_ROUTE_FILTER.val();
        var stopCode = $STOP_FILTER.val();
        var operator = $OPERATOR_FILTER.val();
        var boardingPeriod = $BOARDING_PERIOD_FILTER.val();
        var metrics = $METRIC_FILTER.val();

        var params = dataUrlParams();
        params.startDate = $DAY_FILTER.data("daterangepicker").startDate.format();
        params.endDate = $DAY_FILTER.data("daterangepicker").endDate.format();

        if ($AUTH_ROUTE_FILTER.length && authRoute) {
            params.authRoute = authRoute;
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
        if ($STOP_FILTER.length && stopCode) {
            params.stopCode = stopCode;
        }
        if ($HOUR_RANGE_FILTER.length) {
            params.hourPeriodFrom = hourPeriodFrom;
            params.hourPeriodTo = hourPeriodTo - 1;
        }
        if (!$AUTH_ROUTE_FILTER.length && userRoute) {
            params.userRoute = userRoute;
        }
        if (operator) {
            params.operator = operator;
        }
        if (boardingPeriod) {
            params.boardingPeriod = boardingPeriod;
        }
        if (metrics) {
            params.metrics = metrics;
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
                if (data.status) {
                    showMessage(data.status);
                    return;
                }
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
    if ($OPERATOR_FILTER.length) {
        var processRouteData = function (data) {
            // console.log(data);
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
                var userRouteList = [];
                if (data.availableRoutes[operatorId] !== undefined) {
                    userRouteList = Object.keys(data.availableRoutes[operatorId]);
                }
                userRouteList.sort();
                userRouteList = userRouteList.map(function (el) {
                    return {id: el, text: el};
                });
                $USER_ROUTE_FILTER.empty();
                if ($AUTH_ROUTE_FILTER.length) {
                    $USER_ROUTE_FILTER.select2({data: userRouteList});
                    // call event to update auth route filter
                    var selectedItem = $USER_ROUTE_FILTER.select2("data")[0];
                    $USER_ROUTE_FILTER.trigger({type: "select2:select", params: {data: selectedItem}});
                } else {
                    $USER_ROUTE_FILTER.select2({data: userRouteList, allowClear: true, placeholder: PLACEHOLDER_ALL});
                }
            };
            $USER_ROUTE_FILTER.on("select2:select", function (e) {
                var selectedItem = e.params.data;
                var operatorId = $OPERATOR_FILTER.length ? $OPERATOR_FILTER.select2("data")[0].id : Object.keys(data.availableRoutes)[0];
                if ($AUTH_ROUTE_FILTER.length) {
                    updateAuthRouteList(operatorId, selectedItem.id);
                }
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
            if (data.status) {
                showMessage(data.status);
            } else {
                processRouteData(data);
            }
        });
    }

    if ($HOUR_RANGE_FILTER.length) {
        var periods = [
            "00:00", "00:30", "01:00", "01:30", "02:00", "02:30", "03:00", "03:30", "04:00", "04:30", "05:00", "05:30",
            "06:00", "06:30", "07:00", "07:30", "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
            "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30",
            "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00", "21:30", "22:00", "22:30", "23:00", "23:30",
            "00:00"
        ];
        $HOUR_RANGE_FILTER.ionRangeSlider({
            type: "double",
            from: 0,
            to: 48,
            grid: true,
            values: periods
        });
    }

    /**
     * trigger click event over update button
     * */
    this.updateData = function (opts) {
        // update params to send to server
        if (opts !== undefined) {
            dataUrlParams = opts.dataUrlParams || {};
        }
        $BTN_UPDATE_DATA.trigger("click");
    };
}