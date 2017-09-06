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

function setupDayTypeAndTSPeriodForm(_allDaytypes, _dayTypes, _dayTypes_reversed, options) {

    var dayTypeSelect = document.getElementById('dayTypeFilter');

    // fill daytypes
    for (var i=0, l=_allDaytypes.length; i<l; i++)
    {
        var daytype = _allDaytypes[i];
        var option = document.createElement("option");
        option.setAttribute("value", daytype.pk);
        option.appendChild(document.createTextNode(daytype.name));
        dayTypeSelect.appendChild(option);
    }


    // set default day as LABORAL
    for (var i=0, l=dayTypeSelect.options.length, curr; i<l; i++)
    {
        curr = dayTypeSelect.options[i];
        if ( curr.text === "Laboral" ) {
            curr.selected = true;
        }
    }
    updateTSPeriods([_dayTypes_reversed["Laboral"]], _allDaytypes, _dayTypes, _dayTypes_reversed);


    // day type and period filters
    $('#dayTypeFilter')
        .select2({placeholder: 'Cualquiera'})
        .on("select2:select select2:unselect", function(e) {
            var selection_ids = $(this).val();
            updateTSPeriods(selection_ids, _allDaytypes, _dayTypes, _dayTypes_reversed);
        });

    $('#periodFilter')
        .select2({placeholder: 'Todos'});
}

// Updates the list of options for the TS periods selector.
// based on the provided dayTypes list. 
// 
// returns nothing.
//
// TODO: do not delete already selected values!.. PS. keep the list sorted by id.
// TODO: avoid when dayType list has not changed.
function updateTSPeriods(dayTypes, _allDaytypes, _dayTypes, _dayTypes_reversed) {
    if (dayTypes === undefined || dayTypes === null) return;

    var periodSelect = document.getElementById('periodFilter');

    // remove all values
    while (periodSelect.firstChild) {
        periodSelect.removeChild(periodSelect.firstChild);
    }
    if (dayTypes.length === 0) return;

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


// ============================================================================
// Visualization Selector
// ============================================================================

function setupVisualizationForm(options) {

    var data = [
        { id: 'tviaje', text: 'Tiempo de viaje' },
        { id: 'distancia_ruta', text: 'Distancia en ruta' },
        { id: 'distancia_eucl', text: 'Distancia euclideana' },
        { id: 'n_etapas', text: 'Número de Etapas' },
        { id: 'count', text: 'Cantidad de datos' }
    ];    

    $('#vizSelector')
        .select2({
            placeholder: "Seleccione una visualización",
            allowClear: true,
            minimumResultsForSearch: Infinity, // hide search box
            data: data
        })
        .on("select2:select", function(e) {
            var selected = $(this).val();
            updateSelectedVisualization(selected, options);
        })
        .on("select2:unselect", function(e) {
            updateSelectedVisualization(null, options);
        });

    updateSelectedVisualization(options.default_visualization_type, options);
    updateMapTitle(options);
}

function updateSelectedVisualization(visualization_type, options) {
    if (options.curr_visualization_type !== visualization_type) {
        options.curr_visualization_type = visualization_type;
        redraw(options);
    }
}
