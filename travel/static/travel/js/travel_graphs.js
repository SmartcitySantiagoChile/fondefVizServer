"use strict";

var ws_data = {};
ws_data.ready = false;
ws_data.data = null;

// ============================================================================
// Visualizations
// ============================================================================

// Visualization Selector
// --------------------------------------------------------------
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
    updateGraphTitle(options);
}

function updateSelectedVisualization(visualization_type, options) {
    if (options.curr_visualization_type !== visualization_type) {
        options.curr_visualization_type = visualization_type;
        updateGraphTitle(options);
        // redraw(options);
    }
}


// ============================================================================
// SERVER DATA
// ============================================================================

function getDataZoneById(data, zone_id, options) {
    // missing data
    if (data === null) return null;
    if (zone_id === undefined || zone_id === null) return null;
    if (options === undefined || options === null) return null;
    if (options.curr_sector === null) return null;

    // unknown sector aggregation
    if (!(options.curr_sector in data.aggregations)) return null;

    // seek zone
    var result = null;
    data.aggregations[options.curr_sector].by_zone.buckets.forEach(function (zone, idx) {
        if (zone.key == zone_id) {
            result = zone;
        }
    });
    return result;
}

function processData(response) {
    ws_data.data = response.histogram;
    // console.log(response)
    // console.log(ws_data.data)
    redraw(options);
}

// Update Charts from filters
function updateServerData() {
    // TODO: enforce fromDate < toDate.

    var fromDate = $('#dateFromFilter').val();
    var toDate = $('#dateToFilter').val();
    var dayTypes = $('#dayTypeFilter').val();
    var periods = $('#periodFilter').val();

    // console.log("--- update charts ---");
    // console.log("from date: " + fromDate);
    // console.log("to date: " + toDate);
    // console.log("day types: " + dayTypes);
    // console.log("periods: " + periods);
    // console.log("-- -- -- -- -- -- -- ");

    var request = {
        from: fromDate,
        to: toDate,
        daytypes: dayTypes,
        periods: periods
    };

    // put loading spinner on update button
    var update_button = $(this);
    var loading_text = "Actualizar Datos <i class='fa fa-cog fa-spin fa-2x fa-fw'>";
    update_button.html(loading_text);

    // put spinner on graph
    ws_data.graph.showLoading(null, {text: 'Cargando...'});

    // load data and remove spinners
    $.getJSON('getGraphsData', request, processData).always(function(){
        update_button.html('Actualizar Datos')
        ws_data.graph.hideLoading();
    });
}


// ============================================================================
// MAIN
// ============================================================================

$(document).ready(function () {

    // Forms
    console.log("> Building forms.")
    setupDateForm(options);
    setupDayTypeAndTSPeriodForm(_allDaytypes, _dayTypes, _dayTypes_reversed, options);
    setupVisualizationForm(options);

    // graphs
    console.log("> Building Graph ... ")
    setupGraph(options);

    // load with default parameters
    console.log("> Loading default data ... ")
    updateServerData();

    // buttons
    $('#btnUpdateChart').click(updateServerData);
});
