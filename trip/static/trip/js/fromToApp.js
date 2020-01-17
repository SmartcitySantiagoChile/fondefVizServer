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

        var minCircleSize = 3;
        var maxCircleSize = 23;

        var originMapLegend = L.control({position: "bottomright"});
        var destinationMapLegend = L.control({position: "bottomright"});

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
            document.getElementById("tripTotalNumberValue").innerHTML = Number(tripQuantity.toFixed(2)).toLocaleString();

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
            var min = Infinity;
            var setMaxMin = function (v) {
                max = Math.max(max, v.expansion_factor.value);
                min = Math.min(min, v.expansion_factor.value);
            };
            if (originSelected.size === 0 && destinationSelected.size === 0) {
                originZones.forEach(setMaxMin);
                destinationZones.forEach(setMaxMin);
            } else if (originSelected.size === 0) {
                originZones.forEach(setMaxMin);
                destinationZones.filter(function (el) {
                    return destinationSelected.has(el.key);
                }).forEach(setMaxMin);
            } else if (destinationSelected.size === 0) {
                destinationZones.forEach(setMaxMin);
                originZones.filter(function (el) {
                    return originSelected.has(el.key);
                }).forEach(setMaxMin);
            } else {
                originZones.filter(function (el) {
                    return originSelected.has(el.key);
                }).forEach(setMaxMin);
                destinationZones.filter(function (el) {
                    return destinationSelected.has(el.key);
                }).forEach(setMaxMin);
            }
            return {
                max: max,
                min: min
            };
        };

        var setMapLegend = function (mapInstance, control, divId) {
            control.onAdd = function (map) {
                var div = L.DomUtil.create("canvas", "info legend");
                div.id = divId;
                return div;
            };

            control.update = function () {
                // loop through our density intervals and generate a label with a colored square for each interval
                var div = document.getElementById(divId);
                div.style.display = "none";

                var bounds = getCircleBounds();

                var ctx = div.getContext("2d");
                var half = (maxCircleSize + minCircleSize) / 2.0;
                var border = 10;

                var circles = [{
                    x: border + maxCircleSize,
                    y: border + maxCircleSize,
                    r: maxCircleSize,
                    label: Number(bounds.max.toFixed(0)).toLocaleString() + " viajes"
                }, {
                    x: border + maxCircleSize,
                    y: border + 2 * maxCircleSize - half,
                    r: half,
                    label: Number(((bounds.min + bounds.max) / 2.0).toFixed(0)).toLocaleString() + " viajes"
                }, {
                    x: border + maxCircleSize,
                    y: border + 2 * maxCircleSize - minCircleSize,
                    r: minCircleSize,
                    label: Number(bounds.min.toFixed(0)).toLocaleString() + " viajes"
                }];

                // this ocurrs when select same zone as origin and destination
                if (bounds.min === bounds.max) {
                    circles =[circles[2]];
                }

                var drawCircle = function (circle) {
                    ctx.beginPath();
                    ctx.arc(circle.x, circle.y, circle.r, 0, 2 * Math.PI);
                    ctx.moveTo(circle.x, circle.y - circle.r);
                    ctx.lineTo(2 * border + 2 * maxCircleSize, circle.y - circle.r);
                    ctx.font = "small-caps 10px Arial";
                    ctx.fillText(circle.label, 2 * border + 2 * maxCircleSize, circle.y - circle.r + 4);
                    ctx.stroke();

                    var xFirstPoint = 2 * border + 2 * maxCircleSize;
                    var yFirstPoint = circle.y - circle.r;
                    ctx.beginPath();
                    ctx.moveTo(xFirstPoint, yFirstPoint);
                    ctx.lineTo(xFirstPoint - 3, yFirstPoint + 3);
                    ctx.lineTo(xFirstPoint - 3, yFirstPoint - 3);
                    ctx.closePath();
                    ctx.fill();
                };

                var maxTextLength = 0;
                circles.forEach(function (circle) {
                    maxTextLength = Math.max(maxTextLength, ctx.measureText(circle.label).width);
                });

                var width = 40 + 2 * maxCircleSize + maxTextLength;
                var height = 20 + 2 * maxCircleSize;

                div.width = width;
                div.height = height;
                ctx.clearRect(0, 0, width, height);
                circles.forEach(drawCircle);

                div.style.display = "inline";
            };
            control.addTo(mapInstance);

            return control;
        };

        this.updateMap = function () {
            console.log("updateMap method called!");
            originGroupLayer.clearLayers();
            destinationGroupLayer.clearLayers();

            var bounds = getCircleBounds();

            var originZoneInfo = {};
            originMapApp.getZoneLayer().eachLayer(function (layer) {
                originZoneInfo[layer.feature.properties.id] = {
                    center: layer.getBounds().getCenter()
                };
            });
            var destinationZoneInfo = {};
            destinationMapApp.getZoneLayer().eachLayer(function (layer) {
                destinationZoneInfo[layer.feature.properties.id] = {
                    center: layer.getBounds().getCenter()
                };
            });
            var createCircleMarker = function (position, indicator, color) {
                var boundRange = bounds.max - bounds.min === 0 ? 1 : bounds.max - bounds.min;
                var radius = minCircleSize + (indicator - bounds.min) * (maxCircleSize - minCircleSize) / boundRange;
                return L.circleMarker(position, {
                    radius: radius,
                    fillColor: color,
                    weight: 0,
                    opacity: 1,
                    fillOpacity: 0.5,
                    interactive: false
                });
            };

            originZones.forEach(function (item) {
                try {
                    createCircleMarker(originZoneInfo[item.key].center, item.expansion_factor.value, "#FFFF00").addTo(originGroupLayer);
                } catch (error) {
                    console.log(error);
                }
                });
            destinationZones.forEach(function (item) {
                try {
                    createCircleMarker(destinationZoneInfo[item.key].center, item.expansion_factor.value, "#A900FF").addTo(destinationGroupLayer);
                } catch (error) {
                    console.log(error);
                }
                });

            originMapLegend.update();
            destinationMapLegend.update();
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
            selectedColor: "#d8d813"
        });
        var destinationMapOpts = mapOptionBuilder({
            mapId: "mapChart2",
            selectedZoneSet: destinationSelected,
            getDataSource: function () {
                return destinationZones;
            },
            baseColor: "#0000FF",
            selectedColor: "#9d2bdb"
        });
        var originMapApp = new MapApp(originMapOpts);
        var destinationMapApp = new MapApp(destinationMapOpts);

        // synchronize maps
        var originMap = originMapApp.getMapInstance();
        var destinationMap = destinationMapApp.getMapInstance();

        setMapLegend(originMap, originMapLegend, "circleMapLegend1").update();
        setMapLegend(destinationMap, destinationMapLegend, "circleMapLegend2").update();

        originMap.sync(destinationMap);
        destinationMap.sync(originMap);

        originGroupLayer.addTo(originMap);
        destinationGroupLayer.addTo(destinationMap);

        this.loadLayers = function (readyFunction) {
            originMapApp.loadLayers();
            destinationMapApp.loadLayers(readyFunction);
        };
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
        loadRangeCalendar(Urls["esapi:availableTripDays"](),{});


        var app = new FromToApp();

        var afterCall = function (data) {
            console.log(data);
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