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

var origin = [];
var destination = [];

// ============================================================================
// SERVER DATA
// ============================================================================
function getDataZoneByIds(data, zone_ids, options) {
    // missing data
    if (data === null) return null;
    if (zone_ids === undefined || zone_ids === null) return null;
    if (options === undefined || options === null) return null;

    var results = [];

    data.aggregations.by_zone.buckets.forEach(function (zone, idx) {
        if($.inArray(zone.key, zone_ids) >= 0) {
            results.push([zone]);
        }
    });
    return results;
}

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
        strategies: response.strategies
    };

    var processed_data = Object.keys(ws_data.data.strategies).map(function(x){
        var pieces = x.split(' | ');
        return {nviajes: ws_data.data.strategies[x].travels.length, etapa1: pieces[0], etapa2: pieces[1], etapa3: pieces[2], etapa4: pieces[3]};
    });
    var _datatable = $('#tupleDetail').DataTable();
    console.log('2', _datatable);
    _datatable.clear();
    _datatable.rows.add(processed_data);
    _datatable.columns.adjust().draw();

    console.log("fill the table here");
}

function setupStrategyTable(options){
    var _datatable = $('#tupleDetail').DataTable({
        lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "Todos"]],
        language: {
        url: '//cdn.datatables.net/plug-ins/1.10.13/i18n/Spanish.json'
        },
        columns: [
            {title: 'N° viajes', data: 'nviajes', searchable: true},
            {title: 'Servicio Etapa 1', data: 'etapa1', className: 'text-right', searchable: false},
            {title: 'Servicio Etapa 2', data: 'etapa2', className: 'text-right', searchable: false},
            {title: 'Servicio Etapa 3', data: 'etapa3', className: 'text-right', searchable: false},
            {title: 'Servicio Etapa 4', data: 'etapa4', className: 'text-right', searchable: false}
        ],
        order: [[0, 'desc']]
    });
    console.log('1', _datatable);
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

    if(origin.length==0 || destination.length==0){
        console.log("Origen o destino vacio");
        var update_button = $("#btnUpdateChart");
        update_button.html('Actualizar Datos')
        return;
    }

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
    $.getJSON('getStrategiesData', request, processData).always(function(){
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
    setupHalfHours(options);

    setupDayTypeAndTSPeriodForm(options);

    setupStrategyTable(options);
    // map
    console.log("> Building Map ... ")
    setupStrategiesMap(options);

    // load with default parameters
    console.log("> Loading default data ... ")

    updateServerData();

    // buttons
    $('#btnUpdateChart').click(updateServerData);
});
