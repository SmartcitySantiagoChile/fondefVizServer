"use strict";
$(document).ready(function () {
    // define logic to manipulate data
    function Trip(expeditionId, route, licensePlate, busCapacity, stopTime, stopTimePeriod, dayType, loadProfile,
                  expandedGetIn, expandedLanding) {
        this.expeditionId = expeditionId;
        this.route = route;
        this.licensePlate = licensePlate;
        this.busCapacity = busCapacity;
        this.stopTime = stopTime;
        this.stopTimePeriod = stopTimePeriod;
        this.dayType = dayType;
        this.loadProfile = loadProfile;
        this.expandedGetIn = expandedGetIn;
        this.expandedLanding = expandedLanding;
        this.visible = true;
    }

    // define logic to manipulate data
    function Stop(name, userStopCode, authorityStopCode, expandedBoarding, expandedALighting, loadProfile,
                  busCapacity, busSaturation, maxLoadProfile) {
        this.name = name;
        this.userStopCode = userStopCode;
        this.authorityStopCode = authorityStopCode;
        this.expandedBoarding = expandedBoarding;
        this.expandedAlighting = expandedALighting;
        this.loadProfile = loadProfile;
        this.busCapacity = busCapacity;
        this.busSaturation = busSaturation;
        this.maxLoadProfile = maxLoadProfile;
        this.visible = true;

    }

    /*
     * to manage grouped data
     */
    function DataManager() {
        //stops
        let _stops = [];
        // stop list
        var _xAxisData = null;
        // y average data
        var _yAxisData = null;
        // trips used to calculate average profile
        var _stopsUsed = 0;

        this.addStop = function (stop) {
            // create stop identifier
            _stops.push(stop);
        };

        this.getStops = function(){
            return _stops;
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
        this.stopUsed = function () {
            return _stopsUsed;
        };
        this.cleanData = function () {
            _stops = [];
            _xAxisData = null;
            _yAxisData = null;
            _stopsUsed = 0;
        };

        this.calculateAverage = function () {
            // erase previous visible data
            var xAxisLength = _xAxisData.length;
            var counterByStop = [];
            var capacityByStop = [];
            var stopQuantity = _stops.length;

            _yAxisData = {
                expandedLanding: [],
                expandedGetIn: [],
                saturationRateBefore: [],
                saturationRateAfter: [],
                saturationDiff: [],
                positiveSaturationRateAfter: [],
                negativeSaturationRateAfter: [],
                averageSaturationRateBefore: [],
                averageSaturationRateAfter: []
            };

            for (var i = 0; i < xAxisLength; i++) {
                _yAxisData.expandedGetIn.push(0);
                _yAxisData.expandedLanding.push(0);
                _yAxisData.saturationRateBefore.push(0);
                _yAxisData.saturationRateAfter.push(0);
                _yAxisData.saturationDiff.push(0);
                _yAxisData.positiveSaturationRateAfter.push(0);
                _yAxisData.negativeSaturationRateAfter.push(0);
                _yAxisData.averageSaturationRateBefore.push(0);
                _yAxisData.averageSaturationRateAfter.push(0);

                counterByStop.push(0);
                capacityByStop.push(0);
            }

            for (var stopIndex = 0; stopIndex < stopQuantity; stopIndex++) {
                var stop = _stops[stopIndex];

                if (!stop.visible) {
                    continue;
                }

                var key = _xAxisData.indexOf(stop.userStopCode);

                _yAxisData.expandedLanding[key] += stop.expandedAlighting;
                _yAxisData.expandedGetIn[key] += stop.expandedBoarding;
                _yAxisData.saturationRateBefore[key] += stop.loadProfile;
                _yAxisData.saturationDiff[key] += stop.expandedBoarding - stop.expandedAlighting;

                counterByStop[key] += 1;
                capacityByStop[key] += stop.busCapacity;
            }


            // it calculates average
            for (var stopIndex = 0; stopIndex < xAxisLength; stopIndex++) {
                var percentageAfter = 0;

                if (counterByStop[stopIndex] !== 0) {
                    _yAxisData.expandedLanding[stopIndex] = _yAxisData.expandedLanding[stopIndex] / counterByStop[stopIndex];
                    _yAxisData.expandedGetIn[stopIndex] = _yAxisData.expandedGetIn[stopIndex] / counterByStop[stopIndex];

                    _yAxisData.averageSaturationRateBefore[stopIndex] = _yAxisData.saturationRateBefore[stopIndex] / counterByStop[stopIndex];
                    _yAxisData.averageSaturationRateAfter[stopIndex] = (_yAxisData.saturationRateBefore[stopIndex] + _yAxisData.saturationDiff[stopIndex]) / counterByStop[stopIndex];
                } else {
                    _yAxisData.expandedLanding[stopIndex] = 0;
                    _yAxisData.expandedGetIn[stopIndex] = 0;
                    _yAxisData.averageSaturationRateBefore[stopIndex] = 0;
                    _yAxisData.averageSaturationRateAfter[stopIndex] = 0;
                }

                if (capacityByStop[stopIndex] !== 0) {
                    _yAxisData.saturationRateBefore[stopIndex] = _yAxisData.saturationRateBefore[stopIndex] / capacityByStop[stopIndex] * 100;
                    percentageAfter = _yAxisData.saturationDiff[stopIndex] / capacityByStop[stopIndex] * 100;
                } else {
                    _yAxisData.saturationRateBefore[stopIndex] = 0;
                }

                var incValue = 0;
                var decValue = 0;
                if (percentageAfter > 0) {
                    incValue = percentageAfter;
                } else if (percentageAfter < 0) {
                    decValue = percentageAfter * -1;
                }
                _yAxisData.saturationRateAfter[stopIndex] = _yAxisData.saturationRateBefore[stopIndex] + percentageAfter;
                _yAxisData.positiveSaturationRateAfter[stopIndex] = incValue;
                _yAxisData.negativeSaturationRateAfter[stopIndex] = decValue;
            }
        };

        this.getAttrGroup = function (attrName, formatFunc) {
            var values = [];
            var dict = {};
            for (var i in _stops) {
                var stop = _stops[i];
                if (!stop.visible) {
                    continue;
                }
                var attrValue = stop[attrName];
                attrValue = (formatFunc === undefined ? attrValue : formatFunc(attrValue));
                if (dict[attrValue]) {
                    dict[attrValue]++;
                } else {
                    dict[attrValue] = 1;
                }
            }
            for (var name in dict) {
                values.push({
                    name: name,
                    value: dict[name]
                });
            }
            return values;
        };
    }

    function ExpeditionApp() {
        var _self = this;
        var _dataManager = new DataManager();
        var _barChart = echarts.init(document.getElementById("barChart"), theme);

        this.dataManager = function (dataManager) {
            if (dataManager === undefined) {
                return _dataManager;
            }
            _dataManager = dataManager;
            this.updateCharts();
        };

        this.resizeCharts = function () {
            _barChart.resize();
        };

        var _updateBarChart = function () {
            _dataManager.calculateAverage(); //todo: aqui estoy
            var yAxisData = _dataManager.yAxisData();
            var xAxisData = _dataManager.xAxisData();

            // get out, get in, load profile, percentage ocupation
            var yAxisDataName = ["Subidas promedio", "Bajadas promedio", "% Ocupación promedio a la llegada"];
            var yChartType = ["bar", "bar", "bar", "bar", "bar"];
            var yStack = [null, null, "stack", "stack", "stack"];
            var xGridIndex = [1, 1, 0, 0, 0];
            var yGridIndex = [1, 1, 0, 0, 0];
            var dataName = ["expandedGetIn",
                "expandedLanding",
                //"saturationRateBefore",
                "saturationRateAfter",
                "positiveSaturationRateAfter",
                "negativeSaturationRateAfter"];
            var positiveItemStyle = {
                normal: {
                    color: "#33CC70",
                    barBorderRadius: 0,
                    label: {
                        show: true,
                        position: "top",
                        formatter: function (p) {
                            return p.value > 0 ? ("▲" + p.value.toFixed(1) + "%") : "";
                        }
                    }
                }
            };
            var negativeItemStyle = {
                normal: {
                    color: "#C12301",
                    barBorderRadius: 0,
                    stack: "stack",
                    label: {
                        show: true,
                        position: "top",
                        formatter: function (p) {
                            return p.value > 0 ? ("▼" + p.value.toFixed(1) + "%") : "";
                        }
                    }
                }
            };

            var yItemStyle = [{}, {}, {}, positiveItemStyle, negativeItemStyle];

            var series = [];
            for (var index = 0; index < dataName.length; index++) {
                var serie = {
                    name: yAxisDataName[index],
                    stack: yStack[index],
                    type: yChartType[index],
                    data: yAxisData[dataName[index]],
                    itemStyle: yItemStyle[index],
                    xAxisIndex: xGridIndex[index],
                    yAxisIndex: yGridIndex[index]
                };
                series.push(serie);
            }

            var options = {

                legend: {
                    data: yAxisDataName,
                    right: 0,
                    top: "45px"
                },
                axisPointer: {
                    link: [{xAxisIndex: "all"}],
                    snap: true
                },
                toolbox: {
                    show: true,
                    itemSize: 20,
                    left: "center",
                    bottom: "0px",
                    feature: {
                        mark: {show: false},
                        restore: {show: false, title: "restaurar"},
                        saveAsImage: {show: true, title: "Guardar imagen", name: "Paraderos"},  //TODO: elegir un nombre para guardar
                        dataView: {
                            show: true,
                            title: "Ver datos",
                            lang: ["Datos del gráfico", "cerrar", "refrescar"],
                            buttonColor: "#169F85",
                            readOnly: true,
                            optionToContent: function (opt) {
                                var axisData = opt.xAxis[0].data;
                                var series = opt.series;
                                var yData = _dataManager.yAxisData();

                                var textarea = document.createElement('textarea');
                                textarea.style.cssText = 'width:100%;height:100%;font-family:monospace;font-size:14px;line-height:1.6rem;';
                                textarea.readOnly = "true";

                                var dayTypeFilter = $("#dayTypeFilter").val() !== null ? $("#dayTypeFilter").val().join("\t") : ["Todos"];
                                var periodFilter = $("#periodFilter").val() !== null ? $("#periodFilter").val().join("\t") : ["Todos"];
                                var meta = "tipo(s) de día:\t" + dayTypeFilter + "\n";
                                meta += "período(s):\t" + periodFilter + "\n\n";

                                var header = "Código usuario\tCódigo transantiago\tNombre parada\tServicio\tCarga promedio a la llegada\tCarga promedio a la salida";
                                series.forEach(function (el, index) {
                                    var name = el.name;
                                    if (index === 3) {
                                        name = "Variación % positiva"
                                    } else if (index === 4) {
                                        name = "Variación % negativa"
                                    }
                                    header += "\t" + name;
                                });
                                header += "\n";
                                var body = "";
                                axisData.forEach(function (authorityStopCode, index) {
                                    var serieValues = [yData.averageSaturationRateBefore[index], yData.averageSaturationRateAfter[index]];
                                    series.forEach(function (serie) {
                                        serieValues.push(serie.data[index]);
                                    });
                                    serieValues = serieValues.join("\t").replace(/\./g, ",") + "\n";
                                    body += ["codigo", "codigo-autoridad", "nombre", "codigo-ruta", serieValues].join("\t"); // TODO:crear segun serie
                                });

                                textarea.value = meta + header + body;
                                return textarea;
                            }
                        }
                    }
                },
                grid: [
                    {x: "10px", y: "70px", height: "30%", right: "0px", containLabel: true},
                    {x: "30px", y2: "75px", height: "33%", right: "0px", containLabel: true}
                ],
                xAxis: [
                    {
                        gridIndex: 0,
                        type: "category",
                        data: xAxisData,
                        axisLabel: {show: false},
                        axisTick: {interval: 0}
                    },
                    {gridIndex: 1, type: "category", data: xAxisData, axisLabel: {rotate: 30, interval: 0}}
                ],
                yAxis: [
                    {
                        gridIndex: 0, type: "value", name: "Porcentaje", max: 100,
                        axisLabel: {formatter: "{value} %"}, nameLocation: "middle", nameGap: 40,
                        axisLine: {onZero: false}
                    },
                    {
                        gridIndex: 1,
                        type: "value",
                        name: "Pasajeros",
                        position: "left",
                        nameLocation: "middle",
                        nameGap: 30
                    }
                ],
                series: series,
                tooltip: {
                    axisPointer: {
                        type: "shadow"
                    },
                    trigger: "axis",
                    //alwaysShowContent: true,
                    formatter: function (params) {
                        if (Array.isArray(params)) {
                            params.sort(function (a, b) {
                                return a.seriesIndex > b.seriesIndex
                            });
                            var xValue = params[0].dataIndex;
                            var head = xAxisData[xValue];
                            var info = [];
                            info.push("Código usuario: " + head);
                            info.push("Código transantiago: " + _dataManager.getStops()[xValue].authorityStopCode);
                            info.push("Nombre paradero: " + _dataManager.getStops()[xValue].name);
                            var ball = "<span style='display:inline-block;margin-right:5px;border-radius:10px;width:9px;height:9px;background-color:{}'></span>";
                            for (var i = 0; i < params.length - 1; i++) {
                                var el = params[i];
                                var serieIndex = el.seriesIndex;
                                var name = el.seriesName;
                                var value = el.value.toFixed(2);
                                if (serieIndex === 2) {
                                    value = yAxisData.saturationRateBefore[xValue].toFixed(1) + "% (" + yAxisData.averageSaturationRateBefore[xValue].toFixed(2) + ")";
                                } else if (serieIndex === 3) {
                                    var sign = "▲";
                                    if (el.value === 0) {
                                        el = params[i + 1];
                                        sign = "▼";
                                    }
                                    name = "Variación";
                                    value = sign + el.value.toFixed(1) + "%";
                                }
                                var colorBall = ball.replace("{}", el.color);
                                info.push(colorBall + name + ": " + value);
                            }
                            // add saturation rate after
                            var saturationRateInfo = ball.replace("{}", "#3145f7") + "Tasa ocupación promedio a la salida:" + yAxisData.saturationRateAfter[xValue].toFixed(1) + "% (" + yAxisData.averageSaturationRateAfter[xValue].toFixed(2) + ")";
                            info.push(saturationRateInfo);
                            return info.join("<br />");
                        } else {
                            var title = params.data.name;
                            var name = params.seriesName;
                            var value = params.value.toFixed(2);
                            return title + "<br />" + name + ": " + value;
                        }
                    }
                }
            };

            _barChart.clear();
            _barChart.setOption(options, {
                notMerge: true
            });
        };

        var _updateGlobalStats = function () {
            $("#expeditionNumber").html(_dataManager.stopUsed());
            $("#expeditionNumber2").html(_dataManager.stopUsed());
        };

        this.updateCharts = function () {
            _updateBarChart();
            _updateGlobalStats();
        };

        this.showLoadingAnimationCharts = function () {
            var loadingText = "Cargando...";
            _barChart.showLoading(null, {text: loadingText});
        };
        this.hideLoadingAnimationCharts = function () {
            _barChart.hideLoading();
        };
    }

    function processData(dataSource, app) {

        if (dataSource.status) {
            return;
        }

        var dataManager = new DataManager();
        var stopGroupXAxisData = [];


        for (let stop in dataSource){
            let name = dataSource[stop].userStopName.hits['hits'][0]['_source']['userStopName'];
            let userStopCode = dataSource[stop].userStopCode.hits['hits'][0]['_source']['userStopCode'];
            let authorityStopCode = dataSource[stop].key;
            let expandedBoarding = dataSource[stop].expandedBoarding.value;
            let expandedAlighting = dataSource[stop].expandedAlighting.value;
            let loadProfile = dataSource[stop].loadProfile.value;
            let busCapacity = dataSource[stop].busCapacity.value;
            let busSaturation = dataSource[stop].busSaturation.value;
            let maxLoadProfile = dataSource[stop].maxLoadProfile.value;
            let stop_object = new Stop(name, userStopCode, authorityStopCode, expandedBoarding, expandedAlighting, loadProfile,
                busCapacity, busSaturation, maxLoadProfile);

            dataManager.addStop(stop_object);
        }

        var xAxisData = dataManager.getAttrGroup("userStopCode").map(function (e) {
            return e.name;
        });
        dataManager.xAxisData(xAxisData);
        app.dataManager(dataManager);
    }

    // load filters
    (function () {
        loadAvailableDays(Urls["esapi:availableProfileDays"]());
        loadRangeCalendar(Urls["esapi:availableProfileDays"](), {});


        var app = new ExpeditionApp();
        var previousCall = function () {
            app.showLoadingAnimationCharts();
        };
        var afterCall = function (data) {
            processData(data, app);
            app.hideLoadingAnimationCharts();
        };
        var opts = {
            urlFilterData: Urls["esapi:BoardingAndAlightingAverageByStops"](),
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
    })();
});