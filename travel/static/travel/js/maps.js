"use strict";

var map;
var geojson;
var map_legend;
var map_info;

// ============================================================================
// MAP
// ============================================================================




// ============================================================================
// INFO BAR
// ============================================================================

function setupMapInfoBar(options) {

    map_info = L.control();

    map_info.onAdd = function (map) {
        this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
        this.update();
        return this._div;
    };

    // method that we will use to update the control based on feature properties passed
    map_info.update = function (props) {
        this._div.innerHTML = '<h4>Zonificación 777</h4>';
        if (props) {
            this._div.innerHTML += '<b>' + props.comuna + '</b> (' + props.id + ')';

            var zone = getMapZoneById(_map_data, props.id, options);
            if (zone != null) {
                // console.log(zone)
                this._div.innerHTML += 
                    '<br/> - # Datos: ' + zone.doc_count +
                    '<br/> - # Etapas: ' + zone.n_etapas.value.toFixed(2) +
                    '<br/> - Duración: ' + zone.tviaje.value.toFixed(1) + ' [min]' +
                    '<br/> - Distancia (en ruta): ' + (zone.distancia_ruta.value / 1000.0).toFixed(2) + ' [km]' +
                    '<br/> - Distancia (euclideana): ' + (zone.distancia_eucl.value / 1000.0).toFixed(2) + ' [km]';
            } else {
                this._div.innerHTML += 
                    '<br/> Sin información para los filtros'
                    + '<br/> seleccionados';
            }
            
        } else {
            this._div.innerHTML += 'Pon el ratón sobre una zona';
        }
    };
}

// ============================================================================
// LEGEND
// ============================================================================

function setupMapLegend(options) {

    map_legend = L.control({position: 'bottomright'});

    map_legend.onAdd = function (map) {

        var div = L.DomUtil.create('div', 'info legend');
        div.id = "map_legend";
        return div;
    };

    map_legend.updateVisualization = function (options) {
        if (options === undefined || options === null) { return; }
        if (options.curr_visualization_type === null) { return div; }
        var grades = options.visualization_mappings[options.curr_visualization_type].grades;
        var grades_str = options.visualization_mappings[options.curr_visualization_type].grades_str;
        var grades_post_str = options.visualization_mappings[options.curr_visualization_type].legend_post_str;

        // loop through our density intervals and generate a label with a colored square for each interval
        var div = document.getElementById("map_legend");
        div.innerHTML = "";
        for (var i = 0; i < grades.length; i++) {
            div.innerHTML +=
                '<i style="background:' + getZoneColor(grades[i] + 1, options) + '"></i> ' +
                grades_str[i] + (grades_str[i + 1] ? '&ndash;' + grades_str[i + 1] + ' ' + grades_post_str + '<br>' : '+ ' + grades_post_str);
        }
        div.innerHTML +=
            '<br> <i style="background:' + getZoneColor(null, options) + '"></i>Sin Datos<br>';
    }  
}




// ============================================================================
// INTERACTIONS
// ============================================================================

function getZoneColor(value, options) {
    if (value === undefined || value === null) { return "#cccccc"; }
    if (options === undefined || options === null) { return "#cccccc"; }
    if (options.curr_visualization_type === null) { return "#cccccc"; }

    var grades = options.visualization_mappings[options.curr_visualization_type].grades;
    var colors = options.visualization_mappings[options.curr_visualization_type].colors;

    if (value < grades[0]) return "#cccccc";
    for (var i=1; i<grades.length; i++) {
        if (value <= grades[i]) return colors[i-1];
    }
    return colors[grades.length - 1];
}

// REQUIRES GLOBAL vars: options and _map_data
function styleFunction(feature) {
    if (_map_data === null) {
        return {
            weight: 2,
            opacity: 0.1,
            color: 'white',
            dashArray: '3',
            fillOpacity: 0.1
        };
    }

    var is_sector = options.curr_sector !== null && options.curr_sector.toUpperCase() === feature.properties.comuna.toUpperCase();
    if (is_sector) {
        return {
            fillColor: "green",
            weight: 2, // TODO: draw this on a top layer.. which can be deactivated on hover.. avoid dissapearing margins
            opacity: 1,
            color: 'green',
            dashArray: '0',
            fillOpacity: 0.5
        };
    }

    var zone = getMapZoneById(_map_data, feature.properties.id, options);
    var zone_value = getZoneValue(zone, options);
    var zone_color = getZoneColor(zone_value, options);

    return {
        fillColor: zone_color,
        weight: 1,
        opacity: 1,
        color: 'white',
        dashArray: '3',
        fillOpacity: 0.8
    };
}

function highlightFeatureForZone(e) {
    var layer = e.target;

    layer.setStyle({
        weight: 5,
        color: '#666',
        dashArray: '',
        fillOpacity: 0.7
    });

    if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
        layer.bringToFront();
    }
    map_info.update(layer.feature.properties);
}
function resetHighlight(e) {
    // resets style to default
    geojson.resetStyle(e.target);
    map_info.update();
}
function zoomToFeature(e) {
    map.fitBounds(e.target.getBounds());
}

function onEachFeature(feature, layer) {
    layer.on({
        mouseover: highlightFeatureForZone,
        mouseout: resetHighlight,
        click: zoomToFeature
    });
}

function setupMap(options) {

    map = L.map("mapChart").setView(options.map_default_lat_lon, options.map_min_zoom);

    L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/light-v9/tiles/256/{z}/{x}/{y}?access_token={accessToken}', {
        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, Imagery © <a href="http://mapbox.com">Mapbox</a>',
        minZoom: options.map_min_zoom,
        maxZoom: options.map_max_zoom,
        accessToken: options.map_access_token
    }).addTo(map);

    map.setMaxBounds(map.getBounds());
    map.setView(options.map_default_lat_lon, options.map_default_zoom);
    
    // load zonas
    $.ajax({
        'global': false,
        // 'url': '/static/travel/data/sectores.geojson',
        // 'url': '/static/travel/data/lineasMetro.geojson',
        'url': '/static/js/data/zonificacion777.geojson',
        'dataType': "json",
        'success': function (data) {
            // sets a default style
            geojson = L.geoJson(data, {
                style: styleFunction,
                onEachFeature: onEachFeature
            }).addTo(map);
            map_info.addTo(map);
            map_legend.addTo(map);
        }
    });
}

function redraw(options) {
    if (geojson === undefined) return;

    geojson.setStyle(styleFunction);
    map_legend.updateVisualization(options);
    updateMapDocCount(options);
    updateMapTitle(options);
}

function updateMapTitle(options) {
    var map_title = document.getElementById("mapTitle");
    if (options.curr_visualization_type !== null) {
        map_title.innerHTML = toTitleCase(options.visualization_mappings[options.curr_visualization_type].name);
    } else {
        map_title.innerHTML = "Mapa";
    }
}

function updateMapDocCount(options) {
    var map_type_doc_count = document.getElementById("visualization_type_doc_count");
    if (options.curr_sector !== null && options.curr_sector in _map_data.aggregations) {
        map_type_doc_count.innerHTML = _map_data.aggregations[options.curr_sector].doc_count;
    } else {
        map_type_doc_count.innerHTML = 0;
    }
}

function updateSelectedSector(selected, options) {
    if (options.curr_sector !== selected) {
        options.curr_sector = selected;
        redraw(options);
    }
}
