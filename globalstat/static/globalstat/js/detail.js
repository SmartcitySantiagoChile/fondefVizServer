"use strict";
$(document).ready(function () {
    function DetailApp() {
        var charts = [];
        let dataTables = [];
        let metricValues = [];

        this.updateMetrics = function (data) {
            // var header = data.header;
            var chartNames = data.chartNames;
            var ids = data.ids;
            var row = data.rows[0];
            var days = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"];
            ids.forEach(function (id, index) {
                var value = row[index];
                if ($.isNumeric(value)) {
                    if (["tripsThatUseMetro", "tripsWithOnlyMetro", "tripsWithoutLastAlighting"].indexOf(id) >= 0) {
                        value = Number(value.toFixed(2)).toLocaleString() + " %";
                    } else {
                        value = Number(value).toLocaleString();
                    }
                }
                if (id === "date") {
                    value = days[(new Date(value)).getUTCDay()];
                }
                try {
                    $("#" + id).html(value);
                    metricValues.push("#" + id)
                } catch (e) {
                    console.log("error: " + e);
                }
            });

            var pieChartFormatter = function (params) {
                return params.data.name + "\n" + params.percent.toLocaleString() + " %";
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
                        return params.marker + params.axisValueLabel + ": " + number + " %";
                    }
                },
                xAxis: {
                    type: "category",
                    splitLine: {
                        show: false
                    },
                    data: []
                },
                yAxis: {
                    axisLabel: {
                        formatter: "{value} %"
                    }
                },
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
                $.extend(true, {title: {text: "Transacciones de bus según asignación de servicio"}}, pieChartOpt),
                $.extend(true, {title: {text: "Distribución de transacciones por modo de transporte"}}, pieChartOpt),
                $.extend(true, {title: {text: "Porcentaje de viajes según N° de etapas"}}, pieChartOpt),
                $.extend(true, {
                    title: {text: "Porcentaje de etapas con bajada estimada según lugar de validación"},
                    xAxis: {
                        type: "category",
                        splitLine: {show: false},
                        data: ["Bus", "Metro", "Metrotren", "Zona paga"]
                    }
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
                        if (["transactionInMorningRushHour", "transactionInAfternoonRushHour"].indexOf(keyValue) >= 0) {
                            value = value / 100 * row[ids.indexOf("transactionNumber")];
                        }
                        if (!isNaN(value)) {
                            value = Number(Number(value).toFixed(2)).toLocaleString();
                        }
                        values.push("<td>" + value + "</td>");
                    });
                    dataTable.append(tableRow.replace("{0}", index + 1).replace("{1}", values.join("")));
                });
                dataTables.push(dataTable);
            }
        };

        this.resizeCharts = function () {
            charts.forEach(function (chart) {
                chart.resize();
            });
        };

        /**
         * Clear information in bar chart, datatables and map.
         */
        this.clearDisplayData = function () {
            charts.forEach(chart => chart.clear());
            dataTables.forEach(table => table.empty());
            metricValues.forEach(metric => $(metric).html(""));
        };
    }

    // load filters
    (function () {
        var calendar_opts = {
            singleDatePicker: true
        };

        loadAvailableDays(Urls["esapi:availableStatisticDays"]());
        loadRangeCalendar(Urls["esapi:availableStatisticDays"](), calendar_opts);


        var app = new DetailApp();
        var afterCall = function (answer, status) {
            if (status) {
                app.updateMetrics(answer.data);
            } else {
                app.clearDisplayData();
            }
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