"use strict";
$(document).ready(function () {
    function FromToApp() {
        var _self = this;
        var originSelected = new Set([]);
        var destinationSelected = new Set([]);

        var mapZoneInfoLegend = L.control({position: "topright"});
        var mapLegend = L.control({position: "bottomright"});

        // data given by server
        var data = null;

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
            data = newData;
            printAmountOfData(newData);
        };

        this.updateMap = function (opts) {
            console.log("updateMap method called!");
        };

        var colors = {
            none: "#CCCCCC",
            origin: "#fc8d59",
            destination: "#ffffbf",
            both: "#91bfdb"
        };

        var setZoneStyle = function (layer) {
            var zoneId = layer.feature.properties.id;
            if (originSelected.has(zoneId) && destinationSelected.has(zoneId)) {
                layer.setStyle(mapApp.styles.zoneWithColor(layer.feature, colors.both));
            } else if (originSelected.has(zoneId) && !destinationSelected.has(zoneId)) {
                layer.setStyle(mapApp.styles.zoneWithColor(layer.feature, colors.origin));
            } else if (!originSelected.has(zoneId) && destinationSelected.has(zoneId)) {
                layer.setStyle(mapApp.styles.zoneWithColor(layer.feature, colors.destination));
            } else {
                layer.setStyle(mapApp.styles.zoneWithoutData(layer.feature));
            }
        };

        var mapOpts = {
            hideMapLegend: true,
            hideZoneLegend: true,
            showMetroStations: false,
            showMacroZones: false,
            onClickZone: function (e) {
                var layer = e.target;
                var zoneId = layer.feature.properties.id;
                if (originSelected.has(zoneId) && destinationSelected.has(zoneId)) {
                    originSelected.delete(zoneId);
                    destinationSelected.delete(zoneId);
                } else if (originSelected.has(zoneId) && !destinationSelected.has(zoneId)) {
                    originSelected.delete(zoneId);
                    destinationSelected.add(zoneId);
                } else if (!originSelected.has(zoneId) && destinationSelected.has(zoneId)) {
                    originSelected.add(zoneId);
                } else {
                    originSelected.add(zoneId);
                }
                setZoneStyle(layer);
                layer.setStyle(this.styles.zoneOnHover());
            },
            onMouseinZone: function (e) {
                var zoneId = e.target.feature.properties.id;
                mapZoneInfoLegend.update(zoneId);
                this.defaultOnMouseinZone(e);
            },
            onMouseoutZone: function (e) {
                var layer = e.target;
                mapZoneInfoLegend.update();
                setZoneStyle(layer);
            }
        };

        var mapApp = new MapApp(mapOpts);

        var constructZoneInfoLegend = function () {
            mapZoneInfoLegend.onAdd = function (map) {
                var div = L.DomUtil.create("div", "info legend");
                div.id = "mapZoneInfoLegend";
                return div;
            };

            mapZoneInfoLegend.update = function (zoneId) {
                zoneId = zoneId || "";
                var div = document.getElementById("mapZoneInfoLegend");
                div.innerHTML = "<h4>Zonificación 777: </h4>";
                div.innerHTML += "<b>Zona " + zoneId + "</b>";
            };
            mapZoneInfoLegend.addTo(mapApp.getMapInstance());
            mapZoneInfoLegend.update();
        };

        var constructColorLenged = function () {
            mapLegend.onAdd = function (map) {
                var div = L.DomUtil.create("div", "info legend");
                div.id = "mapLegend";
                return div;
            };

            mapLegend.update = function () {
                var div = document.getElementById("mapLegend");
                div.innerHTML = "<h4>Leyenda: </h4>";
                var rows = [{
                    label: "Zonas no seleccionadas",
                    color: colors.none
                }, {
                    label: "Zonas de origen",
                    color: colors.origin
                }, {
                    label: "Zonas de destino",
                    color: colors.destination
                }, {

                    label: "Zonas de origen y destino",
                    color: colors.both
                }];
                rows.forEach(function (el) {
                    div.innerHTML += "<i style='background:" + el.color + "'></i><b> " + el.label + "</b>";
                    div.innerHTML += "<br />";
                });
            };
            mapLegend.addTo(mapApp.getMapInstance());
            mapLegend.update();
        };

        this.loadLayers = function (readyFunction) {
            constructColorLenged();
            constructZoneInfoLegend();
            mapApp.loadLayers(readyFunction);
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

        var app = new FromToApp();

        var afterCall = function (data) {
            processData(data, app);
        };
        var opts = {
            urlFilterData: Urls["esapi:fromToMapData"](),
            afterCallData: afterCall,
            dataUrlParams: function () {
                return {
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