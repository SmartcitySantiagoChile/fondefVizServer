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
    // console.log(value, options);
    // sanity checks
    if (value === undefined || value === null) { return null; }
    if (options === undefined || options === null) { return null; }
    if (options.curr_visualization_type === null) { return null; }


    // use mapping
    var grades = options.visualization_mappings[options.curr_visualization_type].grades;
    var colors = options.curr_map_color_scale;

    if (value < options.visible_limits[0]) return null;
    if (value > options.visible_limits[1]) return null;

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

function setupMapInfoBar2(options) {
    ws_data.map_info2 = L.control({position: 'topright'});

    ws_data.map_info2.onAdd = function (map) {
        this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
        this.update();
        return this._div;
    };

    // method that we will use to update the control based on feature properties passed
    ws_data.map_info2.update = function (props) {
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
        for (var i = 0; i < grades.length-1; i++) {
            div.innerHTML +=
                '<i style="background:' + options.curr_map_color_scale[i] + '"></i> ' +
                grades_str[i] + '&ndash;' + grades_str[i + 1] + ' ' + grades_post_str;
            div.innerHTML += '<br>';
        }
        div.innerHTML +=
            '<i style="background:' + options.curr_map_color_scale[grades.length-1] + '"></i> ' +
            grades_str[i] + '+ ' + grades_post_str;
        div.innerHTML +=
            '<br><i style="background:' + "#cccccc" + '"></i>Sin Datos<br>';
    }
}

function setupMapLegendSizes(options) {
    ws_data.map_legend = L.control({position: 'bottomright'});
    ws_data.map_legend2 = L.control({position: 'bottomright'});

    ws_data.map_legend.onAdd = function (map) {
        var div = L.DomUtil.create('div', 'info legend');
        div.id = "map_legend";
        return div;
    };
    ws_data.map_legend2.onAdd = function (map) {
        var div = L.DomUtil.create('div', 'info legend');
        div.id = "map_legend2";
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
        for (var i = 0; i < grades.length-1; i++) {
            div.innerHTML +=
                '<i style="background:' + options.curr_map_color_scale[i] + '"></i> ' +
                grades_str[i] + '&ndash;' + grades_str[i + 1] + ' ' + grades_post_str;
            div.innerHTML += '<br>';
        }
        div.innerHTML +=
            '<i style="background:' + options.curr_map_color_scale[grades.length-1] + '"></i> ' +
            grades_str[i] + '+ ' + grades_post_str;
        div.innerHTML +=
            '<br><i style="background:' + "#cccccc" + '"></i>Sin Datos<br>';
    }
}

// ============================================================================
// INTERACTIONS
// ============================================================================

function zoomToZoneEvent(e) {
    ws_data.map.fitBounds(e.target.getBounds(), {maxZoom: options.map_feature_zoom});
}

function zoomToZoneEvent2(e) {
    ws_data.map2.fitBounds(e.target.getBounds(), {maxZoom: options.map_feature_zoom});
}

// sets feature highlight style and updates info window
function highlightZone(e) {
    var layer = e.target;
    layer.setStyle(styleZoneOnHover(layer.feature));
    ws_data.map_info.update(layer.feature.properties);
}

function highlightZone2(e) {
    var layer = e.target;
    layer.setStyle(styleZoneOnHover(layer.feature));
    ws_data.map_info2.update(layer.feature.properties);
}

// resets style to default
function resetZoneHighlight(e) {
    ws_data.zones_layer.resetStyle(e.target);
    ws_data.map_info.update();
}

function resetZoneHighlight2(e) {
    ws_data.zones_layer.resetStyle(e.target);
    ws_data.map_info.update();
}

function onEachODZoneFeatureMap1(feature, layer) {
    layer.on({
        click: function(e) {
            var lyr = e.target;
            var zone_id = lyr.feature.properties.id;
            origin = zone_id;
            destination = -1;

            updateServerData();

            ws_data.map.fitBounds(e.target.getBounds(), {maxZoom: options.map_feature_zoom});
            ws_data.map2.fitBounds(ws_data.zones_layer2.getBounds(), {maxZoom: options.map_default_zoom});
        }
    });
}

function onEachODZoneFeatureMap2(feature, layer) {
    layer.on({
        click: function(e) {
            var lyr = e.target;
            var zone_id = lyr.feature.properties.id;
            destination = zone_id;
            origin = -1;

            updateServerData();

            ws_data.map2.fitBounds(e.target.getBounds(), {maxZoom: options.map_feature_zoom});
            ws_data.map.fitBounds(ws_data.zones_layer.getBounds(), {maxZoom: options.map_default_zoom});
        }
    });
}

// hook this interactions to each zone
function onEachZoneFeature(feature, layer) {
    layer.on({
        mouseover: highlightZone,
        mouseout: resetZoneHighlight,
        click: zoomToZoneEvent
    });
}

function onEachZoneFeature2(feature, layer) {
    layer.on({});
}

function onEachDistrictFeature(feature, layer) {
    layer.on({});
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

function zoomToSectorEvent2(e) {
    zoomToCurrentSector2();
}

function onEachSectorFeature(layer) {
    layer.on({
        mouseover: onSectorMouseOver,
        mouseout: onSectorMouseOut,
        click: zoomToSectorEvent
    })
}

function onEachSectorFeature2(layer) {
    layer.on({
        mouseover: onSectorMouseOver2,
        mouseout: onSectorMouseOut2,
        click: zoomToSectorEvent2
    })
}


// ============================================================================
// MAIN MAP
// ============================================================================
function setupDoubleMap(options) {

    ws_data.map = L.map("mapChart").setView(options.map_default_lat_lon, options.map_min_zoom);
    ws_data.map2 = L.map("mapChart2").setView(options.map_default_lat_lon, options.map_min_zoom);

    ws_data.tile_layer = L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/light-v9/tiles/256/{z}/{x}/{y}?access_token={accessToken}', {
        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, Imagery © <a href="http://mapbox.com">Mapbox</a>',
        minZoom: options.map_min_zoom,
        maxZoom: options.map_max_zoom,
        accessToken: options.map_access_token
    }).addTo(ws_data.map);
    ws_data.tile_layer2 = L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/light-v9/tiles/256/{z}/{x}/{y}?access_token={accessToken}', {
        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, Imagery © <a href="http://mapbox.com">Mapbox</a>',
        minZoom: options.map_min_zoom,
        maxZoom: options.map_max_zoom,
        accessToken: options.map_access_token
    }).addTo(ws_data.map2);

    ws_data.map.setMaxBounds(ws_data.map.getBounds());
    ws_data.map2.setMaxBounds(ws_data.map2.getBounds());
    ws_data.map.setView(options.map_default_lat_lon, options.map_default_zoom);
    ws_data.map2.setView(options.map_default_lat_lon, options.map_default_zoom);
    ws_data.zones_map = {};

    function loadZonesGeoJSON() {
        return $.ajax({
            'global': false,
            'url': '/static/js/data/zones777.geojson',
            'dataType': "json",
            'success': function (data) {
                ws_data.zones_geojson = data;
                data.features.forEach(function(v, i){
                    var sums = v.geometry.coordinates[0].reduce(function(a,b){return [a[0]+b[0], a[1]+b[1]];});
                    ws_data.zones_map[v.properties.id] = [sums[1]/v.geometry.coordinates[0].length, sums[0]/v.geometry.coordinates[0].length]
                });
                ws_data.zones_layer = L.geoJson(data, {
                    style: {
                        weight: 1,
                        color: '#0000FF',
                        opacity: 0.5,
                        dashArray: '1',
                        fillOpacity: 0.3,
                        fillColor: '#0000FF'
                    },
                    onEachFeature: onEachODZoneFeatureMap1
                }).addTo(ws_data.map);
                ws_data.zones_layer2 = L.geoJson(data, {
                    style: {
                        weight: 1,
                        color: '#0000FF',
                        opacity: 0.5,
                        dashArray: '1',
                        fillOpacity: 0.3,
                        fillColor: '#0000FF'
                    },
                    onEachFeature: onEachODZoneFeatureMap2
                }).addTo(ws_data.map2);
            }
        });
    }

    // load zonas layer
    function loadDistrictsGeoJSON() {
        return $.ajax({
            'global': false,
            'url': '/static/js/data/comunas.geojson',
            'dataType': 'json',
            'success': function (data) {
                // ws_data.districts_geojson = data;
                ws_data.districts_layer = L.geoJson(data, {
                    style: function(feature){
                        return {
                            fillOpacity: 0.0,
                            opacity: 1,
                            color: 'black',
                            weight: 3,
                            dashArray: '3'
                        };
                    },
                    onEachFeature: onEachDistrictFeature
                }).addTo(ws_data.map);
                ws_data.districts_layer2 = L.geoJson(data, {
                    style: function(feature){
                        return {
                            fillOpacity: 0.0,
                            opacity: 1,
                            color: 'black',
                            weight: 3,
                            dashArray: '3'
                        };
                    },
                    onEachFeature: onEachDistrictFeature
                }).addTo(ws_data.map2);
            }
        });
    }

    // lineas de metro layer
    function loadMetroGeoJson() {
        return $.ajax({
            'global': false,
            'url': '/static/js/data/metro.geojson',
            'dataType': 'json',
            'success': function (data) {
                ws_data.subway_layer = L.geoJson(data, {
                    onEachFeature: onEachSubwayFeature,
                    pointToLayer: function (feature, latlng) {
                        return L.circleMarker(latlng, {
                            radius: 3,
                            fillColor: '#FF0000',
                            color: '#000000',
                            weight: 1,
                            opacity: 1,
                            fillOpacity: 1.0
                        });
                    }
                }).addTo(ws_data.map);
                ws_data.subway_layer2 = L.geoJson(data, {
                    onEachFeature: onEachSubwayFeature,
                    pointToLayer: function (feature, latlng) {
                        return L.circleMarker(latlng, {
                            radius: 3,
                            fillColor: '#FF0000',
                            color: '#000000',
                            weight: 1,
                            opacity: 1,
                            fillOpacity: 1.0
                        });
                    }
                }).addTo(ws_data.map2);

            }
        });
    }

    $.when(loadZonesGeoJSON(), loadMetroGeoJson(), loadDistrictsGeoJSON()).done(
        function(respZones, respMetro) {
            console.log(" - GeoJSON loading finished !")

            console.log(" - Setting up map info bar.")
            setupMapInfoBar(options);
            setupMapInfoBar2(options);
            ws_data.map_info.addTo(ws_data.map);
            ws_data.map_info2.addTo(ws_data.map2);

            console.log(" - Setting up map legend.")
            setupMapLegendSizes(options);
            ws_data.map_legend.addTo(ws_data.map);
            ws_data.map_legend2.addTo(ws_data.map2);

            console.log(" - Setting up map layer control.")
            var control_mapping = {};
            control_mapping["Origenes"] = ws_data.origins_layer;
            control_mapping["Zonas 777"] = ws_data.zones_layer;
            control_mapping["Comunas"] = ws_data.districts_layer;
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
            var control_mapping2 = {};
            control_mapping2["Destinos"] = ws_data.destinations_layer;
            control_mapping2["Zonas 777"] = ws_data.zones_layer2;
            control_mapping2["Comunas"] = ws_data.districts_layer2;
            control_mapping2["Líneas de Metro"] = ws_data.subway_layer2;
            if (options.use_map_sectors) {
                control_mapping2["Sector de Destino"] = ws_data.sector_layer2;
            }
            ws_data.map_layer_control2 = L.control.layers(
                null,
                control_mapping2,
                {
                    collapsed: true,
                    autoZIndex: true,
                    position: 'topleft'
                }).addTo(ws_data.map2);

            // Make sure we keep the layers in order
            ws_data.origins_layer.is_active = true;
            ws_data.zones_layer.is_active = true;
            ws_data.sector_layer.is_active = true;
            ws_data.districts_layer.is_active = true;
            ws_data.subway_layer.is_active = true;
            ws_data.map.on("overlayremove", function (event) {
                event.layer.is_active = false;
            });

            ws_data.destinations_layer.is_active = true;
            ws_data.zones_layer2.is_active = true;
            ws_data.sector_layer2.is_active = true;
            ws_data.districts_layer2.is_active = true;
            ws_data.subway_layer2.is_active = true;
            ws_data.map2.on("overlayremove", function (event) {
                event.layer.is_active = false;
            });

            function rearrange_layers() {
                if (ws_data.zones_layer.is_active) ws_data.zones_layer.bringToFront();
                if (options.use_map_sectors && ws_data.sector_layer.is_active) ws_data.sector_layer.bringToFront();
                if (ws_data.districts_layer.is_active) ws_data.districts_layer.bringToFront();
                if (ws_data.subway_layer.is_active) ws_data.subway_layer.bringToFront();
                if (ws_data.origins_layer.is_active) ws_data.origins_layer.bringToFront();

                if (ws_data.zones_layer2.is_active) ws_data.zones_layer2.bringToFront();
                if (options.use_map_sectors && ws_data.sector_layer.is_active) ws_data.sector_layer2.bringToFront();
                if (ws_data.districts_layer2.is_active) ws_data.districts_layer2.bringToFront();
                if (ws_data.subway_layer2.is_active) ws_data.subway_layer2.bringToFront();
                if (ws_data.destinations_layer.is_active) ws_data.destinations_layer.bringToFront();
            }

            ws_data.map.on("overlayadd", function (event) {
                event.layer.is_active = true;
                rearrange_layers();
            });
            ws_data.map2.on("overlayadd", function (event) {
                event.layer.is_active = true;
                rearrange_layers();
            });

            rearrange_layers();
            ws_data.ready = true;
            ws_data.ready2 = true;
        }
    );
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

    // load zonas layer
    function loadDistrictsGeoJSON() {
        return $.ajax({
            'global': false,
            'url': '/static/js/data/comunas.geojson',
            'dataType': 'json',
            'success': function (data) {
                // ws_data.districts_geojson = data;
                ws_data.districts_layer = L.geoJson(data, {
                    style: function(feature){
                        return {
                            fillOpacity: 0.0,
                            opacity: 1,
                            color: 'black',
                            weight: 3,
                            dashArray: '3'
                        };
                    },
                    onEachFeature: onEachDistrictFeature
                }).addTo(ws_data.map);
            }
        });
    }

    // lineas de metro layer
    function loadMetroGeoJson() {
        return $.ajax({
            'global': false,
            'url': '/static/js/data/metro.geojson',
            'dataType': 'json',
            'success': function (data) {
                ws_data.subway_layer = L.geoJson(data, {
                    onEachFeature: function(feature, layer){
                        var popup_text = feature.properties.name + "<br/>" + ((feature.properties.color == "#000000")?"Combinación ":"") + feature.properties.line;
                        layer.bindPopup(popup_text);
                    },
                    pointToLayer: function (feature, latlng) {
                        if(feature.properties.line=="MetroTren"){
                            return L.circleMarker(latlng, {
                                radius: 3,
                                fillColor: feature.properties.color2,
                                color: feature.properties.color1,
                                weight: 1.5,
                                opacity: 1,
                                fillOpacity: 1.0
                            });
                        }else{
                            return L.circleMarker(latlng, {
                                radius: 3,
                                fillColor: feature.properties.color,
                                color: "#000000",
                                weight: 1,
                                opacity: 1,
                                fillOpacity: 1.0
                            });
                        }
                    }
                }).addTo(ws_data.map);
            }
        });
    }

    $.when(loadZonesGeoJSON(), loadMetroGeoJson(), loadDistrictsGeoJSON()).done(
        function(respZones, respMetro, respDist) {
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
            control_mapping["Comunas"] = ws_data.districts_layer;
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
            ws_data.districts_layer.is_active = true;
            ws_data.subway_layer.is_active = true;
            ws_data.map.on("overlayremove", function (event) {
                event.layer.is_active = false;
            });

            function rearrange_layers() {
                if (ws_data.zones_layer.is_active) ws_data.zones_layer.bringToFront();
                if (options.use_map_sectors && ws_data.sector_layer.is_active) ws_data.sector_layer.bringToFront();
                if (ws_data.districts_layer.is_active) ws_data.districts_layer.bringToFront();
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
    if (ws_data.ready){
        ws_data.zones_layer.setStyle(styleZone);
        ws_data.map_legend.updateVisualization(options);
    }
    updateMapDocCount(options);
    updateMapTitle(options);
}

function redraw2(options) {
    if (ws_data.ready && ws_data.ready2){
        // ws_data.map_legend.updateVisualization(options);

        if(origin < 0 && destination < 0){
            var dcounts = ws_data.data.origin_zones.aggregations.by_zone.buckets.map(function(v, i){return v.doc_count;});
            dcounts = dcounts.concat(ws_data.data.destination_zones.aggregations.by_zone.buckets.map(function(v, i){return v.doc_count;}));
            var min_value = Math.min(...dcounts);
            var max_value = Math.max(...dcounts);
        }else if(destination < 0){ // origin selected
            var dcounts = ws_data.data.destination_zones.aggregations.by_zone.buckets.map(function(v, i){return v.doc_count;});
            var min_value = Math.min(...dcounts);
            var max_value = Math.max(...dcounts);
        }else if(origin < 0){ // destination selected
            var dcounts = ws_data.data.origin_zones.aggregations.by_zone.buckets.map(function(v, i){return v.doc_count;});
            var min_value = Math.min(...dcounts);
            var max_value = Math.max(...dcounts);
        }

        ws_data.origins_layer.clearLayers();
        if(origin < 0){
            ws_data.data.origin_zones.aggregations.by_zone.buckets.forEach(function(item, index) {
                var cm = L.circleMarker(ws_data.zones_map[item.key], {
                    radius: options.min_size + (item.doc_count-min_value)*(options.max_size-options.min_size)/(max_value-min_value),
                    fillColor: '#FFFF00',
                    weight: 0,
                    opacity: 1,
                    fillOpacity: 0.5
                }).addTo(ws_data.origins_layer);
                ws_data.origins_layer.addTo(ws_data.map);
            });
        }
        ws_data.zones_layer.eachLayer(function (layer) {
            layer.setStyle({
                weight: 1,
                color: (layer.feature.properties.id==origin)?'#FFFF00':'#0000FF',
                opacity: 0.5,
                dashArray: '1',
                fillOpacity: (layer.feature.properties.id==origin)?0.5:0.3,
                fillColor: (layer.feature.properties.id==origin)?'#FFFF00':'#0000FF'
            });
        });

        ws_data.destinations_layer.clearLayers();
        if(destination < 0){
            ws_data.data.destination_zones.aggregations.by_zone.buckets.forEach(function(item, index) {
                var cm = L.circleMarker(ws_data.zones_map[item.key], {
                    radius: options.min_size + (item.doc_count-min_value)*(options.max_size-options.min_size)/(max_value-min_value),
                    fillColor: '#A900FF',
                    weight: 0,
                    opacity: 1,
                    fillOpacity: 0.5
                }).addTo(ws_data.destinations_layer);
                ws_data.destinations_layer.addTo(ws_data.map2);
            });
        }
        ws_data.zones_layer2.eachLayer(function (layer) {
            layer.setStyle({
                weight: 1,
                color: (layer.feature.properties.id==destination)?'#A900FF':'#0000FF',
                opacity: 0.5,
                dashArray: '1',
                fillOpacity: (layer.feature.properties.id==destination)?0.5:0.3,
                fillColor: (layer.feature.properties.id==destination)?'#A900FF':'#0000FF'
            });
        });
    }
    if (ws_data.ready || ws_data.ready2){
        updateMapDocCount(options);
        updateMapTitle(options);
    }
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
        if(ws_data.data.large===undefined){
            total = ws_data.data.origin_zones.hits.total;
        }else{
            total = ws_data.data.hits.total;
        }
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

function updateSectorLayer2(options) {

    // remove all layers
    ws_data.sector_layer2.clearLayers();

    // append new GeoJSON objects
    ws_data.zones_geojson2.features.forEach(function(item, index) {
        var zone_id = item.properties.id;
        if (isZoneIdInCurrentSector(zone_id, options)) {
            ws_data.sector_layer2.addData(item);
        }
    });

    // set style before adding elements
    ws_data.sector_layer2.setStyle(styleSectorZone2);

    // setup interactions
    ws_data.sector_layer2.eachLayer(onEachSectorFeature2);

    // add to map
    ws_data.sector_layer2.addTo(ws_data.map2);
}

function zoomToCurrentSector() {
    var bounds = ws_data.sector_layer.getBounds();
    ws_data.map.fitBounds(bounds, {maxZoom: options.map_sector_zoom});
}

function zoomToCurrentSector2() {
    var bounds = ws_data.sector_layer2.getBounds();
    ws_data.map2.fitBounds(bounds, {maxZoom: options.map_sector_zoom});
}

function updateSelectedSector(selected, options) {
    if (options.curr_sector !== selected) {
        options.curr_sector = selected;

        updateSectorLayer(options);
        zoomToCurrentSector();
        redraw(options);
    }
}
