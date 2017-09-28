"use strict";

// ============================================================================
// MAP FEATURE STYLING
// ============================================================================
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
        fillColor: "green",
        weight: 3,
        opacity: 1,
        color: 'green',
        dashArray: '0',
        fillOpacity: 0.5
    };
}

function styleZoneOnHover(feature) {
    return {
        weight: 5,
        color: '#666',
        dashArray: '',
        fillOpacity: 0.7
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

function styleZone(feature) {
    // no data yet
    if (ws_data.data === null) return styleZoneDefault(feature);

    // get zone data
    var zone = getDataZoneById(ws_data.data, feature.properties.id, options);
    var zone_value = getZoneValue(zone, options);

    // paint or invalid
    var zone_color = getZoneColor(zone_value, options);
    if (zone_color === null) return styleZoneNoData(feature);
    return styleZoneWithColor(feature, zone_color);
}

// returns the zone color which depends on the zone value and defined mappings
// returns null if value is invalid, the is no data or the mapping is incomplete.
function getZoneColor(value, options) {
    // sanity checks
    if (value === undefined || value === null) { return null; }
    if (options === undefined || options === null) { return null; }
    if (options.curr_visualization_type === null) { return null; }

    // use mapping
    var grades = options.visualization_mappings[options.curr_visualization_type].grades;
    var colors = options.map_colors;
    if (value < grades[0]) return null;
    for (var i=1; i<grades.length; i++) {
        if (value <= grades[i]) return colors[i-1];
    }
    return colors[grades.length - 1];
}

function getZoneValue(zone, options) {
    // missing data
    if (zone === undefined || zone === null) return null;
    if (options === undefined || options === null) return null;
    if (options.curr_visualization_type === null) return null;
    if (!(options.curr_visualization_type in options.visualization_mappings)) return null;

    return options.visualization_mappings[options.curr_visualization_type].map_fn(zone);
}

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

            var zone = getDataZoneById(ws_data.data, props.id, options);
            if (zone != null) {
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
                grades_str[i] + (grades_str[i + 1] ? '&ndash;' + grades_str[i + 1] + ' ' + grades_post_str : '+ ' + grades_post_str);
            div.innerHTML += '<br>';
        }
        div.innerHTML +=
            '<i style="background:' + "#cccccc" + '"></i>Sin Datos<br>';
    }  
}


// ============================================================================
// INTERACTIONS
// ============================================================================

function zoomToZoneEvent(e) {
    ws_data.map.fitBounds(e.target.getBounds(), {maxZoom: options.map_feature_zoom});
}

// sets feature highlight style and updates info window
function highlightZone(e) {
    var layer = e.target;
    layer.setStyle(styleZoneOnHover(layer.feature));
    ws_data.map_info.update(layer.feature.properties);
}

// resets style to default
function resetZoneHighlight(e) {
    ws_data.zones_layer.resetStyle(e.target);
    ws_data.map_info.update();
}

// hook this interactions to each zone
function onEachZoneFeature(feature, layer) {
    layer.on({
        mouseover: highlightZone,
        mouseout: resetZoneHighlight,
        click: zoomToZoneEvent
    });
}

function onEachSubwayFeature(feature, layer) {
    // do nothing!
    layer.on({});
}

function onSectorMouseOver(e) {
    ws_data.sector_layer.eachLayer(function (layer) {
        layer.setStyle({
            fillOpacity: 0.0
        });
    });
    var layer = e.target;
    ws_data.map_info.update(layer.feature.properties);
}

function onSectorMouseOut(e) {
    ws_data.sector_layer.eachLayer(function (layer) {
        layer.setStyle({
            fillOpacity: 0.5
        });
    });
    ws_data.map_info.update();
}

function zoomToSectorEvent(e) {
    zoomToCurrentSector();
}

function onEachSectorFeature(layer) {
    layer.on({
        mouseover: onSectorMouseOver,
        mouseout: onSectorMouseOut,
        click: zoomToSectorEvent
    })
}


// ============================================================================
// MAIN MAP
// ============================================================================

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
    
    // load zonas layer
    function loadZonesGeoJSON() {
        return $.ajax({
            'global': false,
            'url': '/static/js/data/zones777.geojson',
            'dataType': "json",
            'success': function (data) {
                ws_data.zones_geojson = data;
                ws_data.zones_layer = L.geoJson(data, {
                    style: styleZone,
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
            var control_mapping = {};
            control_mapping["Zonas 777"] = ws_data.zones_layer;
            control_mapping["Líneas de Metro"] = ws_data.subway_layer;
            if (options.use_map_sectors) {
                control_mapping["Sector de Destino"] = ws_data.sector_layer;
            }
            ws_data.map_layer_control = L.control.layers(
                null,
                control_mapping,
                {
                    collapsed: true,
                    autoZIndex: true,
                    position: 'topleft'
                }).addTo(ws_data.map);

            // Make sure we keep the layers in order
            ws_data.zones_layer.is_active = true;
            ws_data.sector_layer.is_active = true;
            ws_data.subway_layer.is_active = true;
            ws_data.map.on("overlayremove", function (event) {
                event.layer.is_active = false;
            });

            function rearrange_layers() {
                if (ws_data.zones_layer.is_active) ws_data.zones_layer.bringToFront();
                if (options.use_map_sectors && ws_data.sector_layer.is_active) ws_data.sector_layer.bringToFront();
                if (ws_data.subway_layer.is_active) ws_data.subway_layer.bringToFront();
            }

            ws_data.map.on("overlayadd", function (event) {
                event.layer.is_active = true;
                rearrange_layers();
            });
            rearrange_layers();
            ws_data.ready = true; 
        }
    );
}

function redraw(options) {
    if (!ws_data.ready) return;

    ws_data.zones_layer.setStyle(styleZone);
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
    var doc_count = document.getElementById("visualization_doc_count");
    var doc_count_txt = document.getElementById("visualization_doc_count_txt");
    var total = 0;
    if (options.use_map_sectors && options.curr_sector !== null && options.curr_sector in ws_data.data.aggregations) {
        total = ws_data.data.aggregations[options.curr_sector].doc_count;
    } else if (!options.use_map_sectors) {
        total = ws_data.data.hits.total;
    }
    doc_count.innerHTML = total;
    doc_count_txt.innerHTML = total == 1 ? "dato" : "datos";
}

function updateSectorLayer(options) {

    // remove all layers
    ws_data.sector_layer.clearLayers();

    // append new GeoJSON objects
    ws_data.zones_geojson.features.forEach(function(item, index) {
        var zone_id = item.properties.id;
        if (isZoneIdInCurrentSector(zone_id, options)) {
            ws_data.sector_layer.addData(item);
        }
    });

    // set style before adding elements
    ws_data.sector_layer.setStyle(styleSectorZone);

    // setup interactions
    ws_data.sector_layer.eachLayer(onEachSectorFeature);

    // add to map
    ws_data.sector_layer.addTo(ws_data.map);
}

function zoomToCurrentSector() {
    var bounds = ws_data.sector_layer.getBounds(); 
    ws_data.map.fitBounds(bounds, {maxZoom: options.map_sector_zoom});
}

function updateSelectedSector(selected, options) {
    if (options.curr_sector !== selected) {
        options.curr_sector = selected;

        updateSectorLayer(options);
        zoomToCurrentSector();
        redraw(options);
    }
}
