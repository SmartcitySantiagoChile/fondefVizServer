"use strict";

function MapApp(opts) {
    let _self = this;

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
                fillColor: "black",
                weight: 3,
                opacity: 1,
                color: "black",
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
    let getDataZoneById = opts.getDataZoneById || null;
    let getZoneValue = opts.getZoneValue || null;
    let getZoneColor = opts.getZoneColor || null;
    let mapId = opts.mapId || "mapChart";
    let maxZoom = opts.maxZoom || 15;
    let minZoom = opts.minZoom || 8;
    let maxBounds = opts.maxBounds || new mapboxgl.LngLatBounds(new mapboxgl.LngLat(-70.942223, -33.697721), new mapboxgl.LngLat(-70.357465, -33.178138));
    let showMetroStations = opts.showMetroStations === undefined ? true : opts.showMetroStations;
    let showMacroZones = opts.showMacroZones === undefined ? true : opts.showMacroZones;
    let selectedStyle = opts.tileLayer || "light";
    let mapStartLocation = opts.startLocation || new mapboxgl.LngLat(-70.645348, -33.459229);
    let onClickZone = opts.onClickZone || function (e) {
        _self.zoomToZoneEvent(e);
    };
    let onMouseoutZone = opts.onMouseoutZone || function (e) {
        _self.defaultOnMouseoutZone(e);
    };
    let onMouseinZone = opts.onMouseinZone || function (e) {
        _self.defaultOnMouseinZone(e);
    };
    let hideMapLegend = opts.hideMapLegend || false;
    let hideZoneLegend = opts.hideZoneLegend || false;
    let defaultZoneStyle = opts.defaultZoneStyle || _self.styles.zoneWithoutData;
    let defaultOverZoneStyle = opts.defaultOverZoneStyle || _self.styles.zoneOnHover;
    let doubleClickZoom = opts.doubleClickZoom || false;
    let zoomControl = opts.zoomControl === undefined ? true : opts.zoomControl;
    let styles = {
        "streets": "mapbox://styles/mapbox/streets-v11",
        "light": "mapbox://styles/mapbox/light-v10",
        "dark": "mapbox://styles/mapbox/dark-v10"
    };
    selectedStyle = styles[selectedStyle];
    let onLoad = opts.onLoad || (() => {});

    /* map options */
    let mapboxAccessToken = "pk.eyJ1IjoiYWRhdHJhcCIsImEiOiJja29hdnk4aXYwM3lsMzJuMnhnNW1xb2RlIn0.Fvn0zCbCeXAjMYmDeEqMmw";
    mapboxgl.accessToken = mapboxAccessToken;
    let map = new mapboxgl.Map({
        container: mapId,
        center: mapStartLocation,
        zoom: minZoom,
        doubleClickZoom: doubleClickZoom,
        minZoom: minZoom,
        maxZoom: maxZoom,
        style: selectedStyle,
        trackResize: true
    });

    map.on('load', () => {
        if (zoomControl) {
            let navigationControl = new mapboxgl.NavigationControl({});
            map.addControl(navigationControl, 'top-left');
        }

        map.setMaxBounds(maxBounds);

        let visibleLimits = [0, 0];
        let defaultZoom = 11;
        let sectorZoom = 12;
        let featureZoom = 12;

        let scales = {
            // http://colorbrewer2.org/#type=sequential&scheme=GnBu&n=5
            sequential: ["#ffffb2", "#fecc5c", "#fd8d3c", "#f03b20", "#bd0026"],
            // http://colorbrewer2.org/#type=diverging&scheme=Spectral&n=5
            divergent: ["#2b83ba", "#abdda4", "#ffffbf", "#fdae61", "#d7191c"]
        };

        let zoneGeoJSON = null;
        let subwayLayer = {
            id: 'subway-layer',
            source: '',
            type: '',
            layout: {},
            paint: {}
        };
        let zoneLayer = {
            id: 'zone-layer',
            source: '',
            type: '',
            layout: {},
            paint: {}
        };
        let districtLayer = {
            id: 'district-layer',
            source: '',
            type: '',
            layout: {},
            paint: {}
        };
        let destinationZoneLayer = {
            id: 'destination-zone-layer',
            source: '',
            type: '',
            layout: {},
            paint: {}
        };

        function rearrangeLayers() {
            let layers = [zoneLayer, destinationZoneLayer, districtLayer, subwayLayer];
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
        });

        let mapInfoBar = {};
        let mapLegend = {};

        this.getMapInstance = function () {
            return map;
        };

        this.getZoneLayer = function () {
            return zoneLayer;
        };

        this.refreshZoneInfoControl = function (properties, zoneData) {
            if (!hideZoneLegend) {
                mapInfoBar.update(properties, zoneData);
            }
        };

        this.defaultOnMouseoutZone = function (e) {
            let currentLayer = e.target;
            currentLayer.setStyle(defaultZoneStyle(currentLayer.feature));
            _self.refreshZoneInfoControl(currentLayer.feature.properties);
        };

        this.defaultOnMouseinZone = function (e) {
            let currentLayer = e.target;
            currentLayer.setStyle(defaultOverZoneStyle(currentLayer.feature));
            _self.refreshZoneInfoControl(currentLayer.feature.properties);
        };

        this.zoomToZoneEvent = function (e) {
            map.flyToBounds(e.target.getBounds(), {
                maxZoom: featureZoom
            });
        };

        function onSectorMouseOver(e) {
            destinationZoneLayer.setStyle({
                fillOpacity: 0.0
            });
            let layer = e.target;
            _self.refreshZoneInfoControl(layer.feature.properties);
        }

        function onSectorMouseOut(e) {
            destinationZoneLayer.setStyle({
                fillOpacity: 0.5
            });
            _self.refreshZoneInfoControl();
        }

        this.refreshMap = function (destinationZoneIds, scale, kpi, legendOpts) {
            console.log("refreshMap");
            // remove all layers
            destinationZoneLayer.clearLayers();
            zoneLayer.clearLayers();

            zoneGeoJSON.features.forEach(function (feature) {
                let zoneId = feature.properties.id;
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

            _self.refreshZoneLayer(kpi, scale);

            // add to map
            destinationZoneLayer.addTo(map);
            zoneLayer.addTo(map);
            legendOpts.scale = scales[scale];
            mapLegend.update(legendOpts);
            rearrangeLayers();
        };

        this.refreshZoneLayer = function (kpi, scale) {
            zoneLayer.eachLayer(function (layer) {
                let feature = layer.feature;
                let zoneId = feature.properties.id;
                let zoneData = getDataZoneById(zoneId);
                let style = _self.styles.zoneWithoutData(feature);
                if (zoneData !== null) {
                    let zoneValue = getZoneValue(zoneData, kpi);
                    let zoneColor = getZoneColor(zoneValue, kpi, scales[scale]);
                    if (zoneColor !== null) {
                        style = _self.styles.zoneWithColor(feature, zoneColor);
                    }
                }
                layer.setStyle(style);
                layer.on({
                    mouseover: function (e) {
                        // highlight style
                        let selectedLayer = e.target;
                        selectedLayer.setStyle(_self.styles.zoneOnHover(selectedLayer.feature));
                        _self.refreshZoneInfoControl(selectedLayer.feature.properties, zoneData);
                    },
                    mouseout: function (e) {
                        // restore style
                        let selectedLayer = e.target;
                        selectedLayer.setStyle(style);
                        _self.refreshZoneInfoControl();
                    }
                });
            });
        };

        let setupMapInfoBar = function () {
            mapInfoBar.onAdd = function (map) {
                this._div = document.createElement('div');
                this._div.className = 'info';
                this.update();
                return this._div;
            };

            // method that we will use to update the control based on feature properties passed
            mapInfoBar.update = function (zoneProps, zoneData) {
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
                    this._div.innerHTML += 'Pon el ratón sobre una zona';
                }
            };

            mapInfoBar.onRemove = function () {
                this._div.parentNode.removeChild(this._div);
            }

            map.addControl(mapInfoBar, 'top-right');
        };

        function setupMapLegend() {
            mapLegend.onAdd = function (map) {
                this._div = document.createElement('div');
                this._div.className = 'info legend';
                this._div.id = 'map_legend';
                return this._div;
            };

            mapLegend.update = function (options) {
                let name = options.name || '';
                let grades = options.grades;
                let grades_str = options.grades_str;
                let grades_post_str = options.legend_post_str;
                let scale = options.scale;

                // loop through our density intervals and generate a label with a colored square for each interval
                let div = document.getElementById("map_legend");
                div.innerHTML = name + "<br />";
                for (let i = 0; i < grades.length - 1; i++) {
                    div.innerHTML += "<i style='background:" + scale[i] + "'></i> " +
                      grades_str[i] + "&ndash;" + grades_str[i + 1] + " " + grades_post_str;
                    div.innerHTML += "<br />";
                }
                div.innerHTML += "<i style='background:" + scale[grades.length - 1] + "'></i> " +
                  grades_str[i] + "+ " + grades_post_str;
                div.innerHTML += "<br><i style='background:" + "#cccccc" + "'></i>Sin Datos<br>";
            };

            mapLegend.onRemove = function () {
                this._div.parentNode.removeChild(this._div);
            }

            map.addControl(mapLegend, 'bottom-right');
        }

        this.loadLayers = function (readyFunction) {
            function loadZoneGeoJSON() {
                let url = "/static/js/data/zones777.geojson";
                return $.getJSON(url, function (data) {
                    zoneGeoJSON = data;
                    zoneLayer.clearLayers();
                    let geojsonLayer = L.geoJson(data, {
                        onEachFeature: function (feature, layer) {
                            layer.on({
                                mouseover: function (e) {
                                    onMouseinZone.call(_self, e);
                                },
                                mouseout: function (e) {
                                    onMouseoutZone.call(_self, e);
                                },
                                click: function (e) {
                                    onClickZone.call(_self, e);
                                }
                            });
                            layer.setStyle(defaultZoneStyle(feature));
                        }
                    });
                    geojsonLayer.getLayers().forEach(function (layer) {
                        zoneLayer.addLayer(layer);
                    });
                });
            }

            function loadSubwayGeoJSON() {
                let url = "/static/js/data/metro.geojson";
                return $.getJSON(url, function (data) {
                    subwayLayer.clearLayers();
                    subwayLayer.addLayer(L.geoJson(data, {
                        onEachFeature: function (feature, layer) {
                            let popupText = feature.properties.name + "<br/>" + ((feature.properties.color === "#000000") ? "Combinación " : "") + feature.properties.line;
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
                let url = "/static/js/data/comunas.geojson";
                return $.getJSON(url, function (data) {
                    districtLayer.clearLayers();
                    districtLayer.addLayer(L.geoJson(data, {
                        style: _self.styles.district
                    }));
                });
            }

            let shapesToLoad = [loadZoneGeoJSON()];
            if (showMetroStations) {
                shapesToLoad.push(loadSubwayGeoJSON());
            }
            if (showMacroZones) {
                shapesToLoad.push(loadDistrictGeoJSON());
            }

            $.when(...shapesToLoad)
              .done(function () {
                  if (!hideZoneLegend) {
                      setupMapInfoBar();
                  }
                  if (!hideMapLegend) {
                      setupMapLegend();
                  }

                  let controlMapping = {
                      "Zonas 777": zoneLayer
                  };
                  if (showMetroStations) {
                      controlMapping["Estaciones de Metro"] = subwayLayer;
                      subwayLayer.addTo(map);
                  }
                  if (showMacroZones) {
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

        this.fitBound = function (sourceList) {
            let bounds = null;
            sourceList.forEach(sourceName => {
               let geojson = map.getSource(sourceName)._data;
               if (geojson.type === 'FeatureCollection') {
                   geojson.features.forEach(feature => {
                       // mejorar esto
                      if (bounds === null) {
                        bounds = new mapboxgl.LngLatBounds();
                      } else {
                        bounds.extend(feature.geometry.coordinates);
                      }
                   });
               }
            });

            if (bounds !== null) {
                map.fitBounds(bounds, {
                    padding: 20
                });
            }
        };

        this.resize = function() {
            map.resize();
        }

        onLoad(map);
    });
}