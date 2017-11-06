"use strict";
$(document).ready(function () {
    var chart = echarts.init(document.getElementById("barChart"), theme);

    var UPDATE_BUTTON = $("#btnUpdateChart");
    var PERIOD_FILTER = $("#periodFilter");
    var DAY_TYPE_FILTER = $("#dayTypeFilter");
    var METRIC_FILTER = $("#metricFilter");

    var ALL_LABEL = "Todos";
    PERIOD_FILTER.select2({placeholder: ALL_LABEL});
    DAY_TYPE_FILTER.select2({placeholder: ALL_LABEL, allowClear: true});
    DAY_TYPE_FILTER.val(null).trigger("change");
    METRIC_FILTER.select2({placeholder: ALL_LABEL});

    var makeAjaxCall = true;
    UPDATE_BUTTON.click(function () {
        if (makeAjaxCall) {
            makeAjaxCall = false;

            var loadingIcon = " " + $("<i>").addClass("fa fa-cog fa-spin fa-2x fa-fw")[0].outerHTML;
            var previousMessage = $(this).html();
            var button = $(this).append(loadingIcon);

            var params = {
                period: PERIOD_FILTER.val(),
                metrics: METRIC_FILTER.val()
            };
            if (DAY_TYPE_FILTER.val()) {
                params.dayType = DAY_TYPE_FILTER.val();
            }
            $.getJSON(Urls["globalstat:data"](), params, function (answer) {
                updateChart(answer);
            }).always(function () {
                makeAjaxCall = true;
                button.html(previousMessage);
            });
        }
    });

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
        METRIC_FILTER.val(metrics).trigger("change");
    });

    var updateChart = function (answer) {
        var header = answer.data.header;
        var rows = answer.data.rows;
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
                        type: ["line", "bar", "stack", "tiled"]
                    }
                }
            },
            series: series
        };

        chart.setOption(option, {notMerge: true});
    };

    $(window).resize(function () {
        chart.resize();
    });
    $("#menu_toggle").click(function () {
        chart.resize();
    });
});