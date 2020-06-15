"use strict";
$(document).ready(function () {
    function OperatorApp() {
        let chart = echarts.init(document.getElementById("barChart"), theme);

        this.updateMetrics = function (answer) {
            let datesKeys = {};
            let header = answer.operators.map(e => e.item);
            header.unshift("Día");
            let operatorsNumber = answer.operators.length;
            let rows = [];
            answer.data.map(e => {
                let row = [];
                let dateTime = e.key_as_string;
                datesKeys[dateTime] = {};
                row.push(dateTime);
                e.operators.buckets.forEach(function (f) {
                    datesKeys[dateTime][f.key - 1] = f.doc_count;
                });
                for (let i = 0; i <= operatorsNumber; i++) {
                    row.push(datesKeys[dateTime][i]);
                }
                rows.push(row);
            });

            // generate range of dates
            let firstDate = new Date(rows[0][0]);
            let endDate = new Date(rows[rows.length - 1][0]);
            let dates = [];
            let currentDate = firstDate;
            while (currentDate <= endDate) {
                dates.push(currentDate.getTime());
                currentDate.setUTCDate(currentDate.getUTCDate() + 1);
            }
            let yAxisDataName = [];
            let series = [];
            let dayName = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"];
            let xData = dates.map(function (date) {
                date = new Date(date);
                let mm = date.getUTCMonth() + 1;
                let dd = date.getUTCDate();
                let day = [date.getUTCFullYear(), (mm > 9 ? "" : "0") + mm, (dd > 9 ? "" : "0") + dd].join("-");
                return day + " (" + dayName[date.getUTCDay()] + ")";
            });

            echarts.util.each(header, function (name, index) {
                if (name === "Día" || name === "Tipo de día") {
                    return;
                }
                let attributeData = rows.map(dateData => dateData[index]);

                yAxisDataName.push(name);

                let serie = {
                    name: name,
                    type: "line",
                    data: attributeData,
                    showSymbol: false,
                    smooth: true
                };
                series.push(serie);
            });

            let option = {
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
                            let head = params[0].axisValueLabel + "<br />";
                            let info = [];
                            params.forEach(function (el) {
                                let ball = el.marker;
                                let name = el.seriesName;
                                let value = "sin datos";
                                if (el.value !== undefined) {
                                    value = Number(Number(el.value).toFixed(2)).toLocaleString();
                                }
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

        let app = new OperatorApp();
        let previousCall = function () {
        };
        let afterCall = function (data, status) {
            if (status) {
                app.updateMetrics(data);
            }
        };
        let opts = {
            urlFilterData: Urls["esapi:operatorBipData"](),
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