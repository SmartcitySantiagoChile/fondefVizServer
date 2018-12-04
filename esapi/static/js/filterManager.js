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
    /* function executed before server returns data */
    var previousCall = undefined;
    /* function executed after server returns data */
    var afterCall = undefined;
    /* url where filter manager asks for data */
    var urlFilterData = opts.urlFilterData;
    /* url where filter manager asks for route data (operator, user route code and authority route code) */
    var urlRouteData = opts.urlRouteData;
    /* let user select just one day */
    var singleDatePicker = opts.singleDatePicker || false;
    /* minimum day window that user has to select */
    var minimumDateLimit = opts.minimumDateLimit || undefined;
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
    var $BTN_EXPORT_DATA = $("#btnExportData");

    /* LABELS */

    var PLACEHOLDER_ALL = "Todos";
    var PLACEHOLDER_USER_ROUTE = "Servicio usuario";
    var PLACEHOLDER_AUTH_ROUTE = "Servicio transantiago";

    /* RETRIEVE DEFAULT VALUES */
    optionDateRangePicker.singleDatePicker = singleDatePicker;
    var localStartDate = window.localStorage.getItem("startDate");
    var localEndDate = window.localStorage.getItem("endDate");
    if (localStartDate !== null) {
        optionDateRangePicker.startDate = moment(localStartDate);
    }
    if (localEndDate !== null) {
        optionDateRangePicker.endDate = moment(localEndDate);
    }

    /* ENABLE select2 library */

    $DAY_FILTER.daterangepicker(optionDateRangePicker);
    $DAY_TYPE_FILTER.select2({placeholder: PLACEHOLDER_ALL});
    $PERIOD_FILTER.select2({placeholder: PLACEHOLDER_ALL});
    $MINUTE_PERIOD_FILTER.select2({placeholder: PLACEHOLDER_ALL});
    $OPERATOR_FILTER.select2();
    $AUTH_ROUTE_FILTER.select2({placeholder: PLACEHOLDER_AUTH_ROUTE});
    $USER_ROUTE_FILTER.select2({placeholder: PLACEHOLDER_USER_ROUTE, allowClear: Boolean($AUTH_ROUTE_FILTER.length)});
    $BOARDING_PERIOD_FILTER.select2({placeholder: PLACEHOLDER_ALL});
    $METRIC_FILTER.select2({placeholder: PLACEHOLDER_ALL});

    /* SET DEFAULT VALUES FOR SELECT INPUTS */
    var localDayTypeFilter = window.localStorage.getItem("dayTypeFilter");
    if (localDayTypeFilter !== null) {
        localDayTypeFilter = JSON.parse(localDayTypeFilter);
        $DAY_TYPE_FILTER.val(localDayTypeFilter);
        $DAY_TYPE_FILTER.trigger("change");
    }
    var localPeriodFilter = window.localStorage.getItem("periodFilter");
    if (localPeriodFilter !== null) {
        localPeriodFilter = JSON.parse(localPeriodFilter);
        $PERIOD_FILTER.val(localPeriodFilter);
        $PERIOD_FILTER.trigger("change");
    }
    var localMinutePeriodFilter = window.localStorage.getItem("minutePeriodFilter");
    if (localMinutePeriodFilter !== null) {
        localMinutePeriodFilter = JSON.parse(localMinutePeriodFilter);
        $MINUTE_PERIOD_FILTER.val(localMinutePeriodFilter);
        $MINUTE_PERIOD_FILTER.trigger("change");
    }
    var localBoardingPeriodFilter = window.localStorage.getItem("boardingPeriodFilter");
    if (localBoardingPeriodFilter !== null) {
        $BOARDING_PERIOD_FILTER.val(localBoardingPeriodFilter);
        $BOARDING_PERIOD_FILTER.trigger("change");
    }
    var localMetricFilter = window.localStorage.getItem("metricFilter");
    if (localMetricFilter !== null) {
        $METRIC_FILTER.val(localMetricFilter);
        $METRIC_FILTER.trigger("change");
    }

    /* ACTIVATE UPDATE OF DEFAULT VALUES */
    $DAY_FILTER.change(function (e) {
        window.localStorage.setItem("startDate", $DAY_FILTER.data("daterangepicker").startDate.format());
        window.localStorage.setItem("endDate", $DAY_FILTER.data("daterangepicker").endDate.format());
    });
    $DAY_TYPE_FILTER.change(function () {
        window.localStorage.setItem("dayTypeFilter", JSON.stringify($DAY_TYPE_FILTER.val()));
    });
    $PERIOD_FILTER.change(function () {
        window.localStorage.setItem("periodFilter", JSON.stringify($PERIOD_FILTER.val()));
    });
    $MINUTE_PERIOD_FILTER.change(function () {
        window.localStorage.setItem("minutePeriodFilter", JSON.stringify($MINUTE_PERIOD_FILTER.val()));
    });
    $BOARDING_PERIOD_FILTER.change(function () {
        window.localStorage.setItem("BoardingPeriodFilter", $BOARDING_PERIOD_FILTER.val());
    });
    $METRIC_FILTER.change(function () {
        window.localStorage.setItem("metricFilter", $METRIC_FILTER.val());
    });

    /* It saves last parameters sent to server */
    var paramsBackup = {};

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
        var localStopFilter = window.localStorage.getItem("stopFilter");
        $STOP_FILTER.val(localStopFilter);
        $STOP_FILTER.trigger("change");
        $STOP_FILTER.change(function () {
            window.localStorage.setItem("stopFilter", $STOP_FILTER.val());
        });
    }

    /* BUTTON ACTION */
    var getParameters = function () {
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

        // check diff days
        if (minimumDateLimit !== undefined && !singleDatePicker) {
            var diffDays = function (startDate, endDate) {
                startDate = new Date(startDate);
                endDate = new Date(endDate);
                var diff = new Date(endDate - startDate);
                var daysWindow = diff / 1000 / 60 / 60 / 24;
                return parseInt(daysWindow);
            };

            if (diffDays(params.startDate, params.endDate) < minimumDateLimit) {
                var status = {
                    message: "La período consultado debe ser mayor a 2 días",
                    title: "Advertencia",
                    type: "warning"
                };
                showMessage(status);
                return;
            }
        }

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

        return params;
    };

    var _makeAjaxCallForUpdateButton = true;
    $BTN_UPDATE_DATA.click(function () {
        if (_makeAjaxCallForUpdateButton) {
            _makeAjaxCallForUpdateButton = false;
            var loadingIcon = " " + $("<i>").addClass("fa fa-cog fa-spin fa-2x fa-fw")[0].outerHTML;
            var previousMessage = $(this).html();
            var button = $(this).append(loadingIcon);

            // actions defined by user
            if (previousCall) {
                previousCall();
            }

            var params = getParameters();
            $.getJSON(urlFilterData, params, function (data) {
                if (data.status) {
                    if (Array.isArray(data.status)) {
                        data.status.forEach(function (message) {
                            showMessage(message);
                        })
                    } else {
                        showMessage(data.status);
                    }
                }
                if (afterCall) {
                    afterCall(data);
                }
                // update backup to the last request params sent to server
                paramsBackup = params;
            }).always(function () {
                _makeAjaxCallForUpdateButton = true;
                button.html(previousMessage);
            });
        }
    });

    // enable modal to export data
    var _makeAjaxCallForExportButton = true;
    var $EXPORT_DATA_MODAL = $("#exportDataModal");
    $EXPORT_DATA_MODAL.on('show.bs.modal', function () {
        // accept event
        $EXPORT_DATA_MODAL.on("click", "button.btn-info", function () {
            if (_makeAjaxCallForExportButton) {
                _makeAjaxCallForExportButton = false;
                var loadingIcon = " " + $("<i>").addClass("fa fa-cog fa-spin fa-2x fa-fw")[0].outerHTML;
                var previousMessage = $BTN_EXPORT_DATA.html();
                var button = $BTN_EXPORT_DATA.append(loadingIcon);

                var params = getParameters();
                $.post(urlFilterData, params, function (data) {
                    if (data.status) {
                        showMessage(data.status);
                    }
                }).always(function () {
                    _makeAjaxCallForExportButton = true;
                    button.html(previousMessage);
                });
            }
        });
    });
    $BTN_EXPORT_DATA.click(function () {
        $EXPORT_DATA_MODAL.modal("show");
    });

    /* LOGIC TO MANAGE OPERATOR, USER ROUTE AND AUTHORITY ROUTE */
    if ($OPERATOR_FILTER.length) {
        var localOperatorFilter = window.localStorage.getItem("operatorFilter");
        if (localOperatorFilter) {
            localOperatorFilter = JSON.parse(localOperatorFilter);
        }
        var localUserRouteFilter = window.localStorage.getItem("userRouteFilter");
        if (localUserRouteFilter) {
            localUserRouteFilter = JSON.parse(localUserRouteFilter);
        }
        var localAuthRouteFilter = window.localStorage.getItem("authRouteFilter");
        if (localAuthRouteFilter) {
            localAuthRouteFilter = JSON.parse(localAuthRouteFilter);
        }

        var processRouteData = function (data) {
            data.operatorDict = data.operatorDict.map(function (el) {
                return {
                    id: el.value,
                    text: el.item
                }
            });
            var updateAuthRouteList = function (operatorId, userRouteId) {
                var authRouteList = data.availableRoutes[operatorId][userRouteId];
                authRouteList.sort();
                authRouteList = authRouteList.map(function (el) {
                    return {id: el, text: el};
                });
                $AUTH_ROUTE_FILTER.empty();
                $AUTH_ROUTE_FILTER.select2({data: authRouteList});
            };
            var updateUserRouteList = function (operatorId, isFirstTime) {
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
                } else {
                    $USER_ROUTE_FILTER.select2({data: userRouteList, allowClear: true, placeholder: PLACEHOLDER_ALL});
                }
                // call event to update auth route filter
                var selectedItem = isFirstTime && localUserRouteFilter !== null ? localUserRouteFilter : $USER_ROUTE_FILTER.select2("data")[0];
                $USER_ROUTE_FILTER.trigger({
                    type: "select2:select",
                    params: {data: selectedItem, isFirstTime: isFirstTime}
                });
            };
            $USER_ROUTE_FILTER.on("select2:select", function (e) {
                var selectedItem = e.params.data;
                var operatorId = $OPERATOR_FILTER.length ? $OPERATOR_FILTER.select2("data")[0].id : Object.keys(data.availableRoutes)[0];
                if (e.params.isFirstTime && localOperatorFilter !== null) {
                    operatorId = localOperatorFilter.id;
                }

                if ($AUTH_ROUTE_FILTER.length) {
                    updateAuthRouteList(operatorId, selectedItem.id);
                }

                if (!e.params.isFirstTime) {
                    window.localStorage.setItem("userRouteFilter", JSON.stringify({id: $USER_ROUTE_FILTER.val()}));
                    window.localStorage.setItem("authRouteFilter", JSON.stringify({id: $AUTH_ROUTE_FILTER.val()}));
                }
            });
            // if operator filter is visible
            if ($OPERATOR_FILTER.length) {
                $OPERATOR_FILTER.select2({data: data.operatorDict});
                $OPERATOR_FILTER.on("select2:select", function (e) {
                    var selectedItem = e.params.data;
                    updateUserRouteList(selectedItem.id, e.params.isFirstTime);

                    if (!e.params.isFirstTime) {
                        window.localStorage.setItem("operatorFilter", JSON.stringify({id: $OPERATOR_FILTER.val()}));
                        window.localStorage.setItem("userRouteFilter", JSON.stringify({id: $USER_ROUTE_FILTER.val()}));
                        window.localStorage.setItem("authRouteFilter", JSON.stringify({id: $AUTH_ROUTE_FILTER.val()}));
                    }
                });
                // call event to update user route filter
                var selectedItem = localOperatorFilter !== null ? localOperatorFilter : $OPERATOR_FILTER.select2("data")[0];
                $OPERATOR_FILTER.trigger({type: "select2:select", params: {data: selectedItem, isFirstTime: true}});
            } else {
                var operatorId = Object.keys(data.availableRoutes)[0];
                updateUserRouteList(operatorId, true);
            }

            $AUTH_ROUTE_FILTER.on("select2:select", function (e) {
                var selectedItem = e.params.data;
                window.localStorage.setItem("authRouteFilter", JSON.stringify({id: selectedItem.id}));
            });

            // ignore if local settings are nulls
            if (localOperatorFilter) {
                //$OPERATOR_FILTER.trigger({type: "select2:select", params: {data: {id: localOperatorFilter}}});
                //$USER_ROUTE_FILTER.trigger({type: "select2:select", params: {data: {id: localUserRouteFilter}}});
                $AUTH_ROUTE_FILTER.trigger({type: "select2:select", params: {data: {id: localAuthRouteFilter}}});
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