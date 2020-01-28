"use strict";
$(document).ready(function () {
    function OperatorApp() {
        var chart = echarts.init(document.getElementById("barChart"), theme);

        this.updateMetrics = function (data) {
            let operators = Array.from(Array(10).keys());
            console.log(operators);
            var header = operators;
            var rows = data.rows;
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

            var rowData = dates.map(function (date) {
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
                        rowData[index][j] = el;
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
                var attributeData = rowData.map(function (dateData) {
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
                dataZoom: [
                    {
                        type: "slider",
                        show: true,
                        xAxisIndex: [0],
                        start: 0,
                        end: 100,
                        bottom: 40
                    },
                    {
                        type: "inside",
                        xAxisIndex: [0],
                        start: 70,
                        end: 100
                    }
                ],
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
                    trigger: "axis",
                    formatter: function (params) {
                        if (Array.isArray(params)) {
                            var head = params[0].axisValueLabel + "<br />";
                            var info = [];
                            params.forEach(function (el) {
                                var ball = el.marker;
                                var name = el.seriesName;
                                var value = Number(Number(el.value).toFixed(2)).toLocaleString();
                                info.push(ball + name + ": " + value);
                            });
                            return head + info.join("<br />");
                        }
                    }
                },
                grid: {
                    bottom: 95
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
                            show: true,
                            type: ["line", "bar"],
                            title: {
                            line: 'Lineas',
                            bar: 'Barras'
                            }
                        },
                        dataView: {
                            show: true,
                            title: "Ver datos",
                            lang: ["Datos del gráfico", "cerrar", "refrescar"],
                            buttonColor: "#169F85",
                            readOnly: true
                        }
                    }
                },
                series: series
            };

            chart.setOption(option, {notMerge: true});
        };

        this.resizeCharts = function () {
            chart.resize();
        };
    }

    // load filters
    (function () {
        loadAvailableDays(Urls["esapi:availableBipDays"]());
        loadRangeCalendar(Urls["esapi:availableBipDays"](), {});

        var app = new OperatorApp();
        var previousCall = function () {
        };
        var afterCall = function (data) {
            console.log(data);
            if (data.status) {
                return;
            }
            app.updateMetrics(data);
        };
        var opts = {
            urlFilterData: Urls["esapi:operatorData"](),
            previousCallData: previousCall,
            afterCallData: afterCall
        };

        new FilterManager(opts);

        $(window).resize(function () {
            app.resizeCharts();
        });
        $("#menu_toggle").click(function () {
            app.resizeCharts();
        });
    })()
});