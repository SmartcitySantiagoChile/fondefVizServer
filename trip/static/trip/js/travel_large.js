"use strict";

ws_data.ready = false;
ws_data.data = null;

// map layers
ws_data.tile_layer;
ws_data.subway_layer = L.geoJSON(); // empty layer
ws_data.districts_layer = L.geoJSON(); // empty layer
ws_data.zones_layer = L.geoJSON(); // empty layer
ws_data.sector_layer = L.geoJSON(); // empty layer

ws_data.map;
ws_data.map_legend;
ws_data.map_info;
ws_data.map_layer_control;


// ============================================================================
// Etapas Checkboxes
// ============================================================================

function setupEtapasSelectors(options, manager) {
    var elems = Array.prototype.slice.call(document.querySelectorAll('.netapas_checkbox'));
    elems.forEach(function (html) {
        var switchery = new Switchery(html, {
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

// ============================================================================
// Coloring Checkboxes
// ============================================================================

function setupColoringSelector(options) {
    var checkbox = document.querySelector('#colorscale_checkbox');
    var switchery = new Switchery(checkbox, {
        size: 'small',
        color: '#777',
        jackColor: '#fff',
        secondaryColor: '#777',
        jackSecondaryColor: '#fff'
    });
    checkbox.onchange = function () {
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
    data.by_zone.buckets.forEach(function (zone, idx) {
        if (zone.key === zone_id) {
            result = zone;
        }
    });
    return result;
}

function fit_grades(min_val, max_val) {
    options.visible_limits = [min_val, max_val];
    var step = (max_val - min_val) / 4;
    var exp_min = Math.floor(Math.log(min_val) / Math.LN10);
    var exp_step = Math.floor(Math.log(step) / Math.LN10);
    var coef_min = Math.floor(2.0 * min_val / Math.pow(10, exp_min)) / 2.0;
    var coef_step = Math.floor(10 * step / Math.pow(10, exp_step)) / 10.0;
    var rounded_min = coef_min * Math.pow(10, exp_min);
    var rounded_step = coef_step * Math.pow(10, exp_step);

    options.visualization_mappings['count']['grades'] = [Math.max(1, rounded_min), rounded_min + rounded_step, rounded_min + 2 * rounded_step, rounded_min + 3 * rounded_step, rounded_min + 4 * rounded_step];
    options.visualization_mappings['count']['grades_str'] = options.visualization_mappings['count']['grades'].map(function (x) {
        return x.toFixed(0);
    });
}

function update_limits(min_val, max_val) {
    var slider = $("#dataLimits").data("ionRangeSlider");
    slider.update({
        min: min_val,
        max: max_val,
        from: min_val,
        to: max_val
    });
}

function processData(response) {
    ws_data.data = response.large;

    // calcular limites para cantidades (para no saturar)?
    var count = ws_data.data.by_zone.buckets.map(function (x) {
        return x.doc_count;
    });
    var min_val = Math.min(...count
)
    ;
    var max_val = Math.max(...count
)
    ;
    update_limits(min_val, max_val);

    fit_grades(min_val, max_val);
    redraw(options);
    updateMapDocCount(options);
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
        urlFilterData: Urls["esapi:largeTravelData"](),
        afterCallData: afterCall,
        dataUrlParams: function () {
            return {
                stages: lookupNEtapasSelectors()
            };
        }
    };
    var manager = new FilterManager(opts);

    setupEtapasSelectors(options, manager);
    setupColoringSelector(options);
    $("#dataLimits").ionRangeSlider({
        type: "double",
        min: 0,
        max: 1,
        from: 0,
        to: 1,
        onFinish: function (data) {
            fit_grades(data.from, data.to);
            redraw(options);
            updateMapDocCount(options);
        }
    });
    setupMap(options);

    // load first time
    manager.updateData();
});