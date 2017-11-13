"use strict";
$(document).ready(function () {

    // define logic to manipulate data
    function Trip(expeditionId,
                  route,
                  licensePlate,
                  busCapacity,
                  timeTripInit,
                  timeTripEnd,
                  authTimePeriod,
                  dayType,
                  data) {
        this.expeditionId = expeditionId;
        this.route = route;
        this.licensePlate = licensePlate;
        this.busCapacity = busCapacity;
        this.timeTripInit = timeTripInit;
        this.timeTripEnd = timeTripEnd;
        this.authTimePeriod = authTimePeriod;
        this.dayType = dayType;
        this.data = data;
        this.visible = true;
    }

    /*
     * to manage grouped data
     */
    function DataManager() {
        // trips
        var _trips = [];
        // trip number that are visible
        var _visibleTrips = 0;
        // grouped data to show in chart
        var _yAxisData = [];

        // file name of chart image
        this.getDataName = function () {
            var FILE_NAME = "Trayectorias con perfil de carga ";
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
            trips.forEach(function(trip, index){
                if (trip.visible) {
                    _visibleTrips++;
                }
                trip.id = index;
            });
            _trips = trips;
        };
        this.addTrip = function (trip) {
            // create trip identifier
            if (trip.visible) {
                _visibleTrips++;
            }
            trip.id = _trips.length;
            _trips.push(trip);
        };
        this.tripsUsed = function () {
            return _visibleTrips;
        };
        this.yAxisData = function (data) {
            if (data === undefined) {
                return _yAxisData;
            }
            _yAxisData = data;
        };
        this.cleanData = function () {
            _trips = [];
            _visibleTrips = 0;
        };
        this.setVisibility = function (tripIdArray, value) {
            tripIdArray.map(function(tripId) {
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
        this.checkAllAreAggregated = function (tripIdArray) {
            var result = tripIdArray.length;
            tripIdArray.map(function(tripId){
                if (!_trips[tripId].visible) {
                    result--;
                }
            });
            return result;
        };
        this.getAttrGroup = function (attrName, formatFunc) {
            var values = [];
            var dict = {};
            _trips.forEach(function(trip) {
                if (!trip.visible) {
                    return;
                }
                var attrValue = trip[attrName];
                attrValue = (formatFunc === undefined ? attrValue : formatFunc(attrValue));
                if (dict[attrValue]) {
                    dict[attrValue]++;
                } else {
                    dict[attrValue] = 1;
                }
            });
            for (var name in dict) {
                values.push({"name": name, "value": dict[name]});
            }
            return values;
        };
        this.getDatatableData = function () {
            var values = [];
            var max = 0;
            _trips.forEach(function(tripObj){
                var trip = $.extend({}, tripObj);
                /*if(!trip.visible){
                  continue;
                }*/
                trip.busDetail = trip.licensePlate + " (" + trip.busCapacity + ")";
                var loadProfile = [];
                var hasNegativeValue = false;
                trip.data.forEach(function(data){
                    var value = data[2];
                    if (value !== undefined && value < 0) {
                        hasNegativeValue = true;
                    }
                    if (max < value) {
                        max = value;
                    }
                    loadProfile.push(value);
                });
                trip.sparkLoadProfile = loadProfile;
                trip.hasNegativeValue = hasNegativeValue;
                values.push(trip);
            });
            return {
                rows: values,
                maxHeight: max
            };
        }
    }

    function ExpeditionApp() {
        var _self = this;
        var _dataManager = new DataManager();
        var _barChart = echarts.init(document.getElementById("barChart"), theme);
        var _datatable = $("#expeditionDetail").DataTable({
            lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "Todos"]],
            language: {
                url: "//cdn.datatables.net/plug-ins/1.10.13/i18n/Spanish.json"
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
                {title: "Patente(capacidad)", data: "busDetail", searchable: true},
                {title: "Período inicio expedición", data: "authTimePeriod", searchable: true},
                {title: "Hora de inicio", data: "timeTripInit", searchable: true},
                {title: "Hora de fin", data: "timeTripEnd", searchable: true},
                {title: "Tipo de día", data: "dayType", searchable: true}
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
                    var tripIds = _datatable.rows({"search": "applied"}).data().map(function (el) {
                        return el.id
                    });
                    _dataManager.setVisibility(tripIds, addToAggr);
                    _self.updateCharts();
                });
            }
        });
        _datatable.on("search.dt", function (event) {

            var el = $("#checkbox-select-all");
            var tripIds = _datatable.rows({"search": "applied"}).data().map(function (el) {
                return el.id
            });
            var resultChecked = _dataManager.checkAllAreAggregated(tripIds);

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
        };

        var _updateDatatable = function () {
            var dataset = _dataManager.getDatatableData();
            var rows = dataset["rows"];
            var maxHeight = dataset["maxHeight"];

            _datatable.off("draw");
            _datatable.on("draw", function (oSettings) {
                $(".spark:not(:has(canvas))").sparkline("html", {
                    type: "bar",
                    barColor: "#169f85",
                    negBarColor: "red",
                    chartRangeMax: maxHeight
                });

                var button = $("tbody input.flat");
                button.iCheck("destroy");
                button.iCheck({
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
                    _dataManager.setVisibility([tripId], addToAggr);
                    _self.updateCharts();
                });
            });
            _datatable.clear();
            _datatable.rows.add(rows);
            _datatable.columns.adjust().draw();

            // attach to attach event
            // TODO: use if datatable is inside tab
            var tab = $("#detail-tab");
            tab.off("shown.bs.tab");
            tab.on("shown.bs.tab", function (event) {
                $(".spark:not(:has(canvas))").sparkline("html", {
                    type: "bar",
                    barColor: "#169f85",
                    negBarColor: "red",
                    chartRangeMax: maxHeight
                });
            })
        };

        var _updateBarChart = function () {

            var trips = _dataManager.trips();
            var series = [];
            var visualMaps = [];
            var scatterData = [];
            var seriesIndex = -1;
            var colors = ["#0008fc", "#d3d352", "#db9500", "#ff0707"];
            trips.forEach(function(trip) {
                if (!trip.visible) {
                    return;
                }
                seriesIndex++;

                var serie = {
                    name: trip.licensePlate,
                    type: "line", data: trip.data,
                    showSymbol: false, hoverAnimation: false, animation: false,
                    lineStyle: {normal: {width: 1}}
                };
                var visualMap = {
                    show: false,
                    type: "piecewise",
                    pieces: [],
                    dimension: 0,
                    seriesIndex: seriesIndex,
                    outOfRange: {
                        color: "black"
                    }
                };
                var previousPiece = null;
                trip.data.forEach(function(data, index, arr){
                    // skip first iteration
                    if (index === 0) return;

                    var value = data[3];
                    var color = null;
                    switch (true) {
                        case (value < 25):
                            color = colors[0];
                            break;
                        case (value < 50):
                            color = colors[1];
                            break;
                        case (value < 75):
                            color = colors[2];
                            break;
                        case (value <= 100):
                            color = colors[3];
                            break;
                    }
                    if (arr[index - 1][0] !== "" && data[0] !== "") {
                        var piece = {
                            gte: (new Date(arr[index - 1][0])).getTime(),
                            lte: (new Date(data[0])).getTime(),
                            color: color
                        };

                        if (previousPiece === null) {
                            previousPiece = piece;
                        } else if (previousPiece.color === piece.color) {
                            previousPiece.lte = piece.lte;
                        } else {
                            visualMap.pieces.push(previousPiece);
                            previousPiece = piece;
                        }
                    }

                    if (index + 1 === arr.length) {
                        previousPiece.lte += 86400000; // add 1 day after, to color upper limit of chart
                        visualMap.pieces.push(previousPiece);
                    }
                });
                series.push(serie);
                visualMap.pieces[0].gte -= 86400000; // begin from 1 day before, to color lower limit of chart
                visualMaps.push(visualMap);
                scatterData = scatterData.concat(trip.data);
            });

            // for scatter plot
            var label = "Subidas";
            var valueIndex = 5;
            var seeLanding = $("#chartSwitch").prop("checked");
            if (seeLanding) {
                label = "Bajadas";
                valueIndex = 4;
            }
            var visualMap = {
                show: true,
                type: "piecewise",
                top: "top",
                right: "right",
                orient: "horizontal",
                pieces: [{gte: 1, lt: 5, color: colors[0], label: "Línea: carga [0, 25) % | {}: [1, 5)".replace("{}", label)},
                         {gte: 5, lt: 13, color: colors[1], label: "Línea: carga [25, 50) % | {}: [5, 13)".replace("{}", label)},
                         {gte: 13, lt: 15, color: colors[2], label: "Línea: carga [25, 75) % | {}: [13, 15)".replace("{}", label)},
                         {gte: 15, color: colors[3], label: "Línea: carga [75-100] % | {}: > 15".replace("{}", label)}],
                dimension: valueIndex,
                seriesIndex: series.length
            };
            visualMaps.push(visualMap);

            var scatterSerie = {
                type: "scatter",
                symbolSize: function (el) {
                    return el[valueIndex] * 0.2 + 4;
                },
                itemStyle: {
                    normal: {
                        color: "red"
                    }
                },
                data: scatterData
            };

            //generates markLines
            var markLines = [];
            var yMax = 0;
            _dataManager.yAxisData().forEach(function (item) {
                if (item.value > yMax) {
                    yMax = item.value;
                }
                var markLine = {
                    yAxis: item.value,
                    name: item.name
                };
                if (item.busStation) {
                    markLine.label = {
                        normal: {
                            color: "red"
                        }
                    };
                    markLine.name += " (ZP)";
                }
                markLines.push(markLine);
            });
            scatterSerie.markLine = {
                data: markLines,
                animation: false,
                silent: true,
                symbol: ["pin", null],
                label: {
                    normal: {
                        formatter: "{b} - {c}     ",
                        textStyle: {
                            fontSize: 9,
                            color: "#000"
                        },
                        position: "left"
                    }
                },
                lineStyle: {
                    normal: {
                        type: "solid",
                        opacity: 0.2,
                        color: "#000"
                    }
                }
            };
            //scatterSerie.data = null;
            series.push(scatterSerie);
            //console.log(series);
            //console.log(visualMaps);

            var options = {
                animation: false,
                series: series,
                visualMap: visualMaps,
                dataZoom: [{
                    show: true, type: "slider", xAxisIndex: 0, start: 0, end: 100,
                    realtime: false, showDataShadow: false, showDetail: false, bottom: "50px"
                }, {
                    show: true, type: "slider", yAxisIndex: 0, start: 0, end: 100,
                    realtime: false, showDataShadow: false, showDetail: false
                }],
                xAxis: {
                    type: "time", name: "Hora", boundaryGap: false, splitNumber: 15, splitLine: {show: false}
                },
                yAxis: {
                    type: "value", name: "Distancia en Ruta", splitLine: {show: false}, splitArea: {show: false},
                    axisLabel: {show: false}, axisTick: {show: false},
                    max: yMax
                },
                tooltip: {
                    show: true,
                    trigger: "item",
                    formatter: function (params) {
                        var row = [];
                        if (params.componentType === "series") {
                            row.push(params.marker);
                            var time = params.data[0];
                            var loadProfile = params.data[2];
                            var getOut = params.data[4];
                            var getIn = params.data[5];
                            if (params.componentSubType === "scatter") {
                                row.push("Tiempo: " + time);
                                row.push("Carga: " + loadProfile);
                                row.push("Bajadas: " + getOut);
                                row.push("Subidas: " + getIn);
                            }
                        }
                        return row.join("<br />");
                    }
                },
                grid: {
                    left: "300px",
                    bottom: "130px",
                    containLabel: false
                },
                toolbox: {
                    show: true,
                    itemSize: 20,
                    left: "center",
                    bottom: "15px",
                    feature: {
                        mark: {show: false},
                        restore: {show: false, title: "restaurar"},
                        saveAsImage: {show: true, title: "Guardar imagen", name: _dataManager.getDataName()},
                        dataView: {
                            show: true,
                            title: "Ver datos",
                            lang: ["Datos del gráfico", "cerrar", "refrescar"],
                            buttonColor: "#169F85",
                            readOnly: true
                        },
                        dataZoom: {
                            show: true, title: {
                                zoom: "Seleccionar área",
                                back: "Restablecer vista"
                            }
                        }
                    }
                }
            };

            // set height of chart
            //$("#barChart").height(yMax * 0.1);
            //_barChart.resize();
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
            _updateGlobalStats();
        };
        this.updateDatatable = function () {
            _updateDatatable();
        };
        this.showLoadingAnimationCharts = function () {
            var LOADING_TEXT = "Cargando...";
            _barChart.showLoading(null, {text: LOADING_TEXT});
        };
        this.hideLoadingAnimationCharts = function () {
            _barChart.hideLoading();
        };
    }

    function processData(dataSource, app) {
        console.log(dataSource);

        if (dataSource["status"]) {
            var status = dataSource["status"];
            showMessage(status);
            return;
        }

        var trips = dataSource.trips;
        var dataManager = new DataManager();
        var globalYAxis = [];
        var updateGlobalYAxis = false;

        for (var expeditionId in trips) {
            var trip = trips[expeditionId];

            // trip info
            var capacity = trip["info"]["capacity"];
            var licensePlate = trip["info"]["licensePlate"];
            var route = trip["info"]["route"];
            var timeTripInit = trip["info"]["timeTripInit"];
            var timeTripEnd = trip["info"]["timeTripEnd"];
            var authTimePeriod = trip["info"]["authTimePeriod"];
            var dayType = trip["info"]["dayType"];

            var stopQuantity = trip["stops"].length;

            if (stopQuantity > globalYAxis.length) {
                globalYAxis = [];
                updateGlobalYAxis = true;
            } else {
                updateGlobalYAxis = false;
            }

            var data = [];
            for (var stopIndex = 0; stopIndex < stopQuantity; stopIndex++) {
                var stopInfo = trip["stops"][stopIndex];
                var authStopCode = stopInfo["authStopCode"];
                var userStopCode = stopInfo["userStopCode"];
                var busStation = stopInfo["busStation"];
                //var order = stopInfo["order"];
                var name = stopInfo["name"];
                var distOnPath = stopInfo["distOnPath"];

                if (updateGlobalYAxis) {
                    var yPoint = {
                        "value": distOnPath,
                        "name": name,
                        "authStopCode": authStopCode,
                        "userStopCode": userStopCode,
                        "busStation": busStation
                    };
                    globalYAxis.push(yPoint);
                }
                var row = [];
                var stopTime = stopInfo["stopTime"];
                row.push(stopTime);
                row.push(stopInfo["distOnPath"]);
                row.push(stopInfo["loadProfile"]);
                row.push(stopInfo["loadProfile"] / capacity * 100);
                row.push(stopInfo["expandedGetOut"]);
                row.push(stopInfo["expandedGetIn"]);
                data.push(row);
            }

            trip = new Trip(expeditionId, route, licensePlate, capacity, timeTripInit,
                timeTripEnd, authTimePeriod, dayType, data);
            dataManager.addTrip(trip);
        }
        dataManager.yAxisData(globalYAxis);
        app.dataManager(dataManager);
    }

    // load filters
    (function () {
        // set locale
        moment.locale("es");

        $("#dayFilter").select2({placeholder: "Todos"});
        $("#dayTypeFilter").select2({placeholder: "Todos"});
        $("#periodFilter").select2({placeholder: "Todos"});
        $("#routeFilter").select2({placeholder: "Servicio"});//, allowClear: true});
        $("#minutePeriodFilter").select2({placeholder: "Todos"});

        var app = new ExpeditionApp();
        var makeAjaxCall = true;
        $("#btnUpdateChart").click(function () {
            var day = $("#dayFilter").val();
            var route = $("#routeFilter").val();
            var dayType = $("#dayTypeFilter").val();
            var period = $("#periodFilter").val();
            var minutes = $("#minutePeriodFilter").val();

            var params = {
                day: day
            };
            if (route) {
                params["route"] = route;
            }
            if (dayType) {
                params["dayType"] = dayType;
            }
            if (period) {
                params["period"] = period;
            }
            if (minutes) {
                params["halfHour"] = minutes;
            }

            if (makeAjaxCall) {
                makeAjaxCall = false;
                app.showLoadingAnimationCharts();
                var loadingIcon = " " + $("<i>").addClass("fa fa-cog fa-spin fa-2x fa-fw")[0].outerHTML;
                var previousMessage = $(this).html();
                var button = $(this).append(loadingIcon);
                $.getJSON(Urls["profile:getExpeditionData"](), params, function (data) {
                    processData(data, app);
                }).always(function () {
                    makeAjaxCall = true;
                    button.html(previousMessage);
                    app.hideLoadingAnimationCharts();
                });
            }
        });
        $(window).resize(function () {
            app.resizeCharts();
        });
        $("#menu_toggle").click(function () {
            app.resizeCharts();
        });
        $("#chartSwitch").change(function(){
            app.updateCharts();
        });
    })()
});