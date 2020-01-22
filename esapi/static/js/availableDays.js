"use strict";

/**
 * Calendar to show available days (dates with data)
 * */
function loadAvailableDays(data_url) {
    var divId = "availableDays";
    var availableDaysChart = echarts.init(document.getElementById(divId), theme);

    var calendarYearTemplate = {
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
        left: "50",
        right: "0",
        cellSize: ["auto", 9]
    };

    var serieTemplate = {
        type: "heatmap",
        coordinateSystem: "calendar",
        calendarIndex: 0,
        data: []
    };

    var opts = {
        tooltip: {
            position: "top",
            formatter: function (p) {
                return echarts.format.formatTime("dd/MM/yyyy", p.data[0]);
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
        calendar: [],
        series: []
    };

    $(window).resize(function () {
        availableDaysChart.resize();
    });
    $("#menu_toggle").click(function () {
        availableDaysChart.resize();
    });

    // show loading
    var loadingText = "Cargando ...";
    availableDaysChart.showLoading(null, {text: loadingText});

    $.get(data_url, function (data) {
        availableDaysChart.hideLoading();
        var years = data.availableDays.map(function (el) {
            return el.split("-")[0];
        }).filter(function (el, index, self) {
            return self.indexOf(el) === index;
        });
        console.log(data);
        data = data.availableDays.map(function (el) {
            return [el, 1];
        });
        if (data.length > 0) {
            var newOpts = $.extend({}, opts);
            var top = 20;
            years.forEach(function (year, index) {
                var calendarYear = $.extend({}, calendarYearTemplate);
                var serie = $.extend({}, serieTemplate);

                calendarYear.range = year;
                calendarYear.top = top;
                top += 100;
                serie.calendarIndex = index;
                serie.data = data;

                newOpts.calendar.push(calendarYear);
                newOpts.series.push(serie);
            });

            $("#" + divId).height(top-20);
            availableDaysChart.setOption(newOpts, {notMerge: true});
            availableDaysChart.resize();
        }
    });
}