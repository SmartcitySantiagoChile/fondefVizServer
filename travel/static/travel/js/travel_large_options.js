"use strict";

var options = {};
options.use_visualization_types = false;
options.use_map_sectors = false;
options.default_visualization_type = 'tviaje';
options.default_sector = 'Centro';
options.curr_sector = null;
options.curr_visualization_type = 'count';

// Orange Scale
// http://colorbrewer2.org/#type=sequential&scheme=GnBu&n=5
options.map_color_scale_secuential = ["#ffffb2", "#fecc5c", "#fd8d3c", "#f03b20", "#bd0026"],

// Diverging Version
// http://colorbrewer2.org/#type=diverging&scheme=Spectral&n=5
options.map_color_scale_diverging = ["#2b83ba", "#abdda4", "#ffffbf", "#fdae61", "#d7191c"];
options.curr_map_color_scale = options.map_color_scale_diverging;

options.visualization_mappings = {
    tviaje: {
        name: 'Tiempo de viaje',
        grades: [0, 30, 45, 60, 75],
        grades_str: ["0", "30", "45", "60", "75"],
        legend_post_str: "min",
        map_fn: function (zone) { return zone.tviaje.value; }
    },
    distancia_ruta: {
        name: 'Distancia en ruta',
        grades: [0, 1000, 5000, 10000, 20000],
        grades_str: ["0", "1", "5", "10", "20"],
        legend_post_str: "km",
        map_fn: function (zone) { return zone.distancia_ruta.value; }
    },
    distancia_eucl: {
        name: 'Distancia euclideana',
        grades: [0, 1000, 5000, 10000, 20000],
        grades_str: ["0", "1", "5", "10", "20"],
        legend_post_str: "km",
        map_fn: function (zone) { return zone.distancia_eucl.value; }
    },
    n_etapas: {
        name: 'Número de etapas',
        grades: [1.0, 1.3, 2.0, 2.3, 3.0],
        grades_str: ["1.0", "1.3", "2.0", "2.3", "3.0"],
        legend_post_str: "",
        map_fn: function (zone) { return zone.n_etapas.avg; }
    },
    count: {
        name: 'Cantidad de datos',
        grades: [1, 10, 20, 30, 40],
        grades_str: ["1", "10", "20", "30", "40"],
        legend_post_str: "",
        map_fn: function (zone) { return zone.doc_count; }
    }
};

options.map_default_lat_lon = L.latLng(-33.459229, -70.645348);
options.visible_limits = [0, 0];
options.map_min_zoom = 8;
options.map_default_zoom = 11;
options.map_feature_zoom = 13;
options.map_max_zoom = 15;
options.map_access_token = "pk.eyJ1IjoidHJhbnNhcHB2aXMiLCJhIjoiY2l0bG9qd3ppMDBiNjJ6bXBpY3J0bm40cCJ9.ajifidV4ypi0cXgiGQwR-A";
