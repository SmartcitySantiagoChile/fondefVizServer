"use strict";
$(document).ready(function () {
    if ($("#availableDays").length) {
        loadAvailableDays(Urls["awsbackup:availableDays"](bucketName));
    }

    $.getJSON(Urls["awsbackup:activeDownloadLink"](), function (activeDownloadLinkData) {
        var tableId = "#dataTableId";
        $(tableId).DataTable({
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
                        if (activeDownloadLinkData.hasOwnProperty(row[0])) {
                            return "<a href='" + activeDownloadLinkData[row[0]].url + "' class='btn btn-success btn-xs'><i class='fas fa-file'></i> Descargar (válido hasta " + (new Date(activeDownloadLinkData[row[0]].expire_at)).toLocaleString() + ")</a>";
                        }
                        return "<button type='button' class='btn btn-warning btn-xs'><i class='fas fa-file'></i> Crear link de descarga</button>";
                    },
                    createdCell: function (td, cellData, rowData, row, col) {
                        $(td).find("button.btn-warning").click(function () {
                            var datatable = $(tableId).DataTable();
                            var row = $(this).closest("tr");
                            var data = datatable.row(row).data();
                            var filename = data[0];

                            var currentText = $(this).html();
                            var spinner = "<i class='fas fa-refresh fa-pulse'></i>";
                            $(this).html(spinner + " " + currentText);
                            $.post(Urls["awsbackup:createDownloadLink"](), {
                                bucket_name: bucketName,
                                filename: filename
                            }, function (result) {
                                activeDownloadLinkData[filename] = result;
                                datatable.row(row).data(data).invalidate("data");
                            }).always(function () {
                                $(this).html(currentText);
                            });
                        });
                    }
                }
            ],
            order: [[0, "desc"]]
        });
    });
});