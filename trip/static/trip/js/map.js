"use strict";

function MapApp(opts) {
    var _self = this;

    var getDataZoneById = opts.getDataZoneById || null;
    var getZoneValue = opts.getZoneValue || null;
    var getZoneColor = opts.getZoneColor || null;
    var mapId = opts.mapId || "mapChart";
    var maxZoom = opts.maxZoom || 15;
    var minZoom = opts.minZoom || 8;
    var maxBounds = opts.maxBounds || L.latLngBounds(L.latLng(-33.697721, -70.942223), L.latLng(-33.178138, -70.357465));
    var showMetroStations= opts.showMetroStations===undefined?true:opts.showMetroStations;
    var showMacroZones = opts.showMacroZones===undefined?true:opts.showMacroZones;

    /* map options */
    var mapDefaultLocation = L.latLng(-33.459229, -70.645348);
    var accessToken = "pk.eyJ1IjoidHJhbnNhcHB2aXMiLCJhIjoiY2l0bG9qd3ppMDBiNjJ6bXBpY3J0bm40cCJ9.ajifidV4ypi0cXgiGQwR-A";

    var map = L.map(mapId).setView(mapDefaultLocation, minZoom);
    L.tileLayer("https://api.mapbox.com/styles/v1/mapbox/light-v9/tiles/256/{z}/{x}/{y}?access_token={accessToken}", {
        attribution: "Map data &copy; <a href='http://openstreetmap.org'>OpenStreetMap</a> contributors, Imagery © <a href='http://mapbox.com'>Mapbox</a>",
        minZoom: minZoom,
        maxZoom: maxZoom,
        accessToken: accessToken
    }).addTo(map);
    map.setMaxBounds(maxBounds);

    var visibleLimits = [0, 0];
    var defaultZoom = 11;
    var sectorZoom = 12;
    var featureZoom = 12;

    var scales = {
        // http://colorbrewer2.org/#type=sequential&scheme=GnBu&n=5
        sequential: ["#ffffb2", "#fecc5c", "#fd8d3c", "#f03b20", "#bd0026"],
        // http://colorbrewer2.org/#type=diverging&scheme=Spectral&n=5
        divergent: ["#2b83ba", "#abdda4", "#ffffbf", "#fdae61", "#d7191c"]
    };

    var zoneGeoJSON = null;
    var subwayLayer = L.geoJSON();
    var zoneLayer = L.geoJSON();
    var districtLayer = L.geoJSON();
    var destinationZoneLayer = L.geoJSON();

    function rearrangeLayers() {
        var layers = [zoneLayer, destinationZoneLayer, districtLayer, subwayLayer];
        layers.forEach(function (layer) {
            if (layer.isActive) {
                layer.bringToFront();
            }
        });
    }

    map.on("overlayremove", function (event) {
        event.layer.isActive = false;
    });
    map.on("overlayadd", function (event) {
        event.layer.isActive = true;
        //rearrangeLayers();
    });

    var mapInfoBar = L.control({position: "topright"});
    var mapLegend = L.control({position: "bottomright"});

    this.getMapInstance = function () {
        return map;
    };
    // ============================================================================
    // MAP FEATURE STYLING
    // ============================================================================
    this.styles = {
        defaultZone: function (feature) {
            return {
                weight: 1,
                opacity: 0.5,
                color: "white",
                dashArray: "3",
                fillOpacity: 0.1
            };
        },
        zoneWithoutData: function (feature) {
            return {
                fillColor: "#cccccc",
                weight: 1,
                opacity: 1,
                color: "white",
                dashArray: "3",
                fillOpacity: 0.8
            };
        },
        zoneWithColor: function (feature, color) {
            return {
                fillColor: color,
                weight: 1,
                opacity: 1,
                color: "white",
                dashArray: "3",
                fillOpacity: 0.8
            };
        },
        destinationZone: function (feature) {
            return {
                fillColor: "green",
                weight: 3,
                opacity: 1,
                color: "green",
                dashArray: "0",
                fillOpacity: 0.5
            };
        },
        zoneOnHover: function (feature) {
            return {
                weight: 5,
                color: "#666",
                dashArray: "",
                fillOpacity: 0.7
            };
        },
        subway: function (feature) {
            return {
                weight: 4,
                opacity: 1,
                color: feature.properties.color,
                dashArray: "0"
            };
        },
        district: function (feature) {
            return {
                fillOpacity: 0.0,
                opacity: 1,
                color: "black",
                weight: 3,
                dashArray: "3"
            };
        }
    };

    function zoomToZoneEvent(e) {
        map.flyToBounds(e.target.getBounds(), {
            maxZoom: featureZoom
        });
    }

    function onSectorMouseOver(e) {
        destinationZoneLayer.setStyle({
            fillOpacity: 0.0
        });
        var layer = e.target;
        mapInfoBar.update(layer.feature.properties);
    }

    function onSectorMouseOut(e) {
        destinationZoneLayer.setStyle({
            fillOpacity: 0.5
        });
        mapInfoBar.update();
    }

    this.refreshMap = function (destinationZoneIds, scale, kpi, legendOpts) {
        console.log("refreshMap");
        // remove all layers
        destinationZoneLayer.clearLayers();
        zoneLayer.clearLayers();

        zoneGeoJSON.features.forEach(function (feature) {
            var zoneId = feature.properties.id;
            if (destinationZoneIds.indexOf(zoneId) >= 0) {
                destinationZoneLayer.addData(feature);
            } else {
                zoneLayer.addData(feature);
            }
        });

        // set style before adding elements
        destinationZoneLayer.setStyle(_self.styles.destinationZone);
        // setup interactions
        destinationZoneLayer.eachLayer(function (layer) {
            layer.on({
                mouseover: onSectorMouseOver,
                mouseout: onSectorMouseOut
                //click: zoomToZoneEvent
            });
        });

        zoneLayer.eachLayer(function (layer) {
            var feature = layer.feature;
            var zoneId = feature.properties.id;
            var zoneData = getDataZoneById(zoneId);
            var style = _self.styles.zoneWithoutData(feature);
            if (zoneData !== null) {
                var zoneValue = getZoneValue(zoneData, kpi);
                var zoneColor = getZoneColor(zoneValue, kpi, scales[scale]);
                if (zoneColor !== null) {
                    style = _self.styles.zoneWithColor(feature, zoneColor);
                }
            }
            layer.setStyle(style);
            layer.on({
                mouseover: function (e) {
                    // highlight style
                    var selectedLayer = e.target;
                    selectedLayer.setStyle(_self.styles.zoneOnHover(selectedLayer.feature));
                    mapInfoBar.update(selectedLayer.feature.properties, zoneData);
                },
                mouseout: function (e) {
                    // restore style
                    var selectedLayer = e.target;
                    selectedLayer.setStyle(style);
                    mapInfoBar.update();
                }
                //click: zoomToZoneEvent
            });
        });

        // add to map
        destinationZoneLayer.addTo(map);
        zoneLayer.addTo(map);
        legendOpts.scale = scales[scale];
        mapLegend.update(legendOpts);
        rearrangeLayers();
    };

    var setupMapInfoBar = function () {
        mapInfoBar.onAdd = function (map) {
            this._div = L.DomUtil.create("div", "info"); // create a div with a class "info"
            this.update();
            return this._div;
        };

        // method that we will use to update the control based on feature properties passed
        mapInfoBar.update = function (zoneProps, zoneData) {
            // console.log(zoneProps);
            // console.log(zoneData);
            this._div.innerHTML = "<h4>Zonificación 777</h4>";
            if (zoneProps) {
                this._div.innerHTML += "<b>Información de la zona " + zoneProps.id + "</b>";

                if (zoneData !== undefined && zoneData !== null) {
                    this._div.innerHTML +=
                        "<br/> - # Datos: " + zoneData.doc_count.toLocaleString() +
                        "<br/> - # Viajes: " + zoneData.expansion_factor.value.toLocaleString() +
                        "<br/> - # Etapas promedio: " + Number(zoneData.n_etapas.value.toFixed(2)).toLocaleString() +
                        "<br/> - Duración promedio: " + Number(zoneData.tviaje.value.toFixed(1)).toLocaleString() + " [min]" +
                        "<br/> - Distancia promedio (en ruta): " + Number((zoneData.distancia_ruta.value / 1000.0).toFixed(2)).toLocaleString() + " [km]" +
                        "<br/> - Distancia promedio (euclideana): " + Number((zoneData.distancia_eucl.value / 1000.0).toFixed(2)).toLocaleString() + " [km]";
                } else {
                    this._div.innerHTML += "<br/> Sin información para los filtros<br/> seleccionados";
                }
            } else {
                this._div.innerHTML += "Pon el ratón sobre una zona";
            }
        };
        mapInfoBar.addTo(map);
    };

    function setupMapLegend() {
        mapLegend.onAdd = function (map) {
            var div = L.DomUtil.create("div", "info legend");
            div.id = "map_legend";
            return div;
        };

        mapLegend.update = function (options) {
            var grades = options.grades;
            var grades_str = options.grades_str;
            var grades_post_str = options.legend_post_str;
            var scale = options.scale;

            // loop through our density intervals and generate a label with a colored square for each interval
            var div = document.getElementById("map_legend");
            div.innerHTML = "";
            for (var i = 0; i < grades.length - 1; i++) {
                div.innerHTML += "<i style='background:" + scale[i] + "'></i> " +
                    grades_str[i] + "&ndash;" + grades_str[i + 1] + " " + grades_post_str;
                div.innerHTML += "<br />";
            }
            div.innerHTML += "<i style='background:" + scale[grades.length - 1] + "'></i> " +
                grades_str[i] + "+ " + grades_post_str;
            div.innerHTML += "<br><i style='background:" + "#cccccc" + "'></i>Sin Datos<br>";
        };
        mapLegend.addTo(map);
    }

    this.loadLayers = function (readyFunction) {
        function loadZoneGeoJSON() {
            var url = "/static/js/data/zones777.geojson";
            return $.getJSON(url, function (data) {
                zoneGeoJSON = data;
                zoneLayer.clearLayers();
                zoneLayer.addLayer(L.geoJson(data, {
                    style: _self.styles.zoneWithoutData(),
                    onEachFeature: function (feature, layer) {
                        layer.on({
                            mouseover: function (e) {
                                var currentLayer = e.target;
                                currentLayer.setStyle(_self.styles.zoneOnHover(currentLayer.feature));
                                mapInfoBar.update(currentLayer.feature.properties);
                            },
                            mouseout: function (e) {
                                var currentLayer = e.target;
                                currentLayer.setStyle(_self.styles.zoneWithoutData(currentLayer.feature));
                                mapInfoBar.update(currentLayer.feature.properties);
                            },
                            click: zoomToZoneEvent
                        });
                    }
                }));
            });
        }

        function loadSubwayGeoJSON() {
            var url = "/static/js/data/metro.geojson";
            return $.getJSON(url, function (data) {
                subwayLayer.clearLayers();
                subwayLayer.addLayer(L.geoJson(data, {
                    onEachFeature: function (feature, layer) {
                        var popupText = feature.properties.name + "<br/>" + ((feature.properties.color === "#000000") ? "Combinación " : "") + feature.properties.line;
                        layer.bindPopup(popupText);
                    },
                    pointToLayer: function (feature, latlng) {
                        if (feature.properties.line === "MetroTren") {
                            return L.circleMarker(latlng, {
                                radius: 3,
                                fillColor: feature.properties.color2,
                                color: feature.properties.color1,
                                weight: 1.5,
                                opacity: 1,
                                fillOpacity: 1.0
                            });
                        } else {
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
                }));
            });
        }

        function loadDistrictGeoJSON() {
            var url = "/static/js/data/comunas.geojson";
            return $.getJSON(url, function (data) {
                districtLayer.clearLayers();
                districtLayer.addLayer(L.geoJson(data, {
                    style: _self.styles.district
                }));
            });
        }

        var shapesToLoad = [loadZoneGeoJSON()];
        if (showMetroStations){
            shapesToLoad.push(loadSubwayGeoJSON());
        }
        if(showMacroZones){
            shapesToLoad.push(loadDistrictGeoJSON());
        }

        $.when(...shapesToLoad)
            .done(function () {
                setupMapInfoBar();
                setupMapLegend();

                var controlMapping = {
                    "Zonas 777": zoneLayer
                };
                if (showMetroStations){
                    controlMapping["Estaciones de Metro"] = subwayLayer;
                    subwayLayer.addTo(map);
                }
                if (showMacroZones){
                    controlMapping["Comunas"] = districtLayer;
                    districtLayer.addTo(map);
                }
                L.control.layers(
                    null,
                    controlMapping, {
                        collapsed: true,
                        autoZIndex: true,
                        position: "topleft"
                    }).addTo(map);

                zoneLayer.addTo(map);
                destinationZoneLayer.addTo(map);

                map.flyToBounds(zoneLayer.getBounds());
                if (readyFunction !== undefined) {
                    readyFunction();
                }
            });
    };
}