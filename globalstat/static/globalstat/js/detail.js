"use strict";
$(document).ready(function () {
    function DetailApp() {
        var charts = [];

        this.updateMetrics = function (data) {
            // var header = data.header;
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
                    console.log("error: " + e);
                }
            });

            var pieChartFormatter = function (params) {
                var number = Number(params.value).toLocaleString();
                return params.data.name + "\n" + params.percent.toLocaleString() + "% (" + number + ")";
            };

            var pieChartOpt = {
                tooltip: {
                    trigger: "item",
                    formatter: pieChartFormatter
                },
                series: [{
                    type: "pie",
                    radius: "60%",
                    center: ["50%", "60%"],
                    data: [],
                    animationType: "scale",
                    animationEasing: "elasticOut",
                    animationDelay: function () {
                        return Math.random() * 200;
                    },
                    label: {
                        normal: {
                            formatter: pieChartFormatter
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
                $.extend(true, {title: {text: "Transacciones por lugar de validación"}}, pieChartOpt),
                $.extend(true, {title: {text: "Transacciones por modo de transporte"}}, pieChartOpt),
                $.extend(true, {title: {text: "Viajes según N° de etapas"}}, pieChartOpt),
                $.extend(true, {title: {text: "Porcentaje de etapas con bajada estimada según lugar de validación"}}, barChartOpt),
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
                $.extend(true, {
                    title: {text: "Viajes por período"},
                    itemStyle: {normal: {color: "#EEE1F4"}}
                }, barChartOpt)
            ];
            var chartIds = ["chart1", "chart2", "chart3", "chart4"];
            var chartAttr = [
                ["transactionWithoutRoute", "transactionWithRoute"],
                ["transactionOnTrainNumber", "transactionOnMetroNumber",
                    "transactionOnBusNumber", "transactionOnBusStation"],
                ["tripsWithOneStage", "tripsWithTwoStages", "tripsWithThreeStages",
                    "tripsWithFourStages", "tripsWithFiveOrMoreStages"],
                ["stagesWithBusAlighting", "stagesWithMetroAlighting", "stagesWithTrainAlighting", "stagesWithBusStationAlighting"]
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

            var tables = {
                dataTable: {
                    labelAttributes: ["Velocidad promedio de viajes (km/h)", "Distancia promedio de viajes (metros)",
                        "Tiempo promedio de viajes (minutos)", "N° de Viajes", "N° de transacciones",
                        "N° de bajadas (suma sobre expansión zona-período)"
                    ],
                    tableAttributes: [
                        ["averageVelocityOfTrips", "averageVelocityInMorningRushTrips", "averageVelocityInAfternoonRushTrips"],
                        ["averageDistanceOfTrips", "averageDistanceInMorningRushTrips", "averageDistanceInAfternoonRushTrips"],
                        ["averageTimeOfTrips", "averageTimeInMorningRushTrips", "averageTimeInAfternoonRushTrips"],
                        ["tripNumber", "tripNumberInMorningRushHour", "tripNumberInAfternoonRushHour"],
                        ["transactionNumber", "transactionInMorningRushHour", "transactionInAfternoonRushHour"],
                        ["alightingNumber", "alightingNumberInMorningRushHour", "alightingNumberInAfternoonRushHour"]
                    ]
                },
                dataTable2: {
                    tableAttributes: [
                        ["firstStopWithMoreValidations", "transactionNumberInFirstStopWithMoreValidations"],
                        ["secondStopWithMoreValidations", "transactionNumberInSecondStopWithMoreValidations"],
                        ["thirdStopWithMoreValidations", "transactionNumberInThirdStopWithMoreValidations"],
                        ["fourthStopWithMoreValidations", "transactionNumberInFourthStopWithMoreValidations"],
                        ["fifthStopWithMoreValidations", "transactionNumberInFifthStopWithMoreValidations"],
                        ["sixthStopWithMoreValidations", "transactionNumberInSixthStopWithMoreValidations"],
                        ["seventhStopWithMoreValidations", "transactionNumberInSeventhStopWithMoreValidations"],
                        ["eighthStopWithMoreValidations", "transactionNumberInEighthStopWithMoreValidations"],
                        ["ninethStopWithMoreValidations", "transactionNumberInNinethStopWithMoreValidations"],
                        ["tenthStopWithMoreValidations", "transactionNumberInTenthStopWithMoreValidations"]
                    ]
                },
                dataTable3: {
                    tableAttributes: [
                        ["firstBusStopWithMoreValidations", "transactionNumberInFirstBusStopWithMoreValidations"],
                        ["secondBusStopWithMoreValidations", "transactionNumberInSecondBusStopWithMoreValidations"],
                        ["thirdBusStopWithMoreValidations", "transactionNumberInThirdBusStopWithMoreValidations"],
                        ["fourthBusStopWithMoreValidations", "transactionNumberInFourthBusStopWithMoreValidations"],
                        ["fifthBusStopWithMoreValidations", "transactionNumberInFifthBusStopWithMoreValidations"],
                        ["sixthBusStopWithMoreValidations", "transactionNumberInSixthBusStopWithMoreValidations"],
                        ["seventhBusStopWithMoreValidations", "transactionNumberInSeventhBusStopWithMoreValidations"],
                        ["eighthBusStopWithMoreValidations", "transactionNumberInEighthBusStopWithMoreValidations"],
                        ["ninethBusStopWithMoreValidations", "transactionNumberInNinethBusStopWithMoreValidations"],
                        ["tenthBusStopWithMoreValidations", "transactionNumberInTenthBusStopWithMoreValidations"]
                    ]
                }
            };

            for (var tableId in tables) {
                var dataTable = $("#" + tableId);
                dataTable.empty();

                var labelAttributes = tables[tableId].labelAttributes;
                var tableAttributes = tables[tableId].tableAttributes;

                var tableRow = "<tr><th scope='row'>{0}</th>{1}</tr>";
                tableAttributes.forEach(function (attrs, index) {
                    var values = [];
                    if (labelAttributes !== undefined) {
                        var label = labelAttributes[index];
                        values.push("<td>" + label + "</td>>");
                    }
                    attrs.forEach(function (keyValue) {
                        var value = row[ids.indexOf(keyValue)];
                        if (!isNaN(value)) {
                            value = Number(Number(value).toFixed(2)).toLocaleString();
                        }
                        values.push("<td>" + value + "</td>");
                    });
                    dataTable.append(tableRow.replace("{0}", index + 1).replace("{1}", values.join("")));
                });
            }
        };

        this.resizeCharts = function () {
            charts.forEach(function (chart) {
                chart.resize();
            });
        };
    }

    // load filters
    (function () {
        loadAvailableDays(Urls["esapi:availableStatisticDays"]());

        var app = new DetailApp();
        var afterCall = function (answer) {
            if (answer.status) {
                return;
            }
            app.updateMetrics(answer.data);
        };
        var opts = {
            urlFilterData: Urls["esapi:resumeData"](),
            afterCallData: afterCall,
            singleDatePicker: true
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