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
            order: [[1, "desc"]],
            columns: [
                null, {
                    render: function (data) {
                        return (new Date(data)).toLocaleString();
                    }
                }, {
                    render: function (data) {
                        if (data !== "None") {
                            return (new Date(data)).toLocaleString();
                        } else {
                            return "";
                        }
                    }
                }, {
                    render: function (data) {
                        if (data !== "None") {
                            return (new Date(data)).toLocaleString();
                        } else {
                            return "";
                        }
                    }
                }, {
                    render: function (data) {
                        var link = "";
                        if (data !== "") {
                            link = "<a href='" + data + "'>Descargar</a>";
                        }
                        return link;
                    }
                },
                null, {
                    render: function (data) {
                        return data.replace(/(?:\r\n|\r|\n)/g, "<br />");
                    }
                }
            ]
        };
        $("#history").DataTable(opts);
    })()
});