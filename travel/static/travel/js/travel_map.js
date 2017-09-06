"use strict";

var _map_data = null;

var options = {};
options.default_sector = 'SANTIAGO'
options.default_visualization_type = 'tviaje';
options.curr_sector = null;
options.curr_visualization_type = null;

// http://colorbrewer2.org/#type=sequential&scheme=GnBu&n=5
options.visualization_mappings = {
    tviaje: {
        name: 'Tiempo de viaje',
        grades: [0, 30, 45, 60, 75],
        grades_str: ["0", "30", "45", "60", "75"],
        legend_post_str: "min",
        colors: ["#ffffb2", "#fecc5c", "#fd8d3c", "#f03b20", "#bd0026"],
        map_fn: function (zone) { return zone.tviaje.value; }
    },
    distancia_ruta: {
        name: 'Distancia en ruta',
        grades: [0, 1000, 5000, 10000, 20000],
        grades_str: ["0", "1", "5", "10", "20"],
        legend_post_str: "km",
        colors: ["#ffffb2", "#fecc5c", "#fd8d3c", "#f03b20", "#bd0026"],
        map_fn: function (zone) { return zone.distancia_ruta.value; }
    },
    distancia_eucl: {
        name: 'Distancia euclideana',
        grades: [0, 1000, 5000, 10000, 20000],
        grades_str: ["0", "1", "5", "10", "20"],
        legend_post_str: "km",
        colors: ["#ffffb2", "#fecc5c", "#fd8d3c", "#f03b20", "#bd0026"],
        map_fn: function (zone) { return zone.distancia_eucl.value; }
    },
    n_etapas: {
        name: 'Número de etapas',
        grades: [1.0, 1.3, 2.0, 2.3, 3.0],
        grades_str: ["1.0", "1.3", "2.0", "2.3", "3.0"],
        legend_post_str: "",
        colors: ["#ffffb2", "#fecc5c", "#fd8d3c", "#f03b20", "#bd0026"],
        map_fn: function (zone) { return zone.n_etapas.value; }
    },
    count: {
        name: 'Cantidad de datos',
        grades: [1, 5, 25, 50, 75],
        grades_str: ["1", "5", "25", "50", "75"],
        legend_post_str: "",
        colors: ["#ffffb2", "#fecc5c", "#fd8d3c", "#f03b20", "#bd0026"],
        map_fn: function (zone) { return zone.doc_count; }
    }
};

options.map_default_lat_lon = L.latLng(-33.459229, -70.645348);
options.map_min_zoom = 8;
options.map_default_zoom = 11;
options.map_max_zoom = 15;
options.map_access_token = "pk.eyJ1IjoidHJhbnNhcHB2aXMiLCJhIjoiY2l0bG9qd3ppMDBiNjJ6bXBpY3J0bm40cCJ9.ajifidV4ypi0cXgiGQwR-A";


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
function updateAvailableSectors(map_data, options) {

    // avoid processing when there is no data
    if (map_data === null) {
        return;
    }
    var sectorSelect = document.getElementById('sectorSelector');
    var last_value = sectorSelect.value;

    // remove all values
    while (sectorSelect.firstChild) {
        sectorSelect.removeChild(sectorSelect.firstChild);
    }
    
    // update
    for (var sector_key in map_data.aggregations) {
        var option = document.createElement("option");
        var sector_text = toTitleCase(sector_key);

        option.setAttribute("value", sector_key.toUpperCase());
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


$(document).ready(function () {

    // Forms
    setupDateForm(options);
    setupDayTypeAndTSPeriodForm(_allDaytypes, _dayTypes, _dayTypes_reversed, options);
    setupSectorForm(options);
    setupVisualizationForm(options);

    // map
    setupMap(options);
    setupMapInfoBar(options);
    setupMapLegend(options);

    // load with default parameters
    updateServerData();

    // buttons
    $('#btnUpdateChart').click(updateServerData);
});