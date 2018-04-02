"use strict";
$(document).ready(function () {
    function FromToApp() {
        var _self = this;

        // data given by server
        var data = null;

        var printAmountOfData = function () {
            var quantity = data.origin_zone.hits.total;
            document.getElementById("visualization_doc_count_txt").innerHTML = quantity === 1 ? "viaje" : "viajes";
            document.getElementById("visualization_doc_count").innerHTML = quantity.toLocaleString();
        };

        this.setData = function (newData) {
            data = newData;
            printAmountOfData();
        };

        this.updateMap = function (opts) {
            console.log("updateMap method called!");

            originMapApp.refreshMap2([], _sef.getSca, "count");
            destinationMapApp.refreshMap2([], undefined, "count")
        };

        var originMapOpts = {
            getDataZoneById: function (zoneId) {
                if (data === null) {
                    return null;
                }
                var zoneData = data.origin_zone.aggregations.by_zone.buckets;
                var answer = zoneData.filter(function (el) {
                    return el.key === zoneId;
                });
                if (answer.length) {
                    return answer[0];
                }
                return null;
            },
            getZoneValue: function (zone, kpi) {
                return mapOpts[kpi].map_fn(zone);
            },
            getZoneColor: function (value, kpi, colors) {
                // use mapping
                var grades = mapOpts[kpi].grades;
                if (value < grades[0]) {
                    return null;
                }

                for (var i = 1; i < grades.length; i++) {
                    if (value <= grades[i]) {
                        return colors[i - 1];
                    }
                }
                return colors[grades.length - 1];
            },
            showMetroStations: false,
            showMacroZones: false
        };
        var destinationMapOpts = {
            getDataZoneById: function (zoneId) {
                if (data === null) {
                    return null;
                }
                var zoneData = data.destination_zone.aggregations.by_zone.buckets;
                var answer = zoneData.filter(function (el) {
                    return el.key === zoneId;
                });
                if (answer.length) {
                    return answer[0];
                }
                return null;
            },
            getZoneValue: function (zone, kpi) {
                return mapOpts[kpi].map_fn(zone);
            },
            getZoneColor: function (value, kpi, colors) {
                // use mapping
                var grades = mapOpts[kpi].grades;
                if (value < grades[0]) {
                    return null;
                }

                for (var i = 1; i < grades.length; i++) {
                    if (value <= grades[i]) {
                        return colors[i - 1];
                    }
                }
                return colors[grades.length - 1];
            },
            showMetroStations: false,
            showMacroZones: false,
            mapId: "mapChart2"
        };
        var originMapApp = new MapApp(originMapOpts);
        var destinationMapApp = new MapApp(destinationMapOpts);

        var originLayer = L.layerGroup([]);
        var destinationLayer = L.layerGroup([]);

        // syncronize maps
        var originMap = originMapApp.getMapInstance();
        var destinationMap = destinationMapApp.getMapInstance();
        originMap.sync(destinationMap);
        destinationMap.sync(originMap);

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
            urlFilterData: Urls["esapi:tripStrategiesData"](),
            afterCallData: afterCall,
            dataUrlParams: function () {
                return {
                    origins: app.getStages(),
                    destinations: app.getTransportModes()
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