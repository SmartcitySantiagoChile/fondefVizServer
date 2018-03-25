"use strict";
$(document).ready(function () {
    // load table
    (function () {
        var opts = {
            lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "Todos"]],
            language: {
                url: "//cdn.datatables.net/plug-ins/1.10.13/i18n/Spanish.json"
            },
            searching: true,
            order: [[1, "desc"]]
        };
        $("#history").DataTable(opts);
    })()
});