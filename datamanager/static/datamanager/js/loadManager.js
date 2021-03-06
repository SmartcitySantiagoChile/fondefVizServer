$(document).ready(function () {
    "use strict";

    function DataManagerApp() {
        var _self = this;
        var _datatableOpts = {
            lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "Todos"]],
            language: {
                url: "//cdn.datatables.net/plug-ins/1.10.13/i18n/Spanish.json"
            },
            searching: false,
            columns: [
                {
                    title: "Archivo",
                    data: "name",
                    searchable: true,
                    render: function (data, type, row, meta) {
                        if (type === "sort") {
                            return (new Date(data.split(".")[0])).getTime();
                        }
                        return data;
                    }
                },
                {
                    title: "Última modificación", data: "lastModified", searchable: true,
                    render: function (data, type, row, meta) {
                        if (type === "sort") {
                            return (new Date(data)).getTime();
                        }
                        return (new Date(data)).toLocaleString();
                    }
                },
                {
                    title: "Registros en archivo",
                    data: "lines",
                    searchable: true,
                    render: $.fn.dataTable.render.number(".", ",")
                },
                {
                    title: "Registros en plataforma",
                    data: "docNumber",
                    searchable: true,
                    render: $.fn.dataTable.render.number(".", ",")
                },
                {
                    title: "Diferencia",
                    searchable: true,
                    render: function (data, type, full, meta) {
                        if (type === "display") {
                            return $.fn.dataTable.render.number(".", ",").display(full.lines - full.docNumber);
                        }
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
            order: [[0, "desc"]],
            createdRow: function (row, data, index) {
                addColorToRow(data, row);
            }
        };

        var addColorToRow = function (data, row) {
            $(row).removeClass("danger warning success");
            if (data.lines !== data.docNumber) {
                $(row).addClass("danger");
            } else {
                $(row).addClass("success");
            }
            if (data.lastExecution !== null) {
                if (["enqueued", "running"].indexOf(data.lastExecution.status) >= 0) {
                    $(row).removeClass("danger success");
                    $(row).addClass("warning");
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
            var LoadingOrReadyToLoad = false;
            var disableJobInfoButton = false;

            var uploadButtonName = "Cargar datos";
            var deleteButtonName = "Eliminar";
            var cancelButtonName = "Cancelar carga";
            var infoButtonName = "<i class='fa fa-info'></i>";

            if (data.lastExecution !== null) {
                if (data.lastExecution.status === "running") {
                    infoButtonName = "<i class='fa fa-refresh fa-pulse'></i> " + infoButtonName;
                    LoadingOrReadyToLoad = true;
                } else if (data.lastExecution.status === "enqueued") {
                    infoButtonName = "<i class='fa fa-spinner fa-pulse'></i> " + infoButtonName;
                    LoadingOrReadyToLoad = true;
                } else if (data.lastExecution.status === "failed") {
                    infoButtonName = "<i class='fa fa-warning'></i> " + infoButtonName;
                }
            } else {
                disableJobInfoButton = true;
            }

            if (data.line === data.docNumber || LoadingOrReadyToLoad) {
                disableUploadButton = true;
            }
            if (!LoadingOrReadyToLoad) {
                disableCancelButton = true;
            }
            if (data.docNumber === 0 || LoadingOrReadyToLoad) {
                disableDeleteButton = true;
            }

            var uploadButton = createHTMLButton(uploadButtonName, "info", disableUploadButton);
            var deleteButton = createHTMLButton(deleteButtonName, "danger", disableDeleteButton);
            var cancelButton = createHTMLButton(cancelButtonName, "warning", disableCancelButton);
            var jobInfoButton = createHTMLButton(infoButtonName, "default", disableJobInfoButton);

            return jobInfoButton + uploadButton + cancelButton + deleteButton;
        };

        this.uploadFile = function (fileName, row) {
            var params = {
                fileName: fileName
            };
            $.post(Urls["datamanager:uploadData"](), params, function (data) {
                showMessage(data.status);
                if (data.status.code === 201) {
                    addColorToRow(data.data, row);
                    var table = row.closest("table").DataTable();
                    table.row(row).data(data.data).invalidate("data");

                    // ask 3 seconds after because there are small file that upload quickly
                    setTimeout(_self.updateToLatestChanges, 3000);
                    setTimeout(_self.updateToLatestChanges, 6000);
                }
            });
        };

        this.deleteFile = function (fileName, row) {
            var params = {
                fileName: fileName
            };
            $.post(Urls["datamanager:deleteData"](), params, function (data) {
                showMessage(data.status);
                if (data.status.code === 202 || data.status.code === 204) {
                    var table = row.closest("table").DataTable();
                    var currentData = table.row(row).data();
                    currentData.docNumber = currentData.docNumber - data.data.deletedDocNumber;
                    addColorToRow(currentData, row);
                    table.row(row).data(currentData).invalidate("data");
                }
            });
        };

        this.cancelFile = function (fileName, row) {
            var params = {
                fileName: fileName
            };
            $.post(Urls["datamanager:cancelData"](), params, function (data) {
                showMessage(data.status);
                if (data.status.code === 203) {
                    addColorToRow(data.data, row);
                    var table = row.closest("table").DataTable();
                    table.row(row).data(data.data).invalidate('data');
                }
            });
        };

        this.updateTables = function () {
            const filters = JSON.parse(document.getElementById('data-filter').textContent);
            var params = {
                filters: filters
            };
            $.get(Urls["datamanager:getLoadFileData"](), params, function (data) {
                var dictFiles = data.routeDictFiles;
                for (var key in dictFiles) {
                    if (dictFiles.hasOwnProperty(key)) {
                        var files = dictFiles[key];
                        var opts = $.extend({data: files}, _datatableOpts);
                        var id = key + "Table";
                        $("#" + id).DataTable(opts);
                    }
                }
                _self.activeButtonEvents();
            });
        };

        this.activeButtonEvents = function () {

            var buttons = [{
                selector: "button.btn-info",
                modalTitle: function (data) {
                    return "Cargar archivo " + data.name;
                },
                modalBody: function () {
                    return "Este proceso puede tomar tiempo ¿está seguro de iniciarlo?";
                },
                modalId: "modal",
                action: _self.uploadFile
            }, {
                selector: "button.btn-danger",
                modalTitle: function (data) {
                    return "Eliminar datos de archivo " + data.name;
                },
                modalBody: function () {
                    return "¿Está seguro que desea eliminar los datos en la plataforma? esta operación es irreversible.";
                },
                modalId: "modal",
                action: _self.deleteFile
            }, {
                selector: "button.btn-warning",
                modalTitle: function (data) {
                    return "Cancelar carga de archivo " + data.name;
                },
                modalBody: function () {
                    return "Está seguro de cancelar la tarea de carga para este archivo?";
                },
                modalId: "modal",
                action: _self.cancelFile
            }, {
                selector: "button.btn-default",
                modalTitle: function () {
                    return "Información de última ejecución de carga de datos";
                },
                modalBody: function (data) {
                    var exec = data.lastExecution;
                    var enqueuedTimestamp = (new Date(exec.enqueueTimestamp)).toLocaleString();
                    var executionStart = exec.executionStart !== null ? (new Date(exec.executionStart)).toLocaleString() : "";
                    var executionEnd = exec.executionEnd !== null ? (new Date(exec.executionEnd)).toLocaleString() : "";
                    var deletedAt = exec.deletedAt !== null ? (new Date(exec.deletedAt)).toLocaleString() : "";

                    function htmlRow(id, label, value) {
                        return "<form class='form-horizontal'><div class='form-group'>" +
                            "<label class='control-label col-sm-5' for='" + id + "'>" + label + "</label><div class='col-sm-7'>" +
                            "<p class='form-control-static'>" + value + "</p></div></div></form>";
                    }

                    var rows = [
                        htmlRow("11", "Estado:", exec.statusName),
                        htmlRow("12", "Envío de tarea:", enqueuedTimestamp),
                        htmlRow("13", "Inicio de tarea:", executionStart),
                        htmlRow("14", "Fin de tarea:", executionEnd),
                        htmlRow("15", "Eliminado:", deletedAt)
                    ];

                    if (exec.error !== "") {
                        rows.push(htmlRow("16", "Error:", exec.error));
                    }

                    return rows.join("");
                },
                modalId: "modal",
                action: function () {
                }
            }];

            function activateEventButton(buttonInfo) {
                var tbody = $("tbody");
                tbody.off("click", buttonInfo.selector);
                tbody.on("click", buttonInfo.selector, function () {
                    var table = $(this).closest("table").DataTable();
                    var rowInstance = $(this).parents("tr");
                    var data = table.row(rowInstance).data();

                    var modal = $("#" + buttonInfo.modalId);
                    modal.off('show.bs.modal');
                    modal.on('show.bs.modal', function () {
                        modal.find('.modal-title').html(buttonInfo.modalTitle(data));
                        modal.find('.modal-body').html(buttonInfo.modalBody(data));
                        // accept event
                        modal.off("click", "button.btn-info");
                        modal.on("click", "button.btn-info", function () {
                            buttonInfo.action(data.name, rowInstance);
                        });
                    });
                    modal.modal("show");
                });
            }

            buttons.forEach(function (buttonInfo) {
                activateEventButton(buttonInfo);
            });
        };

        this.updateToLatestChanges = function () {
            $.get(Urls["datamanager:latestJobChanges"](), function (data) {
                data.changes.forEach(function (rowData) {
                    var tableId = rowData.name.split(".")[1] + "Table";
                    var table = $("#" + tableId).DataTable();
                    var index = table.rows().eq(0).filter(function (rowIdx) {
                        return table.cell(rowIdx, 0).data() === rowData.name;
                    });

                    table.row(index).data(rowData).invalidate("data");
                    addColorToRow(rowData, table.rows(index).nodes());
                });
            });
        };
    }

    // load filters
    (function () {
        var app = new DataManagerApp();
        app.updateTables();

        setInterval(function () {
            app.updateToLatestChanges();
        }, 1000 * 60);
    })();
});