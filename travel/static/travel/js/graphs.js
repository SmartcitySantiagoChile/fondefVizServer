"use strict";

function redraw(options) {
    updateGraphDocCount(options);
    updateGraphTitle(options);
    updateGraph(options);
}

function updateGraphTitle(options) {
    var map_title = document.getElementById("graphTitle");
    if (options.curr_visualization_type !== null) {
        map_title.innerHTML = toTitleCase(options.visualization_mappings[options.curr_visualization_type].name);
    } else {
        map_title.innerHTML = "Mapa";
    }
}

function updateGraphDocCount(options) {
    var graph_type_doc_count = document.getElementById("visualization_type_doc_count");
    if (options.curr_visualization_type !== null && ws_data !== null && ws_data.data !== null) {
        var data = getDataByVisualizationType(ws_data.data, options);
        if (data !== null) {
            var len = data.buckets.length;
            var total = Math.round(data.buckets[len-1].total.value);
            // graph_type_doc_count.innerHTML = ws_data.data.hits.total;
            graph_type_doc_count.innerHTML = total;
            return;
        }
    }
    graph_type_doc_count.innerHTML = 0;
}

function setupGraph(options) {
    ws_data.graph = echarts.init(document.getElementById('graphChart'), theme);
}

function updateGraph(options) {
    // calcular datos
    if (options === undefined || options === null) { return; }
    if (options.curr_visualization_type === undefined || options.curr_visualization_type === null) { return; }
    if (ws_data.graph === undefined || ws_data.graph === null) { return; }

    var mapping = options.visualization_mappings[options.curr_visualization_type];
    var graph_data = getGraphData(options);
    // console.log(graph_data);

    var serie_bin_name = 'Viajes';
    var serie_cum_name = 'Acumulado';

    var graph_options = {
        title: {
            text: ''
        },
        grid: {
            left: '100px',
            right: '80px',
            bottom: '80px'
        },
        legend: {
            data: [serie_bin_name, serie_cum_name]
        },
        xAxis: [{
            type: 'category',
            name: mapping.xaxis_label,
            data: graph_data.xaxis,
            // data: xAxisData.map(function(attr){ return attr.order; })
            axisLabel: {
                formatter: '{value}',
            },
            nameLocation: 'middle',
            nameGap: 25
        }],
        yAxis: [{
            type: 'value',
            name: 'Número de Viajes',
            position: 'left'
        }, {
            // min: 0,
            // max: 100,
            type: 'value',
            name: 'Porcentaje',
            position: 'right',
            axisLabel: {
                formatter: '{value} %',
                textStyle: {
                  color: '#39A7F0'
                }
            },
            axisLine: {
                onZero: true,
                lineStyle: {
                  color: '#39A7F0', width: 2
                }
            },
            nameTextStyle: {
                color: '#39A7F0'
            }
        }],
        series: [{
            name: serie_bin_name,
            type: 'bar',
            data: graph_data.bins,
            yAxisIndex: 0,
            smooth: true,
            // markPoint: {
            //     data: [{
            //         type: 'max',
            //         name: 'Máximo'
            //     }],
            //     label: {
            //         normal: {
            //             formatter: function (param) {
            //                 return param.value.toFixed(2);
            //             }
            //         }
            //     }
            // }
        },
        {
            name: serie_cum_name,
            type: 'line',
            data: graph_data.total_percent,
            yAxisIndex: 1,
            smooth: true,
        }],
        toolbox: {
            show: true,
            itemSize: 20,
            left: 'center',
            bottom: '0px',
            feature : {
                mark : {
                    show: false
                },
                restore : {
                    title: "restaurar",
                    show: false
                },
                saveAsImage : {
                    title: "Guardar imagen",
                    show: true,
                    // name: _dataManager.getDataName()
                    name: mapping.image_name
                },
                dataView: {
                    show: true, 
                    title: 'Ver datos',
                    lang: ['Datos del gráfico', 'cerrar', 'refrescar'],
                    buttonColor: '#169F85',
                    readOnly: true
                }
            }
        },
        tooltip: {
            trigger: 'axis',
            //alwaysShowContent: true,
            formatter: function(params) {
                if (Array.isArray(params)) {
                        let xValue = params[0].dataIndex;
                        let head = 'Rango: ' + params[0].name + ' ' + mapping.xaxis_label + '<br />';
                        let info = [];
                        for (let index in params){
                            let el = params[index];
                            let seriesName = el.seriesName;
                            let value = el.value.toFixed(2);
                            let ball ="<span style='display:inline-block;margin-right:5px;border-radius:10px;width:9px;height:9px;background-color:" + el.color + "'></span>";

                            // depends on the information type
                            let the_text = ball + seriesName + ': ' + value;
                            let suffix = "";
                            if (el.seriesName == serie_bin_name) {
                                the_text = ball + "Número de Viajes: " +  Math.round(el.value) + " / " + graph_data.percent[xValue].toFixed(2) + " %";
                            } else if (el.seriesName == serie_cum_name) {
                                the_text = ball + "Viajes Acumulados: " + graph_data.total[xValue]  + " / " + value  + " %";
                            }

                            info.push(the_text);
                        }
                        return head + info.join('<br />');
                } else {
                    let title = params.data.name;
                    let name = params.seriesName;
                    let value = params.value.toFixed(2);
                    return title + '<br />' + name + ': ' + value;
                }
            }
        },
        calculable: false
    };

    ws_data.graph.clear();
    ws_data.graph.setOption(graph_options, {
        notMerge: true
    });
}