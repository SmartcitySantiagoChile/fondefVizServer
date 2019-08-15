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
                {
                    title: "Factor por día", data: null,
                    render: function (data, type, row) {
                        data = [1.6,2.7,3,4,5,6,7,8];
                        return $("<i>").addClass("spark").append(data.join(","))[0].outerHTML;
                    }
                },
                {title: "Id zona paga", data: "bus_station_id"},
                {title: "Nombre zona paga", data: "bus_station_name"},
                {title: "Asignación", data: "assignation"},
                {title: "Operador", data: "operator"},
                {title: "Tipo de día", data: "day_type"},
                {title: "Total", data: "total"},
                {title: "Suman", data: "sum"},
                {title: "Restan", data: "subtraction"},
                {title: "Neutras", data: "neutral"},
                {
                    title: "Factor", data: null,
                    render: function (data, type, row) {
                        var result = (row.sum - row.subtraction) / row.total;
                        result = row.assignation === "ASIGNADA" ? 1 + result : result;
                        return Number((result * 100).toFixed(2)).toLocaleString() + " %";
                    }
                }
            ],
            order: [[0, "asc"]]
        });

        _self.updateDatatable = function (rows) {
            var maxHeight = 10;
            _datatable.off("draw");
            _datatable.on("draw", function (oSettings) {
                $(".spark:not(:has(canvas))").sparkline("html", {
                    type: "line",
                    width: "100%",
                    Height: "100%",
                    lineColor: "#169f85",
                    negBarColor: "red",
                    chartRangeMax: maxHeight,
                    numberFormatter: function (value) {
                        return Number(value.toFixed(2)).toLocaleString();
                    }
                });
            });

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