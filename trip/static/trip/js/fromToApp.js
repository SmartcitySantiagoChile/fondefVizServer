"use strict";
$(document).ready(function () {
   function FromToApp() {
    let _self = this;
    let $STAGES_SELECTOR = $(".netapas_checkbox");
    let $TRANSPORT_MODES_SELECTOR = $(".modes_checkbox");
    let originGroupLayer = L.featureGroup([]);
    let destinationGroupLayer = L.featureGroup([]);
    let originSelected = new Set([]);
    let destinationSelected = new Set([]);

    // data given by server
    let originZones = [];
    let destinationZones = [];

    let minCircleSize = 3;
    let maxCircleSize = 23;

    let originMapLegend = L.control({position: "bottomright"});
    let destinationMapLegend = L.control({position: "bottomright"});

    [$STAGES_SELECTOR, $TRANSPORT_MODES_SELECTOR].forEach(function (el) {
      el.each(function (index, html) {
        new Switchery(html, {
          size: "small",
          color: "rgb(38, 185, 154)"
        });
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

    let setMapLegend = function (mapInstance, control, divId) {
      control.onAdd = function (map) {
        let div = L.DomUtil.create("canvas", "info legend");
        div.id = divId;
        return div;
      };

      control.update = function () {
        // loop through our density intervals and generate a label with a colored square for each interval
        let div = document.getElementById(divId);
        div.style.display = "none";

        let bounds = getCircleBounds();

        let ctx = div.getContext("2d");
        let half = (maxCircleSize + minCircleSize) / 2.0;
        let border = 10;

        let circles = [{
          x: border + maxCircleSize,
          y: border + maxCircleSize,
          r: maxCircleSize,
          label: Number(bounds.max.toFixed(0)).toLocaleString() + " viajes"
        }, {
          x: border + maxCircleSize,
          y: border + 2 * maxCircleSize - half,
          r: half,
          label: Number(((bounds.min + bounds.max) / 2.0).toFixed(0)).toLocaleString() + " viajes"
        }, {
          x: border + maxCircleSize,
          y: border + 2 * maxCircleSize - minCircleSize,
          r: minCircleSize,
          label: Number(bounds.min.toFixed(0)).toLocaleString() + " viajes"
        }];

        // this ocurrs when select same zone as origin and destination
        if (bounds.min === bounds.max) {
          circles = [circles[2]];
        }

        let drawCircle = function (circle) {
          ctx.beginPath();
          ctx.arc(circle.x, circle.y, circle.r, 0, 2 * Math.PI);
          ctx.moveTo(circle.x, circle.y - circle.r);
          ctx.lineTo(2 * border + 2 * maxCircleSize, circle.y - circle.r);
          ctx.font = "small-caps 10px Arial";
          ctx.fillText(circle.label, 2 * border + 2 * maxCircleSize, circle.y - circle.r + 4);
          ctx.stroke();

          let xFirstPoint = 2 * border + 2 * maxCircleSize;
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

        let width = 40 + 2 * maxCircleSize + maxTextLength;
        let height = 20 + 2 * maxCircleSize;

        div.width = width;
        div.height = height;
        ctx.clearRect(0, 0, width, height);
        circles.forEach(drawCircle);

        div.style.display = "inline";
      };
      control.addTo(mapInstance);

      return control;
    };

    this.updateMap = function () {
      console.log("updateMap method called!");
      originGroupLayer.clearLayers();
      destinationGroupLayer.clearLayers();

      let bounds = getCircleBounds();

      let originZoneInfo = {};
      originMapApp.getZoneLayer().eachLayer(function (layer) {
        originZoneInfo[layer.feature.properties.id] = {
          center: layer.getBounds().getCenter()
        };
      });
      let destinationZoneInfo = {};
      destinationMapApp.getZoneLayer().eachLayer(function (layer) {
        destinationZoneInfo[layer.feature.properties.id] = {
          center: layer.getBounds().getCenter()
        };
      });
      let createCircleMarker = function (position, indicator, color) {
        let boundRange = bounds.max - bounds.min === 0 ? 1 : bounds.max - bounds.min;
        let radius = minCircleSize + (indicator - bounds.min) * (maxCircleSize - minCircleSize) / boundRange;
        return L.circleMarker(position, {
          radius: radius,
          fillColor: color,
          weight: 0,
          opacity: 1,
          fillOpacity: 0.5,
          interactive: false
        });
      };

      originZones.forEach(function (item) {
        try {
          createCircleMarker(originZoneInfo[item.key].center, item.expansion_factor.value, "#FFFF00").addTo(originGroupLayer);
        } catch (error) {
          console.log(error);
        }
      });
      destinationZones.forEach(function (item) {
        try {
          createCircleMarker(destinationZoneInfo[item.key].center, item.expansion_factor.value, "#A900FF").addTo(destinationGroupLayer);
        } catch (error) {
          console.log(error);
        }
      });

      originMapLegend.update();
      destinationMapLegend.update();
    };

    let mapOptionBuilder = function (opts) {
      return {
        mapId: opts.mapId,
        hideMapLegend: true,
        showMetroStations: false,
        showMacroZones: false,
        defaultZoneStyle: function (feature) {
          let zoneId = feature.properties.id;
          let color = originSelected.has(zoneId) ? opts.selectedColor : opts.baseColor;
          let fillOpacity = originSelected.has(zoneId) ? 0.5 : 0.3;
          return {
            weight: 1,
            color: color,
            opacity: 0.5,
            dashArray: "1",
            fillOpacity: fillOpacity,
            fillColor: color
          };
        },
        onClickZone: function (e) {
          let layer = e.target;
          let zoneId = layer.feature.properties.id;
          if (opts.selectedZoneSet.has(zoneId)) {
            opts.selectedZoneSet.delete(zoneId);
            this.defaultOnMouseoutZone(e);
            this.defaultOnMouseinZone(e);
          } else {
            opts.selectedZoneSet.add(zoneId);
            layer.setStyle(this.styles.zoneWithColor(layer.feature, opts.selectedColor));
          }
        },
        onMouseinZone: function (e) {
          let layer = e.target;
          let zoneId = layer.feature.properties.id;
          if (!opts.selectedZoneSet.has(zoneId)) {
            this.defaultOnMouseinZone(e);
          }
          let zoneData = opts.getDataSource().find(function (el) {
            return el.key === zoneId;
          });
          this.refreshZoneInfoControl(layer.feature.properties, zoneData);
        },
        onMouseoutZone: function (e) {
          let layer = e.target;
          let zoneId = layer.feature.properties.id;
          if (!opts.selectedZoneSet.has(zoneId)) {
            this.defaultOnMouseoutZone(e);
          }
          this.refreshZoneInfoControl();
        }
      };
    };

    let originMapOpts = mapOptionBuilder({
      mapId: "mapChart",
      selectedZoneSet: originSelected,
      getDataSource: function () {
        return originZones;
      },
      baseColor: "#0000FF",
      selectedColor: "#d8d813"
    });
    let destinationMapOpts = mapOptionBuilder({
      mapId: "mapChart2",
      selectedZoneSet: destinationSelected,
      getDataSource: function () {
        return destinationZones;
      },
      baseColor: "#0000FF",
      selectedColor: "#9d2bdb"
    });
    let originMapApp = new MapApp(originMapOpts);
    let destinationMapApp = new MapApp(destinationMapOpts);

    // synchronize maps
    let originMap = originMapApp.getMapInstance();
    let destinationMap = destinationMapApp.getMapInstance();

    setMapLegend(originMap, originMapLegend, "circleMapLegend1").update();
    setMapLegend(destinationMap, destinationMapLegend, "circleMapLegend2").update();

    originMap.sync(destinationMap);
    destinationMap.sync(originMap);

    originGroupLayer.addTo(originMap);
    destinationGroupLayer.addTo(destinationMap);

    this.loadLayers = function (readyFunction) {
      originMapApp.loadLayers();
      destinationMapApp.loadLayers(readyFunction);
    };
  }

  function processData(data, app) {
    if (data.status) {
      return;
    }
    app.setData(data);
    app.updateMap();
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