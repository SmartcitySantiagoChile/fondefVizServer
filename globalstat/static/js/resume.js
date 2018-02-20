"use strict";
$(document).ready(function () {
    function ResumeApp() {
        var chart = echarts.init(document.getElementById("barChart"), theme);

        var filters = {
            "clean": [],
            "transaction": ["transactionWithoutRoute", "transactionWithRoute", "transactionNumber",
                "transactionOnTrainNumber", "transactionOnMetroNumber", "transactionOnBusNumber",
                "transactionOnBusStation"],
            "tripByNumberOfStage": ["tripsWithOneStage", "tripsWithTwoStages", "tripsWithThreeStages",
                "tripsWithFourStages", "tripsWithFiveOrMoreStages"],
            "dayTrip": ["validTripNumber", "tripNumber", "averageTimeOfTrips", "averageVelocityOfTrips",
                "averageTimeBetweenGPSPoints", "averageDistanceOfTrips", "tripsWithOnlyMetro",
                "tripsThatUseMetro", "completeTripNumber", "stagesWithBusStationAlighting",
                "tripsWithoutLastAlighting", "smartcardNumber"],
            "afternoonTrip": ["averageVelocityInAfternoonRushTrips", "averageTimeInAfternoonRushTrips",
                "averageDistanceInAfternoonRushTrips", "tripNumberInAfternoonRushHour"],
            "morningTrip": ["averageVelocityInMorningRushTrips", "averageTimeInMorningRushTrips",
                "averageDistanceInMorningRushTrips", "tripNumberInMorningRushHour"],
            "stage": ["stagesWithBusAlighting", "stagesWithTrainAlighting", "stagesWithMetroAlighting"],
            "expedition": ["expeditionNumber", "maxExpeditionTime", "minExpeditionTime", "averageExpeditionTime"],
            "gps": ["licensePlateNumber", "GPSPointsNumber", "GPSNumberWithRoute", "GPSNumberWithoutRoute"]
        };
        $(".btn-filter-group").click(function () {
            var id = $(this).attr("id");
            var metrics = filters[id];
            var $METRIC_FILTER = $("#metricFilter");
            $METRIC_FILTER.val(metrics).trigger("change");
        });

        this.updateMetrics = function (data) {
            var header = data.header;
            var rows = data.rows;
            if (rows === 0) {
                return;
            }

            // generate range of dates
            var firstDate = new Date(rows[0][0]);
            var endDate = new Date(rows[rows.length - 1][0]);
            var dates = [];
            var currentDate = firstDate;
            while (currentDate <= endDate) {
                dates.push(currentDate.getTime());
                currentDate.setUTCDate(currentDate.getUTCDate() + 1);
            }

            var data = dates.map(function (date) {
                var row = header.map(function () {
                    return null;
                });
                row[0] = date;
                return row;
            });
            rows.forEach(function (row) {
                var day = (new Date(row[0])).getTime();
                var index = dates.indexOf(day);
                row.forEach(function (el, j) {
                    if (j !== 0) {
                        data[index][j] = el;
                    }
                });
            });

            var yAxisDataName = [];
            var series = [];
            var dayName = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"];
            var xData = dates.map(function (date) {
                date = new Date(date);
                var mm = date.getUTCMonth() + 1;
                var dd = date.getUTCDate();
                var day = [date.getUTCFullYear(), (mm > 9 ? "" : "0") + mm, (dd > 9 ? "" : "0") + dd].join("-");
                return day + " (" + dayName[date.getUTCDay()] + ")";
            });

            echarts.util.each(header, function (name, index) {
                if (name === "Día" || name === "Tipo de día") {
                    return;
                }
                var attributeData = data.map(function (dateData) {
                    return dateData[index];
                });

                yAxisDataName.push(name);

                var serie = {
                    name: name,
                    type: "line",
                    data: attributeData,
                    showSymbol: false,
                    smooth: true
                };
                series.push(serie);
            });

            var option = {
                legend: {
                    data: yAxisDataName
                },
                dataZoom: [
                    {
                        type: "slider",
                        show: true,
                        xAxisIndex: [0],
                        start: 70,
                        end: 100,
                        bottom: 40
                    },
                    {
                        type: "inside",
                        xAxisIndex: [0],
                        start: 70,
                        end: 100
                    }
                ],
                xAxis: [{
                    type: "category",
                    name: "Días",
                    data: xData
                }],
                yAxis: [{
                    type: "value",
                    name: "",
                    position: "left"
                }],
                tooltip: {
                    trigger: "axis"
                },
                grid: {
                    bottom: 95
                },
                toolbox: {
                    show: true,
                    itemSize: 20,
                    bottom: 0,
                    left: "center",
                    feature: {
                        mark: {show: false},
                        restore: {show: false, title: "restaurar"},
                        saveAsImage: {show: true, title: "Guardar imagen", name: "estadísticas globales"},
                        magicType: {
                            type: ["line", "bar"]
                        },
                        dataView: {
                            show: true,
                            title: "Ver datos",
                            lang: ["Datos del gráfico", "cerrar", "refrescar"],
                            buttonColor: "#169F85",
                            readOnly: true
                        }
                    }
                },
                series: series
            };

            chart.setOption(option, {notMerge: true});
        };

        this.resizeCharts = function () {
            chart.resize();
        };
    }

    // load filters
    (function () {
        loadAvailableDays(Urls["esapi:availableStatisticDays"]());

        var app = new ResumeApp();
        var afterCall = function (answer) {
            if (answer.status) {
                var status = answer.status;
                showMessage(status);
                return;
            }
            app.updateMetrics(answer.data);
        };
        var opts = {
            urlFilterData: Urls["esapi:resumeData"](),
            afterCallData: afterCall
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