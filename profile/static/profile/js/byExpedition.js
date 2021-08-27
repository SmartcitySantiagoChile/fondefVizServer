"use strict";
$(document).ready(function () {
    // define logic to manipulate data
    function Trip(expeditionDayId, route, licensePlate, busCapacity, timeTripInit, timeTripEnd, authTimePeriod, dayType,
                  yAxisData, valid, passengerWithEvasionPerKmSectionSum, capacityPerKmSectionSum) {
        this.expeditionId = expeditionDayId;
        this.route = route;
        this.licensePlate = licensePlate;
        this.busCapacity = busCapacity;
        this.timeTripInit = timeTripInit;
        this.timeTripEnd = timeTripEnd;
        this.authTimePeriod = authTimePeriod;
        this.dayType = dayType;
        this.yAxisData = yAxisData;
        this.valid = valid;
        this.visible = valid === undefined ? true : valid;
        this.passengerWithEvasionPerKmSectionSum = passengerWithEvasionPerKmSectionSum;
        this.capacityPerKmSectionSum = capacityPerKmSectionSum;
    }

    /*
     * to manage grouped data
     */
    function DataManager() {
        // trips
        let _trips = [];
        // stops
        let _xAxisData = null;
        // y average data
        let _yAxisData = null;
        // trips to show in profile view
        let _visibleTrips = 0;
        let _shape = [];
        let _boardingWithAlightingPercentage = 0;
        let _utilizationCoefficient = 0;

        this.trips = function (trips) {
            if (trips === undefined) {
                return _trips;
            }
            _visibleTrips = 0;
            trips.forEach(function (trip) {
                if (trip.visible) {
                    _visibleTrips++;
                }
            });
            _trips = trips;
        };
        this.addTrip = function (trip) {
            if (trip.visible) {
                _visibleTrips++;
            }
            // create trip identifier
            trip.id = _trips.length;
            _trips.push(trip);
        };
        this.xAxisData = function (data) {
            if (data === undefined) {
                return _xAxisData;
            }
            _xAxisData = data;
        };
        this.yAxisData = function (data) {
            if (data === undefined) {
                return _yAxisData;
            }
            _yAxisData = data;
        };
        this.shape = function (shape) {
            if (shape === undefined) {
                return _shape;
            }
            _shape = shape;
        };
        this.tripsUsed = function () {
            return _visibleTrips;
        };
        this.clearData = function () {
            _trips = [];
            _xAxisData = null;
            _yAxisData = null;
            _visibleTrips = 0;
        };
        this.setVisibilty = function (tripIdArray, value) {
            tripIdArray.forEach(function (tripId) {
                if (_trips[tripId].visible !== value) {
                    if (value === false) {
                        _visibleTrips--;
                    } else {
                        _visibleTrips++;
                    }
                }
                _trips[tripId].visible = value;
            });
        };
        this.checkAllAreVisible = function (tripIdArray) {
            var result = tripIdArray.length;
            tripIdArray.forEach(function (tripId) {
                if (!_trips[tripId].visible) {
                    result--;
                }
            });
            return result;
        };
        this.calculateAverage = function () {
            // erase previous visible data
            let xAxisLength = _xAxisData.length;
            let counterByStop = [];
            let capacityByStop = [];
            let boardingTotal = 0;
            let boardingWithAlightingTotal = 0;
            let passengerWithEvasionPerKmSectionTotal = 0;
            let capacityPerKmSectionTotal = 0;

            _yAxisData = {
                expandedAlighting: [],
                expandedBoarding: [],
                loadProfile: [],
                saturationRate: [],
                valueIsNull: [],
                maxLoad: [],
                loadProfileWithEvasion: [],
                expandedEvasionBoarding: [],
                expandedEvasionAlighting: [],
                expandedBoardingPlusExpandedEvasionBoarding: [],
                expandedAlightingPlusExpandedEvasionAlighting: [],
                maxLoadWithEvasion: [],
                saturationRateWithEvasion: []
            };
            for (var i = 0; i < xAxisLength; i++) {
                _yAxisData.expandedBoarding.push(0);
                _yAxisData.expandedAlighting.push(0);
                _yAxisData.loadProfile.push(0);
                _yAxisData.maxLoad.push(0);
                _yAxisData.loadProfileWithEvasion.push(0);
                _yAxisData.expandedEvasionBoarding.push(0);
                _yAxisData.expandedEvasionAlighting.push(0);
                _yAxisData.expandedBoardingPlusExpandedEvasionBoarding.push(0);
                _yAxisData.expandedAlightingPlusExpandedEvasionAlighting.push(0);
                _yAxisData.maxLoadWithEvasion.push(0);

                capacityByStop.push(0);
                counterByStop.push(0);
            }
            _trips.forEach(function (trip) {
                if (!trip.visible) {
                    return;
                }

                for (let stopIndex = 0; stopIndex < xAxisLength; stopIndex++) {
                    if (trip.yAxisData.valueIsNull[stopIndex]) {
                        continue;
                    }
                    _yAxisData.expandedAlighting[stopIndex] += trip.yAxisData.expandedAlighting[stopIndex];
                    _yAxisData.expandedBoarding[stopIndex] += trip.yAxisData.expandedBoarding[stopIndex];
                    _yAxisData.loadProfile[stopIndex] += trip.yAxisData.loadProfile[stopIndex];
                    _yAxisData.maxLoad[stopIndex] = Math.max(_yAxisData.maxLoad[stopIndex], trip.yAxisData.loadProfile[stopIndex]);
                    _yAxisData.loadProfileWithEvasion[stopIndex] += trip.yAxisData.loadProfileWithEvasion[stopIndex];
                    _yAxisData.expandedEvasionBoarding[stopIndex] += trip.yAxisData.expandedEvasionBoarding[stopIndex];
                    _yAxisData.expandedEvasionAlighting[stopIndex] += trip.yAxisData.expandedEvasionAlighting[stopIndex];
                    _yAxisData.expandedBoardingPlusExpandedEvasionBoarding[stopIndex] += trip.yAxisData.expandedBoardingPlusExpandedEvasionBoarding[stopIndex];
                    _yAxisData.expandedAlightingPlusExpandedEvasionAlighting[stopIndex] += trip.yAxisData.expandedAlightingPlusExpandedEvasionAlighting[stopIndex];
                    _yAxisData.maxLoadWithEvasion[stopIndex] = Math.max(_yAxisData.maxLoadWithEvasion[stopIndex], trip.yAxisData.loadProfileWithEvasion[stopIndex]);

                    capacityByStop[stopIndex] += trip.busCapacity;
                    counterByStop[stopIndex]++;
                    boardingTotal += trip.yAxisData.boarding[stopIndex];
                    boardingWithAlightingTotal += trip.yAxisData.boardingWithAlighting[stopIndex];
                    passengerWithEvasionPerKmSectionTotal += trip.passengerWithEvasionPerKmSectionSum;
                    capacityPerKmSectionTotal += trip.capacityPerKmSectionSum;
                }
            });
            // it calculates average
            for (let stopIndex = 0; stopIndex < xAxisLength; stopIndex++) {
                _yAxisData.expandedAlighting[stopIndex] = _yAxisData.expandedAlighting[stopIndex] / counterByStop[stopIndex];
                _yAxisData.expandedBoarding[stopIndex] = _yAxisData.expandedBoarding[stopIndex] / counterByStop[stopIndex];
                let saturationRate = (_yAxisData.loadProfile[stopIndex] / capacityByStop[stopIndex]) * 100;
                _yAxisData.saturationRate.push(saturationRate);
                let saturationRateWithEvasion = (_yAxisData.loadProfileWithEvasion[stopIndex] / capacityByStop[stopIndex]) * 100;
                _yAxisData.saturationRateWithEvasion.push(saturationRateWithEvasion);
                _yAxisData.loadProfile[stopIndex] = _yAxisData.loadProfile[stopIndex] / counterByStop[stopIndex];
                _yAxisData.loadProfileWithEvasion[stopIndex] = _yAxisData.loadProfileWithEvasion[stopIndex] / counterByStop[stopIndex];
                _yAxisData.expandedEvasionBoarding[stopIndex] = _yAxisData.expandedEvasionBoarding[stopIndex] / counterByStop[stopIndex];
                _yAxisData.expandedEvasionAlighting[stopIndex] = _yAxisData.expandedEvasionAlighting[stopIndex] / counterByStop[stopIndex];
                _yAxisData.expandedBoardingPlusExpandedEvasionBoarding[stopIndex] = _yAxisData.expandedBoardingPlusExpandedEvasionBoarding[stopIndex] / counterByStop[stopIndex];
                _yAxisData.expandedAlightingPlusExpandedEvasionAlighting[stopIndex] = _yAxisData.expandedAlightingPlusExpandedEvasionAlighting[stopIndex] / counterByStop[stopIndex];
            }

            this._utilizationCoefficient = passengerWithEvasionPerKmSectionTotal / capacityPerKmSectionTotal;
            this._boardingWithAlightingPercentage = boardingWithAlightingTotal / boardingTotal * 100;
        };

        this.getDatatableData = function () {
            var values = [];
            var max = 0;
            for (var i in _trips) {
                var trip = $.extend({}, _trips[i]);
                trip.busDetail = trip.licensePlate + " (" + trip.busCapacity + ")";
                var loadProfile = [];
                for (var k = 0; k < _xAxisData.length; k++) {
                    var value = trip.yAxisData.loadProfile[k];
                    max = Math.max(max, value);
                    loadProfile.push(value);
                }
                trip.sparkLoadProfile = loadProfile;
                values.push(trip);
            }
            return {
                rows: values,
                maxHeight: max
            };
        };

        this.getDistributionData = function () {
            var globalMax = 0;
            var trips = [];

            for (var i in _trips) {
                var trip = _trips[i];
                var tripData = {};
                if (!trip.visible) {
                    continue;
                }
                tripData.name = trip.timeTripInit;

                var loadProfile = [];
                for (var j = 0; j < _xAxisData.length; j++) {
                    var value = trip.yAxisData.loadProfile[j];
                    if (globalMax < value) {
                        globalMax = value;
                    }
                    loadProfile.push(value);
                }
                tripData.loadProfile = loadProfile;
                trips.push(tripData);
            }

            return {
                globalMax: globalMax,
                trips: trips
            };
        }
    }

    function ExpeditionApp() {
        var _self = this;

        var mapOpts = {
            mapId: "mapid"
        };
        var _mappApp = new MapApp(mapOpts);
        var _routeLayer = L.featureGroup([]);
        var _circleLayer = L.featureGroup([]);
        var _mapInstance = _mappApp.getMapInstance();
        _routeLayer.addTo(_mapInstance);
        _circleLayer.addTo(_mapInstance);

        var fitBoundFirstTime = true;
        $("#tab-1").click(function () {
            setTimeout(function () {
                _mapInstance.invalidateSize(false);
                if (fitBoundFirstTime) {
                    setTimeout(function () {
                        _mappApp.fitBound();
                        fitBoundFirstTime = false;
                    }, 400);
                }
            }, 400);
        });
        $("#tab-0").click(function () {
            setTimeout(function () {
                _self.resizeCharts();
            }, 400);
        });

        this.getDataName = function () {
            var FILE_NAME = "Perfil de carga ";
            return FILE_NAME + $("#authRouteFilter").val();
        };

        var _dataManager = new DataManager();
        var _barChart = echarts.init(document.getElementById("barChart"), theme);
        var _datatable = $("#expeditionDetail").DataTable({
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
                    title: "Perfil de carga sin evasión", data: "sparkLoadProfile", searchable: false,
                    render: function (data, type, row) {
                        return $("<i>").addClass("spark").append(data.join(","))[0].outerHTML;
                    }
                },
                {title: "Patente (capacidad)", data: "busDetail", searchable: true},
                {title: "Período inicio expedición", data: "authTimePeriod", searchable: true},
                {title: "Hora de inicio", data: "timeTripInit", searchable: true},
                {title: "Hora de fin", data: "timeTripEnd", searchable: true},
                {title: "Tipo de día", data: "dayType", searchable: true},
                {
                    title: "Válida", data: "valid", searchable: true,
                    render: function (data) {
                        return data ? "Válida" : "No válida";
                    }
                }
            ],
            order: [[4, "asc"]],
            createdRow: function (row, data, index) {
                if (data.visible) {
                    $(row).addClass("success");
                }
            },
            initComplete: function (settings) {
                // Handle click on "Select all" control
                var mainCheckbox = $("#checkbox-select-all");
                mainCheckbox.iCheck({
                    labelHover: false,
                    cursor: true,
                    checkboxClass: "icheckbox_flat-green"
                });
                mainCheckbox.on("ifToggled", function (event) {
                    // Get all rows with search applied
                    if (_dataManager.trips().length === 0) {
                        return;
                    }
                    var rows = _datatable.rows({"search": "applied"}).nodes();
                    var addToAggr = false;
                    var inputs = $("input.flat", rows);
                    if (event.target.checked) {
                        inputs.prop("checked", true);
                        $(rows).addClass("success");
                        addToAggr = true;
                    } else {
                        inputs.prop("checked", false);
                        $(rows).removeClass("success");
                    }
                    $("tbody input.flat").iCheck("update");
                    var tripIds = $.map(_datatable.rows({"search": "applied"}).data(), function (el) {
                        return el.id;
                    });
                    _dataManager.setVisibilty(tripIds, addToAggr);
                    _dataManager.calculateAverage();
                    _self.updateCharts();
                });
            }
        });
        _datatable.on("search.dt", function (event) {

            var el = $("#checkbox-select-all");
            var tripIds = $.map(_datatable.rows({"search": "applied"}).data(), function (el) {
                return el.id
            });
            var resultChecked = _dataManager.checkAllAreVisible(tripIds);

            if (resultChecked === tripIds.length) {
                el.prop("checked", true);
            } else if (resultChecked === 0) {
                el.prop("checked", false);
            } else {
                el.prop("checked", false);
                el.prop("indeterminate", true);
            }
            el.iCheck("update");
        });

        this.dataManager = function (dataManager) {
            if (dataManager === undefined) {
                return _dataManager;
            }
            _dataManager = dataManager;
        };

        this.resizeCharts = function () {
            _barChart.resize();
        };

        var _updateMap = function () {
            _routeLayer.clearLayers();
            _circleLayer.clearLayers();
            var shape = _dataManager.shape();
            var stops = _dataManager.xAxisData();
            var yAxisData = _dataManager.yAxisData().loadProfile;

            var maxLoadProfile = Math.max(...yAxisData);
            stops.forEach(function (stop, i) {
                var loadProfile = yAxisData[i] ? yAxisData[i] : 0;
                var formattedLoadProfile = Number(loadProfile.toFixed(2)).toLocaleString();
                var radius = loadProfile / maxLoadProfile * 300;
                if (radius <= 0 || isNaN(radius)) {
                    radius = 1;
                }
                var circle = L.circle([stop.latitude, stop.longitude], {
                    radius: radius
                });
                var popup = "Perfil de carga: " + formattedLoadProfile;
                circle.bindPopup(popup);
                _circleLayer.addLayer(circle);
            });

            _mappApp.addPolyline(_routeLayer, shape, {
                route: $("#authRouteFilter").val(),
                stops: stops,
                additonalStopInfo: function (stopPosition) {
                    var loadProfile = yAxisData[stopPosition];
                    if (loadProfile !== null) {
                        loadProfile = Number(loadProfile.toFixed(2)).toLocaleString();
                    }
                    return "<br />Perfil de carga: <b>" + loadProfile + "</b>";
                }
            });
        };

        var _updateDatatable = function () {
            var dataset = _dataManager.getDatatableData();
            var rows = dataset.rows;
            var maxHeight = dataset.maxHeight;

            _datatable.off("draw");
            _datatable.on("draw", function (oSettings) {
                $(".spark:not(:has(canvas))").sparkline("html", {
                    type: "bar",
                    barColor: "#169f85",
                    negBarColor: "red",
                    chartRangeMax: maxHeight,
                    numberFormatter: function (value) {
                        return Number(value.toFixed(2)).toLocaleString();
                    }
                });

                $("tbody input.flat").iCheck("destroy");
                $("tbody input.flat").iCheck({
                    labelHover: false,
                    cursor: true,
                    checkboxClass: "icheckbox_flat-green"
                });

                // activate iCheck in checkbox
                var dtRows = _datatable.rows().nodes();
                // attach events check and uncheck
                $("input.flat", dtRows).off("ifToggled");
                $("input.flat", dtRows).on("ifToggled", function (event) {
                    var tr = $(this).parent().parent().parent();
                    var addToAggr = false;
                    if (event.target.checked) {
                        tr.addClass("success");
                        addToAggr = true;
                    } else {
                        tr.removeClass("success");
                    }

                    // updateChart
                    var tripId = parseInt($(this).attr("name").replace("trip", ""));
                    _dataManager.setVisibilty([tripId], addToAggr);
                    _dataManager.calculateAverage();
                    _self.updateCharts();
                });
            });
            _datatable.clear();
            _datatable.rows.add(rows);
            _datatable.columns.adjust().draw();

            // attach to attach event
            $("#detail-tab").off("shown.bs.tab");
            $("#detail-tab").on("shown.bs.tab", function (event) {
                $(".spark:not(:has(canvas))").sparkline("html", {
                    type: "bar",
                    barColor: "#169f85",
                    negBarColor: "red",
                    chartRangeMax: maxHeight
                });
            })
        };

        const _updateBarChart = function () {
            let yAxisData = _dataManager.yAxisData();
            let xAxisData = _dataManager.xAxisData();

            // get out, get in, load profile, percentage occupation
            let yAxisDataName = [
                "Subidas", "Subidas evadidas",
                "Bajadas", "Bajadas evadidas",
                "Carga prom.", "Carga prom. con evasión",
                "Carga máx.", "Carga máx. con evasión",
                "% ocupación", "% ocupación con evasión"];
            let yAxisIndex = [0, 0, 0, 0, 0, 0, 0, 0, 1, 1];
            let yChartType = [
                "bar", "bar",
                "bar", "bar",
                "line", "line",
                "line", "line",
                "line", "line"];
            let stack = [
                "Subidas", "Subidas",
                "Bajadas", "Bajadas",
                null, null,
                null, null,
                null, null
            ];
            let dataName = [
                "expandedBoarding", "expandedEvasionBoarding",
                "expandedAlighting", "expandedEvasionAlighting",
                "loadProfile", "loadProfileWithEvasion",
                "maxLoad", "maxLoadWithEvasion",
                "saturationRate", "saturationRateWithEvasion"];
            let colors = [
                {itemStyle: {normal: {color: "#2C69B0"}}}, {itemStyle: {normal: {color: "#6BA3D6"}}},
                {itemStyle: {normal: {color: "#F02720"}}}, {itemStyle: {normal: {color: "#EA6B73"}}},
                {itemStyle: {normal: {color: "#4AA96C"}}}, {itemStyle: {normal: {color: "#9FE6A0"}}},
                {itemStyle: {normal: {color: "#610F95"}}}, {itemStyle: {normal: {color: "#B845C4"}}},
                {lineStyle: {normal: {type: "dashed"}}, itemStyle: {normal: {color: "#FFB037"}}},
                {lineStyle: {normal: {type: "dashed"}}, itemStyle: {normal: {color: "#FFE268"}}}
            ];

            let series = [];
            for (let index = 0; index < yAxisIndex.length; index++) {
                let serie = {
                    name: yAxisDataName[index],
                    type: yChartType[index],
                    data: yAxisData[dataName[index]],
                    showSymbol: false,
                    yAxisIndex: yAxisIndex[index],
                    smooth: true
                };
                if (stack[index] != null) {
                    serie["stack"] = stack[index];
                }
                $.extend(serie, colors[index]);
                series.push(serie);
            }
            var maxLabelLength = 0;
            var xData = xAxisData.map(function (attr) {
                var label = attr.order + " " + attr.stopName;
                if (maxLabelLength < label.length) {
                    maxLabelLength = label.length;
                }
                attr.value = attr.stopName;
                label = attr;
                return label;
            });
            var route = $("#authRouteFilter").val();
            var options = {
                legend: {
                    data: yAxisDataName,
                    height: 40,
                    orient: 'vertical',
                    formatter: '{styleA|{name}}',
                    textStyle: {
                        rich: {
                            styleA: {
                                width: 130,
                                lineHeight: 0
                            }
                        }
                    }
                },
                xAxis: [{
                    type: "category",
                    data: xData,
                    axisTick: {
                        length: 10
                    },
                    axisLabel: {
                        rotate: 90,
                        interval: function (index) {
                            var labelWidth = 20;
                            var chartWidth = $("#barChart").width() - 82;
                            var div = chartWidth / labelWidth;
                            if (div >= xData.length) {
                                return true;
                            }
                            div = parseInt(xData.length / div);
                            return !(index % div);
                        },
                        textStyle: {
                            fontSize: 12
                        },
                        formatter: function (value, index) {
                            return (index + 1) + " " + value + " " + (xAxisData[index].busStation ? "(ZP)" : "");
                        },
                        color: function (label, index) {
                            if (xAxisData[index].busStation) {
                                return "red";
                            }
                            return "black";
                        }
                    }
                }],
                yAxis: [{
                    type: "value",
                    name: "N° Pasajeros",
                    //max: capacity - capacity%10 + 10,
                    position: "left"
                }, {
                    type: "value",
                    name: "Porcentaje",
                    //min: 0,
                    max: 100,
                    position: "right",
                    axisLabel: {
                        formatter: "{value} %",
                        textStyle: {
                            color: "#EA8E4D"
                        }
                    },
                    axisLine: {
                        onZero: true,
                        lineStyle: {
                            color: "#EA8E4D", width: 2
                        }
                    },
                    nameTextStyle: {
                        color: "#EA8E4D"
                    }
                }],
                series: series,
                tooltip: {
                    trigger: "axis",
                    //alwaysShowContent: true,
                    formatter: function (params) {
                        if (Array.isArray(params)) {
                            var xValue = params[0].dataIndex;
                            var head = (xValue + 1) + "  " + xAxisData[xValue].userStopCode + " " + xAxisData[xValue].authStopCode + "  " + xAxisData[xValue].stopName + "<br />";
                            var info = [];
                            for (var index in params) {
                                var el = params[index];
                                var ball = el.marker;
                                var name = el.seriesName;
                                var value = Number(el.value.toFixed(2)).toLocaleString();
                                if (el.seriesIndex === 8 || el.seriesIndex === 9) {
                                    value = value + " %";
                                }
                                info.push(ball + name + ": " + value);
                            }
                            return head + info.join("<br />");
                        } else {
                            var title = params.data.name;
                            var name = params.seriesName;
                            var value = Number(params.value.toFixed(2)).toLocaleString();
                            return title + "<br />" + name + ": " + value;
                        }
                    }
                },
                grid: {
                    top: "100px",
                    left: "37px",
                    right: "45px",
                    bottom: maxLabelLength * 5.5 + 20 + "px"
                },
                toolbox: {
                    show: true,
                    itemSize: 20,
                    bottom: 15,
                    left: "center",
                    feature: {
                        mark: {show: false},
                        restore: {show: false, title: "restaurar"},
                        saveAsImage: {show: true, title: "Guardar imagen", name: _self.getDataName()},
                        dataView: {
                            show: true,
                            title: "Ver datos",
                            lang: ["Datos del gráfico", "cerrar", "refrescar"],
                            buttonColor: "#169F85",
                            readOnly: true,
                            optionToContent: function (opt) {
                                var axisData = opt.xAxis[0].data;
                                var series = opt.series;

                                var textarea = document.createElement('textarea');
                                textarea.style.cssText = 'width:100%;height:100%;font-family:monospace;font-size:14px;line-height:1.6rem;white-space: pre;';
                                textarea.readOnly = "true";

                                var header = "Servicio\tOrden\tCódigo usuario\tCódigo transantiago\tNombre parada";
                                series.forEach(function (el) {
                                    header += "\t" + el.name;
                                });
                                header += "\n";
                                var body = "";
                                axisData.forEach(function (el, index) {
                                    var serieValues = [];
                                    series.forEach(function (serie) {
                                        serieValues.push(serie.data[index]);
                                    });
                                    serieValues = serieValues.join("\t");
                                    body += [route, el.order, el.userStopCode, el.authStopCode, el.stopName, serieValues, "\n"].join("\t");
                                });
                                body = body.replace(/\./g, ",");
                                textarea.value = header + body;
                                return textarea;
                            }
                        },
                        myPercentageEditor: {
                            show: true,
                            title: "Cambiar porcentaje máximo",
                            icon: 'image:///static/profile/img/percent.png',
                            onclick: function () {
                                var percentage = prompt("Ingrese el porcentaje máximo");
                                if (percentage !== "") {
                                    options.yAxis[1].max = percentage;
                                } else {
                                    delete options.yAxis[1].max;
                                }
                                _barChart.setOption(options, {notMerge: true});
                            }
                        }
                    }
                },
                calculable: false
            };

            _barChart.clear();
            _barChart.setOption(options, {
                notMerge: true
            });
            hideEvasion();
            let evasionSwitch = $("#evasionSwitch");
            if (!evasionSwitch.length) {
                addSwitch();
            } else {
                if (evasionSwitch.is(":checked")) {
                    evasionSwitch.trigger('click');
                }
            }
        };

        const addSwitch = function () {
            let evasionSwitch = "<input id='evasionSwitch'  type='checkbox'  class='modes_checkbox' data-switchery='true'> Mostrar datos con evasión ";
            $("#barChart").prepend(evasionSwitch);
            let evasionJquerySwitch = $("#evasionSwitch");
            evasionJquerySwitch.each(function (index, html) {
                new Switchery(html, {
                    size: 'small',
                    color: 'rgb(38, 185, 154)'
                });
            });
            let switcherySwitch = $(".switchery");
            switcherySwitch.on("click", () => {
                if (evasionJquerySwitch.is(":checked")) {
                    showEvasion();
                    evasionJquerySwitch.prop('checked', true);

                } else {
                    evasionJquerySwitch.prop('checked', false);
                    hideEvasion();
                }
            });
        };

        const hideEvasion = () => applyToEvasion('legendUnSelect');

        const showEvasion = () => applyToEvasion('legendSelect');

        const applyToEvasion = type => {
            let labels = ["Subidas evadidas", "Bajadas evadidas", "Carga prom. con evasión", "Carga máx. con evasión", "% ocupación con evasión"]
            labels.map(e => {
                _barChart.dispatchAction({
                    type: type,
                    name: e
                })
            })
        }

        var _updateGlobalStats = function (expeditionNumber, boardingWithAlightingPercentage, utilizationCoefficient) {
            expeditionNumber = expeditionNumber || _dataManager.tripsUsed();
            boardingWithAlightingPercentage = boardingWithAlightingPercentage || _dataManager._boardingWithAlightingPercentage || 0;
            utilizationCoefficient = utilizationCoefficient || _dataManager._utilizationCoefficient || 0;
            $("#expeditionNumber").html(expeditionNumber);
            $("#expeditionNumber2").html(expeditionNumber);
            $("#boardingWithAlightingPercentage").html(Number(boardingWithAlightingPercentage.toFixed(2)).toLocaleString());
            $("#utilizationCoefficient").html(Number(utilizationCoefficient.toFixed(2)).toLocaleString());
        };

        const _clearGlobalStats = function(){
            $("#expeditionNumber").html('-');
            $("#expeditionNumber2").html('-');
            $("#boardingWithAlightingPercentage").html('-');
            $("#utilizationCoefficient").html('-');
        };

        this.updateCharts = function (expeditionNumber, boardingWithAlightingPercentage, utilizationCoefficient) {
            _updateBarChart();
            _updateGlobalStats(expeditionNumber, boardingWithAlightingPercentage, utilizationCoefficient);
            _updateMap();
        };
        this.updateDatatable = function () {
            _updateDatatable();
        };
        this.showLoadingAnimationCharts = function () {
            var loadingText = "Cargando...";
            _barChart.showLoading(null, {text: loadingText});
        };
        this.hideLoadingAnimationCharts = function () {
            _barChart.hideLoading();
        };

        /**
         * Clear information in bar chart, datatables and map.
         */
        this.clearDisplayData = function () {
            _barChart.clear();
            _clearGlobalStats();
            _datatable.clear().draw();
            _routeLayer.clearLayers();
            _circleLayer.clearLayers();
        };
    }

    function processData(dataSource, app) {
        if (dataSource.status && (dataSource.status.code !== 252 && dataSource.status.code !== 253)) {
            return;
        }

        let trips = dataSource.trips;
        let stops = dataSource.stops;
        let busStations = dataSource.busStations;
        let shape = dataSource.shape;
        let dataManager = new DataManager();
        dataManager.shape(shape);
        if (dataSource.groupedTrips) {
            busStations = dataSource.groupedTrips.aggregations.stop.station.buckets.map(function (el) {
                return el.key;
            });
            let yAxisDataResult = {
                expandedAlighting: [],
                expandedBoarding: [],
                loadProfile: [],
                saturationRate: [],
                maxLoad: [],
                loadProfileWithEvasion: [],
                expandedEvasionBoarding: [],
                expandedEvasionAlighting: [],
                expandedBoardingPlusExpandedEvasionBoarding: [],
                expandedAlightingPlusExpandedEvasionAlighting: [],
                saturationRateWithEvasion: [],
                maxLoadWithEvasion: [],
            };

            let groupedStops = {};
            dataSource.groupedTrips.aggregations.stops.buckets.forEach(function (el) {
                groupedStops[el.key] = {
                    expandedBoarding: el.expandedBoarding.value,
                    loadProfile: el.loadProfile.value,
                    expandedAlighting: el.expandedAlighting.value,
                    busSaturation: el.busSaturation.value,
                    distOnPath: el.pathDistance.hits.hits[0]._source.stopDistanceFromPathStart,
                    expeditionNumber: el.doc_count,
                    maxLoadProfile: el.maxLoadProfile.value,
                    loadProfileWithEvasion: el.loadProfileWithEvasion.value,
                    maxLoadProfileWithEvasion: el.maxLoadProfileWithEvasion.value,
                    expandedEvasionBoarding: el.expandedEvasionBoarding.value,
                    expandedEvasionAlighting: el.expandedEvasionAlighting.value,
                    expandedBoardingPlusExpandedEvasionBoarding: el.expandedBoardingPlusExpandedEvasionBoarding.value,
                    expandedAlightingPlusExpandedEvasionAlighting: el.expandedAlightingPlusExpandedEvasionAlighting.value,
                    busSaturationWithEvasion: el.busSaturationWithEvasion.value,
                    boarding: el.boarding.value,
                    boardingWithAlighting: el.boardingWithAlighting.value,
                    passengerWithEvasionPerKmSection: el.passengerWithEvasionPerKmSection.value,
                    capacityPerKmSection: el.capacityPerKmSection.value
                }
            });
            let expeditionNumber = 0;
            let boardingTotal = 0;
            let boardingWithAlightingTotal = 0;
            let passengerWithEvasionPerKmSectionTotal = 0;
            let capacityPerKmSectionTotal = 0;
            stops.forEach(function (stop) {
                let item = groupedStops[stop.authStopCode];
                let itemIsNull = item === undefined;

                let expandedAlighting = itemIsNull ? null : item.expandedAlighting;
                let expandedBoarding = itemIsNull ? null : item.expandedBoarding;
                let loadProfile = itemIsNull ? null : item.loadProfile;
                let saturationRate = itemIsNull ? null : item.busSaturation * 100;
                let maxLoadProfile = itemIsNull ? null : item.maxLoadProfile;
                let loadProfileWithEvasion = itemIsNull ? null : item.loadProfileWithEvasion;
                let maxLoadProfileWithEvasion = itemIsNull ? null : item.maxLoadProfileWithEvasion;
                let expandedEvasionBoarding = itemIsNull ? null : item.expandedEvasionBoarding;
                let expandedEvasionAlighting = itemIsNull ? null : item.expandedEvasionAlighting;
                let expandedBoardingPlusExpandedEvasionBoarding = itemIsNull ? null : item.expandedBoardingPlusExpandedEvasionBoarding;
                let expandedAlightingPlusExpandedEvasionAlighting = itemIsNull ? null : item.expandedAlightingPlusExpandedEvasionAlighting;
                let saturationRateWithEvasion = itemIsNull ? null : item.busSaturationWithEvasion * 100;
                let boarding = itemIsNull ? null : item.boarding;
                let boardingWithAlighting = itemIsNull ? null : item.boardingWithAlighting;
                let passengerWithEvasionPerKmSection = itemIsNull ? 0 : item.passengerWithEvasionPerKmSection;
                let capacityPerKmSection = itemIsNull ? 0 : item.capacityPerKmSection;

                yAxisDataResult.expandedAlighting.push(expandedAlighting);
                yAxisDataResult.expandedBoarding.push(expandedBoarding);
                yAxisDataResult.loadProfile.push(loadProfile);
                yAxisDataResult.saturationRate.push(saturationRate);
                yAxisDataResult.maxLoad.push(maxLoadProfile);
                yAxisDataResult.maxLoadWithEvasion.push(maxLoadProfileWithEvasion);
                yAxisDataResult.loadProfileWithEvasion.push(loadProfileWithEvasion);
                yAxisDataResult.expandedEvasionBoarding.push(expandedEvasionBoarding);
                yAxisDataResult.expandedEvasionAlighting.push(expandedEvasionAlighting);
                yAxisDataResult.expandedBoardingPlusExpandedEvasionBoarding.push(expandedBoardingPlusExpandedEvasionBoarding);
                yAxisDataResult.expandedAlightingPlusExpandedEvasionAlighting.push(expandedAlightingPlusExpandedEvasionAlighting);
                yAxisDataResult.saturationRateWithEvasion.push(saturationRateWithEvasion);

                let expNumber = itemIsNull ? 0 : item.expeditionNumber;
                expeditionNumber = Math.max(expNumber, expeditionNumber);
                boardingTotal += boarding;
                boardingWithAlightingTotal += boardingWithAlighting;
                passengerWithEvasionPerKmSectionTotal += passengerWithEvasionPerKmSection;
                capacityPerKmSectionTotal += capacityPerKmSection;
            });
            let boardingWithAlightingPercentage = boardingWithAlightingTotal / boardingTotal * 100;
            let utilizationCoefficient = passengerWithEvasionPerKmSectionTotal / capacityPerKmSectionTotal;

            dataManager.yAxisData(yAxisDataResult);
            let tripGroupXAxisData = stops.map(function (stop) {
                stop.busStation = busStations.indexOf(stop.authStopCode) >= 0;
                return stop;
            });
            dataManager.xAxisData(tripGroupXAxisData);
            app.dataManager(dataManager);
            app.updateCharts(expeditionNumber, boardingWithAlightingPercentage, utilizationCoefficient);
            app.updateDatatable();
        } else {
            for (let expeditionId in trips) {
                let trip = trips[expeditionId];

                // trip info
                let capacity = trip.info[0];
                let licensePlate = trip.info[1];
                let route = trip.info[2];
                let authTimePeriod = trip.info[3];
                let timeTripInit = trip.info[4];
                let timeTripEnd = trip.info[5];
                let dayType = trip.info[6];
                let valid = trip.info[7];

                let yAxisData = {
                    expandedAlighting: [],
                    expandedBoarding: [],
                    loadProfile: [],
                    saturationRate: [],
                    valueIsNull: [],
                    loadProfileWithEvasion: [],
                    expandedEvasionBoarding: [],
                    expandedEvasionAlighting: [],
                    expandedBoardingPlusExpandedEvasionBoarding: [],
                    expandedAlightingPlusExpandedEvasionAlighting: [],
                    saturationRateWithEvasion: [],
                    boarding: [],
                    boardingWithAlighting: []
                };

                let passengerWithEvasionPerKmSectionSum = 0;
                let capacityPerKmSectionSum = 0;
                stops.forEach(function (stop) {
                    let item = trip.stops[stop.authStopCode];
                    let itemIsNull = item === undefined;

                    let expandedAlighting = itemIsNull ? null : item[2];
                    let expandedBoarding = itemIsNull ? null : item[1];
                    let loadProfile = itemIsNull ? null : item[0];
                    let saturationRate = itemIsNull ? null : loadProfile / capacity * 100;
                    let loadProfileWithEvasion = itemIsNull ? null : item[3];
                    let expandedEvasionBoarding = itemIsNull ? null : item[4];
                    let expandedEvasionAlighting = itemIsNull ? null : item[5];
                    let expandedBoardingPlusExpandedEvasionBoarding = itemIsNull ? null : item[6];
                    let expandedAlightingPlusExpandedEvasionAlighting = itemIsNull ? null : item[7];
                    let saturationRateWithEvasion = itemIsNull ? null : loadProfileWithEvasion / capacity * 100;
                    let boarding = itemIsNull ? null : item[8];
                    let boardingWithAlighting = itemIsNull ? null : item[9];
                    let passengerWithEvasionPerKmSection = itemIsNull ? 0 : item[10];
                    let capacityPerKmSection = itemIsNull ? 0 : item[11];

                    passengerWithEvasionPerKmSectionSum += passengerWithEvasionPerKmSection
                    capacityPerKmSectionSum += capacityPerKmSection

                    yAxisData.expandedAlighting.push(expandedAlighting);
                    yAxisData.expandedBoarding.push(expandedBoarding);
                    yAxisData.loadProfile.push(loadProfile);
                    yAxisData.saturationRate.push(saturationRate);
                    yAxisData.valueIsNull.push(itemIsNull)
                    yAxisData.loadProfileWithEvasion.push(loadProfileWithEvasion);
                    yAxisData.expandedEvasionBoarding.push(expandedEvasionBoarding);
                    yAxisData.expandedEvasionAlighting.push(expandedEvasionAlighting);
                    yAxisData.expandedBoardingPlusExpandedEvasionBoarding.push(expandedBoardingPlusExpandedEvasionBoarding);
                    yAxisData.expandedAlightingPlusExpandedEvasionAlighting.push(expandedAlightingPlusExpandedEvasionAlighting);
                    yAxisData.saturationRateWithEvasion.push(saturationRateWithEvasion);
                    yAxisData.boarding.push(boarding);
                    yAxisData.boardingWithAlighting.push(boardingWithAlighting);
                });

                trip = new Trip(expeditionId, route, licensePlate, capacity, timeTripInit, timeTripEnd, authTimePeriod,
                    dayType, yAxisData, valid, passengerWithEvasionPerKmSectionSum, capacityPerKmSectionSum);
                dataManager.addTrip(trip);
            }
            let tripXAxisData = stops.map(function (stop) {
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
        loadRangeCalendar(Urls["esapi:availableProfileDays"](), {});

        var app = new ExpeditionApp();
        var previousCall = function () {
            app.showLoadingAnimationCharts();
        };
        var afterCall = function (data, status) {
            if (status) {
                processData(data, app);
            } else {
                app.clearDisplayData();
            }
            app.hideLoadingAnimationCharts();
        };
        var opts = {
            urlFilterData: Urls["esapi:loadProfileByExpeditionData"](),
            urlRouteData: Urls["esapi:availableProfileRoutes"](),
            previousCallData: previousCall,
            afterCallData: afterCall
        };

        new FilterManager(opts);

        $(window).resize(function () {
            app.resizeCharts();
        });
        $("#menu_toggle").click(function () {
            app.resizeCharts();
        });
    })()
});