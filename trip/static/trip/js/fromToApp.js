"use strict";
$(document).ready(function () {
    function FromToApp() {
        var _self = this;
        var $STAGES_SELECTOR = $(".netapas_checkbox");
        var $TRANSPORT_MODES_SELECTOR = $(".modes_checkbox");

        [$STAGES_SELECTOR, $TRANSPORT_MODES_SELECTOR].forEach(function (el) {
            el.each(function (index, html) {
                new Switchery(html, {
                    size: 'small',
                    color: 'rgb(38, 185, 154)'
                });
            });
        });

        // data given by server
        var data = null;
        var mapOpts = {
            count: {
                name: 'Cantidad de viajes',
                grades: [1, 10, 20, 30, 40],
                grades_str: ["1", "10", "20", "30", "40"],
                legend_post_str: "",
                map_fn: function (zone) {
                    return zone.doc_count;
                }
            }
        };

        this.getStages = function () {
            return $STAGES_SELECTOR.filter(function (index, el) {
                return el.checked;
            }).map(function (index, el) {
                return el.getAttribute('data-ne-str')
            }).get();
        };

        this.getTransportModes = function () {
            return $TRANSPORT_MODES_SELECTOR.filter(function (index, el) {
                return el.checked;
            }).map(function (index, el) {
                return el.getAttribute('data-ne-str')
            }).get();
        };

        var printAmountOfData = function () {
            var tripQuantity = data.aggregations.sum_expansion_factor.value;
            var dataQuantity = data.origin_zone.hits.total;
            document.getElementById("tripTotalNumberLabel").innerHTML = tripQuantity === 1 ? "viaje" : "viajes";
            document.getElementById("tripTotalNumberValue").innerHTML = tripQuantity.toLocaleString();

            document.getElementById("dataTotalNumberLabel").innerHTML = dataQuantity === 1 ? "dato" : "datos";
            document.getElementById("dataTotalNumberValue").innerHTML = dataQuantity.toLocaleString();
        };

        this.setData = function (newData) {
            data = newData;
            printAmountOfData();
        };

        this.calculateBounds = function () {
            if (origin.length === 0 && destination.length === 0) {
                var dcounts = data.origin_zones.by_zone.buckets.map(function (v) {
                    return v.doc_count;
                });
                dcounts = dcounts.concat(data.destination_zones.by_zone.buckets.map(function (v) {
                    return v.doc_count;
                }));
                var minValue = Math.min(...dcounts);
                var maxValue = Math.max(...dcounts);
            } else if (destination.length === 0) { // origin selected
                var dcounts = ws_data.data.destination_zones.by_zone.buckets.map(function (v, i) {
                    return v.doc_count;
                });
                var minValue = Math.min(...dcounts);
                var maxValue = Math.max(...dcounts);
            } else if (origin.length === 0) { // destination selected
                var dcounts = ws_data.data.origin_zones.by_zone.buckets.map(function (v, i) {
                    return v.doc_count;
                });
                var minValue = Math.min(...dcounts);
                var maxValue = Math.max(...dcounts);
            }

            return {
                minValue: minValue,
                maxValue: maxValue
            }
        };
        this.updateMap = function (opts) {
            console.log("updateMap method called!");

            originMapApp.refreshMap2([], _self.getSca, "count");
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