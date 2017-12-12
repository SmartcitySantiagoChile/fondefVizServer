"use strict";
$(document).ready(function () {
    function TransfersApp() {
        var _self = this;
        var chartId = "barChart";
        var _chart = echarts.init(document.getElementById(chartId), theme);

        this.resizeCharts = function () {
            _chart.resize();
        };

        this.updateChart = function (xData, yData, values, stopInfo) {
            var title = stopInfo.name;
            var subtitle = "Código de usuario: " + stopInfo.userCode + " Código de Transantiago: " + stopInfo.authCode;

            var options = {
                title: {
                    text: title,
                    subtext: subtitle
                },
                tooltip: {
                    show: false,
                    position: 'top'
                },
                animation: false,
                grid: {
                    height: '50%',
                    y: '80'
                },
                toolbox: {
                    show: true,
                    itemSize: 20,
                    left: "center",
                    bottom: "0px",
                    feature: {
                        saveAsImage: {show: true, title: "Guardar imagen", name: title}
                    }
                },
                xAxis: {
                    type: 'category',
                    position: 'top',
                    data: xData,
                    splitArea: {
                        show: true
                    },
                    axisTick: {
                        length: 20
                    }
                },
                yAxis: {
                    type: 'category',
                    data: yData,
                    splitArea: {
                        show: true
                    },
                    axisTick: {
                        length: 20
                    }
                },
                /*
                visualMap: {
                    min: 0,
                    max: 10,
                    calculable: true,
                    orient: 'horizontal',
                    left: 'center',
                    bottom: '15%'
                },*/
                series: [{
                    name: 'transfers',
                    type: 'heatmap',
                    data: values,
                    label: {
                        normal: {
                            show: true
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

        var stopInfo = dataSource.data.info;
        var matrix = dataSource.data.matrix;

        var yAxis = [];
        var xAxis = [];
        var data = [];

        var yIndex = 0;
        var xIndex = 0;
        matrix.forEach(function (row) {
            var origin = row.origin;
            var destination = row.destination;
            yAxis.push(origin);
            destination.forEach(function (column) {
                var oldXAxis = xAxis.indexOf(column.name);
                if (oldXAxis >= 0) {
                    data.push([oldXAxis, yIndex, column.value]);
                } else {
                    xAxis.push(column.name);
                    data.push([xIndex, yIndex, column.value]);
                    xIndex++;
                }
            });
            yIndex++;
        });

        console.log(yAxis);
        console.log(xAxis);
        console.log(data);
        //dataManager.stopInfo(stopInfo);
        //app
        app.updateChart(xAxis, yAxis, data, stopInfo);
    }

    // load filters
    (function () {
        // set locale
        moment.locale("es");

        $("#dayFilter").select2();
        $("#stopFilter").select2({
            ajax: {
                delay: 500, // milliseconds
                url: Urls["profile:getStopList"](),
                dataType: "json",
                data: function (params) {
                    return {
                        term: params.term
                    }
                },
                processResults: function (data, params) {
                    return {
                        results: data.items
                    }
                },
                cache: true
            },
            minimumInputLength: 3,
            language: {
                inputTooShort: function () {
                    return "Ingresar 3 o más caracteres";
                }
            }
        });
        $("#dayTypeFilter").select2({placeholder: "Todos"});
        $("#periodFilter").select2({placeholder: "Todos"});
        $("#minutePeriodFilter").select2({placeholder: "Todos"});

        var app = new TransfersApp();
        var makeAjaxCall = true;
        $("#btnUpdateChart").click(function () {
            var day = $("#dayFilter").val();
            var stopCode = $("#stopFilter").val();
            var dayType = $("#dayTypeFilter").val();
            var period = $("#periodFilter").val();
            var minutes = $("#minutePeriodFilter").val();

            var params = {
                day: day
            };
            if (stopCode) {
                params["stopCode"] = stopCode;
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
                $.getJSON(Urls["profile:getTransfersData"](), params, function (data) {
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