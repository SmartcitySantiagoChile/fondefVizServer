"use strict";
$(document).ready(function () {
    function IndexApp() {
        var _self = this;
        this._stopColor = {};

        this.getRandomColor = function () {
            var letters = "0123456789ABCDEF";
            var color = "#";
            for (var i = 0; i < 6; i++) {
                color += letters[Math.floor(Math.random() * 16)];
            }
            return color;
        };

        this.getDataName = function () {
            var FILE_NAME = "Validaciones en zona paga ";
            return FILE_NAME + $("#authRouteFilter").val();
        };

        var _datatable = $("#validationDetail").DataTable({
            lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "Todos"]],
            iDisplayLength: -1,
            language: {
                url: "//cdn.datatables.net/plug-ins/1.10.13/i18n/Spanish.json",
                decimal: ",",
                thousands: "."
            },
            columns: [
                {
                    title: "Factor por día", data: "factor_by_date",
                    render: function (data, type, row) {
                        return $("<i>").addClass("spark")[0].outerHTML;
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
            createdRow: function (row, data, index) {
                console.log(data);
                var values = data.factor_by_date.map(function (el) {
                    return el[1];
                });
                if (!_self._stopColor.hasOwnProperty(data.bus_station_id)) {
                    _self._stopColor[data.bus_station_id] = _self.getRandomColor();
                }
                setTimeout(function () {
                    $(row).find(".spark:not(:has(canvas))").sparkline(values, {
                        type: "bar", barColor: _self._stopColor[data.bus_station_id], chartRangeMax: 100,
                        chartRangeMin: 0,
                        tooltipFormatter: function (sparkline, options, fields) {
                            var date = data.factor_by_date[fields[0].offset][0];
                            date = new Date(date).toISOString().substring(0, 10);
                            return date + ": " + Number(fields[0].value.toFixed(2)).toLocaleString() + " %";
                        }
                    });
                }, 50);
            },
            order: [[1, "asc"]],
            dom: 'Bfrtip',
            buttons: [
                {
                    extend: "excelHtml5",
                    text: "Exportar a excel",
                    attr: {class: "buttons-excel buttons-html5 btn btn-success"}
                }
            ]
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