$(document).ready(function () {
    "use strict";

    function DataManagerApp() {
        var _self = this;
        var _datatableOpts = {
            lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "Todos"]],
            language: {
                url: "//cdn.datatables.net/plug-ins/1.10.13/i18n/Spanish.json"
            },
            order: [[4, "desc"]],
            columns: [
                {
                    title: 'Fecha',
                    data: 'date',
                },
                {
                    title: "Profile",
                    data: null,
                    render: function (data, type, row) {
                        return data.profile_index.toString() + " / " + data.profile_file.toString();
                    }
                },
                {
                    title: "Speed",
                    data: null,
                    render: function (data, type, row) {
                        return data.speed_index.toString() + " / " + data.speed_file.toString();
                    }
                },
                {
                    title: "Bip",
                    data: null,
                    render: function (data, type, row) {
                        return data.bip_index.toString() + " / " + data.bip_file.toString();
                    }
                },
                {
                    title: "Odbyroute",
                    data: null,
                    render: function (data, type, row) {
                        return data.odbyroute_index.toString() + " / " + data.odbyroute_file.toString();
                    }
                },
                {
                    title: "Trip",
                    data: null,
                    render: function (data, type, row) {
                        return data.trip_index.toString() + " / " + data.trip_file.toString();
                    }
                },
                {
                    title: "Paymentfactor",
                    data: null,
                    render: function (data, type, row) {
                        return data.paymentfactor_index.toString() + " / " + data.paymentfactor_file.toString();
                    }
                },
                {
                    title: "General",
                    data: null,
                    render: function (data, type, row) {
                        return data.general_index.toString() + " / " + data.general_file.toString();
                    }
                },
            ]
            //createdRow: function (row, data, index) {
            //    addColorToRow(data, row);
            //}
        };
        console.log(_datatableOpts);

        var addColorToRow = function (data, row) {
            $(row).removeClass("danger warning success");
            if (data.lines !== data.docNumber) {
                $(row).addClass("danger");
            } else {
                $(row).addClass("success");
            }
            if (data.lastExecution !== null) {
                if (["enqueued", "running"].indexOf(data.lastExecution.status) >= 0) {
                    $(row).removeClass("danger success");
                    $(row).addClass("warning");
                }
            }
        };


        this.updateTables = function () {
            $.get(Urls["consistencychecker:getConsistencyData"](), function (data) {
                var dictFiles = JSON.parse(data.response);
                var files = dictFiles.map(e => {
                    return e.fields;
                });
                console.log(files);
                var opts = $.extend({data: files}, _datatableOpts);
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