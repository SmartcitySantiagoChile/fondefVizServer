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
                    render: function (data, type) {
                        var date = new Date(data);
                        if (type === "sort") {
                            return date.getTime();
                        }
                        return date.toLocaleString();
                    }
                }, {
                    render: function (data, type) {
                        if (data !== "None") {
                            var date = new Date(data);
                            if (type === "sort") {
                                return date.getTime();
                            }
                            return date.toLocaleString();
                        } else {
                            return "";
                        }
                    }
                }, {
                    render: function (data, type) {
                        if (data !== "None") {
                            var date = new Date(data);
                            if (type === "sort") {
                                return date.getTime();
                            }
                            return date.toLocaleString();
                        } else {
                            return "";
                        }
                    }
                }, {
                    render: function (data) {
                        var link = "";
                        if (data !== "") {
                            link = "<a class='btn btn-success btn-lg' href='" + data + "'>Descargar</a>";
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