"use strict";
$(document).ready(function () {
    var chart = echarts.init(document.getElementById("barChart"), theme);

    $.getJSON(Urls["globalstat:data"](), function (answer) {
        var data = answer.data;
        console.log(data);

        var N_POINT = data["Día"];

        var grids = [];
        var xAxes = [];
        var yAxes = [];
        var series = [];
        var titles = [];
        var count = 0;
        echarts.util.each(data, function (attributeData, name) {
            if (name === "date") {
                return;
            }

            var data = [];
            for (var i = 0; i < N_POINT.length; i++) {
                var x = N_POINT[i];
                var y = attributeData[i];
                data.push([x, y]);
            }
            grids.push({
                show: true,
                borderWidth: 0,
                backgroundColor: '#fff',
                shadowColor: 'rgba(0, 0, 0, 0.3)',
                shadowBlur: 2
            });
            xAxes.push({
                type: 'time',
                show: false,
                gridIndex: count
            });
            yAxes.push({
                type: 'value',
                show: false,
                gridIndex: count
            });
            series.push({
                name: name,
                type: 'bar',
                xAxisIndex: count,
                yAxisIndex: count,
                data: data,
                showSymbol: false,
                animationEasing: name,
                animationDuration: 1000
            });
            titles.push({
                textAlign: 'center',
                text: name,
                textStyle: {
                    fontSize: 12,
                    fontWeight: 'normal'
                }
            });
            count++;
        });

        var rowNumber = Math.ceil(Math.sqrt(count));
        echarts.util.each(grids, function (grid, idx) {
            grid.left = ((idx % rowNumber) / (rowNumber - 1) * 100 + 0.5) + '%';
            grid.top = (Math.floor(idx / rowNumber) / rowNumber * 100 + 0.5) + '%';
            grid.width = (1 / rowNumber * 100 - 1) + '%';
            grid.height = (1 / rowNumber * 100 - 1) + '%';

            titles[idx].left = parseFloat(grid.left) + parseFloat(grid.width) / 2 + '%';
            titles[idx].top = parseFloat(grid.top) + '%';
        });

        var option = {
            title: titles,
            grid: grids,
            xAxis: xAxes,
            yAxis: yAxes,
            series: series,
            tooltip: {
                show: true,
                formatter: function(params){
                    var marker = params.marker;
                    var date = params.value[0].substring(0, 10);
                    var value = params.value[1];
                    return marker + " " + date + ": " + value.toFixed(2);
                }
            }
        };

        chart.setOption(option);
    });
    $(window).resize(function () {
        chart.resize();
    });
    $("#menu_toggle").click(function () {
        chart.resize();
    });
});