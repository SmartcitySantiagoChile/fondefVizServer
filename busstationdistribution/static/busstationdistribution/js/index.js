"use strict";
$(document).ready(function () {
    function IndexApp() {
        var _self = this;

        this.getDataName = function () {
            var FILE_NAME = "Validaciones en zona paga ";
            return FILE_NAME + $("#authRouteFilter").val();
        };

        var _datatable = $("#validationDetail").DataTable({
            lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "Todos"]],
            language: {
                url: "//cdn.datatables.net/plug-ins/1.10.13/i18n/Spanish.json",
                decimal: ",",
                thousands: "."
            },
            columns: [
                {
                    "targets": 0,
                    "searchable": false,
                    "orderable": false,
                    "className": "text-center",
                    "data": "visible",
                    "render": function (data, type, full, meta) {
                        return $("<input>")
                            .attr("type", "checkbox")
                            .attr("name", "trip" + full.id)
                            .addClass("flat")
                            .attr("checked", full.valid)[0].outerHTML;
                    }
                },
                {
                    title: "Perfil de carga", data: "sparkLoadProfile", searchable: false,
                    render: function (data, type, row) {
                        return $("<i>").addClass("spark").append(data.join(","))[0].outerHTML;
                    }
                },
                {title: "Patente (capacidad)", data: "busDetail", searchable: true},
                {title: "Período inicio expedición", data: "authTimePeriod", searchable: true},
                {title: "Hora de inicio", data: "timeTripInit", searchable: true},
                {title: "Hora de fin", data: "timeTripEnd", searchable: true},
                {title: "Tipo de día", data: "dayType", searchable: true},
                {title: "Válida", data: "valid", searchable: true,
                    render: function (data) {
                        return data?"Válida":"No válida";
                    }
                }
            ],
            order: [[4, "asc"]]
        });

        var _updateDatatable = function () {
            var dataset = _dataManager.getDatatableData();
            var rows = dataset.rows;
            var maxHeight = dataset.maxHeight;

            _datatable.clear();
            _datatable.rows.add(rows);
            _datatable.columns.adjust().draw();
        };

        this.updateDatatable = function () {
            _updateDatatable();
        };
    }

    function processData(dataSource, app) {
        console.log(dataSource);

        if (dataSource.status && (dataSource.status.code !== 252 && dataSource.status.code !== 253)) {
            return;
        }

        var trips = dataSource.trips;
        var stops = dataSource.stops;
        var busStations = dataSource.busStations;
        var shape = dataSource.shape;

        var dataManager = new DataManager();
        dataManager.shape(shape);

        if (dataSource.groupedTrips) {
            busStations = dataSource.groupedTrips.aggregations.stop.station.buckets.map(function (el) {
                return el.key;
            });
            var yAxisDataResult = {
                expandedAlighting: [],
                expandedBoarding: [],
                loadProfile: [],
                saturationRate: [],
                maxLoad: []
            };
            var groupedStops = {};
            dataSource.groupedTrips.aggregations.stops.buckets.forEach(function (el) {
                groupedStops[el.key] = {
                    expandedBoarding: el.expandedBoarding.value,
                    loadProfile: el.loadProfile.value,
                    expandedAlighting: el.expandedAlighting.value,
                    busSaturation: el.busSaturation.value,
                    distOnPath: el.pathDistance.hits.hits[0]._source.stopDistanceFromPathStart,
                    expeditionNumber: el.doc_count,
                    maxLoadProfile: el.maxLoadProfile.value
                }
            });

            var expeditionNumber = 0;
            stops.forEach(function (stop) {
                var item = groupedStops[stop.authStopCode];
                var itemIsNull = item === undefined;

                var expandedAlighting = itemIsNull ? null : item.expandedAlighting;
                var expandedBoarding = itemIsNull ? null : item.expandedBoarding;
                var loadProfile = itemIsNull ? null : item.loadProfile;
                var saturationRate = itemIsNull ? null : item.busSaturation * 100;
                var maxLoadProfile = itemIsNull ? null : item.maxLoadProfile;

                yAxisDataResult.expandedAlighting.push(expandedAlighting);
                yAxisDataResult.expandedBoarding.push(expandedBoarding);
                yAxisDataResult.loadProfile.push(loadProfile);
                yAxisDataResult.saturationRate.push(saturationRate);
                yAxisDataResult.maxLoad.push(maxLoadProfile);

                var expNumber = itemIsNull ? 0 : item.expeditionNumber;
                expeditionNumber = Math.max(expNumber, expeditionNumber);
            });

            dataManager.yAxisData(yAxisDataResult);
            var tripGroupXAxisData = stops.map(function (stop) {
                stop.busStation = busStations.indexOf(stop.authStopCode) >= 0;
                return stop;
            });
            dataManager.xAxisData(tripGroupXAxisData);
            app.dataManager(dataManager);
            app.updateCharts(expeditionNumber);
            app.updateDatatable();
        } else {
            for (var expeditionId in trips) {
                var trip = trips[expeditionId];

                // trip info
                var capacity = trip.info[0];
                var licensePlate = trip.info[1];
                var route = trip.info[2];
                var authTimePeriod = trip.info[3];
                var timeTripInit = trip.info[4];
                var timeTripEnd = trip.info[5];
                var dayType = trip.info[6];
                var valid = trip.info[7];

                var yAxisData = {
                    expandedAlighting: [],
                    expandedBoarding: [],
                    loadProfile: [],
                    saturationRate: [],
                    valueIsNull: []
                };

                stops.forEach(function (stop) {
                    var item = trip.stops[stop.authStopCode];
                    var itemIsNull = item === undefined;

                    var expandedAlighting = itemIsNull ? null : item[2];
                    var expandedBoarding = itemIsNull ? null : item[1];
                    var loadProfile = itemIsNull ? null : item[0];
                    var saturationRate = itemIsNull ? null : loadProfile / capacity * 100;

                    yAxisData.expandedAlighting.push(expandedAlighting);
                    yAxisData.expandedBoarding.push(expandedBoarding);
                    yAxisData.loadProfile.push(loadProfile);
                    yAxisData.saturationRate.push(saturationRate);
                    yAxisData.valueIsNull.push(itemIsNull)
                });

                trip = new Trip(expeditionId, route, licensePlate, capacity, timeTripInit,
                    timeTripEnd, authTimePeriod, dayType, yAxisData, valid);
                dataManager.addTrip(trip);
            }
            var tripXAxisData = stops.map(function (stop) {
                stop.busStation = busStations.indexOf(stop.authStopCode) >= 0;
                return stop;
            });
            dataManager.xAxisData(tripXAxisData);
            dataManager.calculateAverage();
            app.dataManager(dataManager);
            app.updateCharts();
            app.updateDatatable();
        }
    }

    // load filters
    (function () {
        loadAvailableDays(Urls["esapi:availableProfileDays"]());

        var app = new ExpeditionApp();
        var previousCall = function () {
            app.showLoadingAnimationCharts();
        };
        var afterCall = function (data) {
            processData(data, app);
            app.hideLoadingAnimationCharts();
        };
        var opts = {
            urlFilterData: Urls["esapi:loadProfileByExpeditionData"](),
            urlRouteData: Urls["esapi:availableProfileRoutes"](),
            previousCallData: previousCall,
            afterCallData: afterCall
        };

        new FilterManager(opts);
    })()
});