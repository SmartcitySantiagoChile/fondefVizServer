/**
 * Calendar to show available days (dates with data)
 * */
function loadAvailableDays(data) {
    var availableDaysChart = echarts.init(document.getElementById("availableDays"), theme);
    console.log(data)
    function getVirtulData(year) {
        year = year || '2017';
        var date = +echarts.number.parseDate(year + '-01-01');
        var end = +echarts.number.parseDate((+year + 1) + '-01-01');
        var dayTime = 3600 * 24 * 1000;
        var data = [];
        for (var time = date; time < end; time += dayTime) {
            data.push([
                echarts.format.formatTime('yyyy-MM-dd', time),
                Math.floor(Math.random() * 1000)
            ]);
        }
        return data;
    }
    data = getVirtulData('2017');

    var opts = {
        tooltip: {
            position: 'top',
            formatter: function (p) {
                var format = echarts.format.formatTime('yyyy-MM-dd', p.data[0]);
                return format + ': ' + p.data[1];
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
            range: '2017',
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
            data: data
        }]
    };
    availableDaysChart.setOption(opts, {notMerge: true});
    $(window).resize(function () {
        availableDaysChart.resize();
    });
};