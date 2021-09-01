$(document).ready(function () {
  let colors = ["#dfdfdf", "#ff0000", "#ff7f00", "#ffff00", "#00ff00", "#007f00", "#0000ff"];
  let labels = ["Sin Datos", " 0 - 15 k/h", "15 - 19 k/h", "19 - 21 k/h", "21 - 23 k/h", "23 - 30 k/h", " > 30 k/h"];

  let mapOpts = {
    mapId: 'mapid',
    scaleControl: true,
    zoomControl: false,
    tileLayer: 'dark',
    onLoad: (_mapInstance) => {
      class SpeedLegend {
        onAdd(map) {
          let div = document.createElement('div');
          div.className = 'mapboxgl-ctrl info legend';
          div.id = 'speedLegend';
          div.innerHTML = "Velocidad<br />";
          // loop through our density intervals and generate a label with a colored square for each interval
          for (let i = 0; i < colors.length; i++) {
            div.innerHTML += "<i style='background:" + colors[i] + "'></i> " + labels[i];
            div.innerHTML += "<br />";
          }
          return div;
        }

        onRemove() {
          // nothing
        }
      }

      _mapInstance.addControl(new SpeedLegend(), 'bottom-right');

      _mapInstance.addSource('shapes-source', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: []
        }
      });
      _mapInstance.addSource('bound-points-source', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: []
        }
      });

      let shapesLayer = {
        id: 'shapes-layer',
        source: 'shapes-source',
        type: 'line',
        layout: {
          'line-join': 'round',
          'line-cap': 'round'
        },
        paint: {
          'line-color': ['get', 'color'],
          'line-width': 3
        }
      }

      let boundPointsLayer = {
        id: 'bound-points-layer',
        source: 'bound-points-source',
        type: 'circle',
        paint: {
          'circle-radius': 5,
          'circle-color': '#28DCF2'
        }
      }

      _mapInstance.addLayer(shapesLayer);
      _mapInstance.addLayer(boundPointsLayer);
      let img = '/static/trip/img/double-arrow.png';
      _mapInstance.loadImage(img, (err, image) => {
        if (err) {
          console.log(err);
          return;
        }
        _mapInstance.addImage('double-arrow', image, {sdf: true});
        _mapInstance.addLayer({
          'id': 'shape-arrow-layer',
          'type': 'symbol',
          'source': 'shapes-source',
          'layout': {
            'symbol-placement': 'line',
            'symbol-spacing': 30,
            'icon-allow-overlap': true,
            'icon-ignore-placement': true,
            'icon-image': 'double-arrow',
            'icon-size': 0.4
          },
          paint: {
            'icon-color': ['get', 'color']
          }
        });
      });
    }
  };
  let _mapApp = new MapApp(mapOpts);

  let periods = [
    "00:00", "00:30", "01:00", "01:30", "02:00", "02:30", "03:00", "03:30", "04:00", "04:30", "05:00", "05:30", "06:00", "06:30", "07:00", "07:30", "08:00", "08:30", "09:00", "09:30",
    "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30",
    "20:00", "20:30", "21:00", "21:30", "22:00", "22:30", "23:00", "23:30", "00:00"
  ];

  function showSegment(section, dataSource) {
    let routePoints = dataSource.route.points.map(function (el) {
      return [el[1], el[0]];
    });
    let valuesRoute = dataSource.speed;
    let segments = {
      type: 'FeatureCollection',
      features: []
    };
    let boundPoints = {
      type: 'FeatureCollection',
      features: []
    };

    dataSource.route.start_end.forEach(function (elem, index) {
      let start = elem[0];
      let end = elem[1];
      let segmentPoints = routePoints.slice(start, end + 1);
      let segmentColor = colors[valuesRoute[index]];

      let lineString = {
        type: 'Feature',
        geometry: {
          type: 'LineString',
          coordinates: segmentPoints
        },
        properties: {
          color: segmentColor
        }
      };
      segments.features.push(lineString);

      if (index === section) {
        [start, end].forEach(el => {
          boundPoints.features.push({
            type: 'Feature',
            geometry: {
              type: 'Point',
              coordinates: routePoints[el]
            }
          });
        })
      }
    });
    _mapApp.getMapInstance().getSource('shapes-source').setData(segments);
    _mapApp.getMapInstance().getSource('bound-points-source').setData(boundPoints);
    _mapApp.fitBound(['bound-points-source']);
  }

  function RankingApp() {
    let _self = this;
    let _datatable = $("#tupleDetail").DataTable({
      lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "Todos"]],
      language: {
        url: "//cdn.datatables.net/plug-ins/1.10.13/i18n/Spanish.json"
      },
      columns: [
        {title: "Servicio", data: "route", searchable: true},
        {title: "Tramo", data: "section", className: "text-right", searchable: false},
        {
          title: "Periodo", data: "period", searchable: true,
          render: function (data) {
            return periods[data] + " " + periods[data + 1];
          }
        },
        {
          title: "Velocidad [km/h]", data: "speed", className: "text-right", searchable: false,
          render: function (data) {
            return data.toFixed(1);
          }
        },
        {
          title: "Tiempo [s]", data: "time", className: "text-right", searchable: false,
          render: function (data) {
            return data.toFixed(1);
          }
        },
        {
          title: "Distancia [m]", data: "distance", className: "text-right", searchable: false,
          render: function (data) {
            return data.toFixed(1);
          }
        },
        {title: "# obs", data: "n_obs", className: "text-right", searchable: false}
      ],
      order: [[3, "asc"]]
    });

    // action when user clicks on a row
    $("#tupleDetail tbody").on("click", "tr", function () {
      let data = _datatable.row(this).data();
      if (data !== undefined) {
        _datatable.$("tr.success").removeClass("success").removeClass("dark");
        $(this).addClass("success").addClass("dark");

        _self.drawSegment(data.route, data.period, data.section);
      }
    });

    this.updateRows = function (data) {
      _datatable.clear();
      _datatable.rows.add(data);
      _datatable.columns.adjust().draw();
      $(_datatable.row(0).node()).addClass("success").addClass("dark");

      let firstRow = _datatable.row(0).data();
      _self.drawSegment(firstRow.route, firstRow.period, firstRow.section);
    };

    this.drawSegment = function (route, period, section) {
      let urlKey = window.location.pathname;
      let dates = JSON.parse(window.localStorage.getItem(urlKey + "dayFilter")).sort();
      dates = groupByDates(dates);
      dates = dates.map(function (date_range) {
        if (date_range.length === 1) {
          return [date_range[0][0]]
        } else {
          return [date_range[0][0], date_range[date_range.length - 1][0]];
        }
      });
      let dayType = $("#dayTypeFilter").val();

      let params = {
        authRoute: route,
        dates: JSON.stringify(dates),
        period: period
      };
      if (dayType) {
        params.dayType = dayType;
      }

      $.getJSON(Urls["esapi:speedByRoute"](), params, function (response) {
        return showSegment(section, response);
      });
    }

    /**
     * Clear information in bar chart, datatables and map.
     */
    this.clearDisplayData = function () {
      $("#mapid").hide();
      _datatable.clear().draw();
    };
  }

  function processData(dataSource, app) {
    $("#mapid").show();
    let data = dataSource.data;
    app.updateRows(data);
  }

  // load filters
  (function () {
    loadAvailableDays(Urls["esapi:availableSpeedDays"]());
    loadRangeCalendar(Urls["esapi:availableSpeedDays"](), {});

    let app = new RankingApp();

    let afterCall = function (data, status) {
      if (status) {
        processData(data, app);
      } else{
        app.clearDisplayData();
      }
    };
    let opts = {
      urlFilterData: Urls["esapi:rankingData"](),
      urlRouteData: Urls["esapi:availableSpeedRoutes"](),
      afterCallData: afterCall
    };
    new FilterManager(opts);
  })();
});