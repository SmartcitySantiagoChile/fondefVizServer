/**
 * Calendar to show available days (dates with data)
 * */
function loadAvailableDays(data_url) {
    var availableDaysChart = echarts.init(document.getElementById("availableDays"), theme);
    var opts = {
        tooltip: {
            position: 'top',
            formatter: function (p) {
                var format = echarts.format.formatTime('yyyy-MM-dd', p.data[0]);
                return format;
            }
        },
        visualMap: {
            min: 0,
            max: 1000,
            calculable: true,
            orient: 'vertical',
            left: '0',
            top: 'center',
            show: false
        },
        calendar: {
            orient: 'horizontal',
            range: null,
            dayLabel: {
                firstDay: 1,
                nameMap: ['D', 'L', 'M', 'M', 'J', 'V', 'S']
            },
            monthLabel: {
                nameMap: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
            },
            top: 20,
            left: 50,
            right: 30
        },
        series: [{
            type: 'heatmap',
            coordinateSystem: 'calendar',
            data: []
        }]
    };
    $(window).resize(function () {
        availableDaysChart.resize();
    });
    $('#menu_toggle').click(function () {
        availableDaysChart.resize();
    });

    // ask per data
    $.get(data_url, function (data) {
        data = data.availableDays.map(function (el) {
            return [el, 1];
        });
        if (data.length > 0) {
            firstDate = data[0][0];
            lastDate = data[data.length - 1][0];

            lowerBound = firstDate.substring(0, firstDate.length - 3);
            upperBound = lastDate.substring(0, lastDate.length - 3);

            firstDateUTC = Date.UTC(...firstDate.split('-')
        )
            ;
            lastDateUTC = Date.UTC(...lastDate.split('-')
        )
            ;
            dayInMiliSeconds = 24 * 3600 * 1000;
            days = (lastDateUTC - firstDateUTC) / dayInMiliSeconds;
            if (days < 31) {
                lastDateDivided = lastDate.split('-');
                upperBound = new Date(lastDateUTC + 0 * dayInMiliSeconds);
                upperBound = [upperBound.getUTCFullYear(), upperBound.getUTCMonth(), upperBound.getUTCDate()].join('-');
            }

            range = [lowerBound, upperBound];
            opts.series[0].data = data;
            opts.calendar.range = range;
            availableDaysChart.setOption(opts, {notMerge: true});
        }
    });
};