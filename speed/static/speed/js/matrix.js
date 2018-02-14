"use strict";

$(document).ready(function () {

    var periods = [
        "00:00", "00:30", "01:00", "01:30", "02:00", "02:30", "03:00", "03:30", "04:00", "04:30", "05:00", "05:30",
        "06:00", "06:30", "07:00", "07:30", "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
        "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30",
        "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00", "21:30", "22:00", "22:30", "23:00", "23:30"
    ];

    function MappApp(colorScale) {
        var _self = this;

        /* map setting */

        var baseLocation = [-33.437824, -70.650439];
        var mapboxKey = "pk.eyJ1IjoidHJhbnNhcHAiLCJhIjoiY2lzbjl6MDQzMDRkNzJxbXhyZWZ1aTlocCJ9.-xsBhulirrT0nMom_Ay9Og";
        var mapboxUrl = "https://api.mapbox.com/styles/v1/mapbox/dark-v9/tiles/256/{z}/{x}/{y}?access_token=" + mapboxKey;
        var blackLayer = L.tileLayer(mapboxUrl, {
            id: "mapbox.light",
            attribution: "flp"
        });
        var mapId = "mapid";
        var map = L.map(mapId, {
            center: baseLocation,
            zoom: 15,
            layers: [blackLayer]
        });
        L.control.scale().addTo(map);

        var colors = colorScale;

        /* to draw on map */
        var startEndSegments = null;
        var routePoints = null;
        var segmentPolylineList = [];
        var decoratorPolylineList = [];
        var startMarker = null;
        var endMarker = null;

        this._clearMap = function () {
            if (startMarker !== null) {
                map.removeLayer(startMarker);
            }
            if (endMarker !== null) {
                map.removeLayer(endMarker);
            }
            segmentPolylineList.forEach(function (elem) {
                map.removeLayer(elem);
            });
            decoratorPolylineList.forEach(function (elem) {
                map.removeLayer(elem);
            });
        };

        this.highlightSegment = function (segmentId) {

            var startIndex = startEndSegments[segmentId][0];
            var endIndex = startEndSegments[segmentId][1];

            if (startMarker !== null) {
                map.removeLayer(startMarker);
                map.removeLayer(endMarker);
            }

            var firstBound = null;
            var secondBound = null;

            routePoints.forEach(function (el, i) {
                if (i === startIndex) {
                    firstBound = el;
                }
                if (i === endIndex) {
                    secondBound = el;
                }
            });

            endMarker = L.marker(firstBound);
            startMarker = L.marker(secondBound);
            startMarker.addTo(map).bindPopup("<b>Inicio</b>");
            endMarker.addTo(map).bindPopup("<b>Fin</b>");

            map.flyToBounds(L.latLngBounds(firstBound, secondBound));
        };

        this.drawRoute = function (route, valuesRoute) {
            _self._clearMap();

            /* update routes and segments */
            startEndSegments = route.start_end;
            routePoints = route.points.map(function (el) {
                return L.latLng(el[0], el[1]);
            });

            /* create segments with color */
            route.start_end.forEach(function (elem, i) {
                var start = elem[0];
                var end = elem[1];
                var seg = routePoints.slice(start, end + 1);
                var segpol = new L.Polyline(seg, {
                    color: colors[valuesRoute[i][0]],
                    weight: 5,
                    opacity: 1,
                    smoothFactor: 1
                });
                var deco = new L.polylineDecorator(segpol, {
                    patterns: [
                        {
                            offset: 0,
                            endOffset: 0,
                            repeat: "40",
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
                segmentPolylineList.push(segpol);
                decoratorPolylineList.push(deco);
                segpol.addTo(map);
                deco.addTo(map);
            });
            map.flyToBounds(L.latLngBounds(routePoints[0], routePoints[routePoints.length - 1]));
        };
    }

    function MatrixApp() {
        var _self = this;

        var mChart = echarts.init(document.getElementById("main"));
        var matrix = null;
        var route = null;

        // vel_range = ["Sin Datos", " < 15 k/h", "15-19 k/h", "19-21 k/h", "21-25 k/h", "25-30 k/h", " > 30 k/h"];
        var velRange = ["Sin Datos", " < 5 k/h", "5-10 k/h", "10-15 k/h", "15-20 k/h", "20-25 k/h", "25-30 k/h", " > 30 k/h"];
        // colors = ["#dfdfdf", "#ff0000", "#ff7f00", "#ffff00", "#00ff00", "#007f00", "#0000ff"];
        var colors = ["#dfdfdf", "#ff0000", "#ff4500", "#ff8000", "#ffff00", "#01df01", "#088a08", "#045fb4"];

        var mapApp = new MappApp(colors);

        var opts = {
            tooltip: {
                position: "top",
                formatter: function (obj) {
                    var startHour = periods[obj.data[0]];
                    var endHour = periods[(obj.data[0] + 1) % periods.length];
                    var segment = obj.data[1];
                    var speed = ((matrix[obj.data[0]][obj.data[1]][1] < 0) ? "No fue posible calcular" : matrix[obj.data[0]][obj.data[1]][1].toFixed(1));
                    var obsNumber = matrix[obj.data[0]][obj.data[1]][2];
                    return "Horario: entre " + startHour + " y " + endHour + "<br/>" + "Segmento: " + segment + "<br/>" + "Velocidad: " + speed + " km/h" + "<br/># de observaciones: " + obsNumber;
                }
            },
            animation: false,
            grid: {
                left: "60",
                bottom: "90",
                right: "30"
            },
            xAxis: {
                type: "category",
                data: periods,
                splitArea: {
                    show: true
                },
                axisLabel: {
                    rotate: 90,
                    interval: 1
                },
                name: "Período de media hora",
                nameLocation: "center",
                nameGap: 50
            },
            yAxis: {
                type: "category",
                data: [],
                splitArea: {
                    show: true
                },
                name: "Tramos de 500 metros",
                nameLocation: "center",
                nameGap: 40
            },
            visualMap: {
                min: 0,
                max: 6,
                type: "piecewise",
                calculable: true,
                orient: "horizontal",
                right: "5%",
                top: "top",
                pieces: [
                    {min: 6.5, max: 7.5, label: velRange[7]},
                    {min: 5.5, max: 6.5, label: velRange[6]},
                    {min: 4.5, max: 5.5, label: velRange[5]},
                    {min: 3.5, max: 4.5, label: velRange[4]},
                    {min: 2.5, max: 3.5, label: velRange[3]},
                    {min: 1.5, max: 2.5, label: velRange[2]},
                    {min: 0.5, max: 1.5, label: velRange[1]},
                    {max: 0.5, label: velRange[0]}
                ],
                inRange: {
                    color: colors
                }
            },
            series: [{
                name: "Velocidad",
                type: "heatmap",
                data: [],
                label: {
                    normal: {
                        show: false
                    }
                },
                itemStyle: {
                    emphasis: {
                        shadowBlur: 10,
                        shadowColor: "rgba(0, 0, 0, 0.5)"
                    }
                }
            }],
            toolbox: {
                left: "center",
                bottom: "bottom",
                show: true,
                feature: {
                    mark: {show: false},
                    restore: {show: false, title: "restaurar"},
                    saveAsImage: {show: true, title: "Guardar imagen", name: "changeme"}
                }
            }
        };

        mChart.on("click", function (params) {
            if ((params.componentType !== "series") || (params.seriesType !== "heatmap") ||
                (params.seriesIndex !== 0) || (params.seriesName !== "Velocidad")) {
                return;
            }
            var periodId = params.value[0];
            var segmentId = params.value[1];

            // set slider to period clicked
            var slider = $("#filterHourRange").data("ionRangeSlider");
            slider.update({from: periodId});

            mapApp.drawRoute(route, matrix[periodId]);
            mapApp.highlightSegment(segmentId);
        });

        this.showLoadingAnimationCharts = function () {
            mChart.showLoading(null, {text: "Cargando..."});
        };

        this.hideLoadingAnimationCharts = function () {
            mChart.hideLoading();
        };

        this.resizeChart = function () {
            mChart.resize();
        };

        this.setMatrix = function (newMatrix) {
            matrix = newMatrix;
        };
        this.setRoute = function (newRoute) {
            route = newRoute;
            _self.updateLabel(route.name);
        };

        this.updateChart = function (data, segments) {
            opts.yAxis.data = segments;
            opts.series[0].data = data;
            mChart.setOption(opts, {merge: false});

            mapApp.drawRoute(route, matrix[0]);
        };

        this.updateLabel = function (label) {
            $("#route_name").html(label);
        };

        this.updateMap = function (periodId) {
            if (route === null) {
                return;
            }
            mapApp.drawRoute(route, matrix[periodId]);
        };
    }

    function processData(dataSource, app) {
        if (dataSource["status"]) {
            var status = dataSource["status"];
            showMessage(status);
            return;
        }

        app.setMatrix(dataSource.matrix);
        app.setRoute(dataSource.route);

        var data = [];
        dataSource.matrix.forEach(function (vec, i) {
            vec.forEach(function (elem, j) {
                data.push([i, j, elem[0]]);
            });
        });

        app.updateChart(data, dataSource.segments);
    }

    // load filters
    (function () {
        loadAvailableDays(Urls["esapi:availableSpeedDays"]());

        var app = new MatrixApp();

        $("#filterHourRange").ionRangeSlider({
            type: "single",
            values: periods,
            grid: true,
            onFinish: function (data) {
                console.log("slider moved");
                var periodId = data.from;
                app.updateMap(periodId);
            }
        });

        var previousCall = function () {
            app.showLoadingAnimationCharts();
        };
        var afterCall = function (data) {
            processData(data, app);
            app.hideLoadingAnimationCharts();
        };
        var opts = {
            urlFilterData: Urls["esapi:matrixData"](),
            urlRouteData: Urls["esapi:availableSpeedRoutes"](),
            previousCallData: previousCall,
            afterCallData: afterCall
        };
        filterManager(opts);
        $(window).resize(function () {
            app.resizeChart();
        });
        $("#menu_toggle").click(function () {
            app.resizeChart();
        });
    })();
});