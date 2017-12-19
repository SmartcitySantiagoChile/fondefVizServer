"use strict";
$(document).ready(function () {
    function TransfersApp() {
        var _self = this;
        var matrixChartId = "matrixChart";
        var graphChartId = "graphChart";
        var _matrixChart = echarts.init(document.getElementById(matrixChartId), theme);
        var _graphChart = echarts.init(document.getElementById(graphChartId), theme);

        this.resizeCharts = function () {
            _matrixChart.resize();
            _graphChart.resize();
        };

        this.updateMatrixChart = function (xData, yData, values, maxValue) {
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
                            borderWidth: 0.5
                        }
                    }
                }]
            };

            _matrixChart.clear();
            _matrixChart.setOption(options, {
                notMerge: true
            });
        };

        this.updateGraphChart = function (stopCode, stopList, links, maxValue) {
            var colors = ['#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026'];
            function getColor(value) {
                var quantity = colors.length;
                var threshold = maxValue / quantity;
                return colors[parseInt(value / threshold)];
            }
            var data = [];
            var y = 0;
            var x = 0;
            stopList.forEach(function (targetStopCode, index) {
                data.push({
                    name: targetStopCode,
                    x: x,
                    y: y
                });
                x += 60;
            });
            links = links || [];
            links = links.map(function (link) {
                link.lineStyle = {
                    normal: {
                        width: 1 + 8 * link.value / maxValue,
                        curveness: 0.2 + 0.8 * link.value / maxValue,
                        color: getColor(link.value)
                    }
                };
                return link;
            });

            var options = {
                animationDurationUpdate: 1500,
                animationEasingUpdate: "quinticInOut",
                tooltip: {
                    show: true,
                    position: 'top',
                    formatter: function (params) {
                        if (params.componentType === "series" && params.seriesType === "graph") {
                            var legend = "";
                            if (params.dataType === "node") {
                                var labelOrigin = "Parada: ";
                                legend = labelOrigin + params.name;
                            } else if (params.dataType === "edge") {
                                var labelTransactions = "<br />N° Transacciones: ";
                                var transactions = params.value.toFixed(2);
                                legend = params.marker + params.name + labelTransactions + transactions;
                            }
                            return legend;
                        }
                        return "";
                    }
                },
                toolbox: {
                    show: true,
                    itemSize: 20,
                    left: "center",
                    bottom: "0px",
                    feature: {
                        saveAsImage: {show: true, title: "Guardar imagen", name: stopCode}
                    }
                },
                grid: {
                    left: 0,
                    right: 0,
                    bottom: 0,
                    top: 0
                },
                visualMap: {
                    type: "piecewise",
                    min: 0,
                    max: maxValue,
                    calculable: true,
                    realtime: false,
                    splitNumber: 5,
                    inRange: {
                        color: colors
                    },
                    outOfRange: {
                        color: 'black'
                    },
                    percision: 1,
                    orient: 'horizontal',
                    left: 'center',
                    bottom: 30
                },
                series: [{
                    name: 'graph',
                    data: data,
                    links: links,
                    type: 'graph',
                    symbol: 'image:///static/img/stop.png',
                    symbolSize: [15, 20],
                    roam: true,
                    circular: {
                        rotateLabel: true
                    },
                    label: {
                        normal: {
                            show: false,
                            position: 'top',
                            rotate: 45,
                            color: 'black'
                        },
                        emphasis: {
                            show: false
                        }
                    },
                    edgeSymbol: ["circle", "arrow"],
                    edgeSymbolSize: [5, 12],
                    edgeLabel: {
                        normal: {
                            textStyle: {
                                color: "#000",
                                fontSize: 100,
                                show: true
                            }
                        }
                    }
                }]
            };

            _graphChart.clear();
            _graphChart.setOption(options, {
                notMerge: true
            });
        };

        this.updateClickNodeEvent = function(stopList, links, maxValue) {
            _graphChart.off('click');
            _graphChart.on('click', function(params){
                console.log(params);
                if (params.componentType === 'series' && params.componentSubType === 'graph') {
                    var clickedStopCode = params.data.name;
                    _self.updateGraphChart(clickedStopCode, stopList, links[clickedStopCode], maxValue);
                    $("#stops>button.active").removeClass('active');
                    $("#" + clickedStopCode).addClass('active');
                }
            });
        };

        this.showLoadingAnimationCharts = function () {
            var loadingText = "Cargando...";
            _matrixChart.showLoading(null, {text: loadingText});
            _graphChart.showLoading(null, {text: loadingText});
        };
        this.hideLoadingAnimationCharts = function () {
            _matrixChart.hideLoading();
            _graphChart.hideLoading();
        };
    }

    function buildStopButtons(stopCodeList, buttonEventFunction) {
        var DIV = $("#stops");
        DIV.empty();

        stopCodeList.forEach(function (stopCode) {
            var button = $("<button id='" + stopCode + "' class='btn btn-default' type='button'>" + stopCode + "</button>");
            button.click(function () {
                buttonEventFunction(stopCode);
                $("#stops>button.active").removeClass('active');
                $("#" + stopCode).addClass('active');
            });
            DIV.append(button);
        });
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
        var dictionary = {};
        var links = {};
        matrix.forEach(function (row) {
            var originCode = row.origin.userStopCode;
            var destination = row.destination;

            yAxis.push(originCode);
            links[originCode] = [];
            destination.forEach(function (column) {
                var columnName = column.userStopCode;
                var oldXAxis = xAxis.indexOf(columnName);
                if (oldXAxis >= 0) {
                    data.push([oldXAxis, yIndex, column.value.toFixed(2)]);
                } else {
                    xAxis.push(columnName);
                    data.push([xIndex, yIndex, column.value.toFixed(2)]);
                    xIndex++;
                }
                if (column.value > 0) {
                    links[originCode].push({
                        source: originCode,
                        target: columnName,
                        value: column.value
                    });
                }
            });
            yIndex++;
        });
        app.updateMatrixChart(xAxis, yAxis, data, maxValue, dictionary);
        app.updateClickNodeEvent(xAxis, links, maxValue);
        buildStopButtons(xAxis, function(stopCode){
            app.updateGraphChart(stopCode, xAxis, links[stopCode], maxValue);
        });
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