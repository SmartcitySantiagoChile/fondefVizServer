"use strict";

function redraw(options) {
    // if (!ws_data.ready) return;    
    updateGraphDocCount(options);
    updateGraphTitle(options);
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
    if (options.curr_visualization_type !== null) {
        graph_type_doc_count.innerHTML = ws_data.data.hits.total;
    } else {
        graph_type_doc_count.innerHTML = 0;
    }
}

function setupGraph(options) {
    ws_data.graph = echarts.init(document.getElementById('graphChart'), theme);

    if (options === undefined || options === null) { return; }
    if (options.curr_visualization_type === undefined || options.curr_visualization_type === null) { return; }

    var mapping = options.visualization_mappings[options.curr_visualization_type];

    // var mapping = 'ws_data.data.aggregations.tviaje.buckets[i]';
    // var dataName = ['bin.value', 'total.value'];

    var graph_options = {
        title: {
            text: ''
        },
        grid: {
            left: '50px',
            right: '50px',
            bottom: '80px'
        },
        legend: {
            data: [mapping.name, 'Acumulado']
        },
        xAxis: [{
            type: 'category',
            data: ["0", "15", "30", "45", "60", "75"]
            // data: xAxisData.map(function(attr){ return attr.order; })
        }],
        yAxis: [{
            type: 'value',
            name: 'Cantidad',
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
            name: mapping.name,
            type: 'bar',
            data: [25, 25, 20, 15, 10, 5],
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
            name: 'Acumulado',
            type: 'line',
            data: [25, 50, 70, 85, 95, 100],
            yAxisIndex: 1,
            smooth: true,
        }],
        toolbox: {
            show: true,
            itemSize: 20,
            left: 'center',
            bottom: '25px',
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
                        // let head = (xValue + 1) + '  ' + xAxisData[xValue]['userCode'] + ' ' + xAxisData[xValue]['authCode'] + '  ' + xAxisData[xValue]['name'] + '<br />';
                        // let head = 'Poner título aquí<br/>'
                        let head = ''
                        let info = [];
                        for (let index in params){
                            let el = params[index];
                            let ball ="<span style='display:inline-block;margin-right:5px;border-radius:10px;width:9px;height:9px;background-color:" + el.color + "'></span>";
                            let name = el.seriesName;
                            let value = el.value.toFixed(2);
                            info.push(ball + name + ': ' + value);
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

function updateGraph() {
    // calcular datos

}