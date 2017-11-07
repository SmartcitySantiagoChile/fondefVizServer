"use strict";
$(document).ready(function () {
    var UPDATE_BUTTON = $("#btnUpdateChart");
    var PERIOD_FILTER = $("#periodFilter");

    var ALL_LABEL = "Todos";
    PERIOD_FILTER.select2({placeholder: ALL_LABEL});

    var makeAjaxCall = true;
    UPDATE_BUTTON.click(function () {
        if (makeAjaxCall) {
            makeAjaxCall = false;

            var loadingIcon = " " + $("<i>").addClass("fa fa-cog fa-spin fa-2x fa-fw")[0].outerHTML;
            var previousMessage = $(this).html();
            var button = $(this).append(loadingIcon);

            var params = {
                period: [PERIOD_FILTER.val()]
            };
            $.getJSON(Urls["globalstat:data"](), params, function (answer) {
                updateMetrics(answer.data);
            }).always(function () {
                makeAjaxCall = true;
                button.html(previousMessage);
            });
        }
    });

    var charts = [];
    var updateMetrics = function (data) {
        var header = data.header;
        var chartNames = data.chartNames;
        var ids = data.ids;
        var row = data.rows[0];
        var days = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"];

        ids.forEach(function (id, index) {
            var value = row[index];
            if ($.isNumeric(value)) {
                value = Number(value).toLocaleString();
            }
            if (id === "date") {
                value = days[(new Date(value)).getUTCDay()];
            }
            try {
                $("#" + id).html(value);
            } catch (e) {
                console.log("error: ");
            }
        });

        var pieChartOpt = {
            tooltip: {
                trigger: "item"
            },
            series: [{
                type: "pie",
                radius: "60%",
                center: ["50%", "50%"],
                data: [],
                roseType: "area",
                animationType: "scale",
                animationEasing: "elasticOut",
                animationDelay: function () {
                    return Math.random() * 200;
                },
                label: {
                    normal: {
                        formatter: function (params) {
                            var number = Number(params.value).toLocaleString();
                            return params.data.name + "\n" + params.percent + "% (" + number + ")";
                        }
                    }
                }
            }]
        };
        var barChartOpt = {
            tooltip: {
                trigger: "axis",
                formatter: function (params) {
                    params = params[0];
                    var number = "-";
                    if (params.value !== undefined) {
                        number = Number(params.value.toFixed(2)).toLocaleString();
                    }
                    return params.marker + params.axisValueLabel + ": " + number;
                }
            },
            xAxis: {
                type: "category",
                splitLine: {
                    show: false
                },
                data: ["Día", "P. mañana", "P. tarde"]
            },
            yAxis: {},
            series: [{
                type: "bar",
                data: [],
                animationDelay: function (idx) {
                    return idx * 10;
                }
            }],
            animationEasing: "elasticOut",
            animationDelayUpdate: function (idx) {
                return idx * 5;
            },
            grid: {
                containLabel: true,
                bottom: 0,
                top: 30,
                left: 0,
                right: 0
            }
        };
        var chartOpts = [
            $.extend(true, {title: {text: "Transacciones por asignación de servicio"}}, pieChartOpt),
            $.extend(true, {title: {text: "Transacciones por modo de transporte"}}, pieChartOpt),
            $.extend(true, {title: {text: "Viajes según N° de etapas"}}, pieChartOpt),
            $.extend(true, {title: {text: "Etapas según modo de viaje"}}, pieChartOpt),
            $.extend(true, {
                title: {text: "Velocidad promedio de viajes (km/h)"},
                itemStyle: {normal: {color: "#7AC099"}}
            }, barChartOpt),
            $.extend(true, {
                title: {text: "Distancia promedio de viajes (metros)"},
                itemStyle: {normal: {color: "#34495D"}}
            }, barChartOpt),
            $.extend(true, {
                title: {text: "Tiempo promedio de viajes (minutos)"},
                itemStyle: {normal: {color: "#3CA9ED"}}
            }, barChartOpt),
            $.extend(true, {title: {text: "Viajes por período"}, itemStyle: {normal: {color: "#EEE1F4"}}}, barChartOpt)
        ];
        var chartIds = ["chart1", "chart2", "chart3", "chart4", "chart5", "chart6", "chart7", "chart8"];
        var chartAttr = [
            ["transactionWithoutRoute", "transactionWithRoute"],
            ["transactionOnTrainNumber", "transactionOnMetroNumber",
                "transactionOnBusNumber", "transactionOnBusStation"],
            ["tripsWithOneStage", "tripsWithTwoStages", "tripsWithThreeStages",
                "tripsWithFourStages", "tripsWithFiveOrMoreStages"],
            ["stagesWithBusAlighting", "stagesWithMetroAlighting", "stagesWithTrainAlighting", "stagesWithBusStationAlighting"],
            ["averageVelocityOfTrips", "averageVelocityInMorningRushTrips", "averageVelocityInAfternoonRushTrips"],
            ["averageDistanceOfTrips", "averageDistanceInMorningRushTrips", "averageDistanceInAfternoonRushTrips"],
            ["averageTimeOfTrips", "averageTimeInMorningRushTrips", "averageTimeInAfternoonRushTrips"],
            ["tripNumber", "tripNumberInMorningRushHour", "tripNumberInAfternoonRushHour"]
        ];
        chartIds.forEach(function (echartId, index) {
            var chart = echarts.init(document.getElementById(echartId), theme);
            chartAttr[index].forEach(function (attr) {
                var value = row[ids.indexOf(attr)];
                var name = chartNames[ids.indexOf(attr)];
                chartOpts[index].series[0].data.push({value: value, name: name});
            });
            console.log(chartOpts[index]);
            chart.setOption(chartOpts[index]);
            charts.push(chart);
        });
    };

    $(window).resize(function () {
        charts.forEach(function (chart) {
            chart.resize();
        });
    });
    $("#menu_toggle").click(function () {
        charts.forEach(function (chart) {
            chart.resize();
        });
    });
});