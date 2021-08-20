"use strict";
$(document).ready(function () {
  function FromToApp() {
    let _self = this;
    let originSelected = new Set([]);
    let destinationSelected = new Set([]);

    let mapZoneInfoLegend = null;
    let mapLegend = null;

    let mapApp = null;

    let tableOpts = {
      language: {
        url: "//cdn.datatables.net/plug-ins/1.10.13/i18n/Spanish.json",
      },
      columns: [
        {title: "Etapa 1", data: "stage1"},
        {title: "Etapa 2", data: "stage2"},
        {title: "Etapa 3", data: "stage3"},
        {title: "Etapa 4", data: "stage4"},
        {title: "N° viajes", data: "expansionFactor", render: $.fn.dataTable.render.number(".", ",", 2)}
      ],
      order: [[4, "desc"]]
    };
    let _datatable = $("#tupleDetail").DataTable(tableOpts);

    // data given by server
    let data = null;

    this.getOriginZones = function () {
      return Array.from(originSelected);
    };

    this.getDestinationZones = function () {
      return Array.from(destinationSelected);
    };

    let printAmountOfData = function (data) {
      let tripQuantity = data.expansionFactor;
      let dataQuantity = data.docCount;
      document.getElementById("tripTotalNumberLabel").innerHTML = tripQuantity === 1 ? "viaje" : "viajes";
      document.getElementById("tripTotalNumberValue").innerHTML = Number(tripQuantity.toFixed(2)).toLocaleString();

      document.getElementById("dataTotalNumberLabel").innerHTML = dataQuantity === 1 ? "dato" : "datos";
      document.getElementById("dataTotalNumberValue").innerHTML = dataQuantity.toLocaleString();
    };

    this.setData = function (newData) {
      data = newData;
      printAmountOfData(newData);
    };

    this.updateTable = function () {
      console.log("updateTable method called!");
      _datatable.clear();
      _datatable.rows.add(data.strategies);
      _datatable.columns.adjust().draw();
    };

    let colors = {
      none: "#77847e",
      origin: "#fc8d59",
      destination: "#ffffbf",
      both: "#91bfdb"
    };

    let createZoneInfoLegend = function () {
      class MapZoneInfoLegend {
        onAdd(map) {
          let div = document.createElement('div');
          div.className = 'mapboxgl-ctrl info legend';
          div.id = 'mapZoneInfoLegend';
          return div;
        }

        update(zoneId) {
          zoneId = zoneId || '';
          let div = document.getElementById('mapZoneInfoLegend');
          div.innerHTML = '<h4>Zonificación 777: </h4>';
          div.innerHTML += '<b>Zona ' + zoneId + '</b>';
        }
      }

      return new MapZoneInfoLegend();
    };

    let createColorLengend = function () {
      class MapLegend {
        onAdd(map) {
          let div = document.createElement('div')
          div.className = 'mapboxgl-ctrl info legend';
          div.id = 'mapLegend';
          return div;
        }

        update() {
          let div = document.getElementById('mapLegend');
          div.innerHTML = '<h4>Leyenda: </h4>';
          let rows = [{
            label: 'Zonas no seleccionadas',
            color: colors.none
          }, {
            label: 'Zonas de origen',
            color: colors.origin
          }, {
            label: 'Zonas de destino',
            color: colors.destination
          }, {

            label: 'Zonas de origen y destino',
            color: colors.both
          }];
          rows.forEach(function (el) {
            div.innerHTML += "<i style='background:" + el.color + "'></i><b> " + el.label + "</b>";
            div.innerHTML += '<br />';
          });
        }
      }

      return new MapLegend();
    };

    this.loadLayers = function (readyFunction) {
      let hoveredFeature = null;
      let mapOpts = {
        hideMapLegend: true,
        hideZoneLegend: true,
        showMetroStations: false,
        showMacroZones: false,
        onClickZone: function (e) {
          let feature = e.features[0];
          let zoneId = feature.properties.id;
          let states = {origin: false, destination: false, both: false};
          if (originSelected.has(zoneId) && destinationSelected.has(zoneId)) {
            originSelected.delete(zoneId);
            destinationSelected.delete(zoneId);
          } else if (originSelected.has(zoneId) && !destinationSelected.has(zoneId)) {
            originSelected.delete(zoneId);
            destinationSelected.add(zoneId);
            states.destination = true;
          } else if (!originSelected.has(zoneId) && destinationSelected.has(zoneId)) {
            originSelected.add(zoneId);
            states.both = true;
          } else {
            originSelected.add(zoneId);
            states.origin = true;
          }
          mapApp.getMapInstance().setFeatureState({source: 'zones-source', id: feature.id}, states);
        },
        onMousemoveZone: function (e) {
          let feature = e.features[0];
          hoveredFeature = feature;
          let zoneId = feature.properties.id;
          mapZoneInfoLegend.update(zoneId);
          this.defaultOnMousemoveZone(e);
        },
        onMouseleaveZone: function (e) {
          hoveredFeature = null;
          mapZoneInfoLegend.update();
          this.defaultOnMouseleaveZone(e);
        },
        onLoad: (_mapInstance, _mapApp) => {
          _mapApp.loadLayers(() => {
            mapZoneInfoLegend = createColorLengend();
            _mapApp.getMapInstance().addControl(mapZoneInfoLegend, 'bottom-right');
            mapZoneInfoLegend.update();

            mapLegend = createZoneInfoLegend();
            _mapApp.getMapInstance().addControl(mapLegend, 'top-right');
            mapLegend.update();

            let zoneLayer = _mapApp.getZoneLayer();
            zoneLayer.paint['fill-color'] = [
              'case',
              ['boolean', ['feature-state', 'hover'], false], '#666',
              ['boolean', ['feature-state', 'origin'], false], colors.origin,
              ['boolean', ['feature-state', 'destination'], false], colors.destination,
              ['boolean', ['feature-state', 'both'], false], colors.both,
              colors.none
            ];
            _mapApp.setLayer(zoneLayer);

            readyFunction();
          });
        }
      };
      mapApp = new MapApp(mapOpts);
    };
  }

  function processData(data, app) {
    if (data.status) {
      return;
    }

    let rows = [];
    for (let firstStage in data.strategies) {
      for (let secondStage in data.strategies[firstStage]) {
        for (let thirdStage in data.strategies[firstStage][secondStage]) {
          for (let fourthStage in data.strategies[firstStage][secondStage][thirdStage]) {
            let expansionFactor = data.strategies[firstStage][secondStage][thirdStage][fourthStage];
            rows.push({
              stage1: firstStage,
              stage2: secondStage,
              stage3: thirdStage,
              stage4: fourthStage,
              expansionFactor: expansionFactor
            });
          }
        }
      }
    }

    data.strategies = rows;
    app.setData(data);
    app.updateTable();
  }

  // load filters
  (function () {
    loadAvailableDays(Urls["esapi:availableTripDays"]());
    loadRangeCalendar(Urls["esapi:availableTripDays"](), {});

    let app = new FromToApp();

    let afterCall = function (data, status) {
      if (status) {
        processData(data, app);
      }
    };
    let opts = {
      urlFilterData: Urls["esapi:tripStrategiesData"](),
      urlMultiRouteData: Urls["esapi:multiRouteData"](),
      afterCallData: afterCall,
      dataUrlParams: function () {
        return {
          originZones: app.getOriginZones(),
          destinationZones: app.getDestinationZones()
        }
      }
    };
    let manager = new FilterManager(opts);
    // load first time
    app.loadLayers(function () {
      manager.updateData();
    });
  })();
})
;