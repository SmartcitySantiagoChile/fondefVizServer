"use strict";
$(document).ready(function () {
    function MapManagerApp() {
        let _self = this;
        let sectors = null;
        let $SECTOR_SELECTOR = $("#sectorSelector");
        let $KPI_SELECTOR = $("#vizSelector");

        $SECTOR_SELECTOR.on("change", function (e) {
            _self.updateMap({});
        });
        $KPI_SELECTOR.on("change", function (e) {
            _self.updateMap({});
        });

        // data given by server
        let data = null;

        let destinationLegend = "<br /><i style='background:black'></i> Zona de destino";
        let mapOpts = {
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

        let setSectors = function (newSectors) {
            sectors = newSectors;
            let sectorList = Object.keys(sectors).map(function (el) {
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
        let setKPIs = function (KPIs) {
            // update kpi selector input
            $KPI_SELECTOR.select2({
                data: KPIs,
                minimumResultsForSearch: Infinity
            });
        };

        let getColorScale = function () {
            let checkbox = document.querySelector("#colorscale_checkbox");
            if (checkbox.checked) {
                return "sequential";
            } else {
                return "divergent";
            }
        };

        let setScaleSwitch = function () {
            let checkbox = document.querySelector("#colorscale_checkbox");
            new Switchery(checkbox, {
                size: "small",
                color: "#777",
                jackColor: "#fff",
                secondaryColor: "#777",
                jackSecondaryColor: "#fff"
            });
            checkbox.onchange = function () {
                let opts = {
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

        let printAmountOfData = function () {
            let tripQuantity = data.aggregations.sum_expansion_factor.value;
            let dataQuantity = data.hits.total;
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
            let selectedDestinationZone = opts.selectedSector || $SECTOR_SELECTOR.val();
            let scale = opts.scale || getColorScale();
            let selectedKPI = opts.KPI || $KPI_SELECTOR.val();

            let destinationZoneIds = sectors[selectedDestinationZone];

            let legendOpts = mapOpts[selectedKPI];
            mapApp.refreshMap(destinationZoneIds, scale, selectedKPI, legendOpts);
        };

        let opts = {
            getDataZoneById: function (zoneId) {
                if (data === null) {
                    return null;
                }
                let zoneData = data.aggregations[$SECTOR_SELECTOR.val()].by_zone.buckets;
                let answer = zoneData.filter(function (el) {
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
                let grades = mapOpts[kpi].grades;
                if (value < grades[0]) {
                    return null;
                }

                for (let i = 1; i < grades.length; i++) {
                    if (value <= grades[i]) {
                        return colors[i - 1];
                    }
                }
                return colors[grades.length - 1];
            }
        };
        let mapApp = new MapApp(opts);

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

        let app = new MapManagerApp();

        let afterCall = function (data, status) {
            if (status) {
                processData(data, app);
            }
        };
        let opts = {
            urlFilterData: Urls["esapi:tripMapData"](),
            afterCallData: afterCall
        };
        let manager = new FilterManager(opts);
        // load first time
        app.loadLayers(function () {
            manager.updateData();
        });
    })();
})
;