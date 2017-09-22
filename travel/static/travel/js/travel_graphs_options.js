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
        xaxis_fn: function (cur, next) {
            if (next === undefined) { return cur + "+"; }
            return "" + cur + " - " + next;
        },
        xaxis_label: "Minutos"
    },
    distancia_ruta: {
        name: 'Distancia en ruta',
        image_name: 'histograma_distancia_ruta',
        xaxis_fn: function (cur, next) {
            if (next === undefined) { return Math.floor(cur/1000) + "+"; }
            return "" + Math.floor(cur/1000) + " - " + Math.floor(next/1000) + "";
        },
        xaxis_label: "Kilometros"
    },
    distancia_eucl: {
        name: 'Distancia euclideana',
        image_name: 'histograma_distancia_eucl',
        xaxis_fn: function (cur, next) {
            if (next === undefined) { return Math.floor(cur/1000) + "+"; }
            return "" + Math.floor(cur/1000) + " - " + Math.floor(next/1000) + "";
        },
        xaxis_label: "Kilometros"
    },
    n_etapas: {
        name: 'Número de etapas',
        image_name: 'histograma_n_etapas',
        xaxis_fn: function (cur, next) {
            if (next === undefined) { return cur + "+"; }
            return "" + cur;
        },
        xaxis_label: "Cantidad de Etapas"
    }
};
