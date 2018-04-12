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
                return el.getAttribute('data-ne-str')
            }).get();
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
                max = Math.max(max, v.doc_count);
                min = Math.min(min, v.doc_count);
            };
            if (originSelected.size===0 && destinationSelected.size===0){
                originZones.forEach(setMaxMin);
                destinationZones.forEach(setMaxMin);
            } else if (originSelected.size===0){
                originZones.forEach(setMaxMin);
            } else if (destinationSelected.size===0) {
                destinationZones.forEach(setMaxMin);
            }
            return {
                max: max,
                min: min
            }
        };

        this.updateMap = function (opts) {
            console.log("updateMap method called!");
            originGroupLayer.clearLayers();
            destinationGroupLayer.clearLayers();

            var bounds = getCircleBounds();
            var minSize = 3;
            var maxSize = 23;

            var location = {};
            originMapApp.getZoneLayer().eachLayer(function (layer) {
                location[layer.feature.properties.id] = layer.getBounds().getCenter();
                layer.setStyle({
                    weight: 1,
                    color: (originSelected.has(layer.feature.properties.id) >= 0) ? '#FFFF00' : '#0000FF',
                    opacity: 0.5,
                    dashArray: '1',
                    fillOpacity: (originSelected.has(layer.feature.properties.id, origin) >= 0) ? 0.5 : 0.3,
                    fillColor: (originSelected.has(layer.feature.properties.id, origin) >= 0) ? '#FFFF00' : '#0000FF'
                });
            });
            if (originSelected.size===0){
                originZones.forEach(function (item) {
                    var cm = L.circleMarker(location[item.key], {
                        radius: minSize + (item.doc_count - bounds.min) * (maxSize - minSize) / (bounds.max - bounds.min),
                        fillColor: '#FFFF00',
                        weight: 0,
                        opacity: 1,
                        fillOpacity: 0.5,
                        zone_id: item.key
                    }).addTo(originGroupLayer);
                    // cm.on('mouseover', onEachBallFeatureMap1);
                    // cm.on('mouseout', resetStats1);
                });
            }
        };

        var mapOptionBuilder = function(opts) {
            return {
                mapId: opts.mapId,
                showMetroStations: false,
                showMacroZones: false,
                onClickZone: function(e) {
                    var layer = e.target;
                    var zoneId = layer.feature.properties.id;
                    if (opts.selectedZoneSet.has(zoneId)) {
                        opts.selectedZoneSet.delete(zoneId);
                        this.defaultOnMouseoutZone(e);
                        this.defaultOnMouseinZone(e);
                    } else {
                        opts.selectedZoneSet.add(zoneId);
                        layer.setStyle(this.styles.zoneWithColor(layer.feature, "#7dc142"));
                    }
                },
                onMouseinZone: function (e) {
                    var layer = e.target;
                    var zoneId = layer.feature.properties.id;
                    if (!opts.selectedZoneSet.has(zoneId)) {
                        this.defaultOnMouseinZone(e);
                    }
                    var zoneData = opts.getDataSource().find(function(el){
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
            getDataSource: function () { return originZones; }
        });
        var destinationMapOpts = mapOptionBuilder({
            mapId: "mapChart2",
            selectedZoneSet: destinationSelected,
            getDataSource: function () { return destinationZones;}
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
                    transportModes: app.getTransportModes()
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