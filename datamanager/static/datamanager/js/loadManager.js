"use strict";
$(document).ready(function () {
    function DataManagerApp() {
        var _self = this;
        var _datatableOpts = {
            lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "Todos"]],
            language: {
                url: "//cdn.datatables.net/plug-ins/1.10.13/i18n/Spanish.json"
            },
            searching: false,
            columns: [
                {title: "Nombre de archivo", data: "name", searchable: true},
                {
                    title: "Última modificación", data: "lastModified", searchable: true,
                    render: function (data, type, row, meta) {
                        return (new Date(data)).toLocaleString();
                    }
                },
                {title: "N° de líneas archivo", data: "lines", searchable: true},
                {title: "N° de documentos en plataforma", data: "docNumber", searchable: true},
                {
                    title: "Documentos fuera de la plataforma",
                    searchable: true,
                    render: function (data, type, full, meta) {
                        return full.lines - full.docNumber;
                    }
                },
                {
                    title: "Cargar datos a la plataforma|Cancelar carga|Eliminar datos de la plataforma",
                    "searchable": false,
                    "orderable": false,
                    "className": "text-center",
                    render: function (data, type, full, meta) {
                        var loadButton = "<button type='button' class='btn btn-info btn-xs' >Cargar datos</button>";
                        var cancelButton = "<button type='button' class='btn btn-warning btn-xs' >Cancelar carga</button>";
                        var deleteButton = "<button type='button' class='btn btn-danger btn-xs' >Eliminar</button>";
                        return loadButton + cancelButton + deleteButton;
                    }
                }
            ],
            order: [[4, "desc"]],
            createdRow: function (row, data, index) {
                if (data.line !== data.docNumber) {
                    $(row).addClass("danger");
                }
            }
        };

        this.loadFile = function (fileName) {
            var params = {
                fileName: fileName
            };
            $.post(Urls["datamanager:loadData"](), params, function (data) {
                showMessage(data.status);
            });
        };

        this.deleteFile = function (fileName) {
            var params = {
                fileName: fileName
            };
            $.post(Urls["datamanager:deleteData"](), params, function (data) {
                showMessage(data.status);
            });
        };

        this.cancelFile = function (fileName) {
            var params = {
                fileName: fileName
            };
            $.post(Urls["datamanager:cancelData"](), params, function (data) {
                showMessage(data.status);
            });
        };

        this.updateTables = function () {
            $.get(Urls["datamanager:getLoadFileData"](), function (data) {
                console.log(data);
                var dictFiles = data.routeDictFiles;

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
                        var cancelMessage = "Está segur@ de cancelar la tarea de carga para este archivo?";
                        if (buttonName === "Eliminar" && confirm(deleteMessage)) {
                            _self.deleteFile(data.name);
                        } else if (buttonName === "Cargar datos" && confirm(uploadMessage)) {
                            _self.loadFile(data.name);
                        } else if (buttonName === "Cancelar carga" && confirm(cancelMessage)) {
                            _self.cancelFile(data.name);
                        }
                        console.log(data);
                    });
                }
            });
        };
    }

    // load filters
    (function () {
        var app = new DataManagerApp();
        app.updateTables();
    })()
});