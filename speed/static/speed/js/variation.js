$(document).ready(function () {
    // echarts stuffs
    var nPerPag = 20;
    var mChart = echarts.init(document.getElementById('main'));
    mChart.title = 'velocityVariation';
    var periods = [
        '00:00', '00:30', '01:00', '01:30', '02:00', '02:30', '03:00', '03:30', '04:00', '04:30', '05:00', '05:30', '06:00', '06:30', '07:00', '07:30', '08:00', '08:30', '09:00', '09:30',
        '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30',
        '20:00', '20:30', '21:00', '21:30', '22:00', '22:30', '23:00', '23:30'
    ];
    colors = ['#ffffff', '#ff0000', '#ff4500', '#ff8000', '#ffff00', '#01df01', '#088a08', '#045fb4', '#dfdfdf'];
    vel_range = ['Sin Datos Mes', '< 30%', ']30% - 45%]', ']45% - 60%]', ']60% - 75%]', ']75% - 90%]', ']90% - 100%]', '> 100%', 'Sin Datos Dia'];

    colors = ['#ffffff', '#ff0000', '#ff7f00', '#ffff00', '#00ff00', '#007f00', '#0000ff', '#dfdfdf'];

    function processData(dataSource) {
        console.log(dataSource);
        mChart.hideLoading();
        //   if(dataSource['status']){
        //       var status = dataSource['status'];
        //       showMessage(status);
        //       return;
        //   }

        var routes = dataSource['routes'];

        variations = dataSource['variations'];
        data = [];
        $.each(variations, function (i, vec) {
            $.each(vec, function (j, elem) {
                data.push([i, j, elem[0]]);
            });
        });
        var nReal = routes.length;
        var val = '' + (200 + Math.min(nReal, nPerPag) * 15) + 'px';
        $('#main').css('height', val);
        mChart.resize({height: val});
        console.log(val);
        option = {
            tooltip: {
                position: 'top',
                formatter: function (obj) {
                    var s = 'Horario: entre ' + periods[obj.data[0]] + ' y ' + periods[(obj.data[0] + 1) % periods.length];
                    s += '<br/>Servicio: ' + routes[obj.data[1]];
                    if (0 < obj.data[2] && obj.data[2] < 7) {
                        s += '<br/>Variación: ' + (variations[obj.data[0]][obj.data[1]][1] - 100).toFixed(1) + ' %';
                        s += '<br/>Velocidad promedio día: ' + variations[obj.data[0]][obj.data[1]][2].toFixed(1) + ' km/h';
                        s += '<br/>Velocidad promedio 30 días previos: ' + variations[obj.data[0]][obj.data[1]][3].toFixed(1) + ' km/h';
                        s += '<br/># observaciones día: ' + variations[obj.data[0]][obj.data[1]][4];
                        s += '<br/># observaciones 30 días previos: ' + variations[obj.data[0]][obj.data[1]][5];
                        s += '<br/>Desviación día: ' + variations[obj.data[0]][obj.data[1]][6].toFixed(1) + ' km/h';
                        s += '<br/>Desviación 30 días previos: ' + variations[obj.data[0]][obj.data[1]][7].toFixed(1) + ' km/h';
                    } else if (0 == obj.data[2]) {
                        s += '<br/>Sin datos para día seleccionado';
                    } else if (7 == obj.data[2]) {
                        s += '<br/>Sin datos históricos';
                    }

                    return s;
                }
            },
            animation: false,
            grid: {
                x: '10%',
                y: '100',
                height: '' + (Math.min(nReal, nPerPag) * 15) + 'px',
                width: '70%'
            },
            xAxis: {
                type: 'category',
                data: periods,
                splitArea: {
                    show: true
                },
                axisLabel: {
                    rotate: 90,
                    interval: 1
                }
            },
            yAxis: {
                type: 'category',
                data: routes,
                splitArea: {
                    show: true
                },
                axisLabel: {
                    interval: 0
                }
            },
            visualMap: {
                min: 0,
                max: 8,
                type: 'piecewise',
                calculable: true,
                orient: 'vertical',
                right: '5%',
                top: 'center',
                pieces: [
                    {min: 7.5, label: vel_range[8]},
                    {min: 6.5, max: 7.5, label: vel_range[7]},
                    {min: 5.5, max: 6.5, label: vel_range[6]},
                    {min: 4.5, max: 5.5, label: vel_range[5]},
                    {min: 3.5, max: 4.5, label: vel_range[4]},
                    {min: 2.5, max: 3.5, label: vel_range[3]},
                    {min: 1.5, max: 2.5, label: vel_range[2]},
                    {min: 0.5, max: 1.5, label: vel_range[1]},
                    {max: 0.5, label: vel_range[0]}
                ],
                inRange: {
                    color: colors
                }
            },
            series: [{
                name: 'Velocidad',
                type: 'heatmap',
                data: data,
                label: {
                    normal: {
                        show: false
                    }
                },
                itemHeight: '15px',
                itemWidth: '15px',
                itemStyle: {
                    emphasis: {
                        shadowBlur: 10,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }],
            toolbox: {
                show: true,
                feature: {
                    mark: {show: false},
                    restore: {show: false, title: "restaurar"},
                    saveAsImage: {show: true, title: "Guardar imagen", name: 'changeme'}
                }
            }
        };
        if (nReal > nPerPag) {
            option['dataZoom'] = {
                type: "slider",
                yAxisIndex: [0],
                start: 0,
                end: 100 * nPerPag / nReal,
                zoomLock: true,
                labelFormatter: ''
            };
        }
        console.log(nReal, nPerPag, 100 * nPerPag / nReal);
        mChart.setOption(option);
        console.log(mChart.getOption());
    };

    // load filters
    (function () {
        loadAvailableDays(Urls["speed:getAvailableDays"]());


        $('#btnUpdateChart').click(function () {
            var date = $('#filterDate').val();
            var dayType = $('#filterDayType').val();
            var route = $('#filterRoute').val();

            var data = {
                date: date,
                dayType: dayType,
                route: route,
            };
            mChart.showLoading(null, {text: 'Cargando...'});
            var loading = " <i class='fa fa-cog fa-spin fa-2x fa-fw'>";
            var button = $(this).append(loading);
            $.getJSON('getVariationData', data, processData).always(function () {
                button.html('Actualizar datos')
            });
        });
    })()
});