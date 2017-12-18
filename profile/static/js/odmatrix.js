"use strict";
$(document).ready(function () {
    function TransfersApp() {
        var _self = this;
        var chartId = "barChart";
        var _chart = echarts.init(document.getElementById(chartId), theme);

        this.resizeCharts = function () {
            _chart.resize();
        };

        this.updateChart = function (xData, yData, values, maxValue) {
            var options = {
                tooltip: {
                    show: true,
                    position: 'top',
                    formatter: function (params) {
                        if (params.componentType === "series" && params.seriesType === "heatmap") {
                            var labelOrigin = "<br />Origen: ";
                            var labelDestination = "<br />Destino: ";
                            var labelTransactions = "<br />N° Transacciones: ";

                            var origin = xData[params.data[0]] + " CódigoTransantiago " + "Nombre parada";
                            var destination = yData[params.data[1]] + " CódigoTransantiago " + "Nombre parada";
                            var transactions = params.data[2];

                            var legend = labelOrigin + origin + labelDestination + destination + labelTransactions + transactions;
                            return params.marker + legend;
                        }
                        return "";
                    }
                },
                animation: false,
                grid: {
                    height: '65%'
                },
                toolbox: {
                    show: true,
                    itemSize: 20,
                    left: "center",
                    bottom: "0px",
                    feature: {
                        saveAsImage: {show: true, title: "Guardar imagen", name: "506 00I"}
                    }
                },
                xAxis: {
                    type: 'category',
                    position: 'top',
                    data: xData,
                    splitArea: {
                        show: true
                    }
                },
                yAxis: {
                    type: 'category',
                    data: yData,
                    splitArea: {
                        show: true
                    }
                },
                visualMap: {
                    min: 0,
                    max: maxValue,
                    calculable: true,
                    orient: 'horizontal',
                    left: 'center',
                    bottom: '15%',
                    realtime: false,
                    inRange: {
                        color: ['#F5EFB7', '#BE434D']
                    }
                },
                series: [{
                    name: 'transfers',
                    type: 'heatmap',
                    data: values,
                    label: {
                        normal: {
                            show: false
                        }
                    },
                    itemStyle: {
                        normal: {
                            borderColor: 'black',
                            borderWidth: 0.5,
                        }
                    }
                }]
            };

            _chart.clear();
            _chart.setOption(options, {
                notMerge: true
            });
        };

        this.showLoadingAnimationCharts = function () {
            var loadingText = "Cargando...";
            _chart.showLoading(null, {text: loadingText});
        };
        this.hideLoadingAnimationCharts = function () {
            _chart.hideLoading();
        };
    }

    function processData(dataSource, app) {
        console.log(dataSource);

        if (dataSource["status"]) {
            var status = dataSource["status"];
            showMessage(status);
            return;
        }

        var matrix = dataSource.data.matrix;
        var maxValue = dataSource.data.maximum;

        var yAxis = [];
        var xAxis = [];
        var data = [];

        var yIndex = 0;
        var xIndex = 0;
        matrix.forEach(function (row) {
            var origin = row.origin;
            var destination = row.destination;
            yAxis.push(origin.authStopCode);
            destination.forEach(function (column) {
                var columnName = column.authStopCode;
                var oldXAxis = xAxis.indexOf(columnName);
                if (oldXAxis >= 0) {
                    data.push([oldXAxis, yIndex, column.value.toFixed(2)]);
                } else {
                    xAxis.push(columnName);
                    data.push([xIndex, yIndex, column.value.toFixed(2)]);
                    xIndex++;
                }
            });
            yIndex++;
        });
        app.updateChart(xAxis, yAxis, data, maxValue, matrix);
    }

    // load filters
    (function () {
        // set locale
        moment.locale("es");

        $("#dayFilter").select2();
        $("#routeFilter").select2({placeholder: "Servicio"});
        $("#dayTypeFilter").select2({placeholder: "Todos"});
        $("#periodFilter").select2({placeholder: "Todos"});

        var app = new TransfersApp();
        var makeAjaxCall = true;
        $("#btnUpdateChart").click(function () {
            var day = $("#dayFilter").val();
            var route = $("#routeFilter").val();
            var dayType = $("#dayTypeFilter").val();
            var period = $("#periodFilter").val();

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

            if (makeAjaxCall) {
                makeAjaxCall = false;
                app.showLoadingAnimationCharts();
                var loadingIcon = " " + $("<i>").addClass("fa fa-cog fa-spin fa-2x fa-fw")[0].outerHTML;
                var previousMessage = $(this).html();
                var button = $(this).append(loadingIcon);
                $.getJSON(Urls["profile:getODMatrixData"](), params, function (data) {
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
    })();
});