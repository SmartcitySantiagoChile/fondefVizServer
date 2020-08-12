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
    /* url where filter manager asks for multiple route data */
    var urlMultiRouteData = opts.urlMultiRouteData;

    if (opts.hasOwnProperty("previousCallData")) {
        previousCall = opts.previousCallData;
    }
    if (opts.hasOwnProperty("afterCallData")) {
        afterCall = opts.afterCallData;
    }

    /* VARIABLE DEFINITIONS */

    var $DAY_FILTER = $("#dayFilter");
    var $DATE_RANGE_MODAL = $("#dateRangeModal");
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
    var $MULTI_STOP_FILTER = $("#multiStopFilter");
    var $MULTI_AUTH_ROUTE_FILTER = $("#multiAuthRouteFilter");

    var $BTN_UPDATE_DATA = $("#btnUpdateData");
    var $BTN_EXPORT_DATA = $("#btnExportData");

    /* LABELS */

    var PLACEHOLDER_ALL = "Todos";
    var PLACEHOLDER_USER_ROUTE = "Servicio usuario";
    var PLACEHOLDER_AUTH_ROUTE = "Servicio transantiago";


    /* ENABLE select2 library */

    $DAY_TYPE_FILTER.select2({placeholder: PLACEHOLDER_ALL});
    $PERIOD_FILTER.select2({placeholder: PLACEHOLDER_ALL});
    $MINUTE_PERIOD_FILTER.select2({placeholder: PLACEHOLDER_ALL});
    $OPERATOR_FILTER.select2();
    $AUTH_ROUTE_FILTER.select2({placeholder: PLACEHOLDER_AUTH_ROUTE});
    $USER_ROUTE_FILTER.select2({placeholder: PLACEHOLDER_USER_ROUTE, allowClear: Boolean($AUTH_ROUTE_FILTER.length)});
    $BOARDING_PERIOD_FILTER.select2({placeholder: PLACEHOLDER_ALL});
    $METRIC_FILTER.select2({placeholder: PLACEHOLDER_ALL});
    $MULTI_AUTH_ROUTE_FILTER.select2({placeholder: PLACEHOLDER_AUTH_ROUTE});
    let urlKey = window.location.pathname;


    /* SET DEFAULT VALUES FOR SELECT INPUTS */
    var localDayFilter = window.localStorage.getItem(urlKey + "dayFilter");
    if (localDayFilter !== null) {
        localDayFilter = JSON.parse(localDayFilter);
    }
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

    if (singleDatePicker) {
        $DAY_FILTER.parent().text("Día:").append($DAY_FILTER);
    }


    $DAY_FILTER.click(function (e) {
        $DATE_RANGE_MODAL.modal('show');
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

    /* GET DATES */
    const getDates = function () {
        let dates = JSON.parse(window.localStorage.getItem(urlKey + "dayFilter")).sort();
        dates = groupByDates(dates);
        dates = dates.map(function (date_range) {
            if (date_range.length === 1) {
                return [date_range[0][0]]
            } else {
                return [date_range[0][0], date_range[date_range.length - 1][0]];
            }
        });
        return dates
    };


    const updateTimePeriod = function (data) {
        $.map(data['timePeriod'], function (obj) {
            obj.id = obj.id || obj.value;
            obj.text = obj.text || obj.item;
        });
        $PERIOD_FILTER.select2({placeholder: PLACEHOLDER_ALL, "data": data['timePeriod']})
    };


    $DAY_FILTER.change(function () {
        let dates = getDates();
        dates = [dates[0][0], dates[dates.length - 1].pop()];
        $.ajax(Urls["localinfo:timePeriod"](), {
            method: "GET",
            data: {"dates": dates},
            success: function (e) {
                updateTimePeriod(e);
            },
            error: function (e) {
                console.log(e);
                let status = {
                    message: e.responseJSON.error,
                    title: "Error",
                    type: "error"
                };
                showMessage(status);
            },
        });
    });


    $DAY_FILTER.trigger("change");

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
    }
    let localStopFilterVal = window.localStorage.getItem(urlKey + "stopFilter/val") || "";
    let localStopFilterText = window.localStorage.getItem(urlKey + "stopFilter/text") || "";

    let option = new Option(localStopFilterText, localStopFilterVal, false, false);
    $STOP_FILTER.append(option);
    $STOP_FILTER.trigger("change");
    $STOP_FILTER.change(function () {
        window.localStorage.setItem(urlKey + "stopFilter/val", $STOP_FILTER.val());
        window.localStorage.setItem(urlKey + "stopFilter/text", $STOP_FILTER[0].selectedOptions[0].text);
    });


    if ($MULTI_STOP_FILTER.length) {
        $MULTI_STOP_FILTER.select2({
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
    let localMultiStopFilterVal = JSON.parse(window.localStorage.getItem(urlKey + "multiStopFilter/val")) || "";
    let localMultiStopFilterText = JSON.parse(window.localStorage.getItem(urlKey + "multiStopFilter/text")) || "";
    for (let i = 0; i < localMultiStopFilterText.length; i++) {
        let multi_option = new Option(localMultiStopFilterText[i], localMultiStopFilterVal[i], false, true);
        $MULTI_STOP_FILTER.append(multi_option);
        $MULTI_STOP_FILTER.trigger("change");
    }

    $MULTI_STOP_FILTER.change(function () {
        window.localStorage.setItem(urlKey + "multiStopFilter/val", JSON.stringify($MULTI_STOP_FILTER.val()));
        let textOptions = [...$MULTI_STOP_FILTER[0].selectedOptions].map(e => e.innerText);
        window.localStorage.setItem(urlKey + "multiStopFilter/text", JSON.stringify(textOptions));
    });




    /* BUTTON ACTION */
    var getParameters = function () {

        var dates = getDates();
        var dayType = $DAY_TYPE_FILTER.val();
        var period = $PERIOD_FILTER.val();
        var minutes = $MINUTE_PERIOD_FILTER.val();
        var hourPeriodFrom = $HOUR_RANGE_FILTER.data("from");
        var hourPeriodTo = $HOUR_RANGE_FILTER.data("to");
        var userRoute = $USER_ROUTE_FILTER.val();
        var authRoute = $AUTH_ROUTE_FILTER.val();
        var authRoutes = $MULTI_AUTH_ROUTE_FILTER.val();
        var stopCode = $STOP_FILTER.val();
        var stopCodes = $MULTI_STOP_FILTER.val();
        var operator = $OPERATOR_FILTER.val();
        var boardingPeriod = $BOARDING_PERIOD_FILTER.val();
        var metrics = $METRIC_FILTER.val();
        var params = dataUrlParams();
        if (dates) {
            params.dates = JSON.stringify(dates);
        }

        let datesSize = function () {
            let count = 0;
            for (let i in dates) {
                for (let j in dates[i]) {
                    count++;
                }
            }
            return count;
        };

        // check diff days
        if (minimumDateLimit !== undefined && !singleDatePicker) {

            if (datesSize() < minimumDateLimit) {
                let status = {
                    message: "El período consultado debe ser mayor a 2 días",
                    title: "Advertencia",
                    type: "warning"
                };
                showMessage(status);
                return null;
            }


            if (!metrics) {
                let status = {
                    message: "Debe seleccionar alguna métrica",
                    title: "Advertencia",
                    type: "warning"
                };
                showMessage(status);
                return null;
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
        if ($MULTI_STOP_FILTER.length && stopCodes) {
            params.stopCodes = stopCodes;
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

        if ($MULTI_AUTH_ROUTE_FILTER.length && authRoutes) {
            params.authRoutes = authRoutes;
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

            if (params !== null) {
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
                    let status = false;
                    if (!data.status || data.status.code === 252) {
                        status = true;
                    }
                    if (afterCall) {
                        afterCall(data, status);
                    }
                    // update backup to the last request params sent to server
                    paramsBackup = params;
                }).always(function () {
                    _makeAjaxCallForUpdateButton = true;
                    button.html(previousMessage);
                });
            } else {
                _makeAjaxCallForUpdateButton = true;
                button.html(previousMessage);
            }
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
            let routesDict = data.routesDict;
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
                    let dictName = ((routesDict[el]) === undefined) ? "" : ` (${routesDict[el]})`;
                    return {id: el, text: `${el}${dictName}`};
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
                    window.localStorage.setItem("operatorFilter", JSON.stringify({id: $OPERATOR_FILTER.val()}));
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
                $OPERATOR_FILTER.val(selectedItem.id).trigger("change").trigger({
                    type: "select2:select",
                    params: {data: selectedItem, isFirstTime: true}
                });
            } else {
                var operatorId = Object.keys(data.availableRoutes)[0];
                updateUserRouteList(operatorId, true);
            }

            $AUTH_ROUTE_FILTER.on("select2:select", function (e) {
                var selectedItem = e.params.data;
                window.localStorage.setItem("operatorFilter", JSON.stringify({id: $OPERATOR_FILTER.val()}));
                window.localStorage.setItem("userRouteFilter", JSON.stringify({id: $USER_ROUTE_FILTER.val()}));
                window.localStorage.setItem("authRouteFilter", JSON.stringify({id: selectedItem.id}));
            });

            // ignore if local settings are nulls
            if (localOperatorFilter) {
                $OPERATOR_FILTER.val(localOperatorFilter.id).trigger("change");
                $USER_ROUTE_FILTER.val(localUserRouteFilter.id).trigger("change");
                $AUTH_ROUTE_FILTER.val(localAuthRouteFilter.id).trigger("change");
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

    if ($MULTI_AUTH_ROUTE_FILTER.length) {
        var localMultiAuthRouteFilter = JSON.parse(window.localStorage.getItem(urlKey + "multiAuthRouteFilter"))
        if (localMultiAuthRouteFilter !== null) {
            localMultiAuthRouteFilter = localMultiAuthRouteFilter.id;
        } else {
            localMultiAuthRouteFilter = [];
        }
        $MULTI_AUTH_ROUTE_FILTER.val(localMultiAuthRouteFilter);
        $MULTI_AUTH_ROUTE_FILTER.trigger("change");
        $MULTI_AUTH_ROUTE_FILTER.change(function () {
            window.localStorage.setItem(urlKey + "multiAuthRouteFilter", JSON.stringify({id: $MULTI_AUTH_ROUTE_FILTER.val()}));
        });

        var processMultiRouteData = function (data) {
            let routesDict = data.routesDict;
            data.data = data.data.map(function (el) {
                let dictName = ((routesDict[el.item]) === undefined) ? "" : ` (${routesDict[el.item]})`;
                return {id: el.item, text: `${el.item}${dictName}`};
            });
            if ($MULTI_AUTH_ROUTE_FILTER.length) {
                $MULTI_AUTH_ROUTE_FILTER.select2({data: data.data});
                $MULTI_AUTH_ROUTE_FILTER.on("select2:select", function (e) {
                    if (!e.params.isFirstTime) {
                        window.localStorage.setItem(urlKey + "multiAuthRouteFilter", JSON.stringify({id: $MULTI_AUTH_ROUTE_FILTER.val()}));
                    }
                });
                // call event to update user route filter
                var selectedItem = localMultiAuthRouteFilter !== null ? localMultiAuthRouteFilter : $MULTI_AUTH_ROUTE_FILTER.select2("data")[0];
                $MULTI_AUTH_ROUTE_FILTER.val(selectedItem).trigger("change").trigger({
                    type: "select2:select",
                    params: {data: selectedItem, isFirstTime: true}
                });
            }
        };

        $.getJSON(urlMultiRouteData, function (data) {
            if (data.status) {
                showMessage(data.status);
            } else {
                processMultiRouteData(data);
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