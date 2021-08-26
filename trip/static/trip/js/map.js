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
  let maxZoom = opts.maxZoom || 22;
  let minZoom = opts.minZoom || 8;
  let maxBounds = opts.maxBounds || new mapboxgl.LngLatBounds(new mapboxgl.LngLat(-70.942223, -33.697721), new mapboxgl.LngLat(-70.357465, -33.178138));
  let showZones = opts.showZones === undefined ? true : opts.showZones;
  let showMetroStations = opts.showMetroStations === undefined ? true : opts.showMetroStations;
  let showMetroShapes = opts.showMetroShapes === undefined ? true : opts.showMetroShapes;
  let showTrainStations = opts.showTrainStations === undefined ? true : opts.showTrainStations;
  let showTrainShapes = opts.showTrainShapes === undefined ? true : opts.showTrainShapes;
  let showMacroZones = opts.showMacroZones === undefined ? true : opts.showMacroZones;
  let showCommunes = opts.showCommunes === undefined ? true : opts.showCommunes;
  let showLayerGroupControl = opts.showLayerGroupControl === undefined ? true : opts.showLayerGroupControl;
  let showRuleControl = opts.showRuleControl === undefined ? false : opts.showRuleControl;
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
  let fullscreenControl = opts.fullscreenControl === undefined ? false : opts.fullscreenControl;
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
    trackResize: true,
    logoPosition: 'bottom-right',
    preserveDrawingBuffer: true
  });

  map.on('load', () => {
    if (zoomControl) {
      let navigationControl = new mapboxgl.NavigationControl({});
      map.addControl(navigationControl, 'top-left');
    }
    if (scaleControl) {
      let scaleControl = new mapboxgl.ScaleControl({});
      map.addControl(scaleControl, 'bottom-left');
    }
    if (fullscreenControl) {
      map.addControl(new mapboxgl.FullscreenControl(), 'top-right')
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

    let subwayStationLayer = {
      id: 'subway-station-layer',
      source: 'subway-station-source',
      type: 'circle',
      layout: {
        'visibility': 'visible'
      },
      paint: {
        'circle-radius': 2,
        'circle-color': ['get', 'COLOR'],
        'circle-opacity': 1,
        'circle-stroke-color': '#000000',
        'circle-stroke-width': 1,
      }
    };
    let trainStationLayer = {
      id: 'train-station-layer',
      source: 'train-station-source',
      type: 'circle',
      layout: {
        'visibility': 'visible'
      },
      paint: {
        'circle-radius': 2,
        'circle-color': ['get', 'COLOR2'],
        'circle-opacity': 1,
        'circle-stroke-color': ['get', 'COLOR1'],
        'circle-stroke-width': 1,
      }
    };

    let subwayShapeLayer = {
      id: 'subway-shape-layer',
      source: 'subway-shape-source',
      type: 'line',
      layout: {
        'visibility': 'visible'
      },
      paint: {
        'line-color': ['get', 'COLOR'],
        'line-width': 4,
        'line-opacity': 0.3
      }
    };

    let trainShapeLayer = {
      id: 'train-shape-layer',
      source: 'train-shape-source',
      type: 'line',
      layout: {
        'visibility': 'visible'
      },
      paint: {
        'line-color': ['get', 'COLOR'],
        'line-width': 4,
        'line-opacity': 0.3
      }
    };

    let districtLayer = {
      id: 'district-layer',
      source: 'district-source',
      type: 'line',
      layout: {
        'visibility': 'visible'
      },
      paint: {
        'line-color': '#000000',
        'line-width': 1,
        'line-opacity': 0.3
      }
    };
    let communeLayer = {
      id: 'commune-layer',
      source: 'commune-source',
      type: 'line',
      layout: {
        'visibility': 'visible'
      },
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
      layout: {
        'visibility': 'visible'
      },
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
      layout: {
        'visibility': 'visible'
      },
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

    _self.getZoneSource = function () {
      return map.getSource('zones-source')._data;
    };

    _self.setZoneSource = function (newZoneSource) {
      map.getSource('zones-source').setData(newZoneSource);
    };

    _self.getZoneLayer = function () {
      return zoneLayer;
    };

    _self.setLayer = function (newZoneLayer) {
      map.removeLayer(newZoneLayer.id);
      map.addLayer(newZoneLayer);
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
      let zoneSource = {
        type: 'FeatureCollection',
        features: []
      };
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

      _self.setZoneSource(zoneSource);

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

    _self.addRuleControl = () => {
      class RuleControl {
        onAdd(map) {
          this._div = document.createElement('div');
          this._div.className = 'mapboxgl-ctrl legend noprint';
          this._div.innerHTML = `<button id="ruleButton" class="btn btn-default btn-sm" ><span class="fas fa-ruler-combined" aria-hidden="true"></span></button>`;
          return this._div;
        }
      }

      map.addControl(new RuleControl(), 'top-right');

      let ruleSource = {
        type: 'FeatureCollection',
        features: []
      };
      let ruleLayer = {
        id: 'rule-layer',
        source: 'rule-source',
        type: 'line',
        layout: {
          'line-cap': 'round',
          'line-join': 'round'
        },
        paint: {
          'line-color': '#2A3F54',
          'line-width': 2
        },
        filter: ['in', '$type', 'LineString']
      };
      let measurePointLayer = {
        id: 'measure-point-layer',
        type: 'circle',
        source: 'rule-source',
        paint: {
          'circle-radius': 4,
          'circle-color': '#2A3F54'
        },
        filter: ['in', '$type', 'Point']
      };
      let measurePointLabelLayer = {
        id: 'measure-point-label-layer',
        type: 'symbol',
        source: 'rule-source',
        layout: {
          'text-field': ['get', 'distance'],
          'text-offset': [0, 1],
          'text-size': 10
        },
        paint: {
          'text-color': '#2A3F54'
        },
        filter: ['in', '$type', 'Point']
      };

      let linestring = {
        'type': 'Feature',
        'geometry': {
          'type': 'LineString',
          'coordinates': []
        }
      };

      let clickEvent = (e) => {
        const features = map.queryRenderedFeatures(e.point, {layers: ['measure-point-layer']});
        if (ruleSource.features.length > 1) ruleSource.features.pop();

        if (features.length) {
          const id = features[0].properties.id;
          ruleSource.features = ruleSource.features.filter(
            (point) => point.properties.id !== id
          );
        } else {
          const point = {
            'type': 'Feature',
            'geometry': {
              'type': 'Point',
              'coordinates': [e.lngLat.lng, e.lngLat.lat]
            },
            'properties': {
              'id': String(new Date().getTime())
            }
          };

          ruleSource.features.push(point);
        }

        if (ruleSource.features.length > 1) {
          linestring.geometry.coordinates = ruleSource.features.map(
            (point) => point.geometry.coordinates
          );

          let distance = turf.length(linestring);
          distance = `${distance.toLocaleString()}km`;

          ruleSource.features[ruleSource.features.length - 1].properties.distance = distance;
          ruleSource.features.push(linestring);
        }

        map.getSource('rule-source').setData(ruleSource);
      };

      let mouseMoveEvent = (e) => {
        const features = map.queryRenderedFeatures(e.point, {layers: ['measure-point-label-layer', 'measure-point-layer']});
        map.getCanvas().style.cursor = features.length ? 'pointer' : 'crosshair';
      };

      let isEnable = false;
      $('#ruleButton').click(() => {
        if (isEnable) {
          // disable rule mode
          map.removeLayer(ruleLayer.id);
          map.removeLayer(measurePointLayer.id);
          map.removeLayer(measurePointLabelLayer.id);
          map.removeSource('rule-source')

          map.off('click', clickEvent);
          map.off('mousemove', mouseMoveEvent);
          map.getCanvas().style.cursor = 'grab';
          $('#ruleButton').removeClass('active');// esto no funciona
        } else {
          // enable rule mode
          ruleSource.features = [];
          map.addSource('rule-source', {type: 'geojson', data: ruleSource});
          map.addLayer(ruleLayer);
          map.addLayer(measurePointLayer);
          map.addLayer(measurePointLabelLayer);

          map.on('click', clickEvent);
          map.on('mousemove', mouseMoveEvent);
          $('#ruleButton').addClass('active');
        }
        isEnable = !isEnable;
      });
    };

    _self.addLayerGroupControl = (layerGroup) => {
      class LayerGroupControl {
        onAdd(map) {
          this._div = document.createElement('div');
          this._div.className = 'mapboxgl-ctrl info noprint';
          this._div.id = 'layerGroupContainer';
          this._div.innerHTML = `
            <img src="/static/trip/img/layersGroup.png">
            <div>
              <h5>Capas de datos disponibles</h5>
              <div id="layerGroupMenu"></div>
              <!-- <h5>Estilo de mapa disponibles</h5>
              <div class="btn-group" id="mapStyleGroupMenu" data-toggle="buttons"></div> -->
            </div>`;
          return this._div;
        }
      }

      map.addControl(new LayerGroupControl(), 'top-right');

      map.on('idle', () => {
        for (const key of Object.keys(layerGroup)) {
          let layers = layerGroup[key];
          if (document.getElementById(layers[0].id)) {
            continue;
          }

          const link = document.createElement('a');
          link.id = layers[0].id;
          link.href = '#';
          link.textContent = key;
          $(link).data('layerIds', layers.map(layer => layer.id));
          link.className = 'btn btn-xs btn-success active';
          link.onclick = function (e) {
            const clickedLayers = $(this).data('layerIds');
            e.preventDefault();
            e.stopPropagation();

            clickedLayers.forEach(layerId => {
              const visibility = map.getLayoutProperty(layerId, 'visibility');
              if (visibility === 'visible') {
                map.setLayoutProperty(layerId, 'visibility', 'none');
                this.className = 'btn btn-xs btn-dark';
              } else {
                this.className = 'btn btn-xs btn-success active';
                map.setLayoutProperty(layerId, 'visibility', 'visible');
              }
            });
          };

          const layersMenu = document.getElementById('layerGroupMenu');
          layersMenu.appendChild(link);
        }
        /*
        // add map style options
        const mapStyleMenu = document.getElementById('mapStyleGroupMenu');
        let styles = [
          {name: 'Satélite', id: 'satellite', style: 'mapbox://styles/mapbox/satellite-v9'},
          {name: 'Claro', id: 'light', style: 'mapbox://styles/mapbox/light-v10'},
          {name: 'Oscuro', id: 'dark', style: 'mapbox://styles/mapbox/dark-v10'},
          {name: 'Calles', id: 'streets', style: 'mapbox://styles/mapbox/streets-v11'},
        ];
        styles.forEach(el => {
          if (document.getElementById(el.id)) {
            return;
          }

          let styleRadioInput = document.createElement('input');
          styleRadioInput.type = 'radio';
          styleRadioInput.id = el.id;
          styleRadioInput.name = 'rtoggle';
          styleRadioInput.value = el.style;
          styleRadioInput.className = 'join-btn';

          let styleRadioLabel = document.createElement('label');
          styleRadioLabel.className = 'btn btn-dark';
          $(styleRadioLabel).append(styleRadioInput).append(el.name);
          mapStyleMenu.append(styleRadioLabel);

          $('input[name="rtoggle"]').change((e) => {

            let mapStyle = e.target.value;
            map.setStyle(mapStyle);
            map.once('styledata', () => {

            });
          });
        });*/
      });
    };

    _self.loadLayers = function (readyFunction) {
      function loadZoneGeoJSON() {
        let url = '/static/data/zones777.geojson';
        return $.getJSON(url, function (data) {
          data.features = data.features.map((feature) => {
            feature.id = feature.properties.id;
            return feature;
          });
          zoneGeoJSON = data;
          map.addSource('zones-source', {type: 'geojson', data: zoneGeoJSON});
        });
      }

      function loadSubwayStationGeoJSON() {
        let url = "/static/data/metro-estaciones.geojson";
        return $.getJSON(url, function (subwayStationSource) {
          map.addSource('subway-station-source', {type: 'geojson', data: subwayStationSource});
        });
      }

      function loadSubwayShapeGeoJSON() {
        let url = "/static/data/metro-lineas.geojson";
        return $.getJSON(url, function (subwayShapeSource) {
          map.addSource('subway-shape-source', {type: 'geojson', data: subwayShapeSource});
        });
      }

      function loadTrainStationGeoJSON() {
        let url = "/static/data/metrotren-estaciones.geojson";
        return $.getJSON(url, function (trainStationSource) {
          map.addSource('train-station-source', {type: 'geojson', data: trainStationSource});
        });
      }

      function loadTrainShapeGeoJSON() {
        let url = "/static/data/metrotren-lineas.geojson";
        return $.getJSON(url, function (trainShapeSource) {
          map.addSource('train-shape-source', {type: 'geojson', data: trainShapeSource});
        });
      }

      function loadDistrictGeoJSON() {
        let url = "/static/data/macrozonas.geojson";
        return $.getJSON(url, function (districtSource) {
          map.addSource('district-source', {type: 'geojson', data: districtSource});
        });
      }

      function loadCommuneGeoJSON() {
        let url = "/static/data/comunas.geojson";
        return $.getJSON(url, function (communeSource) {
          map.addSource('commune-source', {type: 'geojson', data: communeSource});
        });
      }

      let shapesToLoad = [];
      if (showZones) {
        shapesToLoad.push(loadZoneGeoJSON());
      }
      if (showMetroStations) {
        shapesToLoad.push(loadSubwayStationGeoJSON());
      }
      if (showMetroShapes) {
        shapesToLoad.push(loadSubwayShapeGeoJSON());
      }
      if (showTrainStations) {
        shapesToLoad.push(loadTrainStationGeoJSON());
      }
      if (showTrainShapes) {
        shapesToLoad.push(loadTrainShapeGeoJSON());
      }
      if (showMacroZones) {
        shapesToLoad.push(loadDistrictGeoJSON());
      }
      if (showCommunes) {
        shapesToLoad.push(loadCommuneGeoJSON());
      }

      $.when(...shapesToLoad)
        .done(function () {
          if (!hideZoneLegend) {
            setupMapInfoBar();
          }
          if (!hideMapLegend) {
            setupMapLegend();
          }
          if (showRuleControl) {
            _self.addRuleControl();
          }

          let layerMapping = {};
          if (showZones) {
            layerMapping['Zonas 777'] = [zoneLayer, zoneBorderLayer];
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
          }
          if (showMetroStations) {
            layerMapping['Estaciones de Metro'] = [subwayStationLayer];
            map.addLayer(subwayStationLayer)
          }
          if (showMetroShapes) {
            layerMapping['Líneas de Metro'] = [subwayShapeLayer];
            map.addLayer(subwayShapeLayer)
          }
          if (showTrainStations) {
            layerMapping['Estaciones de Metrotren'] = [trainStationLayer];
            map.addLayer(trainStationLayer)
          }
          if (showTrainShapes) {
            layerMapping['Líneas de Metrotren'] = [trainShapeLayer];
            map.addLayer(trainShapeLayer)
          }
          if (showMacroZones) {
            layerMapping['Macrozonas'] = [districtLayer];
            map.addLayer(districtLayer)
          }
          if (showCommunes) {
            layerMapping['Comunas'] = [communeLayer];
            map.addLayer(communeLayer)
          }

          if (Object.keys(layerMapping).length !== 0 && showLayerGroupControl) {
            _self.addLayerGroupControl(layerMapping);
          }

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
            if (['LineString', 'Polygon'].includes(feature.geometry.type)) {
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