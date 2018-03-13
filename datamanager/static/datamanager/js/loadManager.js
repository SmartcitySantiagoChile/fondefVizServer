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

        this.uploadFile = function (fileName, row) {
            var params = {
                fileName: fileName
            };
            $.post(Urls["datamanager:uploadData"](), params, function (data) {
                showMessage(data.status);
                if (data.status.code === 201) {
                    $(row).removeClass('danger');
                    $(row).removeClass('success');
                    $(row).addClass('warning');
                }
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
                    $("#" + id).DataTable(opts);
                }
                _self.activeButtonEvents();
            });
        };

        this.activeButtonEvents = function () {

            var buttons = [{
                selector: "button.btn-info",
                message: "Este proceso puede tomar tiempo ¿está seguro de iniciarlo?",
                action: _self.uploadFile
            }, {
                selector: "button.btn-danger",
                message: "¿Está seguro que desea eliminar los datos? esta operación es irreversible.",
                action: _self.deleteFile
            }, {
                selector: "button.btn-warning",
                message: "Está seguro de cancelar la tarea de carga para este archivo?",
                action: _self.cancelFile
            }];

            function activateEventButton(buttonInfo) {
                var tbody = $("tbody");
                tbody.off("click", buttonInfo.selector);
                tbody.on("click", buttonInfo.selector, function () {
                    var table = $(this).closest("table").DataTable();
                    var rowInstance = $(this).parents("tr");
                    var data = table.row(rowInstance).data();

                    if (confirm(buttonInfo.message)) {
                        buttonInfo.action(data.name, rowInstance);
                    }
                });
            }

            buttons.forEach(function(buttonInfo){
                activateEventButton(buttonInfo)
            });
        };
    }

    // load filters
    (function () {
        var app = new DataManagerApp();
        app.updateTables();

        /*
        setInterval(function(){
            app.updateTables();
        }, 1000 * 0);*/
    })()
});