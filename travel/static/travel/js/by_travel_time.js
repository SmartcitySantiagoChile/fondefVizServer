"use strict";

var _dayTypes = {
    0: "Laboral",
    1: "Sábado",
    2: "Domingo"
};

var _dayTypes_reversed = {
    "Laboral": 0,
    "Sábado": 1,
    "Domingo": 2
};

var _selected_day_type_ids = [];

$(document).ready(function () {

    function processData(response) {
        console.log(response.state);
    }

    function updateTSPeriods(dayTypes) {
        // avoid when dayType has not changed.

        var periodSelect = document.getElementById('periodFilter');

        // remove all values
        while (periodSelect.firstChild) {
            periodSelect.removeChild(periodSelect.firstChild);
        }
        // clear list! and return
        if (dayTypes === null) {
            _selected_day_type_ids = [];
            return;
        }
        // TODO: do not delete already selected values!.. PS. keep the list sorted by id.
        _selected_day_type_ids = dayTypes;

        // required days as string
        var dayTypes_str = dayTypes.map(function(item) {
            return _dayTypes[item];
        });

        // put new ones
        for (var i=0, l=_allPeriods.length; i<l; i++) {
            var this_period = _allPeriods[i];
            if ( dayTypes_str.indexOf( this_period.fields.dayType ) !== -1 ) {
                var option = document.createElement("option");
                option.setAttribute("value", this_period.pk);
                option.appendChild(document.createTextNode(this_period.fields.transantiagoPeriod));
                periodSelect.appendChild(option);
            }
        }
    }

    // ========================================================================
    // FILTERS
    // ========================================================================
    (function () {

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


        // set default day as LABORAL
        var dayTypeSelect = document.getElementById('dayTypeFilter');
        for (var i=0, l=dayTypeSelect.options.length, curr; i<l; i++)
        {
            curr = dayTypeSelect.options[i];
            if ( curr.text === "Laboral" ) {
                curr.selected = true;
            }
        }
        updateTSPeriods([_dayTypes_reversed["Laboral"]]);


        // day type and period filters
        $('#dayTypeFilter')
            .select2({placeholder: 'Cualquiera'})
            .on("select2:select select2:unselect", function(e) {
                var selection_ids = $(this).val();
                updateTSPeriods(selection_ids);
            });
        $('#periodFilter').select2({placeholder: 'Todos'});

        // $('#communeFilter').select2({placeholder: 'comuna'});
        // $('#halfhourFilter').select2({placeholder: 'media hora'});

        // Update Charts from filters
        $('#btnUpdateChart').click(function () {
            // TODO: enforce fromDate < toDate.

            var fromDate = $('#dateFromFilter').val();
            var toDate = $('#dateToFilter').val();
            var dayTypes = $('#dayTypeFilter').val();
            var periods = $('#periodFilter').val();

            console.log("--- update charts ---");
            console.log("from date: " + fromDate);
            console.log("to date: " + toDate);
            console.log("day types: " + dayTypes);
            console.log("periods: " + periods);
            console.log("-- -- -- -- -- -- -- ");

            var request = {
                from: fromDate,
                to: toDate,
                daytypes: dayTypes,
                periods: periods
            };

            var update_button = $(this);
            var loading_text = update_button.html() + " <i class='fa fa-cog fa-spin fa-2x fa-fw'>";
            update_button.html(loading_text);
            $.getJSON('getDataByTime', request, processData).always(function(){
                update_button.html('Actualizar Datos')
            });

        });
    })() // end filters

});