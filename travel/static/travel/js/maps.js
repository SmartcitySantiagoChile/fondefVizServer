"use strict";


// ============================================================================
// INFO BAR
// ============================================================================

function setupMapInfoBar(options) {

    ws_data.map_info = L.control({position: 'topright'});

    ws_data.map_info.onAdd = function (map) {
        this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
        this.update();
        return this._div;
    };

    // method that we will use to update the control based on feature properties passed
    ws_data.map_info.update = function (props) {
        this._div.innerHTML = '<h4>Zonificación 777</h4>';
        if (props) {
            this._div.innerHTML += '<b>Datos de la zona ' + props.id + '</b>';

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

    ws_data.map_legend = L.control({position: 'bottomright'});

    ws_data.map_legend.onAdd = function (map) {

        var div = L.DomUtil.create('div', 'info legend');
        div.id = "map_legend";
        return div;
    };

    ws_data.map_legend.updateVisualization = function (options) {
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
    if (value === undefined || value === null) { return null; }
    if (options === undefined || options === null) { return null; }
    if (options.curr_visualization_type === null) { return null; }

    var grades = options.visualization_mappings[options.curr_visualization_type].grades;
    var colors = options.visualization_mappings[options.curr_visualization_type].colors;

    if (value < grades[0]) return null;
    for (var i=1; i<grades.length; i++) {
        if (value <= grades[i]) return colors[i-1];
    }
    return colors[grades.length - 1];
}

function styleZoneDefault(feature) {
    return {
        weight: 2,
        opacity: 0.1,
        color: 'white',
        dashArray: '3',
        fillOpacity: 0.1
    };
}

function styleZoneNoData(feature) {
    return {
        fillColor: "#cccccc",
        weight: 1,
        opacity: 1,
        color: 'white',
        dashArray: '3',
        fillOpacity: 0.8
    };
}

function styleZoneWithColor(feature, color) {
    return {
        fillColor: color,
        weight: 1,
        opacity: 1,
        color: 'white',
        dashArray: '3',
        fillOpacity: 0.8
    };
}

function styleSectorZone(feature) {
    return {
        fillColor: "purple",
        weight: 2, // TODO: draw this on a top layer.. which can be deactivated on hover.. avoid dissapearing margins
        opacity: 1,
        color: 'purple',
        dashArray: '0',
        fillOpacity: 0.5
    };
}

function styleSubway(feature) {
    return {
        weight: 4,
        opacity: 1,
        color: feature.properties.color,
        dashArray: '0',
    };   
}

// REQUIRES GLOBAL vars: options and _map_data
function styleFunction(feature) {
    if (_map_data === null) {
        return styleZoneDefault(feature);
    }

    var is_sector = (
        options.curr_sector !== null 
        && options.curr_sector in _allSectors 
        && $.inArray(feature.properties.id, _allSectors[options.curr_sector]) > -1
    );
    if (is_sector) {

        // update sector feature registry
        if (ws_data.sector_group === null) {
            ws_data.sector_features.push(feature);
        }

        return styleSectorZone(feature);
    }

    var zone = getMapZoneById(_map_data, feature.properties.id, options);
    var zone_value = getZoneValue(zone, options);
    var zone_color = getZoneColor(zone_value, options);
    if (zone_color === null) return styleZoneNoData(feature);
    return styleZoneWithColor(feature, zone_color);
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
    ws_data.map_info.update(layer.feature.properties);
}
function resetHighlight(e) {
    // resets style to default
    ws_data.zones_layer.resetStyle(e.target);
    ws_data.map_info.update();
}
function zoomToFeature(e) {
    ws_data.map.fitBounds(e.target.getBounds());
}

function onEachZoneFeature(feature, layer) {
    layer.on({
        mouseover: highlightFeatureForZone,
        mouseout: resetHighlight,
        click: zoomToFeature
    });
}

function onEachSubwayFeature(feature, layer) {
    // do nothing!
    layer.on({});
}

function setupMap(options) {

    ws_data.map = L.map("mapChart").setView(options.map_default_lat_lon, options.map_min_zoom);

    ws_data.tile_layer = L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/light-v9/tiles/256/{z}/{x}/{y}?access_token={accessToken}', {
        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, Imagery © <a href="http://mapbox.com">Mapbox</a>',
        minZoom: options.map_min_zoom,
        maxZoom: options.map_max_zoom,
        accessToken: options.map_access_token
    }).addTo(ws_data.map);

    ws_data.map.setMaxBounds(ws_data.map.getBounds());
    ws_data.map.setView(options.map_default_lat_lon, options.map_default_zoom);
    
    // load zonas
    function loadZonesGeoJSON() {
        return $.ajax({
            'global': false,
            'url': '/static/js/data/zones777.geojson',
            'dataType': "json",
            'success': function (data) {
                ws_data.zones_layer = L.geoJson(data, {
                    style: styleFunction,
                    onEachFeature: onEachZoneFeature
                }).addTo(ws_data.map);
            }
        });
    }

    // lineas de metro layer
    function loadMetroGeoJson() {
        return $.ajax({
            'global': false,
            'url': '/static/js/data/subway.geojson',
            'dataType': "json",
            'success': function (data) {
                ws_data.subway_layer = L.geoJson(data, {
                    style: styleSubway,
                    onEachFeature: onEachSubwayFeature
                }).addTo(ws_data.map);;
            }
        });
    }

    $.when(loadZonesGeoJSON(), loadMetroGeoJson()).done(
        function(respZones, respMetro) {
            console.log(" - GeoJSON loading finished!")

            console.log(" - Setting up map info bar.")
            setupMapInfoBar(options);
            ws_data.map_info.addTo(ws_data.map);

            console.log(" - Setting up map legend.")
            setupMapLegend(options);
            ws_data.map_legend.addTo(ws_data.map);

            console.log(" - Setting up map layer control.")
            ws_data.zones_layer.visualizationZIndex = 1
            ws_data.subway_layer.visualizationZIndex = 2
            L.control.layers(null, {
                "Zonas 777": ws_data.zones_layer,
                "Líneas de Metro": ws_data.subway_layer
                //"Sector de Destino": ws_data.sector_layer
            },
            {
                autoZIndex: true, 
                // autoZIndex is NOT WORKING!: https://stackoverflow.com/questions/16827147/layer-order-changing-when-turning-layer-on-off
                // so i prefered to use a sort function.
                // The following code should work on leaflet v1.2.0 (current is v1.0.0)
                // sortLayers: true, 
                // sortFunction: function(layerA, layerB, nameA, nameB) {
                //     // return 0: keep the same order
                //     // returns < 0: a < b
                //     // returns > 0: b < a
                //     return (layerA.visualizationZIndex - layerB.visualizationZIndex);
                // },
                position: 'topleft'
            }).addTo(ws_data.map);

            ws_data.map.on("overlayadd", function (event) {
                //ws_data.sector_layer.bringToFront();
                ws_data.subway_layer.bringToFront();
            });
        }
    );
}

function redraw(options) {
    if (ws_data.zones_layer === null) return;

    ws_data.zones_layer.setStyle(styleFunction);
    ws_data.map_legend.updateVisualization(options);
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
        ws_data.sector_group = null;
        ws_data.sector_features = [];
        redraw(options);
        if (ws_data.sector_features.length > 0) {
            ws_data.sector_group = L.geoJSON(ws_data.sector_features);
            var bounds = ws_data.sector_group.getBounds(); 
            ws_data.map.fitBounds(bounds);
        }
    }
}
