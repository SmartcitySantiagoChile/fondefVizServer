"use strict";

$(document).ready(function () {

    var VariationApp = function () {
        var _self = this;

        // echarts stuffs
        var nPerPag = 20;
        var mChart = echarts.init(document.getElementById("main"));
        var periods = [
            "00:00", "00:30", "01:00", "01:30", "02:00", "02:30", "03:00", "03:30", "04:00", "04:30", "05:00", "05:30", "06:00", "06:30", "07:00", "07:30", "08:00", "08:30", "09:00", "09:30",
            "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30",
            "20:00", "20:30", "21:00", "21:30", "22:00", "22:30", "23:00", "23:30"
        ];
        // var colors = ["#ffffff", "#ff0000", "#ff4500", "#ff8000", "#ffff00", "#01df01", "#088a08", "#045fb4", "#dfdfdf"];
        var vel_range = ["Sin Datos Mes", "< 30%", "]30% - 45%]", "]45% - 60%]", "]60% - 75%]", "]75% - 90%]", "]90% - 100%]", "> 100%", "Sin Datos Dia"];

        var colors = ["#ffffff", "#ff0000", "#ff7f00", "#ffff00", "#00ff00", "#007f00", "#0000ff", "#dfdfdf"];
        var metaOptions = {
            tooltip: {
                position: "top",
                formatter: ""
            },
            animation: false,
            grid: {
                left: "90",
                bottom: "90",
                right: "210",
                top: "20"
            },
            xAxis: {
                type: "category",
                data: periods,
                splitArea: {
                    show: true
                },
                axisLabel: {
                    rotate: 90,
                    interval: 1
                },
                name: "Período de media hora",
                nameLocation: "center",
                nameGap: 50
            },
            yAxis: {
                type: "category",
                data: [],
                splitArea: {
                    show: true
                },
                axisLabel: {
                    interval: 0
                },
                name: "Servicio",
                nameLocation: "center",
                nameGap: 75
            },
            visualMap: {
                min: 0,
                max: 8,
                type: "piecewise",
                calculable: true,
                orient: "vertical",
                right: "5%",
                top: "center",
                pieces: [
                    {min: 7.5, label: vel_range[8]},
                    {min: 6.5, max: 7.5, label: vel_range[7]},
                    {min: 5.5, max: 6.5, label: vel_range[6]},
                    {min: 4.5, max: 5.5, label: vel_range[5]},
                    {min: 3.5, max: 4.5, label: vel_range[4]},
                    {min: 2.5, max: 3.5, label: vel_range[3]},
                    {min: 1.5, max: 2.5, label: vel_range[2]},
                    {min: 0.5, max: 1.5, label: vel_range[1]},
                    {max: 0.5, label: vel_range[0]}
                ],
                inRange: {
                    color: colors
                }
            },
            series: [{
                name: "Velocidad",
                type: "heatmap",
                data: [],
                label: {
                    normal: {
                        show: false
                    }
                },
                itemHeight: "15px",
                itemWidth: "15px",
                itemStyle: {
                    emphasis: {
                        shadowBlur: 10,
                        shadowColor: "rgba(0, 0, 0, 0.5)"
                    }
                }
            }],
            toolbox: {
                left: "center",
                bottom: "bottom",
                show: true,
                feature: {
                    mark: {show: false},
                    restore: {show: false, title: "restaurar"},
                    saveAsImage: {show: true, title: "Guardar imagen", name: "changeme"}
                }
            }
        };

        this.updateChart = function (nReal, data, routes, variations) {
            var val = "" + (130 + nPerPag * 15) + "px";
            $("#main").css("height", val);

            var options = $.extend({}, metaOptions);
            if (nReal > nPerPag) {
                options.dataZoom = {
                    type: "slider",
                    yAxisIndex: [0],
                    start: 0,
                    end: 100 * nPerPag / nReal,
                    zoomLock: true,
                    labelFormatter: ""
                };
            }
            options.series[0].data = data;
            options.yAxis.data = routes;

            var formatter = function (obj) {
                var s = "Horario: entre " + periods[obj.data[0]] + " y " + periods[(obj.data[0] + 1) % periods.length];
                s += "<br/>Servicio: " + routes[obj.data[1]];
                if (0 < obj.data[2] && obj.data[2] < 7) {
                    s += "<br/>Variación: " + (variations[obj.data[0]][obj.data[1]][1] - 100).toFixed(1) + " %";
                    s += "<br/>Velocidad promedio día: " + variations[obj.data[0]][obj.data[1]][2].toFixed(1) + " km/h";
                    s += "<br/>Velocidad promedio 30 días previos: " + variations[obj.data[0]][obj.data[1]][3].toFixed(1) + " km/h";
                    s += "<br/># observaciones día: " + variations[obj.data[0]][obj.data[1]][4];
                    s += "<br/># observaciones 30 días previos: " + variations[obj.data[0]][obj.data[1]][5];
                    s += "<br/>Desviación día: " + variations[obj.data[0]][obj.data[1]][6].toFixed(1) + " km/h";
                    s += "<br/>Desviación 30 días previos: " + variations[obj.data[0]][obj.data[1]][7].toFixed(1) + " km/h";
                } else if (0 === obj.data[2]) {
                    s += "<br/>Sin datos para día seleccionado";
                } else if (7 === obj.data[2]) {
                    s += "<br/>Sin datos históricos";
                }

                return s;
            };
            options.tooltip.formatter = formatter;
            console.log(nReal, nPerPag, 100 * nPerPag / nReal);

            mChart.setOption(options, {
                notMerge: true
            });
            mChart.resize({});
        };

        this.showLoadingAnimationCharts = function () {
            mChart.showLoading(null, {text: "Cargando..."});
        };

        this.hideLoadingAnimationCharts = function () {
            mChart.hideLoading();
        };

        this.resizeChart = function () {
            mChart.resize();
        };
    };

    function processData(dataSource, app) {
        console.log(dataSource);

        if (dataSource.status && dataSource.status.code !== 250) {
            return;
        }

        var routes = dataSource.routes;
        var variations = dataSource.variations;
        var data = [];
        variations.forEach(function (vec, i) {
            vec.forEach(function (elem, j) {
                data.push([i, j, elem[0]]);
            });
        });
        var nReal = routes.length;
        app.updateChart(nReal, data, routes, variations);
    }

    // load filters
    (function () {
        loadAvailableDays(Urls["esapi:availableSpeedDays"]());
        loadRangeCalendar(Urls["esapi:availableSpeedDays"](),{singleDatePicker: true});

        var app = new VariationApp();

        var previousCall = function () {
            app.showLoadingAnimationCharts();
        };
        var afterCall = function (data) {
            processData(data, app);
            app.hideLoadingAnimationCharts();
        };
        var opts = {
            urlFilterData: Urls["esapi:speedVariation"](),
            urlRouteData: Urls["esapi:availableSpeedRoutes"](),
            previousCallData: previousCall,
            afterCallData: afterCall,
            singleDatePicker: true
        };
        new FilterManager(opts);
        $(window).resize(function () {
            app.resizeChart();
        });
        $("#menu_toggle").click(function () {
            app.resizeChart();
        });
    })();
});