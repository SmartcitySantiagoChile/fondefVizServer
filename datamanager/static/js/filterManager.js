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

    var previousCall = function (){};
    var afterCall = function (){};
    var urlFilterData = opts.urlFilterData;

    if (opts.hasOwnProperty('previousCallData')) {
        previousCall = opts.previousCallData;
    }
    if (opts.hasOwnProperty('afterCallData')) {
        afterCall = opts.afterCallData;
    }

    /* VARIABLE DEFINITIONS */

    var $DAY_FILTER = $('#dayFilter');
    var $STOP_FILTER = $('#stopFilter');
    var $DAY_TYPE_FILTER = $('#dayTypeFilter');
    var $PERIOD_FILTER = $('#periodFilter');
    var $MINUTE_PERIOD_FILTER = $('#minutePeriodFilter');
    var $OPERATOR_FILTER = $('#operatorFilter');
    var $USER_ROUTE_FILTER = $('#userRouteFilter');
    var $AUTH_ROUTE_FILTER = $('#authRouteFilter');

    var $BTN_UPDATE_DATA = $('#btnUpdateData');

    /* LABELS */

    var PLACEHOLDER_ALL = 'Todos';
    var PLACEHOLDER_USER_ROUTE = 'Servicio usuario';
    var PLACEHOLDER_AUTH_ROUTE = 'Servicio transantiago';

    /* ENABLE select2 library */

    $DAY_FILTER.daterangepicker(optionDateRangePicker);
    $DAY_TYPE_FILTER.select2({placeholder: PLACEHOLDER_ALL});
    $PERIOD_FILTER.select2({placeholder: PLACEHOLDER_ALL});
    $MINUTE_PERIOD_FILTER.select2({placeholder: PLACEHOLDER_ALL});
    $OPERATOR_FILTER.select2();
    $USER_ROUTE_FILTER.select2({placeholder: PLACEHOLDER_USER_ROUTE});
    $AUTH_ROUTE_FILTER.select2({placeholder: PLACEHOLDER_AUTH_ROUTE});


    /* BUTTON ACTION */
    var _makeAjaxCall = true;
    $BTN_UPDATE_DATA.click(function () {
        var day = $DAY_FILTER.val();
        var dayType = $DAY_TYPE_FILTER.val();
        var authRoute = $AUTH_ROUTE_FILTER.val();
        var period = $PERIOD_FILTER.val();
        var minutes = $MINUTE_PERIOD_FILTER.val();

        var params = {
            startDate: $DAY_FILTER.data("daterangepicker").startDate.format(),
            endDate: $DAY_FILTER.data("daterangepicker").endDate.format()
        };
        if (authRoute) {
            params["authRoute"] = authRoute;
        }
        if (dayType) {
            params["dayType"] = dayType;
        }
        if (period) {
            params["period"] = period;
        }
        if (minutes) {
            params["halfHour"] = minutes;
        }

        if (_makeAjaxCall) {
            _makeAjaxCall = false;
            var loadingIcon = " " + $("<i>").addClass("fa fa-cog fa-spin fa-2x fa-fw")[0].outerHTML;
            var previousMessage = $(this).html();
            var button = $(this).append(loadingIcon);

            // actions defined by user
            previousCall();

            $.getJSON(urlFilterData, params, function (data) {
                afterCall(data);
            }).always(function () {
                _makeAjaxCall = true;
                button.html(previousMessage);
            });
        }
    });
}