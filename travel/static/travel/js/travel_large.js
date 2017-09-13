"use strict";

var _map_data = null;

var options = {};

// http://colorbrewer2.org/#type=sequential&scheme=GnBu&n=5
options.visualization_mapping = {
    name: 'Cantidad de datos',
    grades: [1, 10, 20, 30, 40],
    grades_str: ["1", "10", "20", "30", "5"],
    legend_post_str: "",
    colors: ["#ffffb2", "#fecc5c", "#fd8d3c", "#f03b20", "#bd0026"],
    map_fn: function (zone) { return zone.doc_count; }
};

options.map_default_lat_lon = L.latLng(-33.459229, -70.645348);
options.map_min_zoom = 8;
options.map_default_zoom = 11;
options.map_max_zoom = 15;
options.map_access_token = "pk.eyJ1IjoidHJhbnNhcHB2aXMiLCJhIjoiY2l0bG9qd3ppMDBiNjJ6bXBpY3J0bm40cCJ9.ajifidV4ypi0cXgiGQwR-A";

var ws_data = {};
ws_data.ready = false;

// map layers 
ws_data.tile_layer;
ws_data.subway_layer = L.geoJSON(); // empty layer
ws_data.zones_layer  = L.geoJSON(); // empty layer
ws_data.sector_layer = L.geoJSON(); // empty layer

ws_data.map;
ws_data.map_legend;
ws_data.map_info;
ws_data.map_layer_control;

// ============================================================================
// MAP SECTORS
// ============================================================================

$(document).ready(function () {

    // Forms
    console.log("> Building forms.")
    setupDateForm(options);
    setupDayTypeAndTSPeriodForm(_allDaytypes, _dayTypes, _dayTypes_reversed, options);
    setupSectorForm(options);
    setupVisualizationForm(options);

    // map
    console.log("> Building Map ... ")
    setupMap(options);

    // load with default parameters
    console.log("> Loading default data ... ")
    updateServerData();

    // buttons
    $('#btnUpdateChart').click(updateServerData);
});