"use strict";

ws_data.data = null;
ws_data.ready = false;
ws_data.ready2 = false;

// map layers
ws_data.tile_layer;
ws_data.tile_layer2;
ws_data.subway_layer = L.geoJSON(); // empty layer
ws_data.subway_layer2 = L.geoJSON(); // empty layer
ws_data.districts_layer = L.geoJSON(); // empty layer
ws_data.districts_layer2 = L.geoJSON(); // empty layer
ws_data.origins_layer = L.featureGroup(); // empty layer
ws_data.destinations_layer = L.featureGroup(); // empty layer
ws_data.zones_layer = L.featureGroup(); // empty layer
ws_data.zones_layer2 = L.featureGroup(); // empty layer
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

function setupEtapasSelectors(options, manager) {
    var elems = Array.prototype.slice.call(document.querySelectorAll('.netapas_checkbox'));
    elems.forEach(function (html) {
        new Switchery(html, {
            size: 'small',
            color: 'rgb(38, 185, 154)'
        });
        html.onchange = function () {
            manager.updateData();
        };
    });
}

function setupModosSelectors(options, manager) {
    var elems = Array.prototype.slice.call(document.querySelectorAll('.modes_checkbox'));
    elems.forEach(function (html) {
        new Switchery(html, {
            size: 'small',
            color: 'rgb(38, 185, 154)'
        });
        html.onchange = function () {
            manager.updateData();
        };
    });
}

function lookupNEtapasSelectors() {

    var response = [];
    var elems = Array.prototype.slice.call(document.querySelectorAll('.netapas_checkbox'));
    elems.forEach(function (html) {
        if (html.checked) {
            response.push(html.getAttribute('data-ne-str'));
        }
    });
    return response;
}

function lookupModosSelectors() {

    var response = [];
    var elems = Array.prototype.slice.call(document.querySelectorAll('.modes_checkbox'));
    elems.forEach(function (html) {
        if (html.checked) {
            response.push(html.getAttribute('data-ne-str'));
        }
    });
    return response;
}

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
        if ($.inArray(zone.key, zone_ids) >= 0) {
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
        origin_zones: response.origin_zone,
        destination_zones: response.destination_zone
    };

    redraw2(options);
    ws_data.map_info.update(origin);
    ws_data.map_info2.update(destination);
}

// ============================================================================
// MAIN
// ============================================================================

$(document).ready(function () {
    loadAvailableDays(Urls["esapi:availableTripDays"]());

    var afterCall = function (data) {
        processData(data);
    };
    var opts = {
        urlFilterData: Urls["esapi:fromToMapData"](),
        afterCallData: afterCall,
        dataUrlParams: function() {
            return {
                stages: lookupNEtapasSelectors(),
                modex: lookupModosSelectors()
            }
        }
    };
    var manager = new FilterManager(opts);

    setupEtapasSelectors(options, manager);
    setupModosSelectors(options, manager);
    // map
    setupDoubleMap(options);

    manager.updateData();
});
