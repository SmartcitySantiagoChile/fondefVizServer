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
                    position: "top",
                    formatter: function (params) {
                        if (params.componentType === "series" && params.seriesType === "heatmap") {
                            var labelOrigin = "<br />Origen: ";
                            var labelDestination = "<br />Destino: ";
                            var labelTransactions = "<br />N° Transacciones: ";

                            var originData = yData[params.data[1]];
                            var origin = originData.userStopCode + " " + originData.authStopCode + " " + originData.stopName;
                            var destinationData = xData[params.data[0]];
                            var destination = destinationData.userStopCode + " " + destinationData.authStopCode + " " + destinationData.stopName;
                            var transactions = params.data[2];

                            var legend = labelOrigin + origin + labelDestination + destination + labelTransactions + transactions;
                            return params.marker + legend;
                        }
                        return "";
                    }
                },
                animation: false,
                grid: {
                    height: "65%"
                },
                toolbox: {
                    show: true,
                    itemSize: 20,
                    left: "center",
                    bottom: "0px",
                    feature: {
                        saveAsImage: {show: true, title: "Guardar imagen", name: $("#authRouteFilter").val()},
                        dataView: {
                            show: true,
                            title: "Ver datos",
                            lang: ["Datos del gráfico", "cerrar", "refrescar"],
                            buttonColor: "#169F85",
                            readOnly: true,
                            optionToContent: function (opt) {
                                console.log(opt);
                                var textarea = document.createElement("textarea");
                                textarea.style.cssText = "width:100%;height:100%;font-family:monospace;font-size:14px;line-height:1.6rem;";
                                textarea.readOnly = "true";

                                var header = "Parada de origen\tPara de destino\tNúmero de etapas\n";
                                var series = opt.series;

                                var stopList = yData;
                                var body = "";

                                series.forEach(function (serie) {
                                    console.log(serie);
                                    var serieValues = [];
                                    serie.data.forEach(function (dataRow) {
                                        var originId = dataRow[1];
                                        var destinationId = dataRow[0];
                                        var stageNumber = dataRow[2];

                                        var originObj = stopList[originId];
                                        var destinationObj = stopList[destinationId];
                                        serieValues.push(originObj.userStopCode + " " + originObj.authStopCode + " " + originObj.stopName);
                                        serieValues.push(destinationObj.userStopCode + " " + destinationObj.authStopCode + " " + destinationObj.stopName);
                                        serieValues.push(stageNumber);
                                        body += serieValues.join("\t") + "\n";
                                        serieValues.length = 0;
                                    });
                                });
                                body = body.replace(/\./g, ",");
                                textarea.value = header + body;
                                return textarea;
                            }
                        }
                    }
                },
                xAxis: {
                    type: "category",
                    name: "Parada de destino",
                    nameLocation: "center",
                    nameTextStyle: {
                        fontSize: 14
                    },
                    nameGap: 30,
                    position: "top",
                    data: xData.map(function (el) {
                        return el.userStopCode;
                    }),
                    splitArea: {
                        show: true
                    }
                },
                yAxis: {
                    type: "category",
                    name: "Parada de origen",
                    nameLocation: "center",
                    nameGap: 60,
                    nameTextStyle: {
                        fontSize: 14
                    },
                    data: yData.map(function (el) {
                        return el.userStopCode;
                    }),
                    splitArea: {
                        show: true
                    },
                    inverse: true
                },
                visualMap: {
                    min: 0,
                    max: maxValue,
                    calculable: true,
                    orient: "horizontal",
                    left: "center",
                    bottom: "15%",
                    realtime: false,
                    inRange: {
                        color: ["#F5EFB7", "#BE434D"]
                    }
                },
                series: [{
                    name: "transfers",
                    type: "heatmap",
                    data: values,
                    label: {
                        normal: {
                            show: false
                        }
                    },
                    itemStyle: {
                        normal: {
                            borderColor: "black",
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

        this.updateGraphChart = function (stopCode, stopObjList, links, maxValue) {
            var colors = ["#fee090", "#fdae61", "#f46d43", "#d73027", "#a50026"];

            function getColor(value) {
                var quantity = colors.length;
                var threshold = maxValue / quantity;
                return colors[parseInt(value / threshold)];
            }

            var data = [];
            var y = 0;
            var x = 0;
            stopObjList.forEach(function (stopObj) {
                data.push({
                    name: stopObj.userStopCode,
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
                backgroundColor: "#CDCDCD",
                animationDurationUpdate: 1500,
                animationEasingUpdate: "quinticInOut",
                tooltip: {
                    show: true,
                    position: "top",
                    formatter: function (params) {
                        console.log(params);
                        if (params.componentType === "series" && params.seriesType === "graph") {
                            var legend = "";
                            if (params.dataType === "node") {
                                var labelOrigin = "Parada: ";
                                var stopObj = stopObjList.filter(function (el) {
                                    return params.name === el.userStopCode
                                })[0];
                                legend = labelOrigin + params.name + " " + stopObj.authStopCode + " " + stopObj.stopName;
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
                        color: "black"
                    },
                    percision: 1,
                    orient: "horizontal",
                    left: "center",
                    bottom: 30
                },
                series: [{
                    name: "graph",
                    data: data,
                    links: links,
                    type: "graph",
                    symbol: "image:///static/profile/img/stop.png",
                    symbolSize: [15, 20],
                    roam: true,
                    circular: {
                        rotateLabel: true
                    },
                    label: {
                        normal: {
                            show: false,
                            position: "top",
                            rotate: 45,
                            color: "black"
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

        this.updateClickNodeEvent = function (stopList, links, maxValue) {
            _graphChart.off("click");
            _graphChart.on("click", function (params) {
                console.log(params);
                if (params.componentType === "series" && params.componentSubType === "graph") {
                    var clickedStopCode = params.data.name;
                    _self.updateGraphChart(clickedStopCode, stopList, links[clickedStopCode], maxValue);
                    $("#stops>button.active").removeClass("active");
                    $("#" + clickedStopCode).addClass("active");
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
                $("#stops>button.active").removeClass("active");
                $("#" + stopCode).addClass("active");
            });
            DIV.append(button);
        });
    }

    function processData(dataSource, app) {
        console.log(dataSource);

        if (dataSource.status) {
            return;
        }

        var matrix = dataSource.data.matrix;
        var maxValue = dataSource.data.maximum;

        var yAxis = dataSource.data.stopList;
        var nameXAxis = dataSource.data.stopList.map(function (el) {
            return el.userStopCode;
        });
        var nameYAxis = nameXAxis.slice();
        var xAxis = dataSource.data.stopList;
        var data = [];

        var links = {};
        matrix.forEach(function (row) {
            var origin = row.origin;
            var destination = row.destination;

            links[origin.userStopCode] = [];
            destination.forEach(function (column) {
                var columnName = column.userStopCode;
                var xIndex = nameXAxis.indexOf(columnName);
                var yIndex = nameYAxis.indexOf(origin.userStopCode);
                data.push([xIndex, yIndex, column.value.toFixed(2)]);

                if (column.value > 0) {
                    links[origin.userStopCode].push({
                        sourceObj: origin,
                        targetObj: column,
                        source: origin.userStopCode,
                        target: columnName,
                        value: column.value
                    });
                }
            });
        });
        app.updateMatrixChart(xAxis, yAxis, data, maxValue);
        app.updateClickNodeEvent(xAxis, links, maxValue);
        buildStopButtons(nameXAxis, function (stopCode) {
            app.updateGraphChart(stopCode, xAxis, links[stopCode], maxValue);
        });
    }

    // load filters
    (function () {
        loadAvailableDays(Urls["esapi:availableODDays"]());

        var app = new TransfersApp();
        var previousCall = function () {
            app.showLoadingAnimationCharts();
        };
        var afterCall = function (data) {
            processData(data, app);
            app.hideLoadingAnimationCharts();
        };
        var opts = {
            urlFilterData: Urls["esapi:ODMatrixData"](),
            urlRouteData: Urls["esapi:availableODRoutes"](),
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