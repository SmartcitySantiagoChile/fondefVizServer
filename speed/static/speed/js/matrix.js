"use strict";

$(document).ready(function () {

  let periods = [
    "00:00", "00:30", "01:00", "01:30", "02:00", "02:30", "03:00", "03:30", "04:00", "04:30", "05:00", "05:30",
    "06:00", "06:30", "07:00", "07:30", "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
    "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30",
    "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00", "21:30", "22:00", "22:30", "23:00", "23:30"
  ];

  function DrawSegmentsApp(colorScale, labels) {
    let _self = this;
    let colors = colorScale;

    this.showSpeedLegend = (show, content) => {
      let speedLegend = $("#speedLegend");
      if (show) {
        speedLegend.css({'visibility': 'visible'});
        if (content !== undefined) {
          speedLegend.html(content);
        }
      } else {
        speedLegend.css({'visibility': 'hidden'});
      }
    };

    let mapOpts = {
      mapId: 'mapid',
      scaleControl: true,
      zoomControl: true,
      tileLayer: 'dark',
      onLoad: (_mapInstance) => {
        class SelectSegmentControl {
          onAdd(map) {
            let div = document.createElement('div');
            div.className = 'mapboxgl-ctrl info legend';
            div.id = 'button_legend';
            div.innerHTML = "<input id='chooseRangeButton' type='checkbox' class='form-check-input' " +
              "> <label class='form-check-label' for='chooseRangeButton'> Selección por tramos</label> ";
            return div;
          }

          onRemove() {
            // nothing
          }
        }

        _mapInstance.addControl(new SelectSegmentControl(), 'top-left');

        class MapLegend {
          onAdd(map) {
            let div = document.createElement('div');
            div.className = 'mapboxgl-ctrl info legend';
            div.id = "map_legend";
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

        _mapInstance.addControl(new MapLegend(), 'bottom-right');

        class SpeedLegend {
          onAdd(map) {
            let div = document.createElement('div');
            div.className = 'mapboxgl-ctrl info legend';
            div.id = "speedLegend";
            div.class = "d-flex justify-content-center";
            div.style.visibility = "hidden";
            return div;
          }

          onRemove() {
            // nothing
          }
        }

        _mapInstance.addControl(new SpeedLegend(), 'top-right');

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
            'line-color': [
              'case',
              ['boolean', ['feature-state', 'selected'], false], '#28DCF2',
              ['get', 'color']
            ],
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
              'icon-color': [
                'case',
                ['boolean', ['feature-state', 'selected'], false], '#28DCF2',
                ['get', 'color']
              ]
            }
          });
        });

        let openSegmentPopup = function (feature) {
          let popUpDescription = "<p>";
          popUpDescription = "Velocidad: " + feature.properties.formattedSpeed + " km/h<br/>";
          popUpDescription += "N° obs: " + feature.properties.obsNumber + "<br/>";
          popUpDescription += "Segmento de 500m: " + feature.properties.segmentIndex;
          popUpDescription += "</p>";
          new mapboxgl.Popup({closeOnClick: true}).setLngLat(feature.geometry.coordinates[0]).setHTML(popUpDescription).addTo(_mapInstance);
        };

        let mouseenter = () => {
          _mapInstance.getCanvas().style.cursor = 'pointer';
        };
        let mouseleave = () => {
          _mapInstance.getCanvas().style.cursor = '';
        };
        let click = e => {
          let feature = e.features[0];
          openSegmentPopup(feature);
        };
        _mapInstance.on('mouseenter', 'shapes-layer', mouseenter);
        _mapInstance.on('mouseleave', 'shapes-layer', mouseleave);
        _mapInstance.on('click', 'shapes-layer', click);

        let aggregateSpeedMouseenter = () => {
          _mapInstance.getCanvas().style.cursor = 'pointer';
        };
        let aggregateSpeedMouseleave = () => {
          _mapInstance.getCanvas().style.cursor = '';
        };

        let aggregateSpeedClick = e => {
          let feature = e.features[0];

          selectedFeatures.push(feature);
          _mapInstance.setFeatureState({source: 'shapes-source', id: feature.id}, {selected: true});

          if (selectedFeatures.length === 2) {
            // calculate speed info
            _self.calculateAggregatedSpeed();
          } else if (selectedFeatures.length > 2) {
            _self.showSpeedLegend(false);
            // clean previous
            let features = _mapInstance.getSource('shapes-source')._data.features;
            features.forEach(feature => {
              _mapInstance.setFeatureState({source: 'shapes-source', id: feature.id}, {selected: false});
            });

            selectedFeatures = [feature];
            _mapInstance.setFeatureState({source: 'shapes-source', id: feature.id}, {selected: true});
          }
        };

        $('#chooseRangeButton').on("change", function () {
          let checkboxValue = $("#chooseRangeButton").prop('checked');
          if (checkboxValue) {
            _mapInstance.off('mouseenter', 'shapes-layer', mouseenter);
            _mapInstance.off('mouseleave', 'shapes-layer', mouseleave);
            _mapInstance.off('click', 'shapes-layer', click);

            _mapInstance.on('mouseenter', 'shapes-layer', aggregateSpeedMouseenter);
            _mapInstance.on('mouseleave', 'shapes-layer', aggregateSpeedMouseleave);
            _mapInstance.on('click', 'shapes-layer', aggregateSpeedClick);
          } else {
            _self.showSpeedLegend(false);
            let features = _mapInstance.getSource('shapes-source')._data.features;
            features.forEach(feature => {
              _mapInstance.setFeatureState({source: 'shapes-source', id: feature.id}, {selected: false});
            });

            _mapInstance.off('mouseenter', 'shapes-layer', aggregateSpeedMouseenter);
            _mapInstance.off('mouseleave', 'shapes-layer', aggregateSpeedMouseleave);
            _mapInstance.off('click', 'shapes-layer', aggregateSpeedClick);

            _mapInstance.on('mouseenter', 'shapes-layer', mouseenter);
            _mapInstance.on('mouseleave', 'shapes-layer', mouseleave);
            _mapInstance.on('click', 'shapes-layer', click);
          }
        });
      }
    };
    let _mapApp = new MapApp(mapOpts);

    let selectedFeatures = [];
    this.calculateAggregatedSpeed = () => {
      let checkboxValue = $("#chooseRangeButton").prop('checked');
      if (selectedFeatures.length < 2 || !checkboxValue) {
        return;
      }
      let firstIndex = Math.min(selectedFeatures[0].id, selectedFeatures[1].id);
      let secondIndex = Math.max(selectedFeatures[0].id, selectedFeatures[1].id);
      let features = _mapApp.getMapInstance().getSource('shapes-source')._data.features;

      let accumulateDistance = 0;
      let accumulateTime = 0;
      features.forEach(feature => {
        if (firstIndex <= feature.id && feature.id <= secondIndex) {
          _mapApp.getMapInstance().setFeatureState({source: 'shapes-source', id: feature.id}, {selected: true});
          accumulateTime += feature.properties.time;
          accumulateDistance += feature.properties.distance;
        }
      });

      let speedInfo = (3.6 * (accumulateDistance / accumulateTime)).toFixed(2).toString().replace(".", ",");
      let speedLegendInfo = `Velocidad entre los tramos ${firstIndex} y ${secondIndex}: <br>  <b> ${speedInfo} km/h </b>`;
      _self.showSpeedLegend(true, speedLegendInfo)
    };

    /* to draw on map */
    let startEndSegments = null;
    let routePoints = null;
    let lastRoute = null;
    let lastValuesRoute = null;

    this.highlightSegment = function (segmentId) {
      let startIndex = startEndSegments[segmentId][0];
      let endIndex = startEndSegments[segmentId][1];

      let boundPointsSource = {
        type: 'FeatureCollection',
        features: []
      };

      routePoints.forEach(function (el, i) {
        if ([startIndex, endIndex].includes(i)) {
          boundPointsSource.features.push({
            type: 'Feature',
            geometry: {
              type: 'Point',
              coordinates: el
            }
          });
        }
      });

      _mapApp.getMapInstance().getSource('bound-points-source').setData(boundPointsSource);
      _mapApp.fitBound(['bound-points-source']);
    };

    this.drawRoute = function (route, valuesRoute) {
      lastRoute = route;
      lastValuesRoute = valuesRoute;
      /* update routes and segments */
      startEndSegments = route.start_end;
      routePoints = route.points.map(function (el) {
        return [el[1], el[0]];
      });
      /* create segments with color */
      let segments = {
        type: 'FeatureCollection',
        features: []
      }

      route.start_end.forEach(function (elem, i) {
        let start = elem[0];
        let end = elem[1];
        let segmentPoints = routePoints.slice(start, end + 1);
        let segmentColor = colors[valuesRoute[i][0]];
        let speed = valuesRoute[i][1];
        let obsNumber = valuesRoute[i][2];
        let distance = valuesRoute[i][3];
        let time = valuesRoute[i][4];
        let lineString = {
          type: 'Feature',
          geometry: {
            type: 'LineString',
            coordinates: segmentPoints
          },
          properties: {
            color: segmentColor,
            speed: speed,
            formattedSpeed: speed.toFixed(2).toString().replace(".", ","),
            obsNumber: obsNumber,
            segmentIndex: i,
            distance: distance,
            time: time
          },
          id: i
        };
        segments.features.push(lineString);
      });

      _mapApp.getMapInstance().getSource('shapes-source').setData(segments);
      _mapApp.fitBound(['shapes-source']);
      _self.calculateAggregatedSpeed();
    };
  }

  function MatrixApp() {
    let _self = this;

    let mChart = echarts.init(document.getElementById("main"));
    let matrix = null;
    let route = null;

    let velRange = ["Sin Datos", " < 5 km/h", "5 - 7,5 km/h", "7,5 - 10 km/h", "10 - 15 km/h", "15 - 20 km/h", "20 - 25 km/h", "25 - 30 km/h", " > 30 km/h"];
    let colors = ["#dfdfdf", "#a100f2", "#ef00d3", "#ff0000", "#ff8000", "#ffff00", "#01df01", "#088a08", "#045fb4"];

    let drawSegmentApp = new DrawSegmentsApp(colors, velRange);

    let opts = {
      tooltip: {
        position: "top",
        formatter: function (obj) {
          let startHour = periods[obj.data[0]];
          let endHour = periods[(obj.data[0] + 1) % periods.length];
          let segment = obj.data[1];
          let speed = ((matrix[obj.data[0]][obj.data[1]][1] < 0) ? "No fue posible calcular" : matrix[obj.data[0]][obj.data[1]][1].toFixed(1));
          let obsNumber = matrix[obj.data[0]][obj.data[1]][2];
          return "Horario: entre " + startHour + " y " + endHour + "<br/>" + "Segmento: " + segment + "<br/>" + "Velocidad: " + speed + " km/h" + "<br/># de observaciones: " + obsNumber;
        }
      },
      animation: false,
      grid: {
        left: "60",
        bottom: "90",
        right: "30"
      },
      xAxis: {
        type: "category",
        data: periods,
        splitArea: {
          show: true
        },
        axisLabel: {
          rotate: 90,
          interval: 1
        },
        name: "Período de media hora",
        nameLocation: "center",
        nameGap: 50
      },
      yAxis: {
        type: "category",
        data: [],
        splitArea: {
          show: true
        },
        name: "Tramos de 500 metros",
        nameLocation: "center",
        nameGap: 40
      },
      visualMap: {
        min: 0,
        max: 6,
        type: "piecewise",
        calculable: true,
        orient: "horizontal",
        right: "5%",
        top: "top",
        pieces: [
          {min: 7.5, max: 8.5, label: velRange[8]},
          {min: 6.5, max: 7.5, label: velRange[7]},
          {min: 5.5, max: 6.5, label: velRange[6]},
          {min: 4.5, max: 5.5, label: velRange[5]},
          {min: 3.5, max: 4.5, label: velRange[4]},
          {min: 2.5, max: 3.5, label: velRange[3]},
          {min: 1.5, max: 2.5, label: velRange[2]},
          {min: 0.5, max: 1.5, label: velRange[1]},
          {max: 0.5, label: velRange[0]}
        ],
        inRange: {
          color: colors
        }
      },
      series: [{
        name: "Velocidad",
        type: "heatmap",
        data: [],
        label: {
          normal: {
            show: false
          }
        },
        itemStyle: {
          emphasis: {
            shadowBlur: 10,
            shadowColor: "rgba(0, 0, 0, 0.5)"
          }
        }
      }],
      toolbox: {
        left: "center",
        bottom: "bottom",
        show: true,
        feature: {
          mark: {show: false},
          restore: {show: false, title: "restaurar"},
          saveAsImage: {show: true, title: "Guardar imagen", name: "changeme"}
        }
      }
    };

    mChart.on("click", function (params) {
      if ((params.componentType !== "series") || (params.seriesType !== "heatmap") ||
        (params.seriesIndex !== 0) || (params.seriesName !== "Velocidad")) {
        return;
      }
      let periodId = params.value[0];
      let segmentId = params.value[1];

      // set slider to period clicked
      let slider = $("#filterHourRange").data("ionRangeSlider");
      slider.update({from: periodId});

      drawSegmentApp.drawRoute(route, matrix[periodId]);
      drawSegmentApp.highlightSegment(segmentId);
    });

    this.showLoadingAnimationCharts = function () {
      mChart.showLoading(null, {text: "Cargando..."});
    };

    this.hideLoadingAnimationCharts = function () {
      mChart.hideLoading();
    };

    this.resizeChart = function () {
      mChart.resize();
    };

    this.setMatrix = function (newMatrix) {
      matrix = newMatrix;
    };
    this.setRoute = function (newRoute) {
      route = newRoute;
      _self.updateLabel(route.name);
    };

    this.updateChart = function (data, segments) {
      opts.yAxis.data = segments;
      opts.series[0].data = data;
      mChart.setOption(opts, {merge: false});
      let slider = $("#filterHourRange").data("ionRangeSlider");
      drawSegmentApp.drawRoute(route, matrix[slider.result.from]);
    };

    this.updateLabel = function (label) {
      $("#route_name").html(label);
    };

    this.updateMap = function (periodId) {
      if (route === null) {
        return;
      }
      drawSegmentApp.drawRoute(route, matrix[periodId]);
    };

    /**
     * Clear information in bar chart and map.
     */
    this.clearDisplayData = function () {
      mChart.clear();
      $("#mapid").hide();
    };
  }

  function processData(dataSource, app) {
    $("#mapid").show();
    if (dataSource.status) {
      return;
    }

    app.setMatrix(dataSource.matrix);
    app.setRoute(dataSource.route);

    let data = [];
    dataSource.matrix.forEach(function (vec, i) {
      vec.forEach(function (elem, j) {
        data.push([i, j, elem[0]]);
      });
    });

    app.updateChart(data, dataSource.segments);
  }

  // load filters
  (function () {
    loadAvailableDays(Urls["esapi:availableSpeedDays"]());
    loadRangeCalendar(Urls["esapi:availableSpeedDays"](), {});

    let app = new MatrixApp();

    $("#filterHourRange").ionRangeSlider({
      type: "single",
      values: periods,
      grid: true,
      onFinish: function (data) {
        console.log("slider moved");
        let periodId = data.from;
        app.updateMap(periodId);
      }
    });

    let previousCall = function () {
      app.showLoadingAnimationCharts();
    };
    let afterCall = function (data, status) {
      if (status) {
        processData(data, app);
      } else{
        app.clearDisplayData();
      }
      app.hideLoadingAnimationCharts();
    };
    let opts = {
      urlFilterData: Urls["esapi:matrixData"](),
      urlRouteData: Urls["esapi:availableSpeedRoutes"](),
      previousCallData: previousCall,
      afterCallData: afterCall
    };
    new FilterManager(opts);
    $(window).resize(function () {
      app.resizeChart();
    });
    $("#menu_toggle").click(function () {
      app.resizeChart();
    });
  })();
});