"use strict";

function MapApp(opts) {
  let _self = this;

  // ============================================================================
  // MAP FEATURE STYLING
  // ============================================================================
  let getDataZoneById = opts.getDataZoneById || null;
  let getZoneValue = opts.getZoneValue || null;
  let getZoneColor = opts.getZoneColor || null;
  let mapId = opts.mapId || "mapChart";
  let maxZoom = opts.maxZoom || 15;
  let minZoom = opts.minZoom || 8;
  let maxBounds = opts.maxBounds || new mapboxgl.LngLatBounds(new mapboxgl.LngLat(-70.942223, -33.697721), new mapboxgl.LngLat(-70.357465, -33.178138));
  let showMetroStations = opts.showMetroStations === undefined ? true : opts.showMetroStations;
  let showMacroZones = opts.showMacroZones === undefined ? true : opts.showMacroZones;
  let selectedStyle = opts.tileLayer || "light";
  let mapStartLocation = opts.startLocation || new mapboxgl.LngLat(-70.645348, -33.459229);
  let onClickZone = opts.onClickZone || function (e) {
    _self.zoomToZoneEvent(e);
  };
  let onMousemoveZone = opts.onMousemoveZone || function (e) {
    _self.defaultOnMousemoveZone(e);
  };
  let onMouseleaveZone = opts.onMouseleaveZone || function (e) {
    _self.defaultOnMouseleaveZone(e);
  };
  let hideMapLegend = opts.hideMapLegend || false;
  let hideZoneLegend = opts.hideZoneLegend || false;
  let doubleClickZoom = opts.doubleClickZoom || false;
  let zoomControl = opts.zoomControl === undefined ? true : opts.zoomControl;
  let scaleControl = opts.scaleControl === undefined ? true : opts.scaleControl;
  let styles = {
    "streets": "mapbox://styles/mapbox/streets-v11",
    "light": "mapbox://styles/mapbox/light-v10",
    "dark": "mapbox://styles/mapbox/dark-v10"
  };
  selectedStyle = styles[selectedStyle];
  let onLoad = opts.onLoad || (() => {
  });

  /* map options */
  let mapboxAccessToken = "pk.eyJ1IjoiYWRhdHJhcCIsImEiOiJja29hdnk4aXYwM3lsMzJuMnhnNW1xb2RlIn0.Fvn0zCbCeXAjMYmDeEqMmw";
  mapboxgl.accessToken = mapboxAccessToken;
  let map = new mapboxgl.Map({
    container: mapId,
    center: mapStartLocation,
    zoom: minZoom,
    doubleClickZoom: doubleClickZoom,
    minZoom: minZoom,
    maxZoom: maxZoom,
    style: selectedStyle,
    trackResize: true
  });

  map.on('load', () => {
    if (zoomControl) {
      let navigationControl = new mapboxgl.NavigationControl({});
      map.addControl(navigationControl, 'top-left');
    }
    if (scaleControl) {
      let navigationControl = new mapboxgl.ScaleControl({});
      map.addControl(navigationControl, 'bottom-left');
    }

    map.setMaxBounds(maxBounds);

    let scales = {
      // http://colorbrewer2.org/#type=sequential&scheme=GnBu&n=5
      sequential: ["#ffffb2", "#fecc5c", "#fd8d3c", "#f03b20", "#bd0026"],
      // http://colorbrewer2.org/#type=diverging&scheme=Spectral&n=5
      divergent: ["#2b83ba", "#abdda4", "#ffffbf", "#fdae61", "#d7191c"]
    };

    let zoneGeoJSON = {
      type: 'FeatureCollection',
      features: []
    };

    let zoneSource = {
      type: 'FeatureCollection',
      features: []
    };
    let subwaySource = {
      type: 'FeatureCollection',
      features: []
    };
    let districtSource = {
      type: 'FeatureCollection',
      features: []
    };

    let subwayLayer = {
      id: 'subway-layer',
      source: 'subway-source',
      type: 'circle',
      layout: {},
      paint: {
        'circle-radius': 3,
        'circle-color': [
          'case',
          ['==', ['get', 'line'], 'MetroTren'], ['get', 'color2'],
          ['get', 'color']
        ],
        'circle-opacity': 1,
        'circle-stroke-color': [
          'case',
          ['==', ['get', 'line'], 'MetroTren'], ['get', 'color1'],
          '#000000'
        ],
        'circle-stroke-width': 1,
      }
    };
    let districtLayer = {
      id: 'district-layer',
      source: 'district-source',
      type: 'line',
      layout: {},
      paint: {
        'line-color': '#000000',
        'line-width': 1,
        'line-opacity': 0.3
      }
    };

    let zoneLayer = {
      id: 'zone-layer',
      source: 'zones-source',
      type: 'fill',
      paint: {
        'fill-color': [
          'case',
          ['boolean', ['get', 'isDestination'], false], 'black',
          ['boolean', ['feature-state', 'hover'], false], '#666',
          ['!=', ['get', 'color'], null], ['get', 'color'],
          '#D8D8D7'
        ],
        'fill-opacity': [
          'case',
          ['boolean', ['get', 'isDestination'], false], 0.6,
          ['boolean', ['feature-state', 'hover'], false], 0.4,
          0.3
        ]
      }
    };
    let zoneBorderLayer = {
      id: 'zone-border-layer',
      source: 'zones-source',
      type: 'line',
      paint: {
        'line-width': [
          'case',
          ['boolean', ['feature-state', 'hover'], false], 4,
          2
        ],
        'line-opacity': 1,
        'line-dasharray': [
          'case',
          ['boolean', ['feature-state', 'hover'], false], ['literal', [1, 0]],
          ['literal', [2, 2]]
        ],
        'line-color': [
          'case',
          ['boolean', ['feature-state', 'hover'], false], 'black',
          'white'
        ],
      }
    };

    let mapInfoBar = {};
    let mapLegend = {};

    _self.getMapInstance = function () {
      return map;
    };

    _self.getZoneLayer = function () {
      return zoneLayer;
    };

    _self.refreshZoneInfoControl = function (properties) {
      if (!hideZoneLegend) {
        mapInfoBar.update(properties);
      }
    };

    let defaultHoveredFeature = null;
    _self.defaultOnMousemoveZone = function (e) {
      let feature = e.features[0];
      if (defaultHoveredFeature == null || feature.id !== defaultHoveredFeature.id) {
        if (defaultHoveredFeature !== null) {
          map.setFeatureState({source: 'zones-source', id: defaultHoveredFeature.id}, {hover: false});
        }
        defaultHoveredFeature = feature;
        map.setFeatureState({source: 'zones-source', id: feature.id}, {hover: true});
        _self.refreshZoneInfoControl(feature.properties);
      }
    };

    _self.defaultOnMouseleaveZone = function (e) {
      map.setFeatureState({source: 'zones-source', id: defaultHoveredFeature.id}, {hover: false});
      _self.refreshZoneInfoControl(defaultHoveredFeature.properties);
      defaultHoveredFeature = null;
    };

    _self.zoomToZoneEvent = function (e) {
      let feature = e.features[0];
      let bounds = new mapboxgl.LngLatBounds();
      feature.geometry.coordinates.forEach((point) => {
        bounds.extend(point);
      });
      map.fitBounds(bounds, {
        maxZoom: 12
      });
    };

    _self.refreshMap = function (destinationZoneIds, scale, kpi, legendOpts) {
      console.log("refreshMap");
      zoneSource.features = [];
      zoneGeoJSON.features.forEach(function (feature) {
        let zoneId = feature.properties.id;
        if (destinationZoneIds.includes(zoneId)) {
          feature.properties.isDestination = true;
        } else {
          feature.properties.isDestination = false;
        }
        let zoneData = getDataZoneById(zoneId);
        let zoneColor = null;
        if (zoneData !== null) {
          let zoneValue = getZoneValue(zoneData, kpi);
          zoneColor = getZoneColor(zoneValue, kpi, scales[scale])
        }
        feature.properties.color = zoneColor === null ? '#D8D8D7' : zoneColor;
        feature.properties.data = zoneData;
        zoneSource.features.push(feature);
      });

      map.getSource('zones-source').setData(zoneSource);

      // add to map
      legendOpts.scale = scales[scale];
      mapLegend.update(legendOpts);
    };

    let setupMapInfoBar = function () {
      class MapInfoBar {
        onAdd(map) {
          this._div = document.createElement('div');
          this._div.className = 'mapboxgl-ctrl info';
          this.update();
          return this._div;
        }

        // method that we will use to update the control based on feature properties passed
        update(zoneProps) {
          this._div.innerHTML = "<h4>Zonificación 777</h4>";
          if (zoneProps && zoneProps.data !== undefined) {
            let zoneData = JSON.parse(zoneProps.data);
            this._div.innerHTML += "<b>Información de la zona " + zoneProps.id + "</b>";
            if (zoneData !== undefined && zoneData !== null) {
              this._div.innerHTML +=
                "<br/> - # Datos: " + zoneData.doc_count.toLocaleString() +
                "<br/> - # Viajes: " + zoneData.expansion_factor.value.toLocaleString() +
                "<br/> - # Etapas promedio: " + Number(zoneData.n_etapas.value.toFixed(2)).toLocaleString() +
                "<br/> - Duración promedio: " + Number(zoneData.tviaje.value.toFixed(1)).toLocaleString() + " [min]" +
                "<br/> - Distancia promedio (en ruta): " + Number((zoneData.distancia_ruta.value / 1000.0).toFixed(2)).toLocaleString() + " [km]" +
                "<br/> - Distancia promedio (euclideana): " + Number((zoneData.distancia_eucl.value / 1000.0).toFixed(2)).toLocaleString() + " [km]";
            } else {
              this._div.innerHTML += "<br/> Sin información para los filtros<br/> seleccionados";
            }
          } else {
            this._div.innerHTML += 'Pon el ratón sobre una zona';
          }
        }

        onRemove() {
          this._div.parentNode.removeChild(this._div);
        }
      }

      mapInfoBar = new MapInfoBar();
      map.addControl(mapInfoBar, 'top-right');
    };

    function setupMapLegend() {
      class MapLegend {
        onAdd(map) {
          this._div = document.createElement('div');
          this._div.className = 'mapboxgl-ctrl info legend';
          this._div.id = 'map_legend';
          return this._div;
        }

        update(options) {
          let name = options.name || '';
          let grades = options.grades;
          let grades_str = options.grades_str;
          let grades_post_str = options.legend_post_str;
          let scale = options.scale;

          // loop through our density intervals and generate a label with a colored square for each interval
          let div = document.getElementById("map_legend");
          div.innerHTML = name + "<br />";
          let i = 0;
          for (i = 0; i < grades.length - 1; i++) {
            div.innerHTML += "<i style='background:" + scale[i] + "'></i> " +
              grades_str[i] + "&ndash;" + grades_str[i + 1] + " " + grades_post_str;
            div.innerHTML += "<br />";
          }
          div.innerHTML += "<i style='background:" + scale[grades.length - 1] + "'></i> " +
            grades_str[i] + "+ " + grades_post_str;
          div.innerHTML += "<br><i style='background:" + "#cccccc" + "'></i>Sin Datos<br>";
        }

        onRemove() {
          this._div.parentNode.removeChild(this._div);
        }
      }

      mapLegend = new MapLegend();
      map.addControl(mapLegend, 'bottom-right');
    }

    _self.loadLayers = function (readyFunction) {
      function loadZoneGeoJSON() {
        let url = '/static/js/data/zones777.geojson';
        return $.getJSON(url, function (data) {
          data.features = data.features.map((feature) => {
            feature.id = feature.properties.id;
            return feature;
          });
          zoneGeoJSON = data;
          map.addSource('zones-source', {type: 'geojson', data: zoneGeoJSON});
          map.addLayer(zoneLayer);
          map.addLayer(zoneBorderLayer);
          map.on('mousemove', zoneLayer.id, (e) => {
            onMousemoveZone.call(_self, e);
          });
          map.on('mouseleave', zoneLayer.id, (e) => {
            onMouseleaveZone.call(_self, e);
          });
          map.on('click', zoneLayer.id, (e) => {
            onClickZone.call(_self, e);
          });
        });
      }

      function loadSubwayGeoJSON() {
        let url = "/static/js/data/metro.geojson";
        return $.getJSON(url, function (data) {
          subwaySource = data;
          map.addSource('subway-source', {type: 'geojson', data: subwaySource});
        });
      }

      function loadDistrictGeoJSON() {
        let url = "/static/js/data/comunas.geojson";
        return $.getJSON(url, function (data) {
          districtSource = data;
          map.addSource('district-source', {type: 'geojson', data: districtSource});
        });
      }

      let shapesToLoad = [loadZoneGeoJSON()];
      if (showMetroStations) {
        shapesToLoad.push(loadSubwayGeoJSON());
      }
      if (showMacroZones) {
        shapesToLoad.push(loadDistrictGeoJSON());
      }

      $.when(...shapesToLoad)
        .done(function () {
          if (!hideZoneLegend) {
            setupMapInfoBar();
          }
          if (!hideMapLegend) {
            setupMapLegend();
          }

          let controlMapping = {
            "Zonas 777": zoneLayer
          };
          if (showMetroStations) {
            controlMapping["Estaciones de Metro"] = subwayLayer;
            map.addLayer(subwayLayer)
          }
          if (showMacroZones) {
            controlMapping["Comunas"] = districtLayer;
            map.addLayer(districtLayer)
          }

          /*
          hay que poner los checkbox en la pantalla
          para poder ocultar o mostrar las capas
          */

          if (readyFunction !== undefined) {
            readyFunction();
          }
        });
    };

    _self.fitBound = function (sourceList) {
      let bounds = null;
      sourceList.forEach(sourceName => {
        let geojson = map.getSource(sourceName)._data;
        if (geojson.type === 'FeatureCollection') {
          geojson.features.forEach(feature => {
            if (bounds === null) {
              bounds = new mapboxgl.LngLatBounds();
            }
            if (feature.geometry.type === 'LineString') {
              feature.geometry.coordinates.forEach(point => {
                bounds.extend(point);
              });
            } else if (feature.geometry.type === 'Point') {
              bounds.extend(feature.geometry.coordinates);
            }
          });
        }
      });

      if (bounds !== null) {
        map.fitBounds(bounds, {
          padding: 20
        });
      }
    };

    _self.resize = function () {
      map.resize();
    }

    onLoad(map, _self);
  });
}