"use strict";
$(document).ready(function () {
    function IndexApp() {
        var _self = this;

        this.getDataName = function () {
            var FILE_NAME = "Validaciones en zona paga ";
            return FILE_NAME + $("#authRouteFilter").val();
        };

        var _datatable = $("#validationDetail").DataTable({
            lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "Todos"]],
            language: {
                url: "//cdn.datatables.net/plug-ins/1.10.13/i18n/Spanish.json",
                decimal: ",",
                thousands: "."
            },
            columns: [
                {title: "Id zona paga", data: "bus_station_id"},
                {title: "Nombre zona paga", data: "bus_station_name"},
                {title: "Asignación", data: "assignation"},
                {title: "Operador", data: "operator"},
                {title: "Total", data: "total"},
                {title: "Suman", data: "sum"},
                {title: "Restan", data: "subtraction"},
                {title: "Neutras", data: "neutral"},
                {
                    title: "Resultado 1", data: null,
                    render: function (data, type, row) {
                        return Number(((row.sum - row.subtraction) / row.total).toFixed(3)).toLocaleString();
                    }
                },
                {
                    title: "Resultado 2", data: null,
                    render: function (data, type, row) {
                        var result = (row.sum - row.subtraction) / row.total;
                        return Number((row.assignation === "ASIGNADA" ? 1 + result : result).toFixed(3)).toLocaleString();
                    }
                }
            ],
            order: [[0, "asc"]]
        });

        _self.updateDatatable = function (rows) {
            _datatable.clear();
            _datatable.rows.add(rows);
            _datatable.columns.adjust().draw();
        };
    }

    function processData(dataSource, app) {
        console.log(dataSource);

        if (dataSource.status) {
            return;
        }

        app.updateDatatable(dataSource.rows);
    }

    // load filters
    (function () {
        loadAvailableDays(Urls["esapi:availableBusstationdistDays"]());

        var app = new IndexApp();
        var afterCall = function (data) {
            processData(data, app);
        };
        var opts = {
            urlFilterData: Urls["esapi:busstationdistData"](),
            afterCallData: afterCall
        };

        new FilterManager(opts);
    })()
});