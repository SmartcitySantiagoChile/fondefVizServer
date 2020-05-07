$(document).ready(function () {
    "use strict";

    function DataManagerApp() {
        var _self = this;
        var indexNames = ["Profile", "Speed", "Bip", "Odbyroute", "Trip", "Paymentfactor", "General"];
        var lowerIndexNames = indexNames.map(e => e.toLowerCase());

        var _datatableOpts = {
            lengthMenu: [[20, 50, 100, -1], [20, 50, 100, "Todos"]],
            language: {
                url: "//cdn.datatables.net/plug-ins/1.10.13/i18n/Spanish.json"
            },
            dom: 'Blfrtip',
            order: [[0, 'desc']],
            autowidth: true,

            buttons: [
                {
                    extend: 'csvHtml5',
                    text: 'Guardar como CSV',
                    className: "buttons-csv buttons-html5 btn btn-success",
                },
                {
                    extend: 'excelHtml5',
                    text: 'Guardar como Excel',
                    className: "buttons-excel buttons-html5 btn btn-success",

                },
            ],

            createdRow: function (row, data, index) {
                addColorToRow(data, row);
            }
        };


        var addColorToRow = function (data, row) {
            $(row).removeClass("danger warning success");
            let calculatedDiff = lowerIndexNames.map(index => data[index + "_file"] - data[index + "_index"]);
            const sum_diff = calculatedDiff.reduce((a, b) => a + b);
            $(row).addClass(sum_diff ? "danger" : "success");
        };

        const daysDict = {
            0: 'Domingo',
            1: 'Lunes',
            2: 'Martes',
            3: 'Miércoles',
            4: 'Jueves',
            5: 'Viernes',
            6: 'Sábado'
        };

        this.updateTables = function () {
            $.get(Urls["consistencychecker:getConsistencyData"](), function (data) {
                var dictFiles = JSON.parse(data.response);
                var files = dictFiles.map(e => {
                    let row = e.fields;
                    let date = new Date(row.date);
                    date = new Date(date.getTime() + date.getTimezoneOffset() * 60000);
                    row['day'] = daysDict[date.getDay()];
                    return row;
                });

                let columns = [
                    {
                        title: 'Fecha',
                        data: 'date'
                    },
                    {
                        title: 'Días',
                        data: 'day'
                    }
                ];


                for (let index in lowerIndexNames) {
                    let lower_index = lowerIndexNames[index].toLowerCase();
                    columns.push(
                        {
                            title: lowerIndexNames[index],
                            data: null,
                            render: function (data) {
                                return data[lower_index + "_index"].toString() + " / " + data[lower_index + "_file"].toString();
                            }

                        }
                    )
                }
                var opts = $.extend({data: files, columns: columns}, _datatableOpts);
                $("#fechas-id").DataTable(opts);

            });
        };


    }

    // load filters
    (function () {
        var app = new DataManagerApp();
        app.updateTables();
    })();
});