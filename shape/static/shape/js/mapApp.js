"use strict";
$(document).ready(function () {
  let reA = /[^a-zA-Z]/g;
  let reN = /[^0-9]/g;

  const sortAlphaNum = (a, b) => {
    let aA = a.replace(reA, "");
    let bA = b.replace(reA, "");
    if (aA === bA) {
      let aN = parseInt(a.replace(reN, ""), 10);
      let bN = parseInt(b.replace(reN, ""), 10);
      return aN === bN ? 0 : aN > bN ? 1 : -1;
    } else {
      return aA > bA ? 1 : -1;
    }
  };

  const getRandomColor = (index) => {
    index = index - 1;
    if (typeof index === 'number' && 0 <= index && index <= 9) {
      const staticColors = ["#E50909", "#1226E8", "#207A08", "#000000", "#EA7E07", "#0FBFD9", "#9825E7", "#7AEA21", "#82838B", "#CDCC0A"];
      return staticColors[index];
    }

    const letters = "0123456789ABCDEF";
    let color = "#";
    for (let i = 0; i < 6; i++) {
      color += letters[Math.floor(Math.random() * 16)];
    }

    return color;
  };

  function MapShapeApp() {
    let _self = this;
    let selectorId = 1;
    let selectorStopId = 1;
    let routeLegendControl = null;
    let routeControl = null;
    let stopLegendControl = null;
    let stopControl = null;
    let isAddingRouteRow = false;

    this.addShapeLayers = (layerId, shapeStopsSource, shapeSource, previousLayerId) => {
      if (previousLayerId !== null) {
        previousLayerId = `shape-${previousLayerId}`;
      }

      shapeStopsSource = {
        type: "FeatureCollection",
        features: shapeStopsSource
      };
      shapeSource = {
        type: "FeatureCollection",
        features: shapeSource
      };

      let shapeLayerTemplate = {
        id: 'shape-layer',
        source: 'shape-source',
        type: 'line',
        layout: {
          'line-join': 'round',
          'line-cap': 'round'
        },
        paint: {
          'line-color': ['get', 'color'],
          'line-width': 2
        }
      };
      let shapeStopsLayerTemplate = {
        id: 'shape-stops-layer',
        source: 'shape-stops-source',
        type: 'circle',
        paint: {
          'circle-radius': ['interpolate', ['linear'], ['zoom'],
            12, 3,
            14, 6,
            20, 12,
          ],
          'circle-color': ['get', 'color']
        }
      };
      let shapeStopLabelLayerTemplate = {
        id: 'shape-stop-label-layer',
        source: 'shape-stops-source',
        type: 'symbol',
        layout: {
          'text-field': '{userStopCode}',
          'text-size': 10,
          'text-offset': [0, 1]
        }
      };
      let shapeArrowLayerTemplate = {
        id: 'shape-arrow-layer',
        type: 'symbol',
        source: 'shape-source',
        layout: {
          'symbol-placement': 'line',
          'symbol-spacing': 100,
          'icon-allow-overlap': true,
          'icon-ignore-placement': true,
          'icon-image': 'double-arrow',
          'icon-size': 0.4,
          'visibility': 'visible'
        },
        paint: {
          'icon-color': ['get', 'color'],
          'icon-halo-color': '#fff',
          'icon-halo-width': 2,
        }
      };

      _self.removeShapeLayers(layerId);

      let shapeLayer = $.extend({}, shapeLayerTemplate);
      let shapeArrowLayer = $.extend({}, shapeArrowLayerTemplate);
      let shapeStopsLayer = $.extend({}, shapeStopsLayerTemplate);
      let shapeStopLabelLayer = $.extend({}, shapeStopLabelLayerTemplate);

      shapeLayer.id = `shape-${layerId}`;
      shapeLayer.source = `shape-source-${layerId}`;
      shapeArrowLayer.id = `shape-arrow-${layerId}`;
      shapeArrowLayer.source = `shape-source-${layerId}`;

      shapeStopsLayer.id = `shape-stops-${layerId}`;
      shapeStopsLayer.source = `shape-stops-source-${layerId}`;
      shapeStopLabelLayer.id = `shape-stop-label-${layerId}`;
      shapeStopLabelLayer.source = `shape-stops-source-${layerId}`;

      _mapApp.getMapInstance().addSource(`shape-source-${layerId}`, {type: 'geojson', data: shapeSource});
      _mapApp.getMapInstance().addSource(`shape-stops-source-${layerId}`, {
        type: 'geojson',
        data: shapeStopsSource
      });

      _mapApp.getMapInstance().addLayer(shapeStopLabelLayer, previousLayerId);
      _mapApp.getMapInstance().addLayer(shapeStopsLayer, shapeStopLabelLayer.id);
      _mapApp.getMapInstance().addLayer(shapeArrowLayer, shapeStopsLayer.id);
      _mapApp.getMapInstance().addLayer(shapeLayer, shapeArrowLayer.id);

      let openStopPopup = function (feature) {
        let popUpDescription = "<p>";
        popUpDescription += " Servicio: <b>" + feature.properties.route + "</b><br />";
        popUpDescription += " Nombre: <b>" + feature.properties.stopName + "</b><br />";
        popUpDescription += " Código transantiago: <b>" + feature.properties.authStopCode + "</b><br />";
        popUpDescription += " Código usuario: <b>" + feature.properties.userStopCode + "</b><br />";
        popUpDescription += " Posición en la ruta: <b>" + (feature.properties.order + 1) + "</b><br />";
        popUpDescription += " Servicios que se detienen: <b>" + feature.properties.routes + "</b><br />";
        popUpDescription += "</p>";

        new mapboxgl.Popup({closeOnClick: false}).setLngLat(feature.geometry.coordinates).setHTML(popUpDescription).addTo(_mapApp.getMapInstance());
      };

      let mouseenter = () => {
        _mapApp.getMapInstance().getCanvas().style.cursor = 'pointer';
      };
      let mouseleave = () => {
        _mapApp.getMapInstance().getCanvas().style.cursor = '';
      };
      let click = e => {
        console.log("opening popup...");
        let feature = e.features[0];
        openStopPopup(feature);
      };

      _mapApp.getMapInstance().on('mouseenter', shapeStopsLayer.id, mouseenter);
      _mapApp.getMapInstance().on('mouseleave', shapeStopsLayer.id, mouseleave);
      _mapApp.getMapInstance().on('click', shapeStopsLayer.id, click);

      _mapApp.getMapInstance().on('mouseenter', shapeStopLabelLayer.id, mouseenter);
      _mapApp.getMapInstance().on('mouseleave', shapeStopLabelLayer.id, mouseleave);
      _mapApp.getMapInstance().on('click', shapeStopLabelLayer.id, click);
    };

    this.addStopLayers = (layerId, stopsSource) => {
      stopsSource = {
        type: "FeatureCollection",
        features: stopsSource
      };

      let stopsLayerTemplate = {
        id: 'stops-layer',
        source: 'stops-source',
        type: 'circle',
        paint: {
          'circle-radius': ['interpolate', ['linear'], ['zoom'],
            12, 2,
            14, 4,
            20, 8,
          ],
          'circle-color': ['get', 'color']
        }
      };
      let stopLabelLayerTemplate = {
        id: 'stop-label-layer',
        source: 'stops-source',
        type: 'symbol',
        layout: {
          'text-field': '{userStopCode}',
          'text-size': 10,
          'text-offset': [0, 1]
        }
      };
      _self.removeStopLayers(layerId);

      let stopsLayer = $.extend({}, stopsLayerTemplate);
      let stopLabelLayer = $.extend({}, stopLabelLayerTemplate);

      stopsLayer.id = `stops-${layerId}`;
      stopsLayer.source = `stops-source-${layerId}`;
      stopLabelLayer.id = `stop-label-${layerId}`;
      stopLabelLayer.source = `stops-source-${layerId}`;

      _mapApp.getMapInstance().addSource(`stops-source-${layerId}`, {type: 'geojson', data: stopsSource});
      _mapApp.getMapInstance().addLayer(stopsLayer);
      _mapApp.getMapInstance().addLayer(stopLabelLayer);

      let openStopPopup = function (feature) {
        let popUpDescription = "<p>";
        popUpDescription += " Nombre: <b>" + feature.properties.stopName + "</b><br />";
        popUpDescription += " Código transantiago: <b>" + feature.properties.authStopCode + "</b><br />";
        popUpDescription += " Código usuario: <b>" + feature.properties.userStopCode + "</b><br />";
        popUpDescription += " Posición: <b>" + feature.properties.latitude + "," + feature.properties.longitude + "</b><br />";
        popUpDescription += " Servicios que se detienen: <b>" + feature.properties.routes + "</b><br />";
        popUpDescription += "</p>";

        new mapboxgl.Popup({closeOnClick: false}).setLngLat(feature.geometry.coordinates).setHTML(popUpDescription).addTo(_mapApp.getMapInstance());
      };

      let mouseenter = () => {
        _mapApp.getMapInstance().getCanvas().style.cursor = 'pointer';
      };
      let mouseleave = () => {
        _mapApp.getMapInstance().getCanvas().style.cursor = '';
      };
      let click = e => {
        let feature = e.features[0];
        openStopPopup(feature);
      };

      _mapApp.getMapInstance().on('mouseenter', stopsLayer.id, mouseenter);
      _mapApp.getMapInstance().on('mouseleave', stopsLayer.id, mouseleave);
      _mapApp.getMapInstance().on('click', stopsLayer.id, click);

      _mapApp.getMapInstance().on('mouseenter', stopLabelLayer.id, mouseenter);
      _mapApp.getMapInstance().on('mouseleave', stopLabelLayer.id, mouseleave);
      _mapApp.getMapInstance().on('click', stopLabelLayer.id, click);

    };

    this.removeShapeLayers = (layerId) => {
      // remove data
      if (_mapApp.getMapInstance().getLayer(`shape-${layerId}`)) {
        _mapApp.getMapInstance().removeLayer(`shape-${layerId}`);
        _mapApp.getMapInstance().removeLayer(`shape-stops-${layerId}`);
        _mapApp.getMapInstance().removeLayer(`shape-stop-label-${layerId}`);
        _mapApp.getMapInstance().removeLayer(`shape-arrow-${layerId}`);

        _mapApp.getMapInstance().removeSource(`shape-source-${layerId}`);
        _mapApp.getMapInstance().removeSource(`shape-stops-source-${layerId}`);
      }
    };

    this.removeStopLayers = (layerId) => {
      // remove data
      if (_mapApp.getMapInstance().getLayer(`stops-${layerId}`)) {
        _mapApp.getMapInstance().removeLayer(`stops-${layerId}`);
        _mapApp.getMapInstance().removeLayer(`stop-label-${layerId}`);
        _mapApp.getMapInstance().removeSource(`stops-source-${layerId}`);
      }
    };

    this.setShapeLayerVisibility = (layerId, show) => {
      let visible = show ? 'visible' : 'none';
      _mapApp.getMapInstance().setLayoutProperty(`shape-${layerId}`, 'visibility', visible);
      _mapApp.getMapInstance().setLayoutProperty(`shape-arrow-${layerId}`, 'visibility', visible);
    };

    this.setShapeStopLayerVisibility = (layerId, show) => {
      let visible = show ? 'visible' : 'none';
      _mapApp.getMapInstance().setLayoutProperty(`shape-stops-${layerId}`, 'visibility', visible);
    };

    this.setShapeStopLabelLayerVisibility = (layerId, show) => {
      let visible = show ? 'visible' : 'none';
      _mapApp.getMapInstance().setLayoutProperty(`shape-stop-label-${layerId}`, 'visibility', visible);
    };

    this.addHelpControl = (mapInstance) => {
      class HelpControl {
        onAdd(map) {
          let div = document.createElement('div');
          div.className = 'mapboxgl-ctrl legend noprint';
          div.innerHTML = `<button id="helpButton" class="btn btn-default btn-sm" ><span class="fas fa-info" aria-hidden="true"></span></button>`;
          return div;
        }

        onRemove() {
          // nothing
        }
      }

      mapInstance.addControl(new HelpControl(), 'top-right');
    };

    this.addOperationInfoControl = (mapInstance) => {
      class OperationInfoControl {
        onAdd(map) {
          let div = document.createElement('div');
          div.className = 'mapboxgl-ctrl legend noprint';
          div.innerHTML = `
            <button id="operationInfoButton" class="btn btn-default btn-sm" >
              <span class="fas fa-bus-alt" aria-hidden="true"></span> <span class="fas fa-info" aria-hidden="true"></span> Datos operacionales
            </button>`;
          return div;
        }

        onRemove() {
          // nothing
        }
      }

      mapInstance.addControl(new OperationInfoControl(), 'top-left');
    };


    this.addRouteListControl = (mapInstance) => {
      class RouteListControl {
        onAdd(map) {
          let div = document.createElement('div');
          div.className = 'mapboxgl-ctrl info noprint';
          div.id = 'listControl';
          div.innerHTML += `
            <button id="addRouteInMapButton" class="btn btn-default btn-sm" >
              <span class="fas fa-bus-alt" aria-hidden="true"></span> Rutas en mapa
            </button>`;
          return div;
        }
      }

      mapInstance.addControl(new RouteListControl(), 'top-left');
    };

    this.addStopListControl = (mapInstance) => {
      class StopListControl {
        onAdd(map) {
          let div = document.createElement('div');
          div.className = 'mapboxgl-ctrl info noprint';
          div.id = 'stopListControl';
          div.innerHTML += `
            <button id="addStopInMapButton" class="btn btn-default btn-sm" >
              <span class="fas fa-traffic-light" aria-hidden="true"></span> Paradas en mapa
            </button>`;
          return div;
        }
      }

      mapInstance.addControl(new StopListControl(), 'top-left');
    }

    this.addBearingControl = (mapInstance) => {
      class BearingControl {
        onAdd(map) {
          this._map = map;
          this._div = document.createElement('canvas');
          this._div.className = 'mapboxgl-ctrl info legend';
          this._div.width = 43;
          this._div.height = 43;
          this._div.id = 'bearingControl';
          return this._div;
        }

        drawArrowToNorth(ctx, fromX, fromY, mapAngle) {
          let distance = 7;
          let angle = -90 + -1 * mapAngle;
          let angleInRadians = angle * Math.PI / 180;
          let headLength = 3; // length of head in pixels
          let toX = fromX + distance * Math.cos(angleInRadians);
          let toY = fromY + distance * Math.sin(angleInRadians);

          ctx.beginPath();
          ctx.moveTo(fromX, fromY);
          ctx.lineTo(toX, toY);
          ctx.moveTo(toX, toY);
          ctx.lineTo(toX - headLength * Math.cos(angleInRadians - Math.PI / 6), toY - headLength * Math.sin(angleInRadians - Math.PI / 6));
          ctx.moveTo(toX, toY);
          ctx.lineTo(toX - headLength * Math.cos(angleInRadians + Math.PI / 6), toY - headLength * Math.sin(angleInRadians + Math.PI / 6));

          ctx.font = '11px serif';
          let offsetX = (distance + 4) * Math.cos(angleInRadians);
          let offsetY = (distance + 4) * Math.sin(angleInRadians);

          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.strokeText('N', fromX + offsetX, fromY + offsetY);

          let radius = 2
          ctx.moveTo(fromX + radius, fromY);
          ctx.arc(fromX, fromY, radius, 0, 2 * Math.PI);
          ctx.stroke();

          radius = 20
          ctx.moveTo(fromX + radius, fromY);
          ctx.arc(fromX, fromY, radius, 0, 2 * Math.PI);
          ctx.stroke();
        }

        update() {
          this._div.style.display = "none";
          let ctx = this._div.getContext("2d");
          ctx.clearRect(0, 0, this._div.width, this._div.height);
          this.drawArrowToNorth(ctx, 21, 21, this._map.getBearing());
          this._div.style.display = "inline";
        }
      }

      let bearingControl = new BearingControl();
      mapInstance.addControl(bearingControl, 'bottom-left');
      bearingControl.update();
      mapInstance.on('rotate', () => {
        bearingControl.update();
      });
    }

    this.addScreenshotControl = (mapInstance) => {
      class ScreenshotControl {
        onAdd(map) {
          let div = document.createElement('div');
          div.className = 'mapboxgl-ctrl legend noprint';
          div.innerHTML = `<button id="screenshotButton" class="btn btn-default btn-sm" ><span class="fas fa-camera" aria-hidden="true"></span></button>`;
          return div;
        }

        update() {
          $('#screenshotButton').click(() => {
            html2canvas(document.getElementById('mapid')).then(canvas => {
              let link = document.createElement("a");
              document.body.appendChild(link);
              link.download = "imagen.png";
              link.href = canvas.toDataURL("image/png");
              link.target = '_blank';
              link.click();
            });
          });
        }
      }

      let screenshotControl = new ScreenshotControl();
      mapInstance.addControl(screenshotControl, 'top-right');
      screenshotControl.update();
    };

    this.addRouteLegendControl = (mapInstance) => {
      class RouteLegendControl {
        onAdd(map) {
          this._div = document.createElement('div');
          this._div.className = 'mapboxgl-ctrl info legend';
          this._div.id = 'routeLegendControl';
          this._div.style.display = "none";
          this._div.width = 230;
          this._div.innerHTML = `
            <table>
              <thead>
                <th>Color</th>
                <th>P. operación</th>
                <th>Unidad de Servicio</th>
                <th>Servicio</th>
              </thead>
              <tbody id='routeLegendTable'>
              </tbody>
            </table>`;
          return this._div;
        }

        setRouteColorCanvas(canvasId, color) {
          let canvas = document.getElementById(canvasId);
          canvas.width = 40;
          canvas.height = 10;
          let ctx = canvas.getContext("2d");
          ctx.fillStyle = color;
          ctx.fillRect(0, 0, canvas.width, canvas.height);
        }

        update() {
          let rows = $('#routeListContainer tr');
          this._div.style.display = "none";

          if (rows.length > 0) {
            // remove previous rows
            $("#routeLegendTable").empty();

            rows.each((index, el) => {
              let id = $(el).data('id');
              let opDate = $(`#dateSelect-${id}`).val();
              let operator = $(`#operatorSelect-${id}`).val();
              let userRoute = $(`#userRouteSelect-${id}`).val();
              let authRoute = $(`#routeSelect-${id}`).val();
              let color = $(`#colorSelect-${id}`).colorpicker('getValue');
              let canvasId = `canvas-${id}`;

              let legendRow = `<tr>
                <td><canvas id="${canvasId}"></canvas></td>
                <td>${opDate}</td>
                <td>${operator}</td>
                <td>${userRoute} (${authRoute})</td>
              </tr>`;
              $('#routeLegendTable').append(legendRow);
              this.setRouteColorCanvas(canvasId, color);
            });

            this._div.style.display = "inline";
          }
        }
      }

      let routeLegendControl = new RouteLegendControl();
      mapInstance.addControl(routeLegendControl, 'bottom-right');
      routeLegendControl.update();
      return routeLegendControl;
    };

    /**
     * Define and create a RouteControl instance.
     * This class have the route control selectors.
     * @param mapInstance
     * @returns {RouteControl} a new instance of this class
     */
    this.addRouteControl = (mapInstance) => {
      class RouteControl {
        onAdd(map) {
          this._div = document.createElement('div');
          this._div.className = 'mapboxgl-ctrl info legend';
          this._div.id = 'routeControl';
          this._div.style.display = "none";
          this._div.width = 230;
          this._div.innerHTML = `
            <div class='row'>
              <div class='col-lg-12'>
                <button id='backToRouteControl' class='btn btn-default btn-sm'>
                  <span class='fas fa-minus' aria-hidden='true'></span>
                  Minimizar
                </button>
                <button id='addRouteButton' class='btn btn-default btn-sm'>
                  <span class='fas fa-plus' aria-hidden='true'></span>
                   Agregar ruta
                </button>
              </div>
            </div>
            <div class='row' >
              <div class='col-lg-12'>
                <table class='table table-condensed'>
                  <thead>
                  	<th></th>
                  	<th></th>
                    <th>Fecha PO</th>
                    <th>Unidad de Servicio</th>
                    <th>Servicio</th>
                    <th>Servicio TS</th>
                    <th></th><th></th><th></th><th></th>
                  </thead>
                  <tbody id='routeListContainer'>
                  </tbody>
                </table>
              </div>
            </div>`;
          return this._div;
        }

        show() {
          this._div.style.display = "inline";
          if ($("#routeListContainer").children().length === 0) {
            $("#addRouteButton").trigger("click");
          }
        }


        hide() {
          this._div.style.display = "none";
        }
      }

      let routeControl = new RouteControl();
      mapInstance.addControl(routeControl, 'top-left');
      return routeControl;
    }

    /**
     * Add a stop legend to map instance.
     * @param mapInstance
     * @returns {StopLegendControl}
     */
    this.addStopLegendControl = (mapInstance) => {
      class StopLegendControl {
        onAdd(map) {
          this._div = document.createElement('div');
          this._div.className = 'mapboxgl-ctrl info legend';
          this._div.id = 'stopLegendControl';
          this._div.style.display = "none";
          this._div.width = 230;
          this._div.innerHTML = `
            <table>
              <thead>
                <th>Color</th>
                <th> P. operación</th>
                <th> C. de Usuario</th>
                <th> Código TS</th>
                <th> Nombre de Parada</th>
              </thead>
              <tbody id='stopLegendTable'>
              </tbody>
            </table>`;
          return this._div;
        }

        setRouteColorCanvas(canvasId, color) {
          let canvas = document.getElementById(canvasId);
          canvas.width = 40;
          canvas.height = 10;
          let ctx = canvas.getContext("2d");
          ctx.fillStyle = color;
          ctx.fillRect(0, 0, canvas.width, canvas.height);
        }

        update() {
          let rows = $('#stopListContainer tr');
          this._div.style.display = "none";

          if (rows.length > 0) {
            // remove previous rows
            $("#stopLegendTable").empty();
            rows.each((index, el) => {
              const id = $(el).data('id');
              const source = _mapApp.getMapInstance().getSource(`stops-source-${id}`)
              if (source) {
                const data = source._data.features;
                const isSingleStop = data.length === 1;
                const canvasId = `stop-canvas-${id}`;
                const stopDate = $(`#stopDateSelect-${id}`).val();
                const userStopCode = isSingleStop ? data[0].properties.userStopCode : "Todas las paradas";
                const stopName = isSingleStop ? data[0].properties.stopName : "";
                const authStopCode = isSingleStop ? data[0].properties.authStopCode : "";
                const color = $(`#stopColorSelect-${id}`).colorpicker('getValue');
                const legendRow = `<tr>
                                <td><canvas id="${canvasId}"></canvas></td>
                                <td>${stopDate}</td>
                                <td>${userStopCode}</td>
                                <td>${authStopCode}</td>
                                <td>${stopName}</td>
                              </tr>`;
                $('#stopLegendTable').append(legendRow);
                this.setRouteColorCanvas(canvasId, color);
              }
            });

            this._div.style.display = "inline";
          }
        }
      }

      let stopLegendControl = new StopLegendControl();
      mapInstance.addControl(stopLegendControl, 'bottom-right');
      stopLegendControl.update();
      return stopLegendControl;
    };

    /**
     * Define and create a StopControl instance.
     * This class have the stop control selectors.
     * @param mapInstance
     * @returns {StopControl} a new instance of this class
     */
    this.addStopControl = (mapInstance) => {
      class StopControl {
        onAdd(map) {
          this._div = document.createElement('div');
          this._div.className = 'mapboxgl-ctrl info legend';
          this._div.id = 'stopControl';
          this._div.style.display = "none";
          this._div.width = 230;
          this._div.innerHTML = `
            <div class='row'>
              <div class='col-lg-12'>
                <button id='backToStopControl' class='btn btn-default btn-sm'>
                  <span class='fas fa-minus' aria-hidden='true'></span>
                  Minimizar
                </button>
                <button id='addStopButton' class='btn btn-default btn-sm'>
                  <span class='fas fa-plus' aria-hidden='true'></span>
                   Agregar parada
                </button>
              </div>
            </div>
            <div class='row' >
              <div class='col-lg-12'>
                <table class='table table-condensed'>
                  <thead>
                  	<th></th>
                    <th>Fecha PO</th>
                    <th>Parada</th>
                    <th>Color</th>
                    <th></th><th></th><th></th><th></th>
                  </thead>
                  <tbody id='stopListContainer'>
                  </tbody>
                </table>
              </div>
            </div>`;
          return this._div;
        }

        show() {
          this._div.style.display = "inline";
          if ($("#stopListContainer").children().length === 0) {
            $("#addStopButton").trigger("click");
          }
        }

        hide() {
          this._div.style.display = "none";
        }
      }

      let stopControl = new StopControl();
      mapInstance.addControl(stopControl, 'top-left');
      return stopControl;
    }


    this.loadBaseData = () => {
      $.getJSON(Urls["esapi:shapeBase"](), function (data) {
        // data for selectors
        let currentDate = data.dates[0]
        _self.dates_period_dict = data.dates_periods_dict;
        _self.op_routes_dict = data.op_routes_dict;
        _self.periods = data.periods;
        let operatorList = Object.keys(data.op_routes_dict[currentDate])
        let currentOperator = operatorList[0];
        operatorList = operatorList.map(e => ({id: e, text: e}));
        let userRouteList = (Object.keys(data.op_routes_dict[currentDate][currentOperator]).sort(sortAlphaNum));
        userRouteList = userRouteList.map(e => ({id: e, text: e}));
        let dateList = data.dates.map(e => ({id: e, text: e}));

        // activate add button when data exist
        $("#addRouteButton").click(function () {
          _self.addRow(dateList, operatorList, userRouteList);
        });
        $("#addStopButton").click(function () {
          _self.addStopRow(dateList);
        });
      });

      _self.addTableInfo();
    };

    this.enableEvents = () => {
      $("#helpButton").click(function () {
        $("#helpModal").modal("show");
      });
      $("#addRouteInMapButton").click(function () {
        $(this).css("display", "none")
        routeControl.show();
      });
      $("#backToRouteControl").click(function () {
        routeControl.hide();
        $("#addRouteInMapButton").css("display", "inline");
      });

      $("#addStopInMapButton").click(function () {
        $(this).css("display", "none");
        stopControl.show();
      });

      $("#backToStopControl").click(function () {
        stopControl.hide();
        $("#addStopInMapButton").css("display", "inline");
      });

      $("#operationInfoButton").click(function () {
        let routeSelector = $("#routeListContainer");
        let periodInfoList = [];
        let requestList = [];
        let uniqueInfoSet = new Set();

        routeSelector.children().each(function (index, el) {
          let routeText = $(el).closest(".selectorRow").find(".route option:selected").text();
          let route = routeText.substring(routeText.indexOf("(") + 1, routeText.indexOf(")"));
          route = route.split(",")[0];
          let userRoute = $(el).closest(".selectorRow").find(".userRoute").val();
          let date = $(el).closest(".selectorRow").find(".date").val();
          date = date !== null ? [[date]] : [[]];
          let params = {
            opRouteCode: route,
            dates: JSON.stringify(date)
          };
          let info = date[0][0] + route;
          if (!uniqueInfoSet.has(info)) {
            uniqueInfoSet.add(info);
            requestList.push(
              $.getJSON(Urls["esapi:opdataAuthRoute"](), params, function (data) {
                if (data.status) {
                  showMessage(data.status);
                } else {
                  Object.entries(data["data"]).forEach(([key, value]) => {
                    value["authRoute"] = routeText;
                    value["userRoute"] = userRoute;
                    value["date"] = date[0][0];
                    value["periodId"] = key;
                    periodInfoList.push(value);
                  });
                }
              })
            );
          }
        });
        $.when(...requestList).then(
          function () {
            let $INFOMODAL = $("#shape_info");
            $INFOMODAL.modal("show");
            $INFOMODAL.on('shown.bs.modal', function () {
              let $TABLE = $('#shapeDetail').DataTable();
              $TABLE.clear();
              for (const value of Object.values(periodInfoList)) {
                $TABLE.rows.add([value]);
              }
              $TABLE.draw();
              $TABLE.columns.adjust();
              $(this).off('shown.bs.modal');
            });
          }
        );
      });
    };

    this.addRow = function (dateList, operatorList, userRouteList) {
      _self.isAddingRouteRow = true;
      let newId = selectorId;
      selectorId++;
      let row = `
        <tr class="selectorRow" data-id="${newId}">
            <td><i class="fas fa-bars fa-2x"></i></td>
            <td><button class="btn btn-danger btn-sm" ><span class="fas fa-trash-alt" aria-hidden="true"></span></button></td>
            <td><select id=dateSelect-${newId} class="form-control date"></select></td>
            <td><select id=operatorSelect-${newId} class="form-control operator"></select></td>
            <td><select id=userRouteSelect-${newId} class="form-control userRoute"></select></td>
            <td><select id=routeSelect-${newId} class="form-control route"></select></td>
            <td><button id=colorSelect-${newId} class="btn btn-default btn-sm color-button" ><span class="fas fa-tint" aria-hidden="true"></span></button></td>
            <td><button id=visibilityRoutes-${newId} class="btn btn-success btn-sm visibility-routes" ><span class="fas fa-route" aria-hidden="true"></span></button></td>
            <td><button id=visibilityStops-${newId} class="btn btn-success btn-sm visibility-stops" ><span class="fas fa-traffic-light" aria-hidden="true"></span></button></td>
            <td><button id=visibilityUserStopLabels-${newId} class="btn btn-success btn-sm visibility-user-stops" ><span class="fas fa-user-tag" aria-hidden="true"></span></button></td>
        </tr>`;

      $("#routeListContainer").append(row);
      $(`#dateSelect-${newId}`).select2({
        width: 'auto',
        data: dateList,
        dropdownParent: $('#routeListContainer').parent()
      });
      $(`#operatorSelect-${newId}`).select2({
        width: 'auto',
        data: operatorList,
        dropdownParent: $('#routeListContainer').parent()
      });
      $(`#userRouteSelect-${newId}`).select2({
        width: 'auto',
        data: userRouteList,
        dropdownParent: $('#routeListContainer').parent()
      });
      $(`#routeSelect-${newId}`).select2({width: 'auto', dropdownParent: $('#routeListContainer').parent()});

      _self.refreshControlEvents(newId);
      _self.refreshRemoveButton();
      _self.refreshColorPickerButton();
      _self.refreshVisibilityRoutesButton();
      _self.refreshVisibilityStopsButton();
      _self.refreshVisibilityUserStopLabelsButton();
      _self.refreshSortableFeature();
    };

    /**
     * Add stop row selector with OP date list.
     * @param opDateList available operation programs.
     */
    this.addStopRow = function (opDateList) {
      const newStopId = selectorStopId;
      selectorStopId++;
      const row = `
            <tr class="stopSelectorRow" data-id="${newStopId}">
                <td><button class="btn btn-danger btn-sm" ><span class="fas fa-trash-alt" aria-hidden="true"></span></button></td>
                <td><select id=stopDateSelect-${newStopId} class="form-control stopDate"></select></td>
                <td><select id=stopNameSelect-${newStopId} class="form-control stopName"></select></td>
                <td><button id=stopColorSelect-${newStopId} class="btn btn-default btn-sm color-button" ><span class="fas fa-tint" aria-hidden="true"></span></button></td>
               </tr>`;
      $("#stopListContainer").append(row);
      $(`#stopDateSelect-${newStopId}`).select2({
        width: 'auto',
        data: opDateList,
        dropdownParent: $('#stopListContainer').parent()
      });
      _self.refreshStopControlEvents(newStopId);
      _self.refreshRemoveStopButton();
      _self.refreshColorPickerStopButton();
    };

    let mapOpts = {
      mapId: 'mapid',//$(".right_col")[0],
      zoomControl: false,
      scaleControl: true,
      showZones: false,
      showMacroZones: false,
      hideZoneLegend: true,
      hideMapLegend: true,
      showCommunes: true,
      showEducationLayer: true,
      showHealthcareLayer: true,
      showRuleControl: true,
      tileLayer: 'streets',
      onLoad: (_mapInstance, _mapApp) => {
        let img = '/static/trip/img/double-arrow.png';
        _mapInstance.loadImage(img, (err, image) => {
          if (err) {
            console.log(err);
            return;
          }
          _mapInstance.addImage('double-arrow', image, {sdf: true});

          _self.addHelpControl(_mapInstance);
          _self.addOperationInfoControl(_mapInstance);
          _self.addRouteListControl(_mapInstance);
          routeControl = _self.addRouteControl(_mapInstance);
          stopControl = _self.addStopControl(_mapInstance);
          _self.addStopListControl(_mapInstance);
          _self.addBearingControl(_mapInstance);
          stopLegendControl = _self.addStopLegendControl(_mapInstance);
          routeLegendControl = _self.addRouteLegendControl(_mapInstance);

          _self.addScreenshotControl(_mapInstance);

          _self.loadBaseData();

          // enable events
          _self.enableEvents();

          _mapApp.loadLayers();

          // set map height
          $('#mapid').css('min-height', $(window).height() - 100);
          _mapInstance.resize();
        });
      }
    };
    let _mapApp = new MapApp(mapOpts);


    this.sendShapeData = function (selectorRow) {
      let selectorIndex = selectorRow.index();
      let previousSelectorId = null;
      if (selectorIndex > 0) {
        previousSelectorId = selectorRow.prev().data("id");
      }
      let selectorId = selectorRow.data("id");
      let route = $(`#routeSelect-${selectorId}`).val();
      let date = $(`#dateSelect-${selectorId}`).val();
      let params = {
        route: route,
        operationProgramDate: date
      };
      $.getJSON(Urls['esapi:shapeRoute'](), params, function (data) {
        if (data.status) {
          if (data.status.code === 414) {
            showMessage(data.status)
            data.stops = [];
          } else {
            showMessage(data.status);
            if (!('points' in data) || !data.stops) {
              return;
            }
          }
        }

        // update map data
        let stopsSource = [];

        data.stops.forEach((stop) => {
          let routes = [];
          try {
            routes = stop.routes.join(', ');
          } catch (error) {
            routes = undefined
          }
          stopsSource.push({
            type: 'Feature',
            geometry: {
              type: 'Point',
              coordinates: [stop.longitude, stop.latitude]
            },
            properties: {
              route: route,
              color: 'black',
              authStopCode: stop.authStopCode,
              userStopCode: stop.userStopCode,
              stopName: stop.stopName,
              order: stop.order,
              routes: routes,
              layerId: selectorId
            }
          });
        });
        let shapeSource = [];
        shapeSource.push({
          type: 'Feature',
          geometry: {
            type: 'LineString',
            coordinates: data.points.map((p) => [p.longitude, p.latitude])
          },
          properties: {
            color: 'black',
            route: route,
            layerId: selectorId
          }
        });

        _self.addShapeLayers(selectorId, stopsSource, shapeSource, previousSelectorId);

        let $COLOR_BUTTON = $(`#colorSelect-${selectorId}`);
        let color = $COLOR_BUTTON.colorpicker('getValue');
        if (_self.isAddingRouteRow) {
          let rowNumber = $("#routeListContainer tr").length;
          color = getRandomColor(rowNumber)
          _self.isAddingRouteRow = false;
        }
        $COLOR_BUTTON.colorpicker('setValue', color);
        updateLayerColor(color, selectorId);

        let routeNumberInMap = $('#routeListContainer tr').length;
        if (routeNumberInMap === 1) {
          _mapApp.fitBound([`shape-source-${selectorId}`]);
        }
      });
    };

    /**
     * Get stops data and update map with the data.
     * @param e: stop selector
     */
    this.sendStopData = function (e) {
      const selector = $(e).closest(".stopSelectorRow");
      const selectorId = selector.data("id");
      const stopDate = selector.find(".stopDate").first().val();
      const stopName = selector.find(".stopName").first().val();
      const params = {
        stop: stopName,
        date: stopDate
      };
      $.getJSON(Urls['esapi:stopInfo'](), params, function (data) {
        if (data.status) {
          showMessage(data.status);
        } else {

          // update map data
          let stopsSource = [];

          data.info.forEach((stop) => {
            stopsSource.push({
              type: 'Feature',
              geometry: {
                type: 'Point',
                coordinates: [stop.longitude, stop.latitude]
              },
              properties: {
                color: 'black',
                authStopCode: stop.authCode,
                userStopCode: stop.userCode,
                stopName: stop.name,
                layerId: selectorId,
                latitude: stop.latitude,
                longitude: stop.longitude,
                routes: stop.routes.join(', ')
              }
            });
          });
          if ($(`#stopDateSelect-${selectorId}`).length) {
            _self.addStopLayers(selectorId, stopsSource);
          }
          // update color
          if ($(`#stopDateSelect-${selectorId}`).length) {
            const colorButton = $(`#stopColorSelect-${selectorId} `);
            const color = getRandomColor();
            colorButton.colorpicker('setValue', color);
            updateStopLayerColor(color, selectorId);

            const stopNumberInMap = $('#stopListContainer tr').length;
            if (stopNumberInMap === 1) {
              _mapApp.fitBound([`stops-source-${selectorId}`]);
            }
          }
        }
      });
    };

    this.refreshControlEvents = function (id) {

      // handle route selector
      let $ROUTE = $(`#routeSelect-${id}`);
      $ROUTE.change(function (e, params) {
        console.log("route changed");
        let selectorRow = $(this).closest(".selectorRow");
        _self.sendShapeData(selectorRow);
      });

      // handle user route selector
      let $USER_ROUTE = $(`#userRouteSelect-${id}`);
      $USER_ROUTE.change(function (e, params) {
        console.log("user route changed");
        let selector = $(this).closest(".selectorRow");
        let route = selector.find(".route").first();
        let userRoute = selector.find(".userRoute").first().val();
        let operator = selector.find(".operator").first().val();
        let date = selector.find(".date").first().val();

        //update auth route list
        let routeValues = [];
        if (_self.op_routes_dict.hasOwnProperty(date) &&
          _self.op_routes_dict[date].hasOwnProperty(operator) &&
          _self.op_routes_dict[date][operator].hasOwnProperty(userRoute)) {
          routeValues = _self.op_routes_dict[date][operator][userRoute];
        }
        route.empty();
        route.select2({
          data: Object.keys(routeValues).map(authRouteCode => {
            let opRouteCode = routeValues[authRouteCode];
            let text = `${authRouteCode} (${opRouteCode})`;
            return {
              id: authRouteCode,
              opRouteCode: opRouteCode,
              text: text
            }
          })
        });

        if (!(params && params.freeze)) {
          route.trigger("change");
        }
      });

      let $OPERATOR = $(`#operatorSelect-${id}`);
      $OPERATOR.change(function (e, params) {
        console.log("operator changed");
        let selector = $(this).closest(".selectorRow");
        let date = selector.find(".date").first().val();
        let operator = selector.find(".operator").first().val();
        let userRoutes = selector.find(".userRoute").first();

        userRoutes.empty();
        let userRouteDict = _self.op_routes_dict.hasOwnProperty(date) && _self.op_routes_dict[date].hasOwnProperty(operator)? _self.op_routes_dict[date][operator] : {};
        let dataList = Object.keys(userRouteDict).sort(sortAlphaNum);
        userRoutes.select2({
          data: dataList.map(e => {
            return {
              id: e,
              text: e
            }
          })
        });

        if (!(params && params.freeze)) {
          userRoutes.trigger("change");
        }
      });

      // handle date selector
      let $DATE = $(`#dateSelect-${id}`);
      $DATE.change(function (e, params) {
        console.log("date changed");
        let selector = $(this).closest(".selectorRow");
        let date = selector.find(".date").first().val();
        let operator = selector.find(".operator").first();

        operator.empty();
        let operatorDict = _self.op_routes_dict.hasOwnProperty(date) ? _self.op_routes_dict[date] : [];
        let operatorList = Object.keys(operatorDict).sort(sortAlphaNum);
        operator.select2({
          data: operatorList.map(e => {
            return {
              id: e,
              text: e
            }
          })
        });

        if (!(params && params.freeze)) {
          operator.trigger("change");
        }
      });

      // handle clone selector
      let selector = $(".selectorRow");
      if (selector.length > 1) {
        let lastSelected = selector.slice(-2, -1);
        $DATE.val(lastSelected.find(".date").first().val());
        $DATE.trigger("change", {freeze: true});
        $OPERATOR.val(lastSelected.find(".operator").first().val());
        $OPERATOR.trigger("change", {freeze: true});
        $USER_ROUTE.val(lastSelected.find(".userRoute").first().val());
        $USER_ROUTE.trigger("change", {freeze: true});
        $ROUTE.val(lastSelected.find(".route").first().val());
        $ROUTE.trigger("change");

        let routesButton = lastSelected.find(".visibility-routes").find("span");
        $(`#visibilityRoutes-${id}`).find("span").removeClass().addClass(routesButton.attr("class"));
        let stopButton = lastSelected.find(".visibility-stops");
        $(`#visibilityStops-${id}`).removeClass().addClass(stopButton.attr("class"));
        let userStopButton = lastSelected.find(".visibility-user-stops");
        $(`#visibilityUserStopLabels-${id}`).removeClass().addClass(userStopButton.attr("class"));
      } else {
        $DATE.trigger("change");
      }
    };

    /**
     * Handle control events for stop date and stop name selector.
     * Create stop selector based on stop date.
     * If it is not the first selector, copy last selector.
     * @param stopId: stop selector's id
     */
    this.refreshStopControlEvents = function (stopId) {
      // handle date selector
      const dateSelector = $(`#stopDateSelect-${stopId}`);
      const stopSelector = $(`#stopNameSelect-${stopId}`)
      dateSelector.change(function () {
        const selector = $(this).closest(".stopSelectorRow");
        const date = selector.find(".stopDate").first().val();
        const stops = selector.find(".stopName").first();

        stops.select2({
          ajax: {
            delay: 500, // milliseconds
            url: Urls["esapi:matchedStopData"](),
            dataType: "json",
            data: function (params) {
              return {
                term: params.term,
                date: date
              }
            },
            processResults: function (data, params) {
              return {
                results: data.items
              }
            },
            cache: true
          },
          minimumInputLength: 3,
          language: {
            inputTooShort: function () {
              return "Ingresar 3 o más caracteres";
            }
          },
          dropdownParent: selector,
          placeholder: "Todos",
          width: 'style'
        });
      });

      stopSelector.change(function () {
        _self.sendStopData(this);
      });

      // handle clone selector
      const selector = $(".stopSelectorRow");
      if (selector.length > 1) {
        const lastSelected = selector.slice(-2, -1);
        dateSelector.val(lastSelected.find(".stopDate").first().val());
        dateSelector.data("first", true);
        stopSelector.val(lastSelected.find(".stopName").first().val());
        stopSelector.data("first", true);
        const color = lastSelected.find(".fa-tint").css("color");
        $(`#stopColorSelect-${stopId}`).css("color", color);
      }
      dateSelector.trigger("change");
      stopSelector.trigger("change");
    };

    this.refreshRemoveButton = function () {
      let $REMOVE_BUTTON = $("#routeControl .btn-danger");
      $REMOVE_BUTTON.off("click");
      $REMOVE_BUTTON.click(function () {
        let removeButtonRef = $(this);
        let layerId = removeButtonRef.parent().parent().data("id");
        // update last selected
        _self.removeShapeLayers(layerId);
        removeButtonRef.parent().parent().remove();
        routeLegendControl.update();
      });
    };

    /**
     * Handle control events for stop remove button.
     */
    this.refreshRemoveStopButton = function () {
      const removeStopButton = $("#stopControl .btn-danger");
      removeStopButton.off("click");
      removeStopButton.click(function () {
        const removeButtonRef = $(this);
        const layerId = removeButtonRef.parent().parent().data("id");
        // update last selected
        _self.removeStopLayers(layerId);
        removeButtonRef.parent().parent().remove();
        stopLegendControl.update();
      });
    };

    const updateLayerColor = (color, layerId) => {
      let stopsSource = _mapApp.getMapInstance().getSource(`shape-stops-source-${layerId}`)._data;
      stopsSource.features = stopsSource.features.map(feature => {
        feature.properties.color = color;
        return feature;
      });
      let shapeSource = _mapApp.getMapInstance().getSource(`shape-source-${layerId}`)._data;
      shapeSource.features = shapeSource.features.map(feature => {
        feature.properties.color = color;
        return feature;
      });
      _mapApp.getMapInstance().getSource(`shape-stops-source-${layerId}`).setData(stopsSource);
      _mapApp.getMapInstance().getSource(`shape-source-${layerId}`).setData(shapeSource);
      // update stop legend
      routeLegendControl.update();
    };

    /**
     * Change the stop layer's color based on id.
     * @param color: new color to change
     * @param layerId: stop layer id
     */
    const updateStopLayerColor = (color, layerId) => {
      let stopsSource = _mapApp.getMapInstance().getSource(`stops-source-${layerId}`)._data;
      stopsSource.features = stopsSource.features.map(feature => {
        feature.properties.color = color;
        return feature;
      });
      _mapApp.getMapInstance().getSource(`stops-source-${layerId}`).setData(stopsSource);
      // update stop legend
      stopLegendControl.update();
    };

    this.refreshColorPickerButton = function () {
      let $COLOR_BUTTON = $(".selectorRow .btn-default");
      $COLOR_BUTTON.off("changeColor");
      $COLOR_BUTTON.colorpicker({format: "rgb"}).on("changeColor", function (e) {
        let color = e.color.toString("rgba");
        let layerId = $(this).parent().parent().data("id");
        $(this).css("color", color);
        updateLayerColor(color, layerId);
      });
    };

    /**
     * Update stop color picker on change color.
     */
    this.refreshColorPickerStopButton = function () {
      const stopColorButton = $(".stopSelectorRow .btn-default");
      stopColorButton.off("changeColor");
      stopColorButton.colorpicker({format: "rgb"}).on("changeColor", function (e) {
        const color = e.color.toString("rgba");
        const layerId = $(this).parent().parent().data("id");
        $(this).css("color", color);
        updateStopLayerColor(color, layerId);
      });
    };

    const updateLayerRoute = (isVisible, layerId, button, span) => {
      if (isVisible) {
        button.removeClass("btn-success").addClass("btn-warning");
        _self.setShapeLayerVisibility(layerId, false);
      } else {
        button.removeClass("btn-warning").addClass("btn-success");
        _self.setShapeLayerVisibility(layerId, true);
      }
    };

    this.refreshVisibilityRoutesButton = function () {
      let $VISIBILITY_BUTTON = $(".selectorRow .visibility-routes");
      $VISIBILITY_BUTTON.off("click");
      $VISIBILITY_BUTTON.click(function () {
        let button = $(this);
        let span = button.find("span");
        let layerId = button.parent().parent().data("id");
        let isVisible = button.hasClass("btn-success");
        updateLayerRoute(isVisible, layerId, button, span);
      });
    };

    this.setStopLayerVisibility = (layerId, show) => {
      let visible = show ? 'visible' : 'none';
      _mapApp.getMapInstance().setLayoutProperty(`shape-stops-${layerId}`, 'visibility', visible);
    };

    this.setStopLabelLayerVisibility = (layerId, show) => {
      let visible = show ? 'visible' : 'none';
      _mapApp.getMapInstance().setLayoutProperty(`shape-stop-label-${layerId}`, 'visibility', visible);
    };

    const updateStopRoutes = (active, layerId, button, span) => {
      if (active) {
        button.removeClass("btn-success").addClass("btn-warning");
        span.removeClass("fa-bus").addClass("fa-bus");
        _self.setStopLayerVisibility(layerId, false);
      } else {
        button.removeClass("btn-warning").addClass("btn-success");
        span.removeClass("fa-bus").addClass("fa-bus");
        _self.setStopLayerVisibility(layerId, true);
      }
    };

    this.refreshVisibilityStopsButton = function () {
      let $VISIBILITY_BUTTON = $(".selectorRow .visibility-stops");
      $VISIBILITY_BUTTON.off("click");
      $VISIBILITY_BUTTON.click(function () {
        let button = $(this);
        let span = button.find("span");
        let layerId = button.parent().parent().data("id");
        let active = button.hasClass("btn-success");
        updateStopRoutes(active, layerId, button, span);
      });
    };

    const updateUserStopLabels = (active, layerId, button, span) => {
      if (active) {
        button.removeClass("btn-success").addClass("btn-warning");
        _self.setStopLabelLayerVisibility(layerId, false);
      } else {
        button.removeClass("btn-warning").addClass("btn-success");
        _self.setStopLabelLayerVisibility(layerId, true);
      }
    };

    this.refreshVisibilityUserStopLabelsButton = function () {
      let $VISIBILITY_BUTTON = $(".selectorRow .visibility-user-stops");
      $VISIBILITY_BUTTON.off("click");
      $VISIBILITY_BUTTON.click(function () {
        let button = $(this);
        let span = button.find("span");
        let layerId = button.parent().parent().data("id");
        let active = button.hasClass("btn-success");
        updateUserStopLabels(active, layerId, button, span);
      });
    };

    this.refreshSortableFeature = function() {
      function dragStart (e) {
        let index = $(e.target).closest(".selectorRow").index();
        e.dataTransfer.setData('text/plain', index);
      }

      function dropped (e) {
        cancelDefault(e);
        // get dropped item reference
        let oldIndex = e.dataTransfer.getData('text/plain');
        let dropped = $(this).parent().children().eq(oldIndex);

        let target = $(e.target).closest(".selectorRow");
        let newIndex = target.index();

        // insert the dropped items at new place
        if (newIndex < oldIndex) {
          dropped.insertBefore(target);
        } else {
          dropped.insertAfter(target);
        }
        routeLegendControl.update();
        _self.sendShapeData(target);
      }

      function cancelDefault (e) {
        e.preventDefault();
        e.stopPropagation();
        return false;
      }

      let $ROWS = $("table > tbody > tr.selectorRow");
      $ROWS.each(function (i, row) {
        $(row).off("dragstart");
        $(row).off("drop");
        $(row).off("dragenter");
        $(row).off("dragover");

        $(row).prop('draggable', true)
        row.addEventListener('dragstart', dragStart)
        row.addEventListener('drop', dropped)
        row.addEventListener('dragenter', cancelDefault)
        row.addEventListener('dragover', cancelDefault)
      });
    };

    this.addTableInfo = function () {
      let $TABLE = $('#shapeDetail');
      $TABLE.DataTable({
        language: {
          url: "//cdn.datatables.net/plug-ins/1.10.13/i18n/Spanish.json",
          decimal: ",",
          thousands: "."
        },
        scrollX: true,
        responsive: true,
        pageLength: 15,
        paging: true,
        retrieve: true,
        searching: true,
        order: [[0, "asc"], [1, "asc"], [2, "asc"]],
        dom: 'Bfr<"periodSelector">iptpi',
        buttons: [
          {
            extend: "excelHtml5",
            text: "Exportar a excel",
            title: 'datos_de_ruta',
            className: "buttons-excel buttons-html5 btn btn-success",
            exportOptions: {
              columns: [1, 2, 3, 4, 5, 6, 7, 8, 9]
            }
          },
          {
            extend: 'copy',
            text: "Copiar datos",
            className: "buttons-excel buttons-html5 btn btn-default",
          }
        ],
        columns: [
          {title: "Programa de Operación", data: "date", searchable: true},
          {title: "Servicio Usuario", data: "userRoute", searchable: true},
          {title: "Servicio Sonda", data: "authRoute", searchable: true},
          {
            title: "Periodo Transantiago", data: "timePeriod", searchable: true,
            render: function (data) {
              return data.replace(/ *\([^)]*\) */g, "");
            }
          },
          {title: "Inicio", data: "startPeriodTime", searchable: false},
          {title: "Fin", data: "endPeriodTime", searchable: false},
          {title: "Frecuencia [Bus/h]", data: "frequency", searchable: false},
          {title: "Capacidad [Plazas/h]", data: "capacity", searchable: false},
          {title: "Distancia [km]", data: "distance", searchable: false},
          {title: "Velocidad [km/h]", data: "speed", searchable: false},
        ],
        createdRow: function () {
          this.api().columns([3]).every(function () {
            let column = this;
            let select = $('<select id="periodTimeSelector" multiple="multiple" style="width: 400px; height: 60px"></select>')
              .appendTo($(".periodSelector").empty())
              .on('change', function () {
                let selectedValues = $(this).val() || [];
                let regexValues = selectedValues.map(e => $.fn.dataTable.util.escapeRegex(e));
                regexValues = regexValues.map(e => `^${e}$`);
                let query = regexValues.join("|");
                column
                  .search(query, true, false)
                  .draw();
              });
            select.select2({
              width: 'element',
              height: 'element',
              placeholder: " Filtrar según periodo transantiago",

            });
            let selectorValues = [];
            column.data().each(e => selectorValues.push(e.replace(/ *\([^)]*\) */g, "")));
            selectorValues = new Set(selectorValues);
            selectorValues.forEach(function (d, j) {
              select.append('<option value="' + d.replace(/ *\([^)]*\) */g, "") + '">' + d.replace(/ *\([^)]*\) */g, "") + '</option>')
            });
          });
        }
      });
    };
  }

  new MapShapeApp();
  $("#modalList").detach().appendTo($(".main_container")[0]);
  document.activeElement.blur();
});