"use strict";
$(document).ready(function () {
    function FromToApp() {
        var _self = this;
        var $STAGES_SELECTOR = $(".netapas_checkbox");
        var $TRANSPORT_MODES_SELECTOR = $(".modes_checkbox");
        var originGroupLayer = L.featureGroup([]);
        var destinationGroupLayer = L.featureGroup([]);
        var originSelected = new Set([]);
        var destinationSelected = new Set([]);

        // data given by server
        var originZones = [];
        var destinationZones = [];

        [$STAGES_SELECTOR, $TRANSPORT_MODES_SELECTOR].forEach(function (el) {
            el.each(function (index, html) {
                new Switchery(html, {
                    size: "small",
                    color: "rgb(38, 185, 154)"
                });
            });
        });

        this.getStages = function () {
            return $STAGES_SELECTOR.filter(function (index, el) {
                return el.checked;
            }).map(function (index, el) {
                return el.getAttribute("data-ne-str");
            }).get();
        };

        this.getTransportModes = function () {
            return $TRANSPORT_MODES_SELECTOR.filter(function (index, el) {
                return el.checked;
            }).map(function (index, el) {
                return el.getAttribute("data-ne-str");
            }).get();
        };

        this.getOriginZones = function () {
            return Array.from(originSelected);
        };

        this.getDestinationZones = function () {
            return Array.from(destinationSelected);
        };

        var printAmountOfData = function (data) {
            var tripQuantity = data.origin_zone.aggregations.expansion_factor.value;
            var dataQuantity = data.origin_zone.hits.total;
            document.getElementById("tripTotalNumberLabel").innerHTML = tripQuantity === 1 ? "viaje" : "viajes";
            document.getElementById("tripTotalNumberValue").innerHTML = tripQuantity.toLocaleString();

            document.getElementById("dataTotalNumberLabel").innerHTML = dataQuantity === 1 ? "dato" : "datos";
            document.getElementById("dataTotalNumberValue").innerHTML = dataQuantity.toLocaleString();
        };

        this.setData = function (newData) {
            printAmountOfData(newData);
            originZones = newData.origin_zone.aggregations.by_zone.buckets;
            destinationZones = newData.destination_zone.aggregations.by_zone.buckets;
        };

        var getCircleBounds = function () {
            var max = 0;
            var min = 0;
            var setMaxMin = function (v) {
                max = Math.max(max, v.expansion_factor.value);
                min = Math.min(min, v.expansion_factor.value);
            };
            if (originSelected.size === 0 && destinationSelected.size === 0) {
                originZones.forEach(setMaxMin);
                destinationZones.forEach(setMaxMin);
            } else if (originSelected.size === 0) {
                originZones.forEach(setMaxMin);
            } else if (destinationSelected.size === 0) {
                destinationZones.forEach(setMaxMin);
            }
            return {
                max: max,
                min: min
            };
        };

        this.updateMap = function (opts) {
            console.log("updateMap method called!");
            originGroupLayer.clearLayers();
            destinationGroupLayer.clearLayers();

            var bounds = getCircleBounds();
            var minSize = 3;
            var maxSize = 23;

            var originZoneInfo = {};
            originMapApp.getZoneLayer().eachLayer(function (layer) {
                originZoneInfo[layer.feature.properties.id] = {
                    center: layer.getBounds().getCenter()
                    // properties: layer.feature.properties
                };
            });
            var destinationZoneInfo = {};
            destinationMapApp.getZoneLayer().eachLayer(function (layer) {
                destinationZoneInfo[layer.feature.properties.id] = {
                    center: layer.getBounds().getCenter()
                    // properties: layer.feature.properties
                };
            });
            var createCircleMarker = function (position, indicator, color, zoneId) {
                var radius  = minSize + (Math.round(indicator) - bounds.min) * (maxSize - minSize) / (bounds.max - bounds.min);
                return L.circleMarker(position, {
                    radius: radius,
                    fillColor: color,
                    weight: 0,
                    opacity: 1,
                    fillOpacity: 0.5,
                    // zoneId: zoneId,
                    interactive: false
                });
            };

            originZones.forEach(function (item) {
                var cm = createCircleMarker(originZoneInfo[item.key].center, item.expansion_factor.value, "#FFFF00", item.key).addTo(originGroupLayer);
                /*
                cm.on("mouseover", function(e) {
                    originMapApp.refreshZoneInfoControl(zoneInfo[e.target.options.zoneId].properties, item);
                });
                cm.on("mouseout", function() {
                    originMapApp.refreshZoneInfoControl();
                });*/
            });
            destinationZones.forEach(function (item) {
                var cm = createCircleMarker(destinationZoneInfo[item.key].center, item.expansion_factor.value, "#A900FF", item.key).addTo(destinationGroupLayer);
                /*
                cm.on("mouseover", function(e) {
                    destinationMapApp.refreshZoneInfoControl(zoneInfo[e.target.options.zoneId].properties, item);
                });
                cm.on("mouseout", function() {
                    destinationMapApp.refreshZoneInfoControl();
                });*/
            });
        };

        var mapOptionBuilder = function (opts) {
            return {
                mapId: opts.mapId,
                hideMapLegend: true,
                showMetroStations: false,
                showMacroZones: false,
                defaultZoneStyle: function (feature) {
                    var zoneId = feature.properties.id;
                    var color = originSelected.has(zoneId) ? opts.selectedColor : opts.baseColor;
                    var fillOpacity = originSelected.has(zoneId) ? 0.5 : 0.3;
                    return {
                        weight: 1,
                        color: color,
                        opacity: 0.5,
                        dashArray: "1",
                        fillOpacity: fillOpacity,
                        fillColor: color
                    };
                },
                onClickZone: function (e) {
                    var layer = e.target;
                    var zoneId = layer.feature.properties.id;
                    if (opts.selectedZoneSet.has(zoneId)) {
                        opts.selectedZoneSet.delete(zoneId);
                        this.defaultOnMouseoutZone(e);
                        this.defaultOnMouseinZone(e);
                    } else {
                        opts.selectedZoneSet.add(zoneId);
                        layer.setStyle(this.styles.zoneWithColor(layer.feature, opts.selectedColor));
                    }
                },
                onMouseinZone: function (e) {
                    var layer = e.target;
                    var zoneId = layer.feature.properties.id;
                    if (!opts.selectedZoneSet.has(zoneId)) {
                        this.defaultOnMouseinZone(e);
                    }
                    var zoneData = opts.getDataSource().find(function (el) {
                        return el.key === zoneId;
                    });
                    this.refreshZoneInfoControl(layer.feature.properties, zoneData);
                },
                onMouseoutZone: function (e) {
                    var layer = e.target;
                    var zoneId = layer.feature.properties.id;
                    if (!opts.selectedZoneSet.has(zoneId)) {
                        this.defaultOnMouseoutZone(e);
                    }
                    this.refreshZoneInfoControl();
                }
            };
        };

        var originMapOpts = mapOptionBuilder({
            mapId: "mapChart",
            selectedZoneSet: originSelected,
            getDataSource: function () {
                return originZones;
            },
            baseColor: "#0000FF",
            selectedColor: "#FFFF00"
        });
        var destinationMapOpts = mapOptionBuilder({
            mapId: "mapChart2",
            selectedZoneSet: destinationSelected,
            getDataSource: function () {
                return destinationZones;
            },
            baseColor: "#0000FF",
            selectedColor: "#A900FF"
        });
        var originMapApp = new MapApp(originMapOpts);
        var destinationMapApp = new MapApp(destinationMapOpts);

        // syncronize maps
        var originMap = originMapApp.getMapInstance();
        var destinationMap = destinationMapApp.getMapInstance();
        originMap.sync(destinationMap);
        destinationMap.sync(originMap);

        originGroupLayer.addTo(originMap);
        destinationGroupLayer.addTo(destinationMap);

        this.loadLayers = function (readyFunction) {
            originMapApp.loadLayers();
            destinationMapApp.loadLayers(readyFunction);
        }
    }

    function processData(data, app) {
        if (data.status) {
            return;
        }
        app.setData(data);
        app.updateMap();
    }

    // load filters
    (function () {
        loadAvailableDays(Urls["esapi:availableTripDays"]());

        var app = new FromToApp();

        var afterCall = function (data) {
            processData(data, app);
        };
        var opts = {
            urlFilterData: Urls["esapi:fromToMapData"](),
            afterCallData: afterCall,
            dataUrlParams: function () {
                return {
                    stages: app.getStages(),
                    transportModes: app.getTransportModes(),
                    originZones: app.getOriginZones(),
                    destinationZones: app.getDestinationZones()
                }
            }
        };
        var manager = new FilterManager(opts);
        // load first time
        app.loadLayers(function () {
            manager.updateData();
        });
    })();
})
;