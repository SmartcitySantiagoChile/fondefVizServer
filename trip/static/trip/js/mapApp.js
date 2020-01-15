"use strict";
$(document).ready(function () {
    function MapManagerApp() {
        var _self = this;
        var sectors = null;
        var $SECTOR_SELECTOR = $("#sectorSelector");
        var $KPI_SELECTOR = $("#vizSelector");

        $SECTOR_SELECTOR.on("change", function (e) {
            _self.updateMap({});
        });
        $KPI_SELECTOR.on("change", function (e) {
            _self.updateMap({});
        });

        // data given by server
        var data = null;

        var destinationLegend = "<br /><i style='background:black'></i> Zona de destino";
        var mapOpts = {
            tviaje: {
                name: "Tiempo de viaje" + destinationLegend,
                grades: [0, 30, 45, 60, 75],
                grades_str: ["0", "30", "45", "60", "75"],
                legend_post_str: "min",
                map_fn: function (zone) {
                    return zone.tviaje.value;
                }
            },
            distancia_ruta: {
                name: "Distancia en ruta" + destinationLegend,
                grades: [0, 1000, 5000, 10000, 20000],
                grades_str: ["0", "1", "5", "10", "20"],
                legend_post_str: "km",
                map_fn: function (zone) {
                    return zone.distancia_ruta.value;
                }
            },
            distancia_eucl: {
                name: "Distancia euclideana" + destinationLegend,
                grades: [0, 1000, 5000, 10000, 20000],
                grades_str: ["0", "1", "5", "10", "20"],
                legend_post_str: "km",
                map_fn: function (zone) {
                    return zone.distancia_eucl.value;
                }
            },
            n_etapas: {
                name: "Número de etapas" + destinationLegend,
                grades: [1.0, 1.5, 2.0, 2.5, 3.0],
                grades_str: ["1.0", "1.5", "2.0", "2.5", "3.0"],
                legend_post_str: "",
                map_fn: function (zone) {
                    return zone.n_etapas.value;
                }
            },
            count: {
                name: "Número de viajes" + destinationLegend,
                grades: [1, 5, 25, 50, 75],
                grades_str: ["1", "5", "25", "50", "75"],
                legend_post_str: "",
                map_fn: function (zone) {
                    return zone.expansion_factor.value;
                }
            }
        };

        var setSectors = function (newSectors) {
            sectors = newSectors;
            var sectorList = Object.keys(sectors).map(function (el) {
                return {
                    id: el,
                    text: el
                };
            });
            // update sector selector input
            $SECTOR_SELECTOR.select2({
                data: sectorList,
                minimumResultsForSearch: Infinity // hide search box
            });
        };
        var setKPIs = function (KPIs) {
            // update kpi selector input
            $KPI_SELECTOR.select2({
                data: KPIs,
                minimumResultsForSearch: Infinity
            });
        };

        var getColorScale = function () {
            var checkbox = document.querySelector("#colorscale_checkbox");
            if (checkbox.checked) {
                return "sequential";
            } else {
                return "divergent";
            }
        };

        var setScaleSwitch = function () {
            var checkbox = document.querySelector("#colorscale_checkbox");
            new Switchery(checkbox, {
                size: "small",
                color: "#777",
                jackColor: "#fff",
                secondaryColor: "#777",
                jackSecondaryColor: "#fff"
            });
            checkbox.onchange = function () {
                var opts = {
                    scale: getColorScale()
                };
                _self.updateMap(opts);
            };
        };
        setScaleSwitch();

        this.setControls = function (newSectors, KPIs) {
            setSectors(newSectors);
            setKPIs(KPIs);
        };

        var printAmountOfData = function () {
            var tripQuantity = data.aggregations.sum_expansion_factor.value;
            var dataQuantity = data.hits.total;
            document.getElementById("tripTotalNumberLabel").innerHTML = tripQuantity === 1 ? "viaje" : "viajes";
            document.getElementById("tripTotalNumberValue").innerHTML = tripQuantity.toLocaleString();

            document.getElementById("dataTotalNumberLabel").innerHTML = dataQuantity === 1 ? "dato" : "datos";
            document.getElementById("dataTotalNumberValue").innerHTML = dataQuantity.toLocaleString();
        };

        this.setData = function (newData) {
            data = newData;
            printAmountOfData();
        };

        this.updateMap = function (opts) {
            console.log("updateMap method called!");
            // destination
            var selectedDestinationZone = opts.selectedSector || $SECTOR_SELECTOR.val();
            var scale = opts.scale || getColorScale();
            var selectedKPI = opts.KPI || $KPI_SELECTOR.val();

            var destinationZoneIds = sectors[selectedDestinationZone];

            var legendOpts = mapOpts[selectedKPI];
            mapApp.refreshMap(destinationZoneIds, scale, selectedKPI, legendOpts);
        };

        var opts = {
            getDataZoneById: function (zoneId) {
                if (data === null) {
                    return null;
                }
                var zoneData = data.aggregations[$SECTOR_SELECTOR.val()].by_zone.buckets;
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
            }
        };
        var mapApp = new MapApp(opts);

        this.loadLayers = function (readyFunction) {
            mapApp.loadLayers(readyFunction);
        }
    }

    function processData(data, app) {
        app.setControls(data.sectors, data.KPIs);
        app.setData(data.map);
        app.updateMap({});
    }

    // load filters
    (function () {
        loadAvailableDays(Urls["esapi:availableTripDays"]());
        loadRangeCalendar(Urls["esapi:availableTripDays"](),{});


        var app = new MapManagerApp();

        var afterCall = function (data) {
            processData(data, app);
        };
        var opts = {
            urlFilterData: Urls["esapi:tripMapData"](),
            afterCallData: afterCall
        };
        var manager = new FilterManager(opts);
        // load first time
        app.loadLayers(function () {
            manager.updateData();
        });
    })();
})
;