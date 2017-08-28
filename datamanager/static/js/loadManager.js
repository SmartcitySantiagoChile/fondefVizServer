"use strict";
$(document).ready(function() {
    const URL = "loadManager/data";
    $.get(URL, function (data) {
        console.log(data);
        let dictFiles = data["routeDictFiles"];

        let _datatableOpts = {
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
                {title: "N° de documentos en plataforma", data: "lines", searchable: true},
                {
                    title: "Cargar datos a la plataforma",
                    "searchable": false,
                    "orderable": false,
                    "className": "text-center",
                    render: function (data, type, full, meta) {
                        return '<button type="button" class="btn btn-info btn-xs" >Cargar datos</button>';
                    }
                },
                {
                    title: "Eliminar datos de la plataforma",
                    "searchable": false,
                    "orderable": false,
                    "className": "text-center",
                    render: function (data, type, full, meta) {
                        return '<button type="button" class="btn btn-danger btn-xs" >Eliminar</button>';
                    }
                },
            ],
            order: [[1, "desc"]],
            createdRow: function (row, data, index) {
                if (data.line !== data.line) {
                    $(row).addClass("danger");
                }
            },
        };

        for (let key in dictFiles) {
            let files = dictFiles[key];
            let opts = $.extend({data: files}, _datatableOpts);
            let id = key + "Table";
            let table = $("#" + id).DataTable(opts);

            $("#" + id + " tbody").on("click", "button", function () {
                let buttonName = $(this).html();
                let data = table.row($(this).parents("tr")).data();

                let deleteMessage = "¿Está segur@ que desea eliminar los datos? Recuerde que esta operación es irreversible.";
                let uploadMessage = "Este proceso dura unos minutos ¿está seguro de iniciarlo?";
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