"use strict";

ws_data.data = null;
ws_data.ready = false;
ws_data.ready2 = false;

// map layers
ws_data.tile_layer;
ws_data.tile_layer2;
ws_data.subway_layer = L.geoJSON(); // empty layer
ws_data.subway_layer2 = L.geoJSON(); // empty layer
ws_data.districts_layer  = L.geoJSON(); // empty layer
ws_data.districts_layer2  = L.geoJSON(); // empty layer
ws_data.origins_layer  = L.featureGroup(); // empty layer
ws_data.destinations_layer  = L.featureGroup(); // empty layer
ws_data.zones_layer  = L.featureGroup(); // empty layer
ws_data.zones_layer2  = L.featureGroup(); // empty layer
// ws_data.zones_layer  = L.geoJSON(); // empty layer
// ws_data.zones_layer2  = L.geoJSON(); // empty layer
ws_data.sector_layer = L.geoJSON(); // empty layer
ws_data.sector_layer2 = L.geoJSON(); // empty layer

ws_data.map;
ws_data.map2;
ws_data.map_legend;
ws_data.map_legend2;
ws_data.map_info;
ws_data.map_info2;
ws_data.map_layer_control;
ws_data.map_layer_control2;

var origin = -1;
var destination = -1;

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

function processData(response) {
    ws_data.data = {
        origin_zones: response.origin_zone,
        destination_zones: response.destination_zone
    };

    redraw2(options);
}


// Update Charts from filters
function updateServerData() {

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
        periods: periods,
        origin: origin,
        destination: destination
    };

    // put loading spinner
    var update_button = $(this);
    var loading_text = "Actualizar Datos <i class='fa fa-cog fa-spin fa-2x fa-fw'>";
    update_button.html(loading_text);

    // load data and remove spinner
    $.getJSON('getFromToMapsData', request, processData).always(function(){
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

    // map
    console.log("> Building Map ... ")
    setupDoubleMap(options);

    // load with default parameters
    console.log("> Loading default data ... ")

    updateServerData();

    // buttons
    $('#btnUpdateChart').click(updateServerData);
});
