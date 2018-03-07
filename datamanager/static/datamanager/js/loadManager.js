"use strict";
$(document).ready(function () {
    $.get(Urls["datamanager:getLoadFileData"](), function (data) {
        console.log(data);
        var dictFiles = data["routeDictFiles"];

        var _datatableOpts = {
            lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "Todos"]],
            language: {
                url: "//cdn.datatables.net/plug-ins/1.10.13/i18n/Spanish.json"
            },
            searching: false,
            columns: [
                {title: "Nombre de archivo", data: "name", searchable: true},
                {
                    title: "Última fecha de carga", data: "discoverAt", searchable: true,
                    render: function (data, type, row, meta) {
                        return (new Date(data)).toLocaleString();
                    }
                },
                {title: "N° de líneas archivo", data: "lines", searchable: true},
                {title: "N° de documentos en plataforma", data: "docNumber", searchable: true},
                {
                    title: "Cargar datos a la plataforma",
                    "searchable": false,
                    "orderable": false,
                    "className": "text-center",
                    render: function (data, type, full, meta) {
                        return "<button type='button' class='btn btn-info btn-xs' >Cargar datos</button>";
                    }
                },
                {
                    title: "Eliminar datos de la plataforma",
                    "searchable": false,
                    "orderable": false,
                    "className": "text-center",
                    render: function (data, type, full, meta) {
                        return "<button type='button' class='btn btn-danger btn-xs' >Eliminar</button>";
                    }
                }
            ],
            order: [[1, "desc"]],
            createdRow: function (row, data, index) {
                if (data.line !== data.line) {
                    $(row).addClass("danger");
                }
            }
        };

        for (var key in dictFiles) {
            var files = dictFiles[key];
            var opts = $.extend({data: files}, _datatableOpts);
            var id = key + "Table";
            var table = $("#" + id).DataTable(opts);

            $("#" + id + " tbody").on("click", "button", function () {
                var buttonName = $(this).html();
                var data = table.row($(this).parents("tr")).data();

                var deleteMessage = "¿Está segur@ que desea eliminar los datos? Recuerde que esta operación es irreversible.";
                var uploadMessage = "Este proceso dura unos minutos ¿está seguro de iniciarlo?";
                if (buttonName === "Eliminar" && confirm(deleteMessage)) {
                    console.log("bbbbb");
                } else if (buttonName === "Cargar datos" && confirm(uploadMessage)) {
                    console.log("aaaa");
                }
                console.log(data);
            });
        }
    });

    // load filters
    (function () {
        // set locale

    })()
});