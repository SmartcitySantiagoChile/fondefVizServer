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
                {title: "Archivo", data: "name", searchable: true},
                {
                    title: "Última modificación", data: "lastModified", searchable: true,
                    render: function (data, type, row, meta) {
                        return (new Date(data)).toLocaleString();
                    }
                },
                {title: "Registros en archivo", data: "lines", searchable: true},
                {title: "Registros en plataforma", data: "docNumber", searchable: true},
                {
                    title: "Diferencia",
                    searchable: true,
                    render: function (data, type, full, meta) {
                        return full.lines - full.docNumber;
                    }
                },
                {
                    title: "Acciones",
                    "searchable": false,
                    "orderable": false,
                    "className": "text-center",
                    render: function (data, type, full, meta) {
                        return renderButtons(full);
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

        var renderButtons = function (data) {
            var createHTMLButton = function (buttonName, classButton, disabled) {
                var disabledTxt = "";
                if (disabled) {
                    disabledTxt = "disabled";
                }
                return "<button type='button' class='btn btn-" + classButton + " btn-xs' " + disabledTxt + " >" + buttonName + "</button>";
            };
            var disableUploadButton = false;
            var disableDeleteButton = false;
            var disableCancelButton = false;
            var isLoading = false;

            if (data.lastExecution !== null && data.lastExecution.status === "running") {
                isLoading = true;
            }

            if (data.line === data.docNumber || isLoading) {
                disableUploadButton = true;
            }
            if (!isLoading) {
                disableCancelButton = true;
            }
            if (data.docNumber === 0) {
                disableDeleteButton = true;
            }
            var uploadButton = createHTMLButton("Cargar datos", "info", disableUploadButton);
            var deleteButton = createHTMLButton("Eiminar", "danger", disableDeleteButton);
            var cancelButton = createHTMLButton("Cancelar carga", "warning", disableCancelButton);

            return uploadButton + cancelButton + deleteButton;
        };

        this.uploadFile = function (fileName) {
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
                }

                var htmlSelector = $("tbody");
                htmlSelector.on("click", "button.btn-info", function () {
                    var table = $(this).closest('table').DataTable();
                    var data = table.row($(this).parents("tr")).data();
                    console.log(data);
                    var uploadMessage = "Este proceso dura unos minutos ¿está seguro de iniciarlo?";
                    if (confirm(uploadMessage)) {
                        _self.uploadFile(data.name);
                    }
                });

                htmlSelector.on("click", "button.btn-warning", function () {
                    var table = $(this).closest('table').DataTable();
                    var data = table.row($(this).parents("tr")).data();

                    var cancelMessage = "Está segur@ de cancelar la tarea de carga para este archivo?";
                    if (confirm(cancelMessage)) {
                        _self.cancelFile(data.name);
                    }
                });

                htmlSelector.on("click", "button.btn-danger", function () {
                    var table = $(this).closest('table').DataTable();
                    var data = table.row($(this).parents("tr")).data();

                    var deleteMessage = "¿Está segur@ que desea eliminar los datos? Recuerde que esta operación es irreversible.";
                    if (confirm(deleteMessage)) {
                        _self.deleteFile(data.name);
                    }
                });
            });
        };
    }

    // load filters
    (function () {
        var app = new DataManagerApp();
        app.updateTables();
    })()
});