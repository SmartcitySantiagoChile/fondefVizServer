"use strict";

var ws_data = {};
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
        { id: 'n_etapas', text: 'Número de Etapas' }
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
        redraw(options);
    }
}

function getDataByVisualizationType(data, options) {
    // missing data
    if (data === null) return null;
    if (options === undefined || options === null) return null;
    if (options.curr_visualization_type === null) return null;

    // unknown sector aggregation
    if (!(options.curr_visualization_type in data.aggregations)) return null;

    return data.aggregations[options.curr_visualization_type];
}

// ============================================================================
// SERVER DATA
// ============================================================================

function getGraphData(options) {
    var data = getDataByVisualizationType(ws_data.data, options);
    if (data === null) return null;

    var xaxis_fn = options.visualization_mappings[options.curr_visualization_type].xaxis_fn;
    
    var result = {};
    result.xaxis = [];
    result.count = [];
    result.bins = [];
    result.total = [];
    result.percent = [];
    result.total_percent = [];

    var len = data.buckets.length;
    var total = Math.round(data.buckets[len-1].total.value);
    if (total <= 0) { total = 1; }

    for (var i=0; i < len - 1; ++i) {
        var item = data.buckets[i];
        var next = data.buckets[i+1];
        result.count.push(Math.round(item.doc_count));
        result.bins.push(Math.round(item.bin.value));
        result.total.push(Math.round(item.total.value));
        result.percent.push(100.0*Math.round(item.bin.value)/total);
        result.total_percent.push(100.0*Math.round(item.total.value)/total);
        result.xaxis.push(xaxis_fn(item.key, next.key));
    }
    result.count.push(Math.round(data.buckets[len-1].doc_count));
    result.bins.push(Math.round(data.buckets[len-1].bin.value));
    result.total.push(Math.round(data.buckets[len-1].total.value));
    result.percent.push(100.0*Math.round(data.buckets[len-1].bin.value)/total);
    result.total_percent.push(100.0*Math.round(data.buckets[len-1].total.value)/total);
    result.xaxis.push(xaxis_fn(data.buckets[len-1].key));
    return result;
}

function processData(response) {
    ws_data.data = response.histogram;
    ws_data.indicators = response.indicators;
    console.log(ws_data.indicators);
    // console.log(ws_data.data);
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
