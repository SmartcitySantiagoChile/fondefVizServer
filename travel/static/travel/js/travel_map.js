"use strict";

var ws_data = {};
ws_data.ready = false;
ws_data.data = null;

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

function setupSectorForm(options) {

    $('#sectorSelector')
        .select2({
            placeholder: "Seleccione un sector",
            allowClear: true,
            minimumResultsForSearch: Infinity // hide search box
        })
        .on("select2:select", function(e) {
            var selected = $(this).val();
            updateSelectedSector(selected, options);
        })
        .on("select2:unselect", function(e) {
            updateSelectedSector(null, options);  
        });
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
    for (var sector_name in _allSectors) {
        var option = document.createElement("option");
        var sector_text = toTitleCase(sector_name);

        option.setAttribute("value", sector_name);
        option.appendChild(document.createTextNode(sector_text));
        sectorSelect.appendChild(option);
    }

    var curr_value = sectorSelect.value;
    var selected;
    if (last_value == "") {
        // use default
        selected = options.default_sector;

    } else if (last_value != curr_value) {
        // keep last
        selected = last_value;
        
    } else {
        // use current
        selected = curr_value;
    }

    for (var i=0, l=sectorSelect.options.length, curr; i<l; i++)
    {
        curr = sectorSelect.options[i];
        curr.selected = false;
        if ( curr.value == selected ) {
            curr.selected = true;
        }
    }
    updateSelectedSector(selected, options);
}

function isSectorSelected(options) {
    return (
        options.curr_sector !== null 
        && options.curr_sector in _allSectors 
    ); 
}

function isZoneIdInCurrentSector(zone_id, options) {
    return (
        isSectorSelected(options)
        && $.inArray(zone_id, _allSectors[options.curr_sector]) > -1
    );
}


// ============================================================================
// MAP Visualizations
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
    ws_data.data = response.map;
    updateAvailableSectors(options);
    redraw(options);
    updateMapDocCount(options);
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

    // put loading spinner
    var update_button = $(this);
    var loading_text = "Actualizar Datos <i class='fa fa-cog fa-spin fa-2x fa-fw'>";
    update_button.html(loading_text);

    // load data and remove spinner
    $.getJSON('getMapData', request, processData).always(function(){
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
    setupDayTypeAndTSPeriodForm(_allDaytypes, _dayTypes, _dayTypes_reversed, options);
    setupSectorForm(options);
    setupVisualizationForm(options);
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
