$(document).ready(function () {
  "use strict";

  function DataManagerApp() {
    const indexNames = ["Profile", "Speed", "Bip", "Odbyroute", "Trip", "Paymentfactor", "General", "stage"];
    const lowerIndexNames = indexNames.map(e => e.toLowerCase());

    let _datatableOpts = {
      lengthMenu: [[20, 50, 100, -1], [20, 50, 100, "Todos"]],
      language: {
        url: "//cdn.datatables.net/plug-ins/1.10.13/i18n/Spanish.json"
      },
      dom: 'Blfrtip',
      order: [[0, 'desc']],
      autoWidth: true,
      buttons: [
        {
          extend: 'csvHtml5',
          text: 'Guardar como CSV',
          className: "buttons-csv buttons-html5 btn btn-success",
        },
        {
          extend: 'excelHtml5',
          text: 'Guardar como Excel',
          className: "buttons-excel buttons-html5 btn btn-success",

        },
      ],
      createdRow: function (row, data) {
        addColorToRow(data, row);
      }
    };

    let addColorToRow = function (data, row) {
      lowerIndexNames.forEach((index_name, index_position) => {
        let cellReference = $(row).find(`td:eq(${index_position + 2})`);
        let diff = 0;
        if (data[index_name + '_index'] !== 0) {
          diff = data[index_name + '_file'] / data[index_name + '_index'];
        }

        if (diff === 1) {
          cellReference.css({
            'background-color': '#d4edda',
            'border-color': '#c3e6cb',
            'color': '#155724'
          });
        } else if (diff > 1) {
          cellReference.css({
            'background-color': '#f8d7da',
            'border-color': '#f5c6cb',
            'color': '#721c24'
          });
        } else {
          cellReference.css({
            'background-color': '#fff3cd',
            'border-color': '#ffeeba',
            'color': '#856404'
          });
        }
      });

      let authorityIndexId = JSON.parse(data['authority_period_index_version']);
      let authorityColumnIndex = 10;
      let cellReference = $(row).find(`td:eq(${authorityColumnIndex})`);
      if (authorityIndexId.length === 1) {
        let diffAuthorityPeriodId = data['authority_period_version'] === authorityIndexId[0].toString();
        if (diffAuthorityPeriodId) {
          cellReference.css({
            'background-color': '#d4edda',
            'border-color': '#c3e6cb',
            'color': '#155724'
          });
        } else {
          cellReference.css({
            'background-color': '#fff3cd',
            'border-color': '#ffeeba',
            'color': '#856404'
          });
        }
      } else if (authorityIndexId.length === 0) {
        cellReference.css({
          'background-color': '#f8d7da',
          'border-color': '#f5c6cb',
          'color': '#721c24'
        });
      } else {
        cellReference.css({
          'background-color': '#fff3cd',
          'border-color': '#ffeeba',
          'color': '#856404'
        });
      }
    };

    const daysDict = {
      0: 'Domingo',
      1: 'Lunes',
      2: 'Martes',
      3: 'Miércoles',
      4: 'Jueves',
      5: 'Viernes',
      6: 'Sábado'
    };

    this.updateTables = function () {
      $.get(Urls["consistencychecker:getConsistencyData"](), function (data) {
        let dictFiles = JSON.parse(data.response);
        let files = dictFiles.map(e => {
          let row = e.fields;
          let date = new Date(row.date);
          date = new Date(date.getTime() + date.getTimezoneOffset() * 60000);
          row['day'] = daysDict[date.getDay()];
          return row;
        });
        let columns = [
          {
            title: 'Fecha',
            data: 'date'
          },
          {
            title: 'Día de la semana',
            data: 'day'
          },
        ];

        for (let index in lowerIndexNames) {
          let lower_index = lowerIndexNames[index].toLowerCase();
          columns.push(
            {
              title: lowerIndexNames[index],
              data: null,
              render: function (data) {
                let addDot = e => e.replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1.');
                return `${addDot(data[lower_index + "_file"].toString())}/${addDot(data[lower_index + "_index"].toString())}`;
              }

            }
          )
        }
        columns.push({
          title: 'Versión de Periodo TS',
          data: null,
          render: function (data) {
            let authorityIndexId = JSON.parse(data['authority_period_index_version']);
            if (authorityIndexId.length === 1) {
              authorityIndexId = authorityIndexId[0];
            } else if (authorityIndexId.length === 0) {
              authorityIndexId = -1
            }
            return data['authority_period_version'] + "/" + authorityIndexId;
          }
        })
        let opts = $.extend({data: files, columns: columns}, _datatableOpts);
        $("#fechas-id").DataTable(opts);
      });
    };
  }

  // load filters
  (function () {
    let app = new DataManagerApp();
    app.updateTables();
  })();
});