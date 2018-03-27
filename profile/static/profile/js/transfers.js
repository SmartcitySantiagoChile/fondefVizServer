"use strict";
$(document).ready(function () {
    function TransferApp() {
        var _self = this;
        var tableId = "#transferTable";
        var firstColumn = {
            title: "Llegada \\ Salida",
            className: "text-center",
            data: "from"
        };
        var lastColumn = {
            title: "Total",
            className: "text-center",
            data: function (data, type, full, meta) {
                var total = 0;
                for (var key in data) {
                    if (!isNaN(data[key])) {
                        total += data[key];
                    }
                }
                return total;
            },
            render: $.fn.dataTable.render.number(".", ",", 0)
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
                        value = $.fn.dataTable.render.number(".", ",", 0).display(value);
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
                    render: $.fn.dataTable.render.number(".", ",", 0),
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
        var data = dataSource.data;
        var rows = [];
        var columns = [];
        for (var route_from in data) {
            if (route_from === "-") {
                continue;
            }
            var row = {
                from: route_from
            };
            for (var route_to in data[route_from]) {
                var key = route_to;
                if (route_to === "-") {
                    key = endOfTripLabel;
                }
                row[key] = data[route_from][route_to];
                if (columns.indexOf(key) < 0 && key !== endOfTripLabel) {
                    columns.push(key);
                }
            }
            rows.push(row);
        }
        columns.push(endOfTripLabel);

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