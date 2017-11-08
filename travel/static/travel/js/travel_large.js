"use strict";

ws_data.ready = false;
ws_data.data = null;

// map layers
ws_data.tile_layer;
ws_data.subway_layer = L.geoJSON(); // empty layer
ws_data.districts_layer  = L.geoJSON(); // empty layer
ws_data.zones_layer  = L.geoJSON(); // empty layer
ws_data.sector_layer = L.geoJSON(); // empty layer

ws_data.map;
ws_data.map_legend;
ws_data.map_info;
ws_data.map_layer_control;


// ============================================================================
// Etapas Checkboxes
// ============================================================================

function setupEtapasSelectors(options) {
    var elems = Array.prototype.slice.call(document.querySelectorAll('.netapas_checkbox'));
    elems.forEach(function(html) {
        var switchery = new Switchery(html, {
            size: 'small',
            color: 'rgb(38, 185, 154)'
        });
        html.onchange = function() {
            updateServerData();
        };
    });
}

function lookupNEtapasSelectors() {

    var response = [];
    var elems = Array.prototype.slice.call(document.querySelectorAll('.netapas_checkbox'));
    elems.forEach(function(html) {
        if (html.checked) {
            response.push(html.getAttribute('data-ne-str'));
        }
    });
    return response;
}

// ============================================================================
// Coloring Checkboxes
// ============================================================================

function setupColoringSelector(options) {
    var checkbox = document.querySelector('#colorscale_checkbox');
    var switchery = new Switchery(checkbox, {
            size: 'small',
            color: '#777',
            jackColor         : '#fff',
            secondaryColor    : '#777',
            jackSecondaryColor: '#fff'
    });
    checkbox.onchange = function() {
        if (checkbox.checked) {
            options.curr_map_color_scale = options.map_color_scale_secuential;
        } else {
            options.curr_map_color_scale = options.map_color_scale_diverging;
        }
        redraw(options);
    };
}

// ============================================================================
// SERVER DATA
// ============================================================================

function getDataZoneById(data, zone_id, options) {
    // missing data
    if (data === null) return null;
    if (zone_id === undefined || zone_id === null) return null;
    if (options === undefined || options === null) return null;

    // seek zone
    var result = null;
    data.aggregations.by_zone.buckets.forEach(function (zone, idx) {
        if (zone.key == zone_id) {
            result = zone;
        }
    });
    return result;
}

function fit_grades(arr){
    var max_val = Math.max(...arr);
    var step = max_val/4;
    var n_pos = Math.floor(Math.log(step)/Math.LN10);
    var most = Math.floor(step/Math.pow(10,n_pos));
    var rounded_step = (most+0.5)*Math.pow(10,n_pos);

    options.visualization_mappings['count']['grades'] = [1, rounded_step, 2*rounded_step, 3*rounded_step, 4*rounded_step];
    options.visualization_mappings['count']['grades_str'] = options.visualization_mappings['count']['grades'].map(function(x){return x.toFixed(0);});
}

function processData(response) {
    ws_data.data = response.large;

    // calcular limites para cantidades (para no saturar)?
    var count = ws_data.data.aggregations.by_zone.buckets.map(function(x){
        return x.doc_count;
    });
    fit_grades(count);

    redraw(options);
    updateMapDocCount(options);
}

// Update Charts from filters
function updateServerData() {

    var fromDate = $('#dateFromFilter').val();
    var toDate = $('#dateToFilter').val();
    var dayTypes = $('#dayTypeFilter').val();
    var periods = $('#periodFilter').val();
    var nEtapas = lookupNEtapasSelectors();

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
        periods: periods,
        n_etapas: nEtapas
    };

    // put loading spinner
    var update_button = $(this);
    var loading_text = "Actualizar Datos <i class='fa fa-cog fa-spin fa-2x fa-fw'>";
    update_button.html(loading_text);

    // load data and remove spinner
    $.getJSON('getLargeTravelsData', request, processData).always(function(){
        update_button.html('Actualizar Datos')
    });
}


// ============================================================================
// MAIN
// ============================================================================

$(document).ready(function () {

    // Forms
    console.log("> Building forms.")
    setupDateForm(options);
    setupDayTypeAndTSPeriodForm(options);
    setupEtapasSelectors(options);
    setupColoringSelector(options);

    // map
    console.log("> Building Map ... ")
    setupMap(options);

    // load with default parameters
    console.log("> Loading default data ... ")

    updateServerData();

    // buttons
    $('#btnUpdateChart').click(updateServerData);
});
