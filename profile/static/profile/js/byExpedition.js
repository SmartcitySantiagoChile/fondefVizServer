"use strict";
$(document).ready(function () {
  // define logic to manipulate data
  function Trip(expeditionDayId, route, licensePlate, busCapacity, timeTripInit, timeTripEnd, authTimePeriod, dayType,
                yAxisData, valid, passengerWithEvasionPerKmSectionSum, capacityPerKmSectionSum) {
    this.expeditionId = expeditionDayId;
    this.route = route;
    this.licensePlate = licensePlate;
    this.busCapacity = busCapacity;
    this.timeTripInit = timeTripInit;
    this.timeTripEnd = timeTripEnd;
    this.authTimePeriod = authTimePeriod;
    this.dayType = dayType;
    this.yAxisData = yAxisData;
    this.valid = valid;
    this.visible = valid === undefined ? true : valid;
    this.passengerWithEvasionPerKmSectionSum = passengerWithEvasionPerKmSectionSum;
    this.capacityPerKmSectionSum = capacityPerKmSectionSum;
  }

  /*
   * to manage grouped data
   */
  function DataManager() {
    // trips
    let _trips = [];
    // stops
    let _xAxisData = null;
    // y average data
    let _yAxisData = null;
    // trips to show in profile view
    let _visibleTrips = 0;
    let _shape = [];
    let _boardingWithAlightingPercentage = 0;
    let _utilizationCoefficient = 0;

    this.trips = function (trips) {
      if (trips === undefined) {
        return _trips;
      }
      _visibleTrips = 0;
      trips.forEach(function (trip) {
        if (trip.visible) {
          _visibleTrips++;
        }
      });
      _trips = trips;
    };
    this.addTrip = function (trip) {
      if (trip.visible) {
        _visibleTrips++;
      }
      // create trip identifier
      trip.id = _trips.length;
      _trips.push(trip);
    };
    this.xAxisData = function (data) {
      if (data === undefined) {
        return _xAxisData;
      }
      _xAxisData = data;
    };
    this.yAxisData = function (data) {
      if (data === undefined) {
        return _yAxisData;
      }
      _yAxisData = data;
    };
    this.shape = function (shape) {
      if (shape === undefined) {
        return _shape;
      }
      _shape = shape;
    };
    this.tripsUsed = function () {
      return _visibleTrips;
    };
    this.clearData = function () {
      _trips = [];
      _xAxisData = null;
      _yAxisData = null;
      _visibleTrips = 0;
    };
    this.setVisibilty = function (tripIdArray, value) {
      tripIdArray.forEach(function (tripId) {
        if (_trips[tripId].visible !== value) {
          if (value === false) {
            _visibleTrips--;
          } else {
            _visibleTrips++;
          }
        }
        _trips[tripId].visible = value;
      });
    };
    this.checkAllAreVisible = function (tripIdArray) {
      let result = tripIdArray.length;
      tripIdArray.forEach(function (tripId) {
        if (!_trips[tripId].visible) {
          result--;
        }
      });
      return result;
    };
    this.calculateAverage = function () {
      // erase previous visible data
      let xAxisLength = _xAxisData.length;
      let counterByStop = [];
      let capacityByStop = [];
      let boardingTotal = 0;
      let boardingWithAlightingTotal = 0;
      let passengerWithEvasionPerKmSectionTotal = 0;
      let capacityPerKmSectionTotal = 0;

      _yAxisData = {
        expandedAlighting: [],
        expandedBoarding: [],
        loadProfile: [],
        saturationRate: [],
        valueIsNull: [],
        maxLoad: [],
        loadProfileWithEvasion: [],
        expandedEvasionBoarding: [],
        expandedEvasionAlighting: [],
        expandedBoardingPlusExpandedEvasionBoarding: [],
        expandedAlightingPlusExpandedEvasionAlighting: [],
        maxLoadWithEvasion: [],
        saturationRateWithEvasion: []
      };
      for (let i = 0; i < xAxisLength; i++) {
        _yAxisData.expandedBoarding.push(0);
        _yAxisData.expandedAlighting.push(0);
        _yAxisData.loadProfile.push(0);
        _yAxisData.maxLoad.push(0);
        _yAxisData.loadProfileWithEvasion.push(0);
        _yAxisData.expandedEvasionBoarding.push(0);
        _yAxisData.expandedEvasionAlighting.push(0);
        _yAxisData.expandedBoardingPlusExpandedEvasionBoarding.push(0);
        _yAxisData.expandedAlightingPlusExpandedEvasionAlighting.push(0);
        _yAxisData.maxLoadWithEvasion.push(0);

        capacityByStop.push(0);
        counterByStop.push(0);
      }
      _trips.forEach(function (trip) {
        if (!trip.visible) {
          return;
        }

        for (let stopIndex = 0; stopIndex < xAxisLength; stopIndex++) {
          if (trip.yAxisData.valueIsNull[stopIndex]) {
            continue;
          }
          _yAxisData.expandedAlighting[stopIndex] += trip.yAxisData.expandedAlighting[stopIndex];
          _yAxisData.expandedBoarding[stopIndex] += trip.yAxisData.expandedBoarding[stopIndex];
          _yAxisData.loadProfile[stopIndex] += trip.yAxisData.loadProfile[stopIndex];
          _yAxisData.maxLoad[stopIndex] = Math.max(_yAxisData.maxLoad[stopIndex], trip.yAxisData.loadProfile[stopIndex]);
          _yAxisData.loadProfileWithEvasion[stopIndex] += trip.yAxisData.loadProfileWithEvasion[stopIndex];
          _yAxisData.expandedEvasionBoarding[stopIndex] += trip.yAxisData.expandedEvasionBoarding[stopIndex];
          _yAxisData.expandedEvasionAlighting[stopIndex] += trip.yAxisData.expandedEvasionAlighting[stopIndex];
          _yAxisData.expandedBoardingPlusExpandedEvasionBoarding[stopIndex] += trip.yAxisData.expandedBoardingPlusExpandedEvasionBoarding[stopIndex];
          _yAxisData.expandedAlightingPlusExpandedEvasionAlighting[stopIndex] += trip.yAxisData.expandedAlightingPlusExpandedEvasionAlighting[stopIndex];
          _yAxisData.maxLoadWithEvasion[stopIndex] = Math.max(_yAxisData.maxLoadWithEvasion[stopIndex], trip.yAxisData.loadProfileWithEvasion[stopIndex]);

          capacityByStop[stopIndex] += trip.busCapacity;
          counterByStop[stopIndex]++;
          boardingTotal += trip.yAxisData.boarding[stopIndex];
          boardingWithAlightingTotal += trip.yAxisData.boardingWithAlighting[stopIndex];
          passengerWithEvasionPerKmSectionTotal += trip.passengerWithEvasionPerKmSectionSum;
          capacityPerKmSectionTotal += trip.capacityPerKmSectionSum;
        }
      });
      // it calculates average
      for (let stopIndex = 0; stopIndex < xAxisLength; stopIndex++) {
        _yAxisData.expandedAlighting[stopIndex] = _yAxisData.expandedAlighting[stopIndex] / counterByStop[stopIndex];
        _yAxisData.expandedBoarding[stopIndex] = _yAxisData.expandedBoarding[stopIndex] / counterByStop[stopIndex];
        let saturationRate = (_yAxisData.loadProfile[stopIndex] / capacityByStop[stopIndex]) * 100;
        _yAxisData.saturationRate.push(saturationRate);
        let saturationRateWithEvasion = (_yAxisData.loadProfileWithEvasion[stopIndex] / capacityByStop[stopIndex]) * 100;
        _yAxisData.saturationRateWithEvasion.push(saturationRateWithEvasion);
        _yAxisData.loadProfile[stopIndex] = _yAxisData.loadProfile[stopIndex] / counterByStop[stopIndex];
        _yAxisData.loadProfileWithEvasion[stopIndex] = _yAxisData.loadProfileWithEvasion[stopIndex] / counterByStop[stopIndex];
        _yAxisData.expandedEvasionBoarding[stopIndex] = _yAxisData.expandedEvasionBoarding[stopIndex] / counterByStop[stopIndex];
        _yAxisData.expandedEvasionAlighting[stopIndex] = _yAxisData.expandedEvasionAlighting[stopIndex] / counterByStop[stopIndex];
        _yAxisData.expandedBoardingPlusExpandedEvasionBoarding[stopIndex] = _yAxisData.expandedBoardingPlusExpandedEvasionBoarding[stopIndex] / counterByStop[stopIndex];
        _yAxisData.expandedAlightingPlusExpandedEvasionAlighting[stopIndex] = _yAxisData.expandedAlightingPlusExpandedEvasionAlighting[stopIndex] / counterByStop[stopIndex];
      }

      this._utilizationCoefficient = passengerWithEvasionPerKmSectionTotal / capacityPerKmSectionTotal;
      this._boardingWithAlightingPercentage = boardingWithAlightingTotal / boardingTotal * 100;
    };

    this.getDatatableData = function () {
      let values = [];
      let max = 0;
      for (let i in _trips) {
        let trip = $.extend({}, _trips[i]);
        trip.busDetail = trip.licensePlate + " (" + trip.busCapacity + ")";
        let loadProfile = [];
        for (let k = 0; k < _xAxisData.length; k++) {
          let value = trip.yAxisData.loadProfile[k];
          max = Math.max(max, value);
          loadProfile.push(value);
        }
        trip.sparkLoadProfile = loadProfile;
        values.push(trip);
      }
      return {
        rows: values,
        maxHeight: max
      };
    };

    this.getDistributionData = function () {
      let globalMax = 0;
      let trips = [];

      for (let i in _trips) {
        let trip = _trips[i];
        let tripData = {};
        if (!trip.visible) {
          continue;
        }
        tripData.name = trip.timeTripInit;

        let loadProfile = [];
        for (let j = 0; j < _xAxisData.length; j++) {
          let value = trip.yAxisData.loadProfile[j];
          if (globalMax < value) {
            globalMax = value;
          }
          loadProfile.push(value);
        }
        tripData.loadProfile = loadProfile;
        trips.push(tripData);
      }

      return {
        globalMax: globalMax,
        trips: trips
      };
    }
  }

  function ExpeditionApp() {
    let _self = this;

    let _shapeLayer = {
      id: 'shape-layer',
      source: 'shape-source',
      type: 'line',
      layout: {
        'line-join': 'round',
        'line-cap': 'round'
      },
      paint: {
        'line-color': 'black',
        'line-width': 2
      }
    };
    let _stopsLayer = {
      id: 'stops-layer',
      source: 'stops-source',
      type: 'circle',
      paint: {
        'circle-radius': ['interpolate', ['linear'], ['zoom'],
          12, 2,
          14, 6,
          20, 12,
        ],
        'circle-color': 'black',
        'circle-stroke-color': '#559BFF',
        'circle-stroke-opacity': 0.4,
        'circle-stroke-width': {
          property: 'radius',
          type: 'identity'
        }
      }
    };
    let _stopLabelLayer = {
      id: 'stop-label-layer',
      source: 'stops-source',
      type: 'symbol',
      layout: {
        'text-field': '{userStopCode}',
        'text-size': 10,
        'text-offset': [0, 2]
      }
    };
    let mapOpts = {
      mapId: 'mapid',
      onLoad: (_mapInstance) => {
        _mapInstance.addSource('shape-source', {
          type: 'geojson',
          data: {
            type: "FeatureCollection",
            features: []
          }
        });
        _mapInstance.addSource('stops-source', {
          type: 'geojson',
          data: {
            type: "FeatureCollection",
            features: []
          }
        });

        _mapInstance.addLayer(_shapeLayer);
        _mapInstance.addLayer(_stopsLayer);
        _mapInstance.addLayer(_stopLabelLayer);
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
            'source': 'shape-source',
            'layout': {
              'symbol-placement': 'line',
              'symbol-spacing': 100,
              'icon-allow-overlap': true,
              'icon-ignore-placement': true,
              'icon-image': 'double-arrow',
              'icon-size': 0.4,
              'visibility': 'visible'
            },
            paint: {
              'icon-color': 'black',
              'icon-halo-color': '#fff',
              'icon-halo-width': 2,
            }
          });
        });

        let openStopPopup = function (feature) {
          let popUpDescription = "<p>";
          popUpDescription += " Servicio: <b>" + feature.properties.route + "</b><br />";
          popUpDescription += " Nombre: <b>" + feature.properties.stopName + "</b><br />";
          popUpDescription += " Código transantiago: <b>" + feature.properties.authStopCode + "</b><br />";
          popUpDescription += " Código usuario: <b>" + feature.properties.userStopCode + "</b><br />";
          popUpDescription += " Posición en la ruta: <b>" + (feature.properties.order + 1) + "</b><br />";
          popUpDescription += " Perfil de carga promedio (sin evasión): <b>" + (feature.properties.loadProfile + 1) + "</b><br />";
          popUpDescription += "</p>";

          new mapboxgl.Popup({closeOnClick: true}).setLngLat(feature.geometry.coordinates).setHTML(popUpDescription).addTo(_mapInstance);
        };

        let mouseenter = () => {
          _mapInstance.getCanvas().style.cursor = 'pointer';
        };
        let mouseleave = () => {
          _mapInstance.getCanvas().style.cursor = '';
        };
        let click = e => {
          let feature = e.features[0];
          openStopPopup(feature);
        };
        _mapInstance.on('mouseenter', 'stops-layer', mouseenter);
        _mapInstance.on('mouseleave', 'stops-layer', mouseleave);
        _mapInstance.on('click', 'stops-layer', click);
      }
    };
    let _mapApp = new MapApp(mapOpts);

    let fitBoundFirstTime = true;
    $("#tab-1").click(function () {
      setTimeout(function () {
        if (fitBoundFirstTime) {
          setTimeout(function () {
            _mapApp.fitBound(['shape-source', 'stops-source']);
            _mapApp.resize();
            fitBoundFirstTime = false;
          }, 400);
        } else {
          _mapApp.resize();
        }
      }, 400);
    });
    $("#tab-0").click(function () {
      setTimeout(function () {
        _self.resizeCharts();
      }, 400);
    });

    this.getDataName = function () {
      let FILE_NAME = "Perfil de carga ";
      return FILE_NAME + $("#authRouteFilter").val();
    };

    let _dataManager = new DataManager();
    let _barChart = echarts.init(document.getElementById("barChart"), theme);
    let _datatable = $("#expeditionDetail").DataTable({
      lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "Todos"]],
      language: {
        url: "//cdn.datatables.net/plug-ins/1.10.13/i18n/Spanish.json",
        decimal: ",",
        thousands: "."
      },
      columns: [
        {
          "targets": 0,
          "searchable": false,
          "orderable": false,
          "className": "text-center",
          "data": "visible",
          "render": function (data, type, full, meta) {
            return $("<input>")
              .attr("type", "checkbox")
              .attr("name", "trip" + full.id)
              .addClass("flat")
              .attr("checked", full.valid)[0].outerHTML;
          }
        },
        {
          title: "Perfil de carga sin evasión", data: "sparkLoadProfile", searchable: false,
          render: function (data, type, row) {
            return $("<i>").addClass("spark").append(data.join(","))[0].outerHTML;
          }
        },
        {title: "Patente (capacidad)", data: "busDetail", searchable: true},
        {title: "Período inicio expedición", data: "authTimePeriod", searchable: true},
        {title: "Hora de inicio", data: "timeTripInit", searchable: true},
        {title: "Hora de fin", data: "timeTripEnd", searchable: true},
        {title: "Tipo de día", data: "dayType", searchable: true},
        {
          title: "Válida", data: "valid", searchable: true,
          render: function (data) {
            return data ? "Válida" : "No válida";
          }
        }
      ],
      order: [[4, "asc"]],
      createdRow: function (row, data, index) {
        if (data.visible) {
          $(row).addClass("success");
        }
      },
      initComplete: function (settings) {
        // Handle click on "Select all" control
        let mainCheckbox = $("#checkbox-select-all");
        mainCheckbox.iCheck({
          labelHover: false,
          cursor: true,
          checkboxClass: "icheckbox_flat-green"
        });
        mainCheckbox.on("ifToggled", function (event) {
          // Get all rows with search applied
          if (_dataManager.trips().length === 0) {
            return;
          }
          let rows = _datatable.rows({"search": "applied"}).nodes();
          let addToAggr = false;
          let inputs = $("input.flat", rows);
          if (event.target.checked) {
            inputs.prop("checked", true);
            $(rows).addClass("success");
            addToAggr = true;
          } else {
            inputs.prop("checked", false);
            $(rows).removeClass("success");
          }
          $("tbody input.flat").iCheck("update");
          let tripIds = $.map(_datatable.rows({"search": "applied"}).data(), function (el) {
            return el.id;
          });
          _dataManager.setVisibilty(tripIds, addToAggr);
          _dataManager.calculateAverage();
          _self.updateCharts();
        });
      }
    });
    _datatable.on("search.dt", function (event) {
      let el = $("#checkbox-select-all");
      let tripIds = $.map(_datatable.rows({"search": "applied"}).data(), function (el) {
        return el.id
      });
      let resultChecked = _dataManager.checkAllAreVisible(tripIds);

      if (resultChecked === tripIds.length) {
        el.prop("checked", true);
      } else if (resultChecked === 0) {
        el.prop("checked", false);
      } else {
        el.prop("checked", false);
        el.prop("indeterminate", true);
      }
      el.iCheck("update");
    });

    this.dataManager = function (dataManager) {
      if (dataManager === undefined) {
        return _dataManager;
      }
      _dataManager = dataManager;
    };

    this.resizeCharts = function () {
      _barChart.resize();
    };

    let _updateMap = function () {
      let shape = _dataManager.shape();
      let stops = _dataManager.xAxisData();
      let yAxisData = _dataManager.yAxisData().loadProfile;

      let shapeSource = {
        type: 'FeatureCollection',
        features: []
      };
      let stopsSource = {
        type: 'FeatureCollection',
        features: []
      };

      let maxLoadProfile = Math.max(...yAxisData);
      stops.forEach(function (stop, i) {
        let loadProfile = yAxisData[i] ? yAxisData[i] : 0;
        let formattedLoadProfile = Number(loadProfile.toFixed(2)).toLocaleString();
        let area = (loadProfile / maxLoadProfile) * 400;
        let radius = Math.sqrt(area / Math.PI);
        if (radius <= 0 || isNaN(radius)) {
          radius = 1;
        }

        stopsSource.features.push({
          type: 'Feature',
          geometry: {
            type: 'Point',
            coordinates: [stop.longitude, stop.latitude]
          },
          properties: {
            radius: radius,
            route: $("#authRouteFilter").val(),
            authStopCode: stop.authStopCode,
            userStopCode: stop.userStopCode,
            stopName: stop.stopName,
            order: stop.order,
            isBusStation: stop.busStation,
            loadProfile: formattedLoadProfile
          }
        });
      });

      shapeSource.features.push({
        type: 'Feature',
        geometry: {
          type: 'LineString',
          coordinates: shape.map(el => [el.longitude, el.latitude])
        }
      });
      _mapApp.getMapInstance().getSource('shape-source').setData(shapeSource);
      _mapApp.getMapInstance().getSource('stops-source').setData(stopsSource);
    };

    let _updateDatatable = function () {
      let dataset = _dataManager.getDatatableData();
      let rows = dataset.rows;
      let maxHeight = dataset.maxHeight;

      _datatable.off("draw");
      _datatable.on("draw", function (oSettings) {
        $(".spark:not(:has(canvas))").sparkline("html", {
          type: "bar",
          barColor: "#169f85",
          negBarColor: "red",
          chartRangeMax: maxHeight,
          numberFormatter: function (value) {
            return Number(value.toFixed(2)).toLocaleString();
          }
        });

        $("tbody input.flat").iCheck("destroy");
        $("tbody input.flat").iCheck({
          labelHover: false,
          cursor: true,
          checkboxClass: "icheckbox_flat-green"
        });

        // activate iCheck in checkbox
        let dtRows = _datatable.rows().nodes();
        // attach events check and uncheck
        $("input.flat", dtRows).off("ifToggled");
        $("input.flat", dtRows).on("ifToggled", function (event) {
          let tr = $(this).parent().parent().parent();
          let addToAggr = false;
          if (event.target.checked) {
            tr.addClass("success");
            addToAggr = true;
          } else {
            tr.removeClass("success");
          }

          // updateChart
          let tripId = parseInt($(this).attr("name").replace("trip", ""));
          _dataManager.setVisibilty([tripId], addToAggr);
          _dataManager.calculateAverage();
          _self.updateCharts();
        });
      });
      _datatable.clear();
      _datatable.rows.add(rows);
      _datatable.columns.adjust().draw();

      // attach to attach event
      $("#detail-tab").off("shown.bs.tab");
      $("#detail-tab").on("shown.bs.tab", function (event) {
        $(".spark:not(:has(canvas))").sparkline("html", {
          type: "bar",
          barColor: "#169f85",
          negBarColor: "red",
          chartRangeMax: maxHeight
        });
      })
    };

    const _updateBarChart = function () {
      let yAxisData = _dataManager.yAxisData();
      let xAxisData = _dataManager.xAxisData();

      // get out, get in, load profile, percentage occupation
      let yAxisDataName = [
        "Subidas", "Subidas evadidas",
        "Bajadas", "Bajadas evadidas",
        "Carga prom.", "Carga prom. con evasión",
        "Carga máx.", "Carga máx. con evasión",
        "% ocupación", "% ocupación con evasión"];
      let yAxisDataNameWithoutEvasion = [
        "Subidas",
        "Bajadas",
        "Carga prom.",
        "Carga máx.",
        "% ocupación"];
      let yAxisIndex = [0, 0, 0, 0, 0, 0, 0, 0, 1, 1];
      let yChartType = [
        "bar", "bar",
        "bar", "bar",
        "line", "line",
        "line", "line",
        "line", "line"];
      let stack = [
        "Subidas", "Subidas",
        "Bajadas", "Bajadas",
        null, null,
        null, null,
        null, null
      ];
      let dataName = [
        "expandedBoarding", "expandedEvasionBoarding",
        "expandedAlighting", "expandedEvasionAlighting",
        "loadProfile", "loadProfileWithEvasion",
        "maxLoad", "maxLoadWithEvasion",
        "saturationRate", "saturationRateWithEvasion"];
      let colors = [
        {itemStyle: {normal: {color: "#2C69B0"}}}, {itemStyle: {normal: {color: "#6BA3D6"}}},
        {itemStyle: {normal: {color: "#F02720"}}}, {itemStyle: {normal: {color: "#EA6B73"}}},
        {itemStyle: {normal: {color: "#4AA96C"}}}, {itemStyle: {normal: {color: "#9FE6A0"}}},
        {itemStyle: {normal: {color: "#610F95"}}}, {itemStyle: {normal: {color: "#B845C4"}}},
        {lineStyle: {normal: {type: "dashed"}}, itemStyle: {normal: {color: "#FFB037"}}},
        {lineStyle: {normal: {type: "dashed"}}, itemStyle: {normal: {color: "#FFE268"}}}
      ];

      let series = [];
      for (let index = 0; index < yAxisIndex.length; index++) {
        let serie = {
          name: yAxisDataName[index],
          type: yChartType[index],
          data: yAxisData[dataName[index]],
          showSymbol: false,
          yAxisIndex: yAxisIndex[index],
          smooth: true
        };
        if (stack[index] != null) {
          serie["stack"] = stack[index];
        }
        $.extend(serie, colors[index]);
        series.push(serie);
      }
      let maxLabelLength = 0;
      let xData = xAxisData.map(function (attr) {
        let label = attr.order + " " + attr.stopName;
        if (maxLabelLength < label.length) {
          maxLabelLength = label.length;
        }
        attr.value = attr.stopName;
        label = attr;
        return label;
      });
      let route = $("#authRouteFilter").val();
      let options = {
        legend: {
          data: yAxisDataNameWithoutEvasion,
          height: 40,
          orient: 'vertical',
          formatter: '{styleA|{name}}',
          textStyle: {
            rich: {
              styleA: {
                width: 130,
                lineHeight: 0
              }
            }
          }
        },
        xAxis: [{
          type: "category",
          data: xData,
          axisTick: {
            length: 10
          },
          axisLabel: {
            rotate: 90,
            interval: function (index) {
              let labelWidth = 20;
              let chartWidth = $("#barChart").width() - 82;
              let div = chartWidth / labelWidth;
              if (div >= xData.length) {
                return true;
              }
              div = parseInt(xData.length / div);
              return !(index % div);
            },
            textStyle: {
              fontSize: 12
            },
            formatter: function (value, index) {
              return (index + 1) + " " + value + " " + (xAxisData[index].busStation ? "(ZP)" : "");
            },
            color: function (label, index) {
              if (xAxisData[index].busStation) {
                return "red";
              }
              return "black";
            }
          }
        }],
        yAxis: [{
          type: "value",
          name: "N° Pasajeros",
          //max: capacity - capacity%10 + 10,
          position: "left"
        }, {
          type: "value",
          name: "Porcentaje",
          //min: 0,
          max: 100,
          position: "right",
          axisLabel: {
            formatter: "{value} %",
            textStyle: {
              color: "#EA8E4D"
            }
          },
          axisLine: {
            onZero: true,
            lineStyle: {
              color: "#EA8E4D", width: 2
            }
          },
          nameTextStyle: {
            color: "#EA8E4D"
          }
        }],
        series: series,
        tooltip: {
          trigger: "axis",
          //alwaysShowContent: true,
          formatter: function (params) {
            if (Array.isArray(params)) {
              let xValue = params[0].dataIndex;
              let head = (xValue + 1) + "  " + xAxisData[xValue].userStopCode + " " + xAxisData[xValue].authStopCode + "  " + xAxisData[xValue].stopName + "<br />";
              let info = [];
              for (let index in params) {
                let el = params[index];
                let ball = el.marker;
                let name = el.seriesName;
                let value = Number(el.value.toFixed(2)).toLocaleString();
                if (el.seriesIndex === 8 || el.seriesIndex === 9) {
                  value = value + " %";
                }
                info.push(ball + name + ": " + value);
              }
              return head + info.join("<br />");
            } else {
              let title = params.data.name;
              let name = params.seriesName;
              let value = Number(params.value.toFixed(2)).toLocaleString();
              return title + "<br />" + name + ": " + value;
            }
          }
        },
        grid: {
          top: "100px",
          left: "37px",
          right: "45px",
          bottom: maxLabelLength * 5.5 + 20 + "px"
        },
        toolbox: {
          show: true,
          itemSize: 20,
          bottom: 15,
          left: "center",
          feature: {
            mark: {show: false},
            restore: {show: false, title: "restaurar"},
            saveAsImage: {show: true, title: "Guardar imagen", name: _self.getDataName()},
            dataView: {
              show: true,
              title: "Ver datos",
              lang: ["Datos del gráfico", "cerrar", "refrescar"],
              buttonColor: "#169F85",
              readOnly: true,
              optionToContent: function (opt) {
                let axisData = opt.xAxis[0].data;
                let series = opt.series;

                let textarea = document.createElement('textarea');
                textarea.style.cssText = 'width:100%;height:100%;font-family:monospace;font-size:14px;line-height:1.6rem;white-space: pre;';
                textarea.readOnly = "true";

                let header = "Servicio\tOrden\tCódigo usuario\tCódigo transantiago\tNombre parada";
                series.forEach(function (el) {
                  header += "\t" + el.name;
                });
                header += "\n";
                let body = "";
                axisData.forEach(function (el, index) {
                  let serieValues = [];
                  series.forEach(function (serie) {
                    serieValues.push(serie.data[index]);
                  });
                  serieValues = serieValues.join("\t");
                  body += [route, el.order, el.userStopCode, el.authStopCode, el.stopName, serieValues, "\n"].join("\t");
                });
                body = body.replace(/\./g, ",");
                textarea.value = header + body;
                return textarea;
              }
            },
            myPercentageEditor: {
              show: true,
              title: "Cambiar porcentaje máximo",
              icon: 'image:///static/profile/img/percent.png',
              onclick: function () {
                let percentage = prompt("Ingrese el porcentaje máximo");
                if (percentage !== "") {
                  options.yAxis[1].max = percentage;
                } else {
                  delete options.yAxis[1].max;
                }
                _barChart.setOption(options, {notMerge: true});
              }
            }
          }
        },
        calculable: false
      };

      _barChart.clear();
      _barChart.setOption(options, {
        notMerge: true
      });
      hideEvasion();
      let evasionSwitch = $("#evasionSwitch");
      if (!evasionSwitch.length) {
        addSwitch();
      } else {
        if (evasionSwitch.is(":checked")) {
          evasionSwitch.trigger('click');
        }
      }
    };

    const addSwitch = function () {
      let evasionSwitch = "<div id='evasionControl'><input id='evasionSwitch'  type='checkbox'  class='modes_checkbox' data-switchery='true'> Mostrar datos con evasión </div>";
      $("#barChart").prepend(evasionSwitch);
      let evasionJquerySwitch = $("#evasionSwitch");
      evasionJquerySwitch.each(function (index, html) {
        new Switchery(html, {
          size: 'small',
          color: 'rgb(38, 185, 154)'
        });
      });
      let switcherySwitch = $(".switchery");
      switcherySwitch.on("click", () => {
        if (evasionJquerySwitch.is(":checked")) {
          showEvasion();
          evasionJquerySwitch.prop('checked', true);

        } else {
          evasionJquerySwitch.prop('checked', false);
          hideEvasion();
        }
      });
    };

    const hideEvasion = () => applyToEvasion('legendUnSelect');

    const showEvasion = () => applyToEvasion('legendSelect');

    const applyToEvasion = type => {
      let labels = ["Subidas evadidas", "Bajadas evadidas", "Carga prom. con evasión", "Carga máx. con evasión", "% ocupación con evasión"]
      labels.map(e => {
        _barChart.dispatchAction({
          type: type,
          name: e
        })
      })
    }

    let _updateGlobalStats = function (expeditionNumber, boardingWithAlightingPercentage, utilizationCoefficient) {
      expeditionNumber = expeditionNumber || _dataManager.tripsUsed();
      boardingWithAlightingPercentage = boardingWithAlightingPercentage || _dataManager._boardingWithAlightingPercentage || 0;
      utilizationCoefficient = utilizationCoefficient || _dataManager._utilizationCoefficient || 0;
      $("#expeditionNumber").html(expeditionNumber);
      $("#expeditionNumber2").html(expeditionNumber);
      $("#boardingWithAlightingPercentage").html(Number(boardingWithAlightingPercentage.toFixed(2)).toLocaleString());
      $("#utilizationCoefficient").html(Number(utilizationCoefficient.toFixed(2)).toLocaleString());
    };

    this.updateCharts = function (expeditionNumber, boardingWithAlightingPercentage, utilizationCoefficient) {
      _updateBarChart();
      _updateGlobalStats(expeditionNumber, boardingWithAlightingPercentage, utilizationCoefficient);
      _updateMap();
    };
    this.updateDatatable = function () {
      _updateDatatable();
    };
    this.showLoadingAnimationCharts = function () {
      let loadingText = "Cargando...";
      _barChart.showLoading(null, {text: loadingText});
    };
    this.hideLoadingAnimationCharts = function () {
      _barChart.hideLoading();
    };

    /**
     * Replace information labels with -.
     * @private
     */
    const _clearGlobalStats = function () {
      $("#expeditionNumber").html('-');
      $("#expeditionNumber2").html('-');
      $("#boardingWithAlightingPercentage").html('-');
      $("#utilizationCoefficient").html('-');
    };

    /**
     * Clear information in bar chart, datatables and map.
     */
    this.clearDisplayData = function () {
      $("#globalStatsTable").hide();
      _barChart.clear();
      _clearGlobalStats();
      _datatable.clear().draw();
      _dataManager.clearData();
      $("#mapid").hide();
    };

    /** Hide or show evasion display
     * If show evasion, add evasion legends.
     * If not show evasion, remove evasion global stat column and hide evasion switch.
     * @param showEvasionData: true if show evasion
     */
    this.manageEvasionDisplay = function (showEvasionData) {
      if (showEvasionData) {
        let options = {
          legend: {
            data: [
              "Subidas", "Subidas evadidas",
              "Bajadas", "Bajadas evadidas",
              "Carga prom.", "Carga prom. con evasión",
              "Carga máx.", "Carga máx. con evasión",
              "% ocupación", "% ocupación con evasión"]
          }
        };
        _barChart.setOption(options, {
          replaceMerge: 'legend'
        });
      } else {
        $("#evasionControl").hide();
        $("#globalStatsTable thead tr").children("th:eq(2)").remove();
        $("#globalStatsTable tbody tr").children("td:eq(2)").remove();
      }
      $("#globalStatsTable").show();
    }
  }

  function processData(dataSource, app) {
    $("#mapid").show();
    if (dataSource.status && (dataSource.status.code !== 252 && dataSource.status.code !== 253)) {
      return;
    }
    let trips = dataSource.trips;
    let stops = dataSource.stops;
    let busStations = dataSource.busStations;
    let shape = dataSource.shape;
    let dataManager = new DataManager();
    const showEvasionData = dataSource.showEvasion;
    dataManager.shape(shape);
    if (dataSource.groupedTrips) {
      busStations = dataSource.groupedTrips.aggregations.stop.station.buckets.map(function (el) {
        return el.key;
      });
      let yAxisDataResult = {
        expandedAlighting: [],
        expandedBoarding: [],
        loadProfile: [],
        saturationRate: [],
        maxLoad: [],
        loadProfileWithEvasion: [],
        expandedEvasionBoarding: [],
        expandedEvasionAlighting: [],
        expandedBoardingPlusExpandedEvasionBoarding: [],
        expandedAlightingPlusExpandedEvasionAlighting: [],
        saturationRateWithEvasion: [],
        maxLoadWithEvasion: [],
      };

      let groupedStops = {};
      dataSource.groupedTrips.aggregations.stops.buckets.forEach(function (el) {
        groupedStops[el.key] = {
          expandedBoarding: el.expandedBoarding.value,
          loadProfile: el.loadProfile.value,
          expandedAlighting: el.expandedAlighting.value,
          busSaturation: el.busSaturation.value,
          distOnPath: el.pathDistance.hits.hits[0]._source.stopDistanceFromPathStart,
          expeditionNumber: el.doc_count,
          maxLoadProfile: el.maxLoadProfile.value,
          loadProfileWithEvasion: showEvasionData ? el.loadProfileWithEvasion.value : 0,
          maxLoadProfileWithEvasion: showEvasionData ? el.maxLoadProfileWithEvasion.value : 0,
          expandedEvasionBoarding: showEvasionData ? el.expandedEvasionBoarding.value : 0,
          expandedEvasionAlighting: showEvasionData ? el.expandedEvasionAlighting.value : 0,
          expandedBoardingPlusExpandedEvasionBoarding: showEvasionData ?
            el.expandedBoardingPlusExpandedEvasionBoarding.value : 0,
          expandedAlightingPlusExpandedEvasionAlighting: showEvasionData ?
            el.expandedAlightingPlusExpandedEvasionAlighting.value : 0,
          busSaturationWithEvasion: showEvasionData ? el.busSaturationWithEvasion.value : 0,
          boarding: el.boarding.value,
          boardingWithAlighting: el.boardingWithAlighting.value,
          passengerWithEvasionPerKmSection: showEvasionData ?
            el.passengerWithEvasionPerKmSection.value : 0,
          capacityPerKmSection: el.capacityPerKmSection.value
        }
      });
      let expeditionNumber = 0;
      let boardingTotal = 0;
      let boardingWithAlightingTotal = 0;
      let passengerWithEvasionPerKmSectionTotal = 0;
      let capacityPerKmSectionTotal = 0;
      stops.forEach(function (stop) {
        let item = groupedStops[stop.authStopCode];
        let itemIsNull = item === undefined;

        let expandedAlighting = itemIsNull ? null : item.expandedAlighting;
        let expandedBoarding = itemIsNull ? null : item.expandedBoarding;
        let loadProfile = itemIsNull ? null : item.loadProfile;
        let saturationRate = itemIsNull ? null : item.busSaturation * 100;
        let maxLoadProfile = itemIsNull ? null : item.maxLoadProfile;
        let loadProfileWithEvasion = itemIsNull ? null : item.loadProfileWithEvasion;
        let maxLoadProfileWithEvasion = itemIsNull ? null : item.maxLoadProfileWithEvasion;
        let expandedEvasionBoarding = itemIsNull ? null : item.expandedEvasionBoarding;
        let expandedEvasionAlighting = itemIsNull ? null : item.expandedEvasionAlighting;
        let expandedBoardingPlusExpandedEvasionBoarding = itemIsNull ? null : item.expandedBoardingPlusExpandedEvasionBoarding;
        let expandedAlightingPlusExpandedEvasionAlighting = itemIsNull ? null : item.expandedAlightingPlusExpandedEvasionAlighting;
        let saturationRateWithEvasion = itemIsNull ? null : item.busSaturationWithEvasion * 100;
        let boarding = itemIsNull ? null : item.boarding;
        let boardingWithAlighting = itemIsNull ? null : item.boardingWithAlighting;
        let passengerWithEvasionPerKmSection = itemIsNull ? 0 : item.passengerWithEvasionPerKmSection;
        let capacityPerKmSection = itemIsNull ? 0 : item.capacityPerKmSection;

        yAxisDataResult.expandedAlighting.push(expandedAlighting);
        yAxisDataResult.expandedBoarding.push(expandedBoarding);
        yAxisDataResult.loadProfile.push(loadProfile);
        yAxisDataResult.saturationRate.push(saturationRate);
        yAxisDataResult.maxLoad.push(maxLoadProfile);
        yAxisDataResult.maxLoadWithEvasion.push(maxLoadProfileWithEvasion);
        yAxisDataResult.loadProfileWithEvasion.push(loadProfileWithEvasion);
        yAxisDataResult.expandedEvasionBoarding.push(expandedEvasionBoarding);
        yAxisDataResult.expandedEvasionAlighting.push(expandedEvasionAlighting);
        yAxisDataResult.expandedBoardingPlusExpandedEvasionBoarding.push(expandedBoardingPlusExpandedEvasionBoarding);
        yAxisDataResult.expandedAlightingPlusExpandedEvasionAlighting.push(expandedAlightingPlusExpandedEvasionAlighting);
        yAxisDataResult.saturationRateWithEvasion.push(saturationRateWithEvasion);

        let expNumber = itemIsNull ? 0 : item.expeditionNumber;
        expeditionNumber = Math.max(expNumber, expeditionNumber);
        boardingTotal += boarding;
        boardingWithAlightingTotal += boardingWithAlighting;
        passengerWithEvasionPerKmSectionTotal += passengerWithEvasionPerKmSection;
        capacityPerKmSectionTotal += capacityPerKmSection;
      });
      let boardingWithAlightingPercentage = boardingWithAlightingTotal / boardingTotal * 100;
      let utilizationCoefficient = passengerWithEvasionPerKmSectionTotal / capacityPerKmSectionTotal;

      dataManager.yAxisData(yAxisDataResult);
      let tripGroupXAxisData = stops.map(function (stop) {
        stop.busStation = busStations.indexOf(stop.authStopCode) >= 0;
        return stop;
      });
      dataManager.xAxisData(tripGroupXAxisData);
      app.dataManager(dataManager);
      app.updateCharts(expeditionNumber, boardingWithAlightingPercentage, utilizationCoefficient);
      app.updateDatatable();
    } else {
      for (let expeditionId in trips) {
        let trip = trips[expeditionId];

        // trip info
        let capacity = trip.info[0];
        let licensePlate = trip.info[1];
        let route = trip.info[2];
        let authTimePeriod = trip.info[3];
        let timeTripInit = trip.info[4];
        let timeTripEnd = trip.info[5];
        let dayType = trip.info[6];
        let valid = trip.info[7];

        let yAxisData = {
          expandedAlighting: [],
          expandedBoarding: [],
          loadProfile: [],
          saturationRate: [],
          valueIsNull: [],
          loadProfileWithEvasion: [],
          expandedEvasionBoarding: [],
          expandedEvasionAlighting: [],
          expandedBoardingPlusExpandedEvasionBoarding: [],
          expandedAlightingPlusExpandedEvasionAlighting: [],
          saturationRateWithEvasion: [],
          boarding: [],
          boardingWithAlighting: []
        };

        let passengerWithEvasionPerKmSectionSum = 0;
        let capacityPerKmSectionSum = 0;
        stops.forEach(function (stop) {
          let item = trip.stops[stop.authStopCode];
          let itemIsNull = item === undefined;

          let expandedAlighting = itemIsNull ? null : item[2];
          let expandedBoarding = itemIsNull ? null : item[1];
          let loadProfile = itemIsNull ? null : item[0];
          let saturationRate = itemIsNull ? null : loadProfile / capacity * 100;
          let loadProfileWithEvasion = itemIsNull ? null : item[3];
          let expandedEvasionBoarding = itemIsNull ? null : item[4];
          let expandedEvasionAlighting = itemIsNull ? null : item[5];
          let expandedBoardingPlusExpandedEvasionBoarding = itemIsNull ? null : item[6];
          let expandedAlightingPlusExpandedEvasionAlighting = itemIsNull ? null : item[7];
          let saturationRateWithEvasion = itemIsNull ? null : loadProfileWithEvasion / capacity * 100;
          let boarding = itemIsNull ? null : item[8];
          let boardingWithAlighting = itemIsNull ? null : item[9];
          let passengerWithEvasionPerKmSection = itemIsNull ? 0 : item[10];
          let capacityPerKmSection = itemIsNull ? 0 : item[11];

          passengerWithEvasionPerKmSectionSum += passengerWithEvasionPerKmSection
          capacityPerKmSectionSum += capacityPerKmSection

          yAxisData.expandedAlighting.push(expandedAlighting);
          yAxisData.expandedBoarding.push(expandedBoarding);
          yAxisData.loadProfile.push(loadProfile);
          yAxisData.saturationRate.push(saturationRate);
          yAxisData.valueIsNull.push(itemIsNull)
          yAxisData.loadProfileWithEvasion.push(loadProfileWithEvasion);
          yAxisData.expandedEvasionBoarding.push(expandedEvasionBoarding);
          yAxisData.expandedEvasionAlighting.push(expandedEvasionAlighting);
          yAxisData.expandedBoardingPlusExpandedEvasionBoarding.push(expandedBoardingPlusExpandedEvasionBoarding);
          yAxisData.expandedAlightingPlusExpandedEvasionAlighting.push(expandedAlightingPlusExpandedEvasionAlighting);
          yAxisData.saturationRateWithEvasion.push(saturationRateWithEvasion);
          yAxisData.boarding.push(boarding);
          yAxisData.boardingWithAlighting.push(boardingWithAlighting);
        });

        trip = new Trip(expeditionId, route, licensePlate, capacity, timeTripInit, timeTripEnd, authTimePeriod,
          dayType, yAxisData, valid, passengerWithEvasionPerKmSectionSum, capacityPerKmSectionSum);
        dataManager.addTrip(trip);
      }
      let tripXAxisData = stops.map(function (stop) {
        stop.busStation = busStations.indexOf(stop.authStopCode) >= 0;
        return stop;
      });
      dataManager.xAxisData(tripXAxisData);
      dataManager.calculateAverage();
      app.dataManager(dataManager);
      app.updateCharts();
      app.updateDatatable();
    }
    app.manageEvasionDisplay(showEvasionData);
  }

  // load filters
  (function () {
    loadAvailableDays(Urls["esapi:availableProfileDays"]());
    loadRangeCalendar(Urls["esapi:availableProfileDays"](), {});

    let app = new ExpeditionApp();
    let previousCall = function () {
      app.showLoadingAnimationCharts();
    };
    let afterCall = function (data, status) {
      if (status) {
        processData(data, app);
      } else {
        app.clearDisplayData();
      }
      app.hideLoadingAnimationCharts();
    };
    let opts = {
      urlFilterData: Urls["esapi:loadProfileByExpeditionData"](),
      urlRouteData: Urls["esapi:availableProfileRoutes"](),
      previousCallData: previousCall,
      afterCallData: afterCall
    };

    new FilterManager(opts);

    $(window).resize(function () {
      app.resizeCharts();
    });
    $("#menu_toggle").click(function () {
      app.resizeCharts();
    });
  })()
});