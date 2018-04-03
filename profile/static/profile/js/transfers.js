"use strict";
$(document).ready(function () {
    function TransferApp() {
        var _self = this;
        var tableId = "#transferTable";
        var firstColumn = {
            title: "Salida \\ Llegada",
            className: "text-center",
            data: "to"
        };
        var lastColumn = {
            title: "Total",
            className: "text-center",
            data: function (data) {
                var total = 0;
                for (var key in data) {
                    if (!isNaN(data[key])) {
                        total += data[key];
                    }
                }
                return total;
            },
            render: $.fn.dataTable.render.number(".", ",", 2)
        };
        var datatableOpts = {
            searching: false,
            paging: false,
            info: false,
            fixedHeader: {
                header: true,
                footer: true
            },
            language: {
                url: "//cdn.datatables.net/plug-ins/1.10.13/i18n/Spanish.json",
                decimal: ",",
                thousands: "."
            },
            columns: [firstColumn],
            order: [[0, "asc"]],
            fnFooterCallback: function (row, data, start, end, display) {
                var api = this.api();
                api.columns().every(function (index) {
                    var value = "Total:";
                    var alignClass = "text-right";
                    if (index !== 0) {
                        var column = this;
                        value = column.data().reduce(function (a, b) {
                            var x = parseFloat(a) || 0;
                            return x + b;
                        }, 0);
                        alignClass = "text-center";
                        value = $.fn.dataTable.render.number(".", ",", 2).display(value);
                    }
                    $("#footer" + index).html(value).parent().removeClass("text-center").addClass(alignClass);
                });
            }
        };
        var datatableInstance = null;

        this.createColumns = function (columns) {
            var columnsConf = [firstColumn];

            var newColumns = columns.map(function (columnName) {
                return {
                    title: columnName,
                    data: function (row, type, set) {
                        if (row[columnName] === undefined) {
                            return null;
                        }
                        return row[columnName];
                    },
                    render: $.fn.dataTable.render.number(".", ",", 2),
                    className: "text-center"
                };
            });
            newColumns.push(lastColumn);

            return columnsConf.concat(newColumns);
        };

        this.updateTable = function (rows, columns) {
            if (datatableInstance !== null) {
                datatableInstance.destroy();
            }
            $(tableId).empty();

            // add footer
            var footer = $(tableId).append("<tfoot><tr></tr></tfoot>").find("tfoot tr");
            for (var i = 0; i < columns.length + 2; i++) {
                footer.append("<th><span id='footer" + i + "'></span></th>");
            }

            var opts = jQuery.extend(true, {
                columns: _self.createColumns(columns),
                data: rows
            }, datatableOpts);
            datatableInstance = $(tableId).DataTable(opts);
        };
        _self.updateTable([], []);
    }

    function processData(dataSource, app) {
        console.log(dataSource);

        if (dataSource.status) {
            return;
        }

        var endOfTripLabel = "Fin de viaje";
        var unknownLabel = "Desconocido";
        var data = dataSource.data;
        var rows = [];
        var columns = [];
        for (var route_to in data) {
            var key = route_to;
            if (key === "end") {
                key = endOfTripLabel;
            }
            else if (key === "-") {
                key = unknownLabel;
            }
            var row = {
                to: key
            };
            for (var route_from in data[route_to]) {
                var rowLabel = route_from;
                if (route_from === "-") {
                    rowLabel = unknownLabel;
                }
                row[rowLabel] = data[route_to][route_from];
                if (columns.indexOf(rowLabel) < 0) {
                    columns.push(rowLabel);
                }
            }
            rows.push(row);
        }

        app.updateTable(rows, columns);
    }

    // load filters
    (function () {
        loadAvailableDays(Urls["esapi:availableTripDays"]());

        var app = new TransferApp();
        var afterCall = function (data) {
            processData(data, app);
        };
        var opts = {
            urlFilterData: Urls["esapi:transfersData"](),
            afterCallData: afterCall
        };
        new FilterManager(opts);
    })();
});