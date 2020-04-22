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
            order: [[0, 'desc']],
            autowidth: true,
            searching: false,

            createdRow: function (row, data, index) {
                addColorToRow(data, row);
            }
        };


        var addColorToRow = function (data, row) {
            $(row).removeClass("danger warning success");
            let sum_dif = 0;
            sum_dif += (data.profile_file - data.profile_index);
            sum_dif += (data.speed_file - data.speed_index);
            sum_dif += (data.bip_file - data.bip_index);
            sum_dif += (data.odbyroute_file - data.odbyroute_index);
            sum_dif += (data.trip_file - data.trip_index);
            sum_dif += (data.paymentfactor_file - data.paymentfactor_index);
            sum_dif += (data.general_file - data.general_index);

            if (sum_dif !== 0) {
                $(row).addClass("danger");
            } else {
                $(row).addClass("success");
            }
        };


        this.updateTables = function () {
            $.get(Urls["consistencychecker:getConsistencyData"](), function (data) {
                var dictFiles = JSON.parse(data.response);
                var files = dictFiles.map(e => {
                    return e.fields;
                });


                let columns = [{
                    title: 'Fecha',
                    data: 'date'
                }];

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