"use strict";

var options = {};
options.use_visualization_types = true;
options.default_visualization_type = 'tviaje'; // TODO: AL PARECER NO FUNCIONA BIEN ESTO!
options.curr_visualization_type = null;

// http://colorbrewer2.org/#type=sequential&scheme=GnBu&n=5
options.visualization_mappings = {
    tviaje: {
        name: 'Tiempo de viaje',
        image_name: 'histograma_tviaje',

        grades: [0, 30, 45, 60, 75],
        grades_str: ["0", "30", "45", "60", "75"],
        legend_post_str: "min",
        colors: ["#ffffb2", "#fecc5c", "#fd8d3c", "#f03b20", "#bd0026"],
        map_fn: function (zone) { return zone.tviaje.value; }
    },
    distancia_ruta: {
        name: 'Distancia en ruta',
        image_name: 'histograma_distancia_ruta',

        grades: [0, 1000, 5000, 10000, 20000],
        grades_str: ["0", "1", "5", "10", "20"],
        legend_post_str: "km",
        colors: ["#ffffb2", "#fecc5c", "#fd8d3c", "#f03b20", "#bd0026"],
        map_fn: function (zone) { return zone.distancia_ruta.value; }
    },
    distancia_eucl: {
        name: 'Distancia euclideana',
        image_name: 'histograma_distancia_eucl',

        grades: [0, 1000, 5000, 10000, 20000],
        grades_str: ["0", "1", "5", "10", "20"],
        legend_post_str: "km",
        colors: ["#ffffb2", "#fecc5c", "#fd8d3c", "#f03b20", "#bd0026"],
        map_fn: function (zone) { return zone.distancia_eucl.value; }
    },
    n_etapas: {
        name: 'Número de etapas',
        image_name: 'histograma_n_etapas',

        grades: [1.0, 1.3, 2.0, 2.3, 3.0],
        grades_str: ["1.0", "1.3", "2.0", "2.3", "3.0"],
        legend_post_str: "",
        colors: ["#ffffb2", "#fecc5c", "#fd8d3c", "#f03b20", "#bd0026"],
        map_fn: function (zone) { return zone.n_etapas.value; }
    },
    count: {
        name: 'Cantidad de datos',
        image_name: 'histograma_count',

        grades: [1, 5, 25, 50, 75],
        grades_str: ["1", "5", "25", "50", "75"],
        legend_post_str: "",
        colors: ["#ffffb2", "#fecc5c", "#fd8d3c", "#f03b20", "#bd0026"],
        map_fn: function (zone) { return zone.doc_count; }
    }
};
