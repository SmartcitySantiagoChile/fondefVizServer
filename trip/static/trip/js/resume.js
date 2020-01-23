"use strict";
$(document).ready(function () {

    function ResumeApp() {
        var _self = this;
        var chart = echarts.init(document.getElementById("graphChart"), theme);
        var histogramData = null;

        var serieBinName = "Viajes";
        var serieCumName = "Acumulado";
        var genericOpts = {
            title: {
                text: ""
            },
            grid: {
                left: "100px",
                right: "80px",
                bottom: "120px"
            },
            legend: {
                data: [serieBinName, serieCumName]
            },
            xAxis: [{
                type: "category",
                name: "",
                data: [],
                // data: xAxisData.map(function(attr){ return attr.order; })
                axisLabel: {
                    formatter: "{value}"
                },
                nameLocation: "middle",
                nameGap: 25
            }],
            yAxis: [{
                type: "value",
                name: "Número de Viajes",
                position: "left"
            }, {
                // min: 0,
                // max: 100,
                type: "value",
                name: "Porcentaje",
                position: "right",
                axisLabel: {
                    formatter: "{value} %",
                    textStyle: {
                        color: "#39A7F0"
                    }
                },
                axisLine: {
                    onZero: true,
                    lineStyle: {
                        color: "#39A7F0", width: 2
                    }
                },
                nameTextStyle: {
                    color: "#39A7F0"
                }
            }],
            series: [{
                name: serieBinName,
                type: "bar",
                data: [],
                yAxisIndex: 0,
                smooth: true
            }, {
                name: serieCumName,
                type: "line",
                data: [],
                yAxisIndex: 1,
                smooth: true
            }],
            toolbox: {
                show: true,
                showTitle: true,
                itemSize: 20,
                left: "center",
                bottom: "20px",
                feature: {
                    mark: {
                        show: false
                    },
                    restore: {
                        title: "restaurar",
                        show: false
                    },
                    saveAsImage: {
                        title: "Guardar imagen",
                        show: true,
                        name: ""
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
            tooltip: {
                trigger: "axis",
                //alwaysShowContent: true,
                formatter: "",
                calculable: false
            }
        };

        var chartOptions = {
            use_visualization_types: true,
            default_visualization_type: "tviaje",
            curr_visualization_type: null,
            visualization_mappings: {
                tviaje: {
                    name: "Tiempo de viaje",
                    image_name: "histograma_tviaje",
                    xaxis_fn: function (cur, next) {
                        if (next === undefined) {
                            return cur + "+";
                        }
                        return "" + cur + " - " + next;
                    },
                    xaxis_label: "Minutos"
                },
                distancia_ruta: {
                    name: "Distancia en ruta",
                    image_name: "histograma_distancia_ruta",
                    xaxis_fn: function (cur, next) {
                        if (next === undefined) {
                            return Math.floor(cur / 1000) + "+";
                        }
                        return "" + Math.floor(cur / 1000) + " - " + Math.floor(next / 1000) + "";
                    },
                    xaxis_label: "Kilometros"
                },
                distancia_eucl: {
                    name: "Distancia euclideana",
                    image_name: "histograma_distancia_eucl",
                    xaxis_fn: function (cur, next) {
                        if (next === undefined) {
                            return Math.floor(cur / 1000) + "+";
                        }
                        return "" + Math.floor(cur / 1000) + " - " + Math.floor(next / 1000) + "";
                    },
                    xaxis_label: "Kilometros"
                },
                n_etapas: {
                    name: "Número de etapas",
                    image_name: "histograma_n_etapas",
                    xaxis_fn: function (cur, next) {
                        if (next === undefined) {
                            return cur + "+";
                        }
                        return "" + cur;
                    },
                    xaxis_label: "Cantidad de Etapas"
                }
            }
        };

        this.showLoadingAnimationCharts = function () {
            chart.showLoading(null, {text: "Cargando..."});
        };

        this.hideLoadingAnimationCharts = function () {
            chart.hideLoading();
        };

        this.resizeChart = function () {
            chart.resize();
        };

        this.updateChart = function (vizType, histogram, indicators) {
            if (histogram !== undefined) {
                histogramData = histogram;
            }
            if (indicators !== undefined) {
                _self.updateIndicators(indicators);
            }
            var chartData = _self.getChartData(vizType);

            // update opts
            var chartType = chartOptions.visualization_mappings[vizType];
            genericOpts.toolbox.feature.saveAsImage.name = chartType.name;
            genericOpts.xAxis[0].name = chartType.xaxis_label;
            genericOpts.xAxis[0].data = chartData.xaxis;
            genericOpts.series[0].data = chartData.bins;
            genericOpts.series[1].data = chartData.total_percent;
            genericOpts.tooltip.formatter = function (params) {
                if (Array.isArray(params)) {
                    var xValue = params[0].dataIndex;
                    var head = "Rango: " + params[0].name + " " + chartType.xaxis_label + "<br />";
                    var info = [];
                    for (var index in params) {
                        var el = params[index];
                        var seriesName = el.seriesName;
                        var value = parseFloat(el.value.toFixed(2)).toLocaleString();

                        // depends on the information type
                        var the_text = el.marker + seriesName + ": " + value;
                        if (el.seriesName === serieBinName) {
                            the_text = el.marker + "Número de Viajes: " + Math.round(el.value).toLocaleString() + " / " + chartData.percent[xValue].toFixed(2) + " %";
                        } else if (el.seriesName === serieCumName) {
                            the_text = el.marker + "Viajes Acumulados: " + chartData.total[xValue].toLocaleString() + " / " + value + " %";
                        }

                        info.push(the_text);
                    }
                    return head + info.join("<br />");
                } else {
                    var title = params.data.name;
                    var name = params.seriesName;
                    var value = parseFloat(params.value.toFixed(2)).toLocaleString();
                    return title + "<br />" + name + ": " + value;
                }
            };

            chart.clear();
            chart.setOption(genericOpts, {merge: false});
        };

        this.updateIndicators = function (data) {
            var viajes = data.viajes.value || 0;
            var documents = data.documentos.value || 0;
            var tviaje_avg = data.tviaje.avg || 0;
            var tviaje_max = data.tviaje.max || 0;
            var netapas_avg = data.n_etapas.avg || 0;
            var netapas_max = data.n_etapas.max || 0;
            var dist_eucl_avg = data.distancia_eucl.avg / 1000.0 || 0;
            var dist_eucl_max = data.distancia_eucl.max / 1000.0 || 0;
            var dist_ruta_avg = data.distancia_ruta.avg / 1000.0 || 0;
            var dist_ruta_max = data.distancia_ruta.max / 1000.0 || 0;

            // display
            $("#indicator-viajes").text(parseFloat(viajes.toFixed(2)).toLocaleString());
            $("#indicator-documentos").text(parseFloat(documents.toFixed(0)).toLocaleString());
            $("#indicator-tviaje-avg").text(parseFloat(tviaje_avg.toFixed(0)).toLocaleString() + " min");
            $("#indicator-tviaje-max").text(parseFloat(tviaje_max.toFixed(0)).toLocaleString() + " min");
            $("#indicator-netapas-avg").text(parseFloat(netapas_avg.toFixed(2)).toLocaleString() + " etapas");
            $("#indicator-netapas-max").text(parseFloat(netapas_max.toFixed(0)).toLocaleString());
            $("#indicator-dist-eucl-avg").text(parseFloat(dist_eucl_avg.toFixed(1)).toLocaleString() + " km");
            $("#indicator-dist-eucl-max").text(parseFloat(dist_eucl_max.toFixed(1)).toLocaleString() + " km");
            $("#indicator-dist-ruta-avg").text(parseFloat(dist_ruta_avg.toFixed(1)).toLocaleString() + " km");
            $("#indicator-dist-ruta-max").text(parseFloat(dist_ruta_max.toFixed(1)).toLocaleString() + " km");
        };

        this.getChartData = function (vizType) {
            var data = histogramData[vizType];

            var xaxis_fn = chartOptions.visualization_mappings[vizType].xaxis_fn;

            var result = {};
            result.xaxis = [];
            result.count = [];
            result.bins = [];
            result.total = [];
            result.percent = [];
            result.total_percent = [];

            var len = data.buckets.length;
            var total = Math.round(data.buckets[len - 1].total.value);
            if (total <= 0) {
                total = 1;
            }

            for (var i = 0; i < len - 1; ++i) {
                var item = data.buckets[i];
                var next = data.buckets[i + 1];
                result.count.push(Math.round(item.doc_count));
                result.bins.push(Math.round(item.bin.value));
                result.total.push(Math.round(item.total.value));
                result.percent.push(100.0 * Math.round(item.bin.value) / total);
                result.total_percent.push(100.0 * Math.round(item.total.value) / total);
                result.xaxis.push(xaxis_fn(item.key, next.key));
            }
            result.count.push(Math.round(data.buckets[len - 1].doc_count));
            result.bins.push(Math.round(data.buckets[len - 1].bin.value));
            result.total.push(Math.round(data.buckets[len - 1].total.value));
            result.percent.push(100.0 * Math.round(data.buckets[len - 1].bin.value) / total);
            result.total_percent.push(100.0 * Math.round(data.buckets[len - 1].total.value) / total);
            result.xaxis.push(xaxis_fn(data.buckets[len - 1].key));
            return result;
        };

        this.setChartSelector = function () {
            var data = [];
            Object.keys(chartOptions.visualization_mappings).forEach(function (key) {
                data.push({id: key, text: chartOptions.visualization_mappings[key].name});
            });

            $("#vizSelector").select2({
                minimumResultsForSearch: Infinity, // hide search box
                data: data
            }).on("select2:select", function (e) {
                var selectedChart = $(this).val();
                _self.updateChart(selectedChart);
            }).val(chartOptions.default_visualization_type).trigger("change"); // force default
        };
        this.setChartSelector();
    }

    function processData(data, app) {
        if (data.status) {
            return;
        }
        var vizType = $("#vizSelector").val();
        app.updateChart(vizType, data.histogram.aggregations, data.indicators.aggregations);
    }

// load filters
    (function () {
        loadAvailableDays(Urls["esapi:availableTripDays"]());
        loadRangeCalendar(Urls["esapi:availableTripDays"](),{});


        var app = new ResumeApp();

        var previousCall = function () {
            app.showLoadingAnimationCharts();
        };
        var afterCall = function (data) {
            processData(data, app);
            app.hideLoadingAnimationCharts();
        };
        var opts = {
            urlFilterData: Urls["esapi:resumeTripData"](),
            previousCallData: previousCall,
            afterCallData: afterCall
        };
        var manager = new FilterManager(opts);
        $(window).resize(function () {
            app.resizeChart();
        });
        $("#menu_toggle").click(function () {
            app.resizeChart();
        });
        // load first time
        manager.updateData();
    })();
})
;