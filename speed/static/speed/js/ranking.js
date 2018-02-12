$(document).ready(function () {
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
    colors = ['#dfdfdf', '#ff0000', '#ff7f00', '#ffff00', '#00ff00', '#007f00', '#0000ff'];
    recievedDataParams = null;
    StartMarker = null;
    EndMarker = null;
    MultiSegment = [];
    MultiDecorator = [];
    var periods = [
        '00:00', '00:30', '01:00', '01:30', '02:00', '02:30', '03:00', '03:30', '04:00', '04:30', '05:00', '05:30', '06:00', '06:30', '07:00', '07:30', '08:00', '08:30', '09:00', '09:30',
        '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30',
        '20:00', '20:30', '21:00', '21:30', '22:00', '22:30', '23:00', '23:30', '00:00'
    ];

    function clearMap() {
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

    function showSegment(section, dataSource) {
        clearMap();
        RoutePoints = dataSource.route.points;
        valuesRoute = dataSource.speed;
        var selected = null;
        $.each(dataSource.route.start_end, function (i, elem) {
            var start = elem[0];
            var end = elem[1];
            var seg = RoutePoints.slice(start, end + 1);

            var aux = L.polyline(seg, {
                color: colors[valuesRoute[i]],
                weight: 5,
                opacity: 1,
                smoothFactor: 1
            });

            segpol = L.polylineDecorator(aux, {
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
                                    color: colors[valuesRoute[i]],
                                    stroke: true
                                }
                            })
                    }
                ]
            });
            if (i === section) {
                StartMarker = L.marker(RoutePoints[start]);
                EndMarker = L.marker(RoutePoints[end]);
                selected = aux;
            }
            MultiDecorator.push(segpol);
            MultiSegment.push(aux);
            aux.addTo(map);
            segpol.addTo(map);
        });
        StartMarker.addTo(map).bindPopup("<b>Inicio</b>");
        EndMarker.addTo(map).bindPopup("<b>Fin</b>");
        map.flyToBounds(selected.getBounds());
    }

    function RankingApp() {
        var _self = this;
        var _datatable = $('#tupleDetail').DataTable({
            lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "Todos"]],
            language: {
                url: '//cdn.datatables.net/plug-ins/1.10.13/i18n/Spanish.json'
            },
            columns: [
                {title: 'Servicio', data: 'route', searchable: true},
                {title: 'Tramo', data: 'section', className: 'text-right', searchable: false},
                {
                    title: 'Periodo', data: 'period', searchable: true,
                    render: function (data, type, full, meta) {
                        return periods[data] + " " + periods[data + 1];
                    }
                },
                {
                    title: 'Velocidad<br>[km/h]', data: 'speed', className: 'text-right', searchable: false,
                    render: function (data, type, full, meta) {
                        return data.toFixed(1);
                    }
                },
                {
                    title: 'Tiempo<br>[s]', data: 'time', className: 'text-right', searchable: false,
                    render: function (data, type, full, meta) {
                        return data.toFixed(1);
                    }
                },
                {
                    title: 'Distancia<br>[m]', data: 'distance', className: 'text-right', searchable: false,
                    render: function (data, type, full, meta) {
                        return data.toFixed(1);
                    }
                },
                {title: '# obs', data: 'n_obs', className: 'text-right', searchable: false}
            ],
            order: [[6, 'asc']]
        });

        // action when user clicks on a row
        $('#tupleDetail tbody').on('click', 'tr', function () {
            var data = _datatable.row(this).data();
            if (data !== undefined) {
                _datatable.$('tr.success').removeClass('success').removeClass('dark');
                $(this).addClass('success').addClass('dark');

                _self.drawSegment(data.route, data.period, data.section);
            }
        });

        this.updateRows = function (data) {
            _datatable.clear();
            _datatable.rows.add(data);
            _datatable.columns.adjust().draw();
            $(_datatable.row(0).node()).addClass('success').addClass('dark');

            var firstRow = _datatable.row(0).data();
            _self.drawSegment(firstRow.route, firstRow.period, firstRow.section);
        };

        this.drawSegment = function (route, period, section) {
            var dateFilter = $("#dayFilter");
            var startDate = dateFilter.data("daterangepicker").startDate.format();
            var endDate = dateFilter.data("daterangepicker").endDate.format();
            var dayType = $("#dayTypeFilter").val();

            var params = {
                route: route,
                startDate: startDate,
                endDate: endDate,
                period: period
            };
            if (dayType) {
                params.dayType = dayType;
            }
            console.log(params);
            $.getJSON(Urls["speed:getSpeedByRoute"](), params, function (response) {
                return showSegment(section, response);
            });
        }
    }

    function processData(dataSource, app) {
        if (dataSource['status']) {
            var status = dataSource['status'];
            showMessage(status);
            return;
        }

        var data = dataSource.data;
        app.updateRows(data);
    }

    // load filters
    (function () {
        loadAvailableDays(Urls["esapi:availableSpeedDays"]());

        var app = new RankingApp();

        var afterCall = function (data) {
            processData(data, app);
        };
        var opts = {
            urlFilterData: Urls["esapi:rankingData"](),
            urlRouteData: Urls["esapi:availableSpeedRoutes"](),
            afterCallData: afterCall
        };
        filterManager(opts);
    })();
});