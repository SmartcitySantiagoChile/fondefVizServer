"use strict";
$(document).ready(function () {
    // Constants
    var FILE_NAME = "Perfil de carga ";

    // define logic to manipulate data
    function Trip(expeditionDayId, route, licensePlate, busCapacity, timeTripInit, timeTripEnd, authTimePeriod, dayType,
                  xAxisData, yAxisData, visible) {
        this.expeditionId = expeditionDayId;
        this.route = route;
        this.licensePlate = licensePlate;
        this.busCapacity = busCapacity;
        this.timeTripInit = timeTripInit;
        this.timeTripEnd = timeTripEnd;
        this.authTimePeriod = authTimePeriod;
        this.dayType = dayType;
        this.xAxisData = xAxisData;
        this.yAxisData = yAxisData;
        this.visible = visible || true;
    }

    /*
     * to manage grouped data
     */
    function DataManager() {
        // trips
        var _trips = [];
        // stops
        var _xAxisData = null;
        // y average data
        var _yAxisData = {
            average: [],
            max: []
        };
        // trips to show in profile view
        var _visibleTrips = 0;

        this.getDataName = function () {
            if (_trips.length > 0) {
                return FILE_NAME + _trips[0].route;
            }
            return "";
        };
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
            var xAxisLength = _xAxisData.length;
            var counterByStop = [];
            var capacityByStop = [];

            _yAxisData = {
                expandedGetOut: [],
                expandedGetIn: [],
                loadProfile: [],
                saturationRate: [],
                maxLoad: []
            };

            for (var i = 0; i < xAxisLength; i++) {
                _yAxisData.expandedGetIn.push(0);
                _yAxisData.expandedGetOut.push(0);
                _yAxisData.loadProfile.push(0);
                _yAxisData.maxLoad.push(0);

                capacityByStop.push(0);
                counterByStop.push(0);
            }

            _trips.forEach(function (trip) {
                if (!trip.visible) {
                    return;
                }

                for (var stopIndex = 0; stopIndex < xAxisLength; stopIndex++) {
                    _yAxisData.expandedGetOut[stopIndex] += trip.yAxisData.expandedGetOut[stopIndex];
                    _yAxisData.expandedGetIn[stopIndex] += trip.yAxisData.expandedGetIn[stopIndex];
                    _yAxisData.loadProfile[stopIndex] += trip.yAxisData.loadProfile[stopIndex];

                    if (_yAxisData.maxLoad[stopIndex] < trip.yAxisData.loadProfile[stopIndex]) {
                        _yAxisData.maxLoad[stopIndex] = trip.yAxisData.loadProfile[stopIndex]
                    }

                    capacityByStop[stopIndex] += trip.busCapacity;
                    counterByStop[stopIndex]++;
                }
            });

            // it calculates average
            for (var stopIndex = 0; stopIndex < xAxisLength; stopIndex++) {
                _yAxisData.expandedGetOut[stopIndex] = _yAxisData.expandedGetOut[stopIndex] / counterByStop[stopIndex];
                _yAxisData.expandedGetIn[stopIndex] = _yAxisData.expandedGetIn[stopIndex] / counterByStop[stopIndex];
                _yAxisData.saturationRate.push((_yAxisData.loadProfile[stopIndex] / capacityByStop[stopIndex]) * 100);
                _yAxisData.loadProfile[stopIndex] = _yAxisData.loadProfile[stopIndex] / counterByStop[stopIndex];
            }
        };
        this.getAttrGroup = function (attrName, formatFunc) {
            var values = [];
            var dict = {};
            for (var i in _trips) {
                var trip = _trips[i];
                if (!trip.visible) {
                    continue;
                }
                var attrValue = trip[attrName];
                attrValue = (formatFunc === undefined ? attrValue : formatFunc(attrValue));
                if (dict[attrValue]) {
                    dict[attrValue]++;
                } else {
                    dict[attrValue] = 1;
                }
            }
            for (var name in dict) {
                values.push({"name": name, "value": dict[name]});
            }
            return values;
        };
        this.getDatatableData = function () {
            var values = [];
            var max = 0;
            for (var i in _trips) {
                var trip = $.extend({}, _trips[i]);
                /*if(!trip.visible){
                  continue;
                }*/
                trip.busDetail = trip.licensePlate + " (" + trip.busCapacity + ")";
                var loadProfile = [];
                var hasNegativeValue = false;
                for (var i = 0; i < _xAxisData.length; i++) {
                    var value = trip.yAxisData.loadProfile[i];
                    if (value !== undefined && value < 0) {
                        hasNegativeValue = true;
                    }
                    if (max < value) {
                        max = value;
                    }
                    loadProfile.push(value);
                }
                trip.sparkLoadProfile = loadProfile;
                trip.hasNegativeValue = hasNegativeValue;
                values.push(trip);
            }
            return {
                "rows": values,
                "maxHeight": max
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
                for (var i = 0; i < _xAxisData.length; i++) {
                    var value = trip.yAxisData.loadProfile[i];
                    if (globalMax < value) {
                        globalMax = value;
                    }
                    loadProfile.push(value);
                }
                tripData.loadProfile = loadProfile;
                trips.push(tripData);
            }

            var result = {};
            result.globalMax = globalMax;
            result.trips = trips;

            return result;
        }
    }

    function ExpeditionApp() {
        var _self = this;
        var _dataManager = new DataManager();
        var _barChart = echarts.init(document.getElementById("barChart"), theme);
        var _wordcloudCharts = [
            echarts.init(document.getElementById("wordcloudChart1"), theme),
            echarts.init(document.getElementById("wordcloudChart2"), theme)];
        var _timePeriodChart = echarts.init(document.getElementById("timePeriodChart"), theme);
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
                            .attr("checked", true)[0].outerHTML;
                    }
                },
                {
                    title: "Perfil de carga", data: "sparkLoadProfile", searchable: false,
                    render: function (data, type, row) {
                        return $("<i>").addClass("spark").append(data.join(","))[0].outerHTML;
                    }
                },
                //{ title: "Servicio-sentido", data: "route",   searchable: true},
                {title: "Patente (capacidad)", data: "busDetail", searchable: true},
                {title: "Período inicio expedición", data: "authTimePeriod", searchable: true},
                {title: "Hora de inicio", data: "timeTripInit", searchable: true},
                {title: "Hora de fin", data: "timeTripEnd", searchable: true},
                {title: "Tipo de día", data: "dayType", searchable: true},
                {title: "Negativo", data: "hasNegativeValue", searchable: true}
            ],
            order: [[4, "asc"]],
            createdRow: function (row, data, index) {
                $(row).addClass("success");
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
            this.updateCharts();
            this.updateDatatable();
        };

        this.resizeCharts = function () {
            _barChart.resize();
            _timePeriodChart.resize();
            _wordcloudCharts.forEach(function (chart) {
                chart.resize();
            });
        };
        var _updateTimePeriodChart = function () {
            var timeTripInit = _dataManager.getAttrGroup("timeTripInit", function (attrValue) {
                return attrValue.substring(11, 13);
            });
            timeTripInit = timeTripInit.sort(function (a, b) {
                a = parseInt(a.name);
                b = parseInt(b.name);
                return a - b;
            });
            var hours = timeTripInit.map(function (el) {
                return el.name;
            });
            var values = timeTripInit.map(function (el, index) {
                return [index, el.value];
            });
            var option = {
                tooltip: {
                    position: "top"
                },
                singleAxis: [{
                    type: "category",
                    boundaryGap: false,
                    data: hours,
                    top: "10%",
                    height: "40%",
                    axisLabel: {
                        interval: 2
                    }
                }],
                series: [{
                    singleAxisIndex: 0,
                    coordinateSystem: "singleAxis",
                    type: "bar",
                    data: values,
                    symbolSize: function (dataItem) {
                        return [10, dataItem[1] * 3];
                    },
                    tooltip: {
                        formatter: function (params) {
                            var value = params.value[1];
                            var name = params.name;
                            var timePeriod = "[" + name + ":00, " + name + ":59]";
                            return value + " expediciones iniciadas entre " + timePeriod;
                        }
                    }
                }]
            };
            _timePeriodChart.clear();
            _timePeriodChart.setOption(option, {notMerge: true});
        };

        var _updateWordcloudCharts = function () {
            var lpValues = _dataManager.getAttrGroup("licensePlate");
            var dayTypeValues = _dataManager.getAttrGroup("dayType");

            $("#licensePlateNumber").html("(" + lpValues.length + ")");

            var values = [lpValues, dayTypeValues];
            for (var i = 0; i < values.length; i++) {
                var chart = _wordcloudCharts[i];

                chart.on("click", function (params) {
                    console.log(params);
                });

                var options = {
                    tooltip: {},
                    series: [{
                        type: "wordCloud",
                        shape: "pentagon",
                        width: "100%",
                        height: "100%",
                        sizeRange: [6, 14],
                        rotationRange: [0, 0],
                        rotationStep: 0,
                        gridSize: 8,
                        textStyle: {
                            normal: {
                                color: function () {
                                    return "rgb(" + [
                                        Math.round(Math.random() * 160),
                                        Math.round(Math.random() * 160),
                                        Math.round(Math.random() * 160)
                                    ].join(",") + ")";
                                }
                            },
                            emphasis: {
                                shadowBlur: 10,
                                shadowColor: "#169F85"
                            }
                        },
                        data: values[i]
                    }]
                };
                chart.clear();
                chart.setOption(options, {notMerge: true});
            }
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
                    numberFormatter: function(value) {
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

        var _updateBarChart = function () {
            _dataManager.calculateAverage();
            var yAxisData = _dataManager.yAxisData();
            var xAxisData = _dataManager.xAxisData();

            // get out, get in, load profile, percentage ocupation
            var yAxisDataName = ["Subidas", "Bajadas", "Carga promedio", "Carga máxima", "Porcentaje ocupación"];
            var yAxisIndex = [0, 0, 0, 0, 1];
            var yChartType = ["bar", "bar", "line", "line", "line"];
            var dataName = ["expandedGetIn", "expandedGetOut", "loadProfile", "maxLoad", "saturationRate"];
            var colors = [
                {itemStyle: {normal: {color: "#BD4845"}}},
                {itemStyle: {normal: {color: "#477BBA"}}},
                {itemStyle: {normal: {color: "#1cd68c"}}},
                {itemStyle: {normal: {color: "#4cd600"}}},
                {lineStyle: {normal: {type: "dashed"}}, itemStyle: {normal: {color: "#EA8E4D"}}}
            ];

            var series = [];
            for (var index = 0; index < yAxisIndex.length; index++) {
                var serie = {
                    name: yAxisDataName[index],
                    type: yChartType[index],
                    data: yAxisData[dataName[index]],
                    showSymbol: false,
                    /*markPoint: {
                        data: [{
                            type: "max",
                            name: "Máximo"
                        }],
                        label: {
                            normal: {
                                formatter: function (param) {
                                    return param.value.toFixed(2);
                                }
                            }
                        }
                    },*/
                    yAxisIndex: yAxisIndex[index],
                    smooth: true
                };
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
            var route = $("#routeFilter").val();
            var options = {
                legend: {
                    data: yAxisDataName
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
                            return index % div ? false : true;
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
                                if (el.seriesIndex === 4) {
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
                        saveAsImage: {show: true, title: "Guardar imagen", name: _dataManager.getDataName()},
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
                                textarea.style.cssText = 'width:100%;height:100%;font-family:monospace;font-size:14px;line-height:1.6rem;';
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
                                    body += [route, el.order, el.userCode, el.authCode, el.name, serieValues, "\n"].join("\t");
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
        };

        var _updateGlobalStats = function () {
            $("#expeditionNumber").html(_dataManager.tripsUsed());
            $("#expeditionNumber2").html(_dataManager.tripsUsed());
        };

        this.updateCharts = function () {
            _updateBarChart();
            _updateWordcloudCharts();
            _updateTimePeriodChart();
            _updateGlobalStats();
        };
        this.updateDatatable = function () {
            _updateDatatable();
        };
        this.showLoadingAnimationCharts = function () {
            var loadingText = "Cargando...";
            _barChart.showLoading(null, {text: loadingText});
            _timePeriodChart.showLoading(null, {text: loadingText});
            for (var i = 0; i < _wordcloudCharts.length; i++) {
                _wordcloudCharts[i].showLoading(null, {text: loadingText});
            }
        };
        this.hideLoadingAnimationCharts = function () {
            _barChart.hideLoading();
            _timePeriodChart.hideLoading();
            for (var i = 0; i < _wordcloudCharts.length; i++) {
                _wordcloudCharts[i].hideLoading();
            }
        };
    }

    function processData(dataSource, app) {
        console.log(dataSource);

        if (dataSource.status) {
            return;
        }

        var trips = dataSource.trips;
        var stops = dataSource.stops;
        var busStations = dataSource.busStations;

        var dataManager = new DataManager();
        var tripGroupXAxisData = stops.map(function (stop) {
            stop.busStation = busStations.indexOf(stop.authStopCode) >= 0;
            return stop;
        });

        for (var expeditionId in trips) {
            var trip = trips[expeditionId];

            // trip info
            var capacity = trip.info.capacity;
            var licensePlate = trip.info.licensePlate;
            var route = trip.info.route;
            var timeTripInit = trip.info.timeTripInit;
            var timeTripEnd = trip.info.timeTripEnd;
            var authTimePeriod = trip.info.authTimePeriod;
            var dayType = trip.info.dayType;

            var yAxisData = {
                "expandedGetOut": [],
                "expandedGetIn": [],
                "loadProfile": [],
                "saturationRate": []
            };

            var xAxisData = stops.map(function (stop) {
                var item = trip.stops[stop.authStopCode];

                var expandedGetOut = item.expandedGetOut === undefined ? 0 : item.expandedGetOut;
                var expandedGetIn = item.expandedGetIn === undefined ? 0 : item.expandedGetIn;
                var loadProfile = item.loadProfile === undefined ? 0 : item.loadProfile;

                yAxisData.expandedGetOut.push(expandedGetOut);
                yAxisData.expandedGetIn.push(expandedGetIn);
                yAxisData.loadProfile.push(loadProfile);
                yAxisData.saturationRate.push(loadProfile / capacity * 100);

                return {
                    authStopCode: stop.authStopCode,
                    userStopCode: stop.userStopCode
                };
            });

            trip = new Trip(expeditionId, route, licensePlate, capacity, timeTripInit,
                timeTripEnd, authTimePeriod, dayType, xAxisData, yAxisData);
            dataManager.addTrip(trip);
        }

        dataManager.xAxisData(tripGroupXAxisData);
        app.dataManager(dataManager);
        //drawDistribution(app.dataManager().trips());
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

        $(window).resize(function () {
            app.resizeCharts();
        });
        $("#menu_toggle").click(function () {
            app.resizeCharts();
        });
    })()
});