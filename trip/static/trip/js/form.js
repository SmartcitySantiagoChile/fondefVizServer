"use strict";
// requires:
// - moment.js
// - daterangepicker
// - jQuery
// - select2


// ============================================================================
// DATE
// ============================================================================

function setupDateForm(options) {

    // set locale
    moment.locale('es');

    var today = new Date();
    var tomorrow = new Date(today.getTime() + 24 * 60 * 60 * 1000);

    // datetime pickers
    $('#dateFromFilter').daterangepicker({
        singleDatePicker: true,
        language: "es",
        "minDate": "01/01/2015",
        "maxDate": tomorrow,
        "startDate": "13/03/2016"
         // "startDate": today,
    });
    $('#dateToFilter').daterangepicker({
        singleDatePicker: true,
        language: 'es',
        "minDate": "01/01/2015",
        "maxDate": tomorrow,
        "startDate": "15/03/2016"
        // "startDate": today,
    });
}


// ============================================================================
// DAY TYPES AND TS PERIODS
// ============================================================================

function setupDayTypeAndTSPeriodForm(options) {

    // get options from the server data
    var day_types_data = [];
    ws_data._day_types.map(function (item) {
        day_types_data.push({ id: item.pk, text: item.name });
    });
    ws_data.all_day_types_data = day_types_data;

    // setup day type filter
    $('#dayTypeFilter')
        .select2({
            placeholder: 'Cualquiera',
            allowClear: true,
            minimumResultsForSearch: Infinity, // hide search box
            data: day_types_data
        })
        .on("select2:select select2:unselect", function(e) {
            updateTSPeriods();
        })
        .val(0).trigger("change"); // force LABORAL day type as default

    // setup period filter
    $('#periodFilter')
        .select2({
            placeholder: 'Todos',
            allowClear: true,
            minimumResultsForSearch: Infinity // hide search box
    });

    // fill initial TS periods
    ws_data.current_day_types = null;
    updateTSPeriods();
}

function setupHalfHours(options) {
    // clear all
    $('#halfHoursFilter').empty();
    $('#halfHoursFilter').val(null).trigger('change');

    $('#halfHoursFilter')
        .select2({
            placeholder: 'Todos',
            allowClear: true,
            minimumResultsForSearch: Infinity // hide search box
    });

    // append new options
    ws_data._half_hours.map(function (item) {
        var hh_id = item.pk;
        var hh_name = item.fields.shortName;

        var new_hh = new Option(hh_name, hh_id, false, false);
        $('#halfHoursFilter').append(new_hh).trigger('change');
    });
}

// Updates the list of options for the TS periods selector.
//
// - clears the multiselector
// - add matching options
// - mark previously selected options as "selected"
function updateTSPeriods() {

    // current day types
    var selected_day_types = $('#dayTypeFilter').select2('data');
    if (selected_day_types.length === 0) selected_day_types = ws_data.all_day_types_data;

    // current TS periods
    var curr_TS_periods = $('#periodFilter').select2('data');

    // clear all
    $('#periodFilter').empty();
    $('#periodFilter').val(null).trigger('change');

    // append new options
    ws_data._TS_periods.map(function (item) {
        var period_id = item.pk;
        var period_day_type = item.fields.dayType;
        var period_name = item.fields.transantiagoPeriod;

        // require this period day is in the selected day list
        var day_match = selected_day_types.reduce(function (prev, value) {
            return prev || (value.text == period_day_type);
        }, false);
        // console.log(day_match, period_id, period_day_type, period_name);

        if (day_match) {
            // select options which were already selected
            var mark_as_selected = $.grep(curr_TS_periods, function(item) {
                return item.id == period_id;
            }).length == 1;

            var new_period = new Option(period_name, period_id, mark_as_selected, mark_as_selected);
            $('#periodFilter').append(new_period).trigger('change');
        }
    });
}
