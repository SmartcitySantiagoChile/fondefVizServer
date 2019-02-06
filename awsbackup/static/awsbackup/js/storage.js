"use strict";
$(document).ready(function () {
    // load filters
    (function () {
        loadAvailableDays(Urls["awsbackup:availableDays"](bucketName));

        var _datatable = $("#dataTableId").DataTable({
            lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "Todos"]],
            language: {
                url: "//cdn.datatables.net/plug-ins/1.10.13/i18n/Spanish.json",
                decimal: ",",
                thousands: "."
            },
            columns: [
                {
                    "className": "text-center"
                },
                {
                    render: function (data, type, row) {
                        return (new Date(data)).toLocaleString();
                    }
                },
                {
                    render: function (data, type, row) {
                        return parseFloat(data).toFixed(2) + " MB";
                    }
                },
                {
                    render: function (data, type, row) {
                        return "<a href='" + data + "'>descargar</a>";
                    }
                }
            ],
            order: [[0, "desc"]]
        });
    })()
});