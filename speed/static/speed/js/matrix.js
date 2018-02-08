$(document).ready(function () {
    // echarts stuffs
    var mChart = echarts.init(document.getElementById('main'));
    mChart.title = 'speedMatrixByService';

    // map stuffs
    var pzaDeArmas = [-33.437824, -70.650439];
    var mbAttr = 'flp',
        mbUrl = 'https://api.mapbox.com/styles/v1/mapbox/dark-v9/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoidHJhbnNhcHAiLCJhIjoiY2lzbjl6MDQzMDRkNzJxbXhyZWZ1aTlocCJ9.-xsBhulirrT0nMom_Ay9Og';
    var black = L.tileLayer(mbUrl, {id: 'mapbox.light', attribution: mbAttr});
    var map = L.map('mapid', {
        center: pzaDeArmas,
        zoom: 15,
        layers: [black]
    });
    L.control.scale().addTo(map);

    // vel_range = ['Sin Datos', ' < 15 k/h', '15-19 k/h', '19-21 k/h', '21-25 k/h', '25-30 k/h', ' > 30 k/h'];
    vel_range = ['Sin Datos', ' < 5 k/h', '5-10 k/h', '10-15 k/h', '15-20 k/h', '20-25 k/h', '25-30 k/h', ' > 30 k/h'];
    // colors = ['#dfdfdf', '#ff0000', '#ff7f00', '#ffff00', '#00ff00', '#007f00', '#0000ff'];
    colors = ['#dfdfdf', '#ff0000', '#ff4500', '#ff8000', '#ffff00', '#01df01', '#088a08', '#045fb4'];
    StartMarker = null;
    EndMarker = null;
    RoutePoints = [];
    RoutePoints_before = [];
    RoutePoints_after = [];
    RoutePolyline = null;
    RoutePolyline2 = null;
    RouteDeco = null;
    RouteDeco2 = null;
    MultiSegment = []
    MultiDecorator = []
    SegmentPoints = [];
    SegmentPolyline = null;
    SegmentDeco = null;
    var startEnd = null;
    var periods = [
        '00:00', '00:30', '01:00', '01:30', '02:00', '02:30', '03:00', '03:30', '04:00', '04:30', '05:00', '05:30', '06:00', '06:30', '07:00', '07:30', '08:00', '08:30', '09:00', '09:30',
        '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30',
        '20:00', '20:30', '21:00', '21:30', '22:00', '22:30', '23:00', '23:30', '00:00'
    ];
    var matrix = null;

    function clearMap() {
        if (RoutePolyline) {
            map.removeLayer(RoutePolyline);
        }
        if (RoutePolyline2) {
            map.removeLayer(RoutePolyline2);
        }
        if (RouteDeco) {
            map.removeLayer(RouteDeco);
        }
        if (RouteDeco2) {
            map.removeLayer(RouteDeco2);
        }
        if (SegmentPolyline) {
            map.removeLayer(SegmentPolyline);
        }
        if (SegmentDeco) {
            map.removeLayer(SegmentDeco);
        }
        if (StartMarker) {
            map.removeLayer(StartMarker);
        }
        if (EndMarker) {
            map.removeLayer(EndMarker);
        }
        $.each(MultiSegment, function (i, elem) {
            map.removeLayer(elem);
        });
        $.each(MultiDecorator, function (i, elem) {
            map.removeLayer(elem);
        });
    }

    mChart.on('click', function (params) {
        if ((params.componentType != 'series') || (params.seriesType != 'heatmap') || (params.seriesIndex != 0) || (params.seriesName != 'Velocidad')) {
            return;
        }
        segment = params.value[1]
        velocity_cat = params.value[2]

        // draw route and segment in map
        clearMap();
        SegmentPoints = [];
        RoutePoints_before = [];
        RoutePoints_after = [];
        var start = startEnd[segment][0];
        var end = startEnd[segment][1];
        $.each(RoutePoints, function (i, elem) {
            if (i <= start) {
                RoutePoints_before.push(elem);
            }
            if (end <= i) {
                RoutePoints_after.push(elem);
            }
            if (i == start) {
                StartMarker = L.marker(elem);
            }
            if (i == end) {
                EndMarker = L.marker(elem);
            }
            if (start <= i && i <= end) {
                SegmentPoints.push(elem);
            }
        });
        RoutePolyline = new L.Polyline(RoutePoints_before, {
            color: '#000000',
            weight: 3,
            opacity: 1,
            smoothFactor: 1
        });
        RouteDeco = L.polylineDecorator(RoutePolyline, {
            patterns: [
                {
                    offset: 0,
                    endOffset: 0,
                    repeat: '40',
                    symbol: L.Symbol.arrowHead(
                        {
                            pixelSize: 10,
                            polygon: true,
                            pathOptions: {
                                fillOpacity: 1,
                                color: '#000000',
                                stroke: true
                            }
                        })
                }
            ]
        });
        RoutePolyline2 = new L.Polyline(RoutePoints_after, {
            color: '#000000',
            weight: 3,
            opacity: 1,
            smoothFactor: 1
        });
        RouteDeco2 = L.polylineDecorator(RoutePolyline2, {
            patterns: [
                {
                    offset: 0,
                    endOffset: 0,
                    repeat: '40',
                    symbol: L.Symbol.arrowHead(
                        {
                            pixelSize: 10,
                            polygon: true,
                            pathOptions: {
                                fillOpacity: 1,
                                color: '#000000',
                                stroke: true
                            }
                        })
                }
            ]
        });
        SegmentPolyline = new L.Polyline(SegmentPoints, {
            color: colors[velocity_cat],
            weight: 5,
            opacity: 1,
            smoothFactor: 1
        });
        SegmentDeco = L.polylineDecorator(SegmentPolyline, {
            patterns: [
                {
                    offset: 0,
                    endOffset: 0,
                    repeat: '40',
                    symbol: L.Symbol.arrowHead(
                        {
                            pixelSize: 10,
                            polygon: true,
                            pathOptions: {
                                fillOpacity: 1,
                                color: colors[velocity_cat],
                                stroke: true
                            }
                        })
                }
            ]
        });
        RoutePolyline.addTo(map);
        RouteDeco.addTo(map);
        RoutePolyline2.addTo(map);
        RouteDeco2.addTo(map);
        SegmentPolyline.addTo(map);
        SegmentDeco.addTo(map);
        StartMarker.addTo(map).bindPopup("<b>Inicio</b>");
        EndMarker.addTo(map).bindPopup("<b>Fin</b>");
        map.fitBounds(SegmentPolyline.getBounds());

    });

    function processData(dataSource) {
        mChart.hideLoading();
        //   if(dataSource['status']){
        //       let status = dataSource['status'];
        //       showMessage(status);
        //       return;
        //   }

        var segments = dataSource['segments'];
        matrix = dataSource['matrix'];
        data = [];
        $.each(matrix, function (i, vec) {
            $.each(vec, function (j, elem) {
                data.push([i, j, elem[0]]);
            });
        });
        startEnd = dataSource['route']['start_end'];
        var route = dataSource['route']['points'];
        var route_name = dataSource['route']['name'];
        $('#route_name').html(route_name);

        option = {
            tooltip: {
                position: 'top',
                formatter: function (obj) {
                    return 'Horario: entre ' + periods[obj.data[0]] + ' y ' + periods[(obj.data[0] + 1) % periods.length] + '<br/>' + 'Segmento: ' + segments[obj.data[1]] + '<br/>' + 'Velocidad: ' + ((matrix[obj.data[0]][obj.data[1]][1] < 0) ? 'No fue posible calcular' : matrix[obj.data[0]][obj.data[1]][1].toFixed(1)) + 'km/h' + '<br/># de observaciones: ' + matrix[obj.data[0]][obj.data[1]][2];
                }
            },
            animation: false,
            grid: {
                x: '5%',
                y: '5%',
                width: '70%',
                height: '80%'
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
                data: segments,
                splitArea: {
                    show: true
                }
            },
            visualMap: {
                min: 0,
                max: 6,
                type: 'piecewise',
                calculable: true,
                orient: 'vertical',
                right: '5%',
                top: 'center',
                pieces: [
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

        mChart.setOption(option);

        // draw route in map
        clearMap();
        RoutePoints = [];
        $.each(route, function (i, elem) {
            var p = L.latLng(elem[0], elem[1]);
            RoutePoints.push(p);
        });
        RoutePolyline = new L.Polyline(RoutePoints, {
            color: '#000000',
            weight: 3,
            opacity: 1,
            smoothFactor: 1
        });
        RouteDeco = L.polylineDecorator(RoutePolyline, {
            patterns: [
                {
                    offset: 0,
                    endOffset: 0,
                    repeat: '40',
                    symbol: L.Symbol.arrowHead(
                        {
                            pixelSize: 10,
                            polygon: true,
                            pathOptions: {
                                fillOpacity: 1,
                                color: '#000000',
                                stroke: true
                            }
                        })
                }
            ]
        });
        RoutePolyline.addTo(map);
        RouteDeco.addTo(map);
        map.fitBounds(RoutePolyline.getBounds());
    };

    // load filters
    (function () {
        loadAvailableDays(Urls["speed:getAvailableDays"]());

        $("#filterHourRange").ionRangeSlider({
            type: 'single',
            values: [
                '00:00', '00:30', '01:00', '01:30', '02:00', '02:30', '03:00', '03:30', '04:00', '04:30', '05:00',
                '05:30', '06:00', '06:30', '07:00', '07:30', '08:00', '08:30', '09:00', '09:30', '10:00', '10:30',
                '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00',
                '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00', '21:30',
                '22:00', '22:30', '23:00', '23:30'
            ],
            onFinish: function (data) {
                if (startEnd == null) {
                    return;
                }
                // draw route in map
                clearMap();
                var valuesRoute = matrix[data.from];
                $.each(startEnd, function (i, elem) {
                    var start = elem[0];
                    var end = elem[1];
                    var seg = RoutePoints.slice(start, end + 1);
                    segpol = new L.Polyline(seg, {
                        color: colors[valuesRoute[i][0]],
                        weight: 5,
                        opacity: 1,
                        smoothFactor: 1
                    });
                    deco = new L.polylineDecorator(segpol, {
                        patterns: [
                            {
                                offset: 0,
                                endOffset: 0,
                                repeat: '40',
                                symbol: L.Symbol.arrowHead(
                                    {
                                        pixelSize: 10,
                                        polygon: true,
                                        pathOptions: {
                                            fillOpacity: 1,
                                            color: colors[valuesRoute[i][0]],
                                            stroke: true
                                        }
                                    })
                            }
                        ]
                    });
                    MultiSegment.push(segpol);
                    MultiDecorator.push(deco);
                    segpol.addTo(map);
                    deco.addTo(map);
                });
                RoutePolyline = new L.Polyline(RoutePoints, {
                    color: '#000000',
                    weight: 3,
                    opacity: 1,
                    smoothFactor: 1
                });
                map.fitBounds(RoutePolyline.getBounds());
            }
        });

        //var app = new ExpeditionApp();
        var previousCall = function () {
            //app.showLoadingAnimationCharts();
            mChart.showLoading(null, {text: 'Cargando...'});
        };
        var afterCall = function (data) {
            processData(data);
            //app.hideLoadingAnimationCharts();
        };
        var opts = {
            urlFilterData: Urls["speed:getMatrixData"](),
            urlRouteData: Urls["speed:getAvailableRoutes"](),
            previousCallData: previousCall,
            afterCallData: afterCall
        };
        filterManager(opts);
        $(window).resize(function () {
            //app.resizeCharts();
        });
        $("#menu_toggle").click(function () {
            //app.resizeCharts();
        });
    })()
});