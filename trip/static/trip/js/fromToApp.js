"use strict";
$(document).ready(function () {
  function FromToApp() {
    let _self = this;
    let originMapApp = null;
    let destinationMapApp = null;

    let $STAGES_SELECTOR = $(".netapas_checkbox");
    let $TRANSPORT_MODES_SELECTOR = $(".modes_checkbox");
    let originSource = {
      type: 'FeatureCollection',
      features: []
    };
    let destinationSource = {
      type: 'FeatureCollection',
      features: []
    };
    let originLayer = {
      id: 'origin-layer',
      type: 'circle',
      source: 'origin-source',
      paint: {
        'circle-color': ['get', 'color'],
        'circle-radius': ['get', 'radius'],
        'circle-opacity': 0.6
      }
    };
    let destinationLayer = {
      id: 'destination-layer',
      type: 'circle',
      source: 'destination-source',
      paint: {
        'circle-color': ['get', 'color'],
        'circle-radius': ['get', 'radius'],
        'circle-opacity': 0.6
      }
    };
    let originSelected = new Set([]);
    let destinationSelected = new Set([]);

    // data given by server
    let originZones = [];
    let destinationZones = [];

    let minCircleArea = 30;
    let maxCircleArea = 800;

    let originMapLegend = null;
    let destinationMapLegend = null;

    [$STAGES_SELECTOR, $TRANSPORT_MODES_SELECTOR].forEach(function (el) {
      el.each(function (index, html) {
        new Switchery(html, {size: "small", color: "rgb(38, 185, 154)"});
      });
    });

    this.getStages = function () {
      return $STAGES_SELECTOR.filter(function (index, el) {
        return el.checked;
      }).map(function (index, el) {
        return el.getAttribute("data-ne-str");
      }).get();
    };

    this.getTransportModes = function () {
      return $TRANSPORT_MODES_SELECTOR.filter(function (index, el) {
        return el.checked;
      }).map(function (index, el) {
        return el.getAttribute("data-ne-str");
      }).get();
    };

    this.getOriginZones = function () {
      return Array.from(originSelected);
    };

    this.getDestinationZones = function () {
      return Array.from(destinationSelected);
    };

    let printAmountOfData = function (data) {
      let tripQuantity = data.origin_zone.aggregations.expansion_factor.value;
      let dataQuantity = data.origin_zone.hits.total;
      document.getElementById("tripTotalNumberLabel").innerHTML = tripQuantity === 1 ? "viaje" : "viajes";
      document.getElementById("tripTotalNumberValue").innerHTML = Number(tripQuantity.toFixed(2)).toLocaleString();

      document.getElementById("dataTotalNumberLabel").innerHTML = dataQuantity === 1 ? "dato" : "datos";
      document.getElementById("dataTotalNumberValue").innerHTML = dataQuantity.toLocaleString();
    };

    this.setData = function (newData) {
      printAmountOfData(newData);
      originZones = newData.origin_zone.aggregations.by_zone.buckets;
      destinationZones = newData.destination_zone.aggregations.by_zone.buckets;
    };

    let getCircleBounds = function () {
      let max = 0;
      let min = Infinity;
      let setMaxMin = function (v) {
        max = Math.max(max, v.expansion_factor.value);
        min = Math.min(min, v.expansion_factor.value);
      };
      if (originSelected.size === 0 && destinationSelected.size === 0) {
        originZones.forEach(setMaxMin);
        destinationZones.forEach(setMaxMin);
      } else if (originSelected.size === 0) {
        originZones.forEach(setMaxMin);
        destinationZones.filter(function (el) {
          return destinationSelected.has(el.key);
        }).forEach(setMaxMin);
      } else if (destinationSelected.size === 0) {
        destinationZones.forEach(setMaxMin);
        originZones.filter(function (el) {
          return originSelected.has(el.key);
        }).forEach(setMaxMin);
      } else {
        originZones.filter(function (el) {
          return originSelected.has(el.key);
        }).forEach(setMaxMin);
        destinationZones.filter(function (el) {
          return destinationSelected.has(el.key);
        }).forEach(setMaxMin);
      }
      return {
        max: max,
        min: min
      };
    };

    let setMapLegend = function (mapInstance, divId, controlPosition) {
      class Control {
        onAdd = function (map) {
          let div = document.createElement('canvas');
          div.className = 'mapboxgl-ctrl info legend';
          div.id = divId;
          return div;
        };

        update = function () {
          // loop through our density intervals and generate a label with a colored square for each interval
          let div = document.getElementById(divId);
          div.style.display = "none";

          let bounds = getCircleBounds();

          let ctx = div.getContext("2d");
          let halfCircleArea = (maxCircleArea + minCircleArea) / 2.0;
          let border = 10;

          let maxRadio = Math.sqrt(maxCircleArea / Math.PI);
          let halfRadio = Math.sqrt(halfCircleArea / Math.PI);
          let minRadio = Math.sqrt(minCircleArea / Math.PI);

          let circles = [{
            x: border + maxRadio,
            y: border + maxRadio,
            r: maxRadio,
            label: Number(bounds.max.toFixed(0)).toLocaleString() + " viajes"
          }, {
            x: border + maxRadio,
            y: border + 2 * maxRadio - halfRadio,
            r: halfRadio,
            label: Number(((bounds.min + bounds.max) / 2.0).toFixed(0)).toLocaleString() + " viajes"
          }, {
            x: border + maxRadio,
            y: border + 2 * maxRadio - minRadio,
            r: minRadio,
            label: Number(bounds.min.toFixed(0)).toLocaleString() + " viajes"
          }];

          // this occurs when select same zone as origin and destination
          if (bounds.min === bounds.max) {
            circles = [circles[2]];
          }

          let drawCircle = function (circle) {
            ctx.beginPath();
            ctx.arc(circle.x, circle.y, circle.r, 0, 2 * Math.PI);
            ctx.moveTo(circle.x, circle.y - circle.r);
            ctx.lineTo(2 * border + 2 * maxRadio, circle.y - circle.r);
            ctx.font = "small-caps 10px Arial";
            ctx.fillText(circle.label, 2 * border + 2 * maxRadio, circle.y - circle.r + 4);
            ctx.stroke();

            let xFirstPoint = 2 * border + 2 * maxRadio;
            let yFirstPoint = circle.y - circle.r;
            ctx.beginPath();
            ctx.moveTo(xFirstPoint, yFirstPoint);
            ctx.lineTo(xFirstPoint - 3, yFirstPoint + 3);
            ctx.lineTo(xFirstPoint - 3, yFirstPoint - 3);
            ctx.closePath();
            ctx.fill();
          };

          let maxTextLength = 0;
          circles.forEach(function (circle) {
            maxTextLength = Math.max(maxTextLength, ctx.measureText(circle.label).width);
          });

          let width = 40 + 2 * maxRadio + maxTextLength;
          let height = 20 + 2 * maxRadio;

          div.width = width;
          div.height = height;
          ctx.clearRect(0, 0, width, height);
          circles.forEach(drawCircle);

          div.style.display = "inline";
        }
      }

      let controlInstance = new Control();
      mapInstance.addControl(controlInstance, controlPosition);

      return controlInstance;
    };

    this.updateMap = function () {
      console.log("updateMap method called!");
      let bounds = getCircleBounds();

      let originZoneInfo = {};
      originMapApp.getZoneSource().features.forEach(function (feature) {
        originZoneInfo[feature.properties.id] = turf.centerOfMass(feature);
      });
      let destinationZoneInfo = {};
      destinationMapApp.getZoneSource().features.forEach(function (feature) {
        destinationZoneInfo[feature.properties.id] = turf.centerOfMass(feature);
      });

      let setCircleFeature = function (feature, indicator, color) {
        let boundRange = bounds.max - bounds.min === 0 ? 1 : bounds.max - bounds.min;
        let area = minCircleArea + (indicator - bounds.min) * (maxCircleArea - minCircleArea) / boundRange;
        let radius = Math.sqrt(area / Math.PI);
        feature.properties.radius = radius;
        feature.properties.color = color;
        return feature;
      };

      originSource.features = [];
      originZones.forEach(function (item) {
        try {
          let feature = setCircleFeature(originZoneInfo[item.key], item.expansion_factor.value, "#FFFF00");
          originSource.features.push(feature);
        } catch (error) {
          console.log(error);
        }
      });

      destinationSource.features = [];
      destinationZones.forEach(function (item) {
        try {
          let feature = setCircleFeature(destinationZoneInfo[item.key], item.expansion_factor.value, "#A900FF");
          destinationSource.features.push(feature);
        } catch (error) {
          console.log(error);
        }
      });
      originMapApp.getMapInstance().getSource('origin-source').setData(originSource);
      destinationMapApp.getMapInstance().getSource('destination-source').setData(destinationSource);

      originMapLegend.update();
      destinationMapLegend.update();
      originMapApp.fitBound(['zones-source']);
      destinationMapApp.fitBound(['zones-source']);
    };

    let mapOptionBuilder = function (opts) {
      let hoveredFeature = null;
      let defaultOpts = {
        hideMapLegend: true,
        showMetroStations: false,
        showMetroShapes: false,
        showTrainStations: false,
        showTrainShapes: false,
        showCommunes: false,
        showLayerGroupControl: false,
        onClickZone: function (e) {
          let map = e.target;
          let feature = e.features[0];
          let zoneId = feature.properties.id;
          if (opts.selectedZoneSet.has(zoneId)) {
            opts.selectedZoneSet.delete(zoneId);
            map.setFeatureState({source: 'zones-source', id: feature.id}, {selected: false});
            this.defaultOnMouseleaveZone(e);
            this.defaultOnMousemoveZone(e);
          } else {
            opts.selectedZoneSet.add(zoneId);
            map.setFeatureState({source: 'zones-source', id: feature.id}, {selected: true});
          }
        },
        onMousemoveZone: function (e) {
          let feature = e.features[0];
          hoveredFeature = feature;
          let zoneId = feature.properties.id;
          let zoneData = opts.getDataSource().find(function (el) {
            return el.key === zoneId;
          });
          feature.properties.data = JSON.stringify(zoneData);
          this.defaultOnMousemoveZone(e);
          this.refreshZoneInfoControl(feature.properties);
        },
        onMouseleaveZone: function (e) {
          this.defaultOnMouseleaveZone(e);
          this.refreshZoneInfoControl();
        }
      };
      return Object.assign({}, defaultOpts, opts);
    };

    this.loadLayers = function (readyFunction) {
      let baseColor = "#0000FF";
      let selectedOriginColor = "#9d2bdb";
      let selectedDestinationColor = "#9d2bdb";

      let originMapOpts = mapOptionBuilder({
        mapId: "mapChart",
        selectedZoneSet: originSelected,
        getDataSource: function () {
          return originZones;
        },
        onLoad: (_mapInstance, _appInstance) => {
          originMapLegend = setMapLegend(_mapInstance, "circleMapLegend1", 'bottom-right');
          originMapLegend.update();
          _appInstance.loadLayers(() => {
            // set style
            let zoneLayer = _appInstance.getZoneLayer();
            zoneLayer.paint['fill-color'] = [
              'case',
              ['boolean', ['feature-state', 'selected'], false], selectedOriginColor,
              baseColor
            ];
            _appInstance.setLayer(zoneLayer);
            _mapInstance.addSource('origin-source', {type: 'geojson', data: originSource});
            _mapInstance.addLayer(originLayer);
          });
        }
      });

      let destinationMapOpts = mapOptionBuilder({
        mapId: "mapChart2",
        selectedZoneSet: destinationSelected,
        getDataSource: function () {
          return destinationZones;
        },
        onLoad: (_mapInstance, _appInstance) => {
          destinationMapLegend = setMapLegend(_mapInstance, "circleMapLegend2", 'bottom-right');
          destinationMapLegend.update();
          _appInstance.loadLayers(() => {
            // set style
            let zoneLayer = _appInstance.getZoneLayer();
            zoneLayer.paint['fill-color'] = [
              'case',
              ['boolean', ['feature-state', 'selected'], false], selectedDestinationColor,
              baseColor
            ];
            _appInstance.setLayer(zoneLayer);
            _mapInstance.addSource('destination-source', {type: 'geojson', data: destinationSource});
            _mapInstance.addLayer(destinationLayer);
            readyFunction();
          });
        }
      });
      originMapApp = new MapApp(originMapOpts);
      destinationMapApp = new MapApp(destinationMapOpts);
    };
  }

  function processData(data, app) {
    app.setData(data);
    app.updateMap();
  }

  // load filters
  (function () {
    loadAvailableDays(Urls["esapi:availableTripDays"]());
    loadRangeCalendar(Urls["esapi:availableTripDays"](), {});

    let app = new FromToApp();

    let afterCall = function (data, status) {
      if (status || data["status"]["code"] === 403) {
        processData(data, app);
      }
    };
    let opts = {
      urlFilterData: Urls["esapi:fromToMapData"](),
      urlMultiRouteData: Urls["esapi:multiRouteData"](),
      afterCallData: afterCall,
      dataUrlParams: function () {
        return {
          stages: app.getStages(),
          transportModes: app.getTransportModes(),
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
});