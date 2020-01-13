"use strict";
$(document).ready(function () {
    function ResumeApp() {
        var chart = echarts.init(document.getElementById("barChart"), theme);

        var subgroupTranslation = {
            smartcard: "Tarjetas y transacciones",
            model: "Modelo",
            transportMode: "Bus, metro, metrotren y zona paga",
            stage: "Etapas",
            expedition: "Expedición",
            tripNumberInPeakHour: "N° viajes en hora punta",
            tripTime: "Tiempo de viaje",
            speed: "Velocidad",
            distance: "Distancia",
            tripWithsubway: "Viajes en metro",
            gps: "Tiempo entre gps",
            gpsNumber: "GPS con asignación de servicio"
        };

        var filters = {
            clean: [],
            transaction: {
                smartcard: ["transactionNumber", "smartcardNumber"],
                model: ["transactionWithoutRoute", "transactionWithRoute"],
                transportMode: ["transactionOnBusNumber", "transactionOnMetroNumber", "transactionOnBusStation",
                                "transactionOnTrainNumber"]
            },
            trip: {
                stage: ["tripsWithOneStage", "tripsWithTwoStages", "tripsWithThreeStages", "tripsWithFourStages",
                        "tripsWithFiveOrMoreStages"],
                expedition: ["GPSPointsNumber", "licensePlateNumber"],
                tripNumberInPeakHour: ["tripNumberInAfternoonRushHour", "tripNumberInMorningRushHour"],
                tripTime: ["averageTimeInAfternoonRushTrips", "averageTimeInMorningRushTrips",
                           "averageTimeOfTrips"],
                speed: ["averageVelocityInMorningRushTrips", "averageVelocityInAfternoonRushTrips",
                        "averageVelocityOfTrips"],
                distance: ["averageDistanceInMorningRushTrips", "averageDistanceInAfternoonRushTrips",
                           "averageDistanceOfTrips"],
                model: ["completeTripNumber", "validTripNumber", "tripNumber", "tripsWithoutLastAlighting"],
                gps: ["averageTimeBetweenGPSPoints"],
                tripWithsubway: ["tripsThatUseMetro", "tripsWithOnlyMetro"]
            },
            stage: {
                transportMode: ["stagesWithBusAlighting", "stagesWithTrainAlighting", "stagesWithMetroAlighting",
                      "stagesWithBusStationAlighting"]
            },
            expedition: {
                expedition: ["expeditionNumber"],
                model: ["maxExpeditionTime", "minExpeditionTime", "averageExpeditionTime"],
                gpsNumber: ["GPSNumberWithRoute", "GPSNumberWithoutRoute"]
            }
        };

        $(".btn-filter-group").click(function () {
            var $METRIC_FILTER = $("#metricFilter");
            var groupId = $(this).attr("id");
            if (groupId === "clean") {
                $METRIC_FILTER.val(filters[groupId]).trigger("change");
                return;
            }
            var container = $("#subgroup");
            container.empty();
            Object.keys(filters[groupId]).forEach(function(subgroup){
                var button = $("<button></button>",{
                    text: subgroupTranslation[subgroup],
                    id: subgroup,
                    class: "btn btn-default btn-round btn-filter-subgroup",
                    click: function () {
                        $METRIC_FILTER.val(filters[groupId][subgroup]).trigger("change");
                    }
                });
                container.append(button);
            });
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

            var rowData = dates.map(function (date) {
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
                        rowData[index][j] = el;
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
                var attributeData = rowData.map(function (dateData) {
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
                        start: 0,
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
                    trigger: "axis",
                    formatter: function (params) {
                        if (Array.isArray(params)) {
                            var head = params[0].axisValueLabel + "<br />";
                            var info = [];
                            params.forEach(function (el) {
                                var ball = el.marker;
                                var name = el.seriesName;
                                var value = Number(Number(el.value).toFixed(2)).toLocaleString();
                                info.push(ball + name + ": " + value);
                            });
                            return head + info.join("<br />");
                        }
                    }
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
        loadRangeCalendar(Urls["esapi:availableStatisticDays"]());

        var app = new ResumeApp();
        var afterCall = function (answer) {
            if (answer.status) {
                return;
            }
            app.updateMetrics(answer.data);
        };
        var opts = {
            urlFilterData: Urls["esapi:resumeData"](),
            afterCallData: afterCall,
            minimumDateLimit: 2
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