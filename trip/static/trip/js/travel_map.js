"use strict";

ws_data.ready = false;
ws_data.data = null;

// map layers
ws_data.tile_layer;
ws_data.subway_layer = L.geoJSON(); // empty layer
ws_data.zones_layer = L.geoJSON(); // empty layer
ws_data.sector_layer = L.geoJSON(); // empty layer

ws_data.map;
ws_data.map_legend;
ws_data.map_info;
ws_data.map_layer_control;


// ============================================================================
// MAP SECTORS
// ============================================================================

function setupSectorForm(options) {

    $('#sectorSelector')
        .select2({
            placeholder: "Seleccione un sector",
            minimumResultsForSearch: Infinity // hide search box
        })
        .on("select2:select", function (e) {
            var selected = $(this).val();
            updateSelectedSector(selected, options);
        })
        .on("select2:unselect", function (e) {
            updateSelectedSector(null, options);
        })
        .val(options.default_sector).trigger("change"); // force default;
}

// updates the sector list with options from the server data
function updateAvailableSectors(options) {

    var sectorSelect = document.getElementById('sectorSelector');
    var last_value = sectorSelect.value;

    // remove all values
    while (sectorSelect.firstChild) {
        sectorSelect.removeChild(sectorSelect.firstChild);
    }

    // update
    for (var sector_name in ws_data._map_sectors) {
        var option = document.createElement("option");
        var sector_text = toTitleCase(sector_name);

        option.setAttribute("value", sector_name);
        option.appendChild(document.createTextNode(sector_text));
        sectorSelect.appendChild(option);
    }

    var curr_value = sectorSelect.value;
    var selected;
    if (last_value === "") {
        // use default
        selected = options.default_sector;

    } else if (last_value !== curr_value) {
        // keep last
        selected = last_value;

    } else {
        // use current
        selected = curr_value;
    }

    for (var i = 0, l = sectorSelect.options.length, curr; i < l; i++) {
        curr = sectorSelect.options[i];
        curr.selected = false;
        if (curr.value === selected) {
            curr.selected = true;
        }
    }
    updateSelectedSector(selected, options);
}

function isSectorSelected(options) {
    return (
        options.curr_sector !== null
        && options.curr_sector in ws_data._map_sectors
    );
}

function isZoneIdInCurrentSector(zone_id, options) {
    return (
        isSectorSelected(options)
        && $.inArray(zone_id, ws_data._map_sectors[options.curr_sector]) > -1
    );
}


// ============================================================================
// MAP Visualizations
// ============================================================================

// Visualization Selector
// --------------------------------------------------------------
function setupVisualizationForm(options) {

    // get options from the visualization mappings
    var data = [];
    Object.keys(options.visualization_mappings).forEach(function (key) {
        data.push({id: key, text: options.visualization_mappings[key].name});
    });

    $('#vizSelector')
        .select2({
            placeholder: "Seleccione una visualización",
            minimumResultsForSearch: Infinity, // hide search box
            data: data
        })
        .on("select2:select", function (e) {
            var selected = $(this).val();
            updateSelectedVisualization(selected, options);
        })
        .on("select2:unselect", function (e) {
            updateSelectedVisualization(null, options);
        })
        .val(options.default_visualization_type).trigger("change"); // force default

    updateSelectedVisualization(options.default_visualization_type, options);
    updateMapTitle(options);
}

function updateSelectedVisualization(visualization_type, options) {
    if (options.curr_visualization_type !== visualization_type) {
        options.curr_visualization_type = visualization_type;
        redraw(options);
    }
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
    if (options.curr_sector === null) return null;

    // unknown sector aggregation
    if (!(options.curr_sector in data)) return null;

    // seek zone
    var result = null;
    data[options.curr_sector].by_zone.buckets.forEach(function (zone, idx) {
        if (zone.key === zone_id) {
            result = zone;
        }
    });
    return result;
}

function processData(response) {
    ws_data.data = response.map;
    var sector = (options.curr_sector == null) ? options.default_sector : options.curr_sector;

    var count = ws_data.data[sector].by_zone.buckets.map(function (x) {
        return x[options.curr_visualization_type];
    });
    // console.log(count);
    options.visible_limits = [Math.min(...count), Math.max(...count)];
    // console.log(options);

    updateAvailableSectors(options);
    redraw(options);
    updateMapDocCount(options);
}


// ============================================================================
// MAIN
// ============================================================================

$(document).ready(function () {
    loadAvailableDays(Urls["esapi:availableTripDays"]());

    // Forms
    console.log("> Building forms.");
    //setupDateForm(options);
    //setupDayTypeAndTSPeriodForm(options);
    setupSectorForm(options);
    setupVisualizationForm(options);
    setupColoringSelector(options);

    var afterCall = function (data) {
        processData(data);
    };
    var opts = {
        urlFilterData: Urls["esapi:tripMapData"](),
        afterCallData: afterCall
    };
    var manager = new FilterManager(opts);
    // load first time
    manager.updateData();

    // map
    console.log("> Building Map ... ");
    setupMap(options);
});
