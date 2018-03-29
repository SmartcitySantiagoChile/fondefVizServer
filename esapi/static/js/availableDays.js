"use strict";
/**
 * Calendar to show available days (dates with data)
 * */
function loadAvailableDays(data_url) {
    var availableDaysChart = echarts.init(document.getElementById("availableDays"), theme);
    var opts = {
        tooltip: {
            position: "top",
            formatter: function (p) {
                var formattedDate = echarts.format.formatTime("dd/MM/yyyy", p.data[0]);
                return formattedDate;
            }
        },
        visualMap: {
            min: 0,
            max: 1000,
            calculable: true,
            orient: "vertical",
            left: "0",
            top: "center",
            show: false
        },
        calendar: {
            orient: "horizontal",
            range: null,
            dayLabel: {
                firstDay: 1,
                nameMap: ["D", "L", "M", "M", "J", "V", "S"]
            },
            monthLabel: {
                nameMap: ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
            },
            top: 20,
            left: 50,
            right: 30
        },
        series: [{
            type: "heatmap",
            coordinateSystem: "calendar",
            data: []
        }]
    };
    $(window).resize(function () {
        availableDaysChart.resize();
    });
    $("#menu_toggle").click(function () {
        availableDaysChart.resize();
    });

    // ask per data
    $.get(data_url, function (data) {
        data = data.availableDays.map(function (el) {
            return [el, 1];
        });
        if (data.length > 0) {
            var firstDate = data[0][0];
            var lastDate = data[data.length - 1][0];

            var dayInMiliSeconds = 24 * 3600 * 1000;
            var lowerBound = firstDate.substring(0, firstDate.length - 3);

            var lastDateUTC = Date.UTC(...lastDate.split("-"));
            lastDateUTC += dayInMiliSeconds * 30;

            var upperBound = new Date(lastDateUTC);
            upperBound = [upperBound.getUTCFullYear(), upperBound.getUTCMonth()].join("-");

            var range = [lowerBound, upperBound];
            opts.series[0].data = data;
            opts.calendar.range = range;
            availableDaysChart.setOption(opts, {notMerge: true});
        }
    });
}