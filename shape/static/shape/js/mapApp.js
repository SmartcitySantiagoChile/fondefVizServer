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

  function MapShapeApp() {
    let _self = this;
    let selectorId = 1;

    this.addLayers = (layerId, stopsSource, shapeSource) => {
      stopsSource = {
        type: "FeatureCollection",
        features: stopsSource
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
      let stopsLayerTemplate = {
        id: 'stops-layer',
        source: 'stops-source',
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
      let shapeArrowLayerTemplate = {
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
          'icon-color': ['get', 'color'],
          'icon-halo-color': '#fff',
          'icon-halo-width': 2,
        }
      };

      _self.removeLayers(layerId);

      let shapeLayer = $.extend({}, shapeLayerTemplate);
      let shapeArrowLayer = $.extend({}, shapeArrowLayerTemplate);
      let stopsLayer = $.extend({}, stopsLayerTemplate);
      let stopLabelLayer = $.extend({}, stopLabelLayerTemplate);

      shapeLayer.id = `shape-${layerId}`;
      shapeLayer.source = `shape-source-${layerId}`;
      shapeArrowLayer.id = `shape-arrow-${layerId}`;
      shapeArrowLayer.source = `shape-source-${layerId}`;

      stopsLayer.id = `stops-${layerId}`;
      stopsLayer.source = `stops-source-${layerId}`;
      stopLabelLayer.id = `stop-label-${layerId}`;
      stopLabelLayer.source = `stops-source-${layerId}`;

      _mapApp.getMapInstance().addSource(`shape-source-${layerId}`, {type: 'geojson', data: shapeSource});
      _mapApp.getMapInstance().addSource(`stops-source-${layerId}`, {type: 'geojson', data: stopsSource});

      _mapApp.getMapInstance().addLayer(shapeLayer);
      _mapApp.getMapInstance().addLayer(shapeArrowLayer);
      _mapApp.getMapInstance().addLayer(stopsLayer);
      _mapApp.getMapInstance().addLayer(stopLabelLayer);

      let openStopPopup = function (feature) {
        let popUpDescription = "<p>";
        popUpDescription += " Servicio: <b>" + feature.properties.route + "</b><br />";
        popUpDescription += " Nombre: <b>" + feature.properties.stopName + "</b><br />";
        popUpDescription += " Código transantiago: <b>" + feature.properties.authStopCode + "</b><br />";
        popUpDescription += " Código usuario: <b>" + feature.properties.userStopCode + "</b><br />";
        popUpDescription += " Posición en la ruta: <b>" + (feature.properties.order + 1) + "</b><br />";
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

    this.removeLayers = (layerId) => {
      // remove data
      if (_mapApp.getMapInstance().getLayer(`shape-${layerId}`)) {
        _mapApp.getMapInstance().removeLayer(`shape-${layerId}`);
        _mapApp.getMapInstance().removeLayer(`stops-${layerId}`);
        _mapApp.getMapInstance().removeLayer(`stop-label-${layerId}`);
        _mapApp.getMapInstance().removeLayer(`shape-arrow-${layerId}`);

        _mapApp.getMapInstance().removeSource(`shape-source-${layerId}`);
        _mapApp.getMapInstance().removeSource(`stops-source-${layerId}`);
      }
    };

    this.setShapeLayerVisibility = (layerId, show) => {
      let visible = show ? 'visible' : 'none';
      _mapApp.getMapInstance().setLayoutProperty(`shape-${layerId}`, 'visibility', visible);
      _mapApp.getMapInstance().setLayoutProperty(`shape-arrow-${layerId}`, 'visibility', visible);
    };

    this.setStopLayerVisibility = (layerId, show) => {
      let visible = show ? 'visible' : 'none';
      _mapApp.getMapInstance().setLayoutProperty(`stops-${layerId}`, 'visibility', visible);
    };

    this.setStopLabelLayerVisibility = (layerId, show) => {
      let visible = show ? 'visible' : 'none';
      _mapApp.getMapInstance().setLayoutProperty(`stop-label-${layerId}`, 'visibility', visible);
    };

    this.addRouteControl = (mapInstance) => {
      class RouteControl {
        onAdd(map) {
          let div = document.createElement('div');
          div.className = 'mapboxgl-ctrl info legend';
          div.innerHTML += '<button id="addRouteButton" class="btn btn-default btn-sm" >' +
            '<span class="glyphicon glyphicon-plus" aria-hidden="true"></span> Agregar ruta' +
            '</button>';
          return div;
        }

        onRemove() {
          // nothing
        }
      }

      mapInstance.addControl(new RouteControl(), 'top-left');
    };

    this.addHelpControl = (mapInstance) => {
      class HelpControl {
        onAdd(map) {
          let div = document.createElement('div');
          div.className = 'mapboxgl-ctrl info legend';
          div.innerHTML += '<button id="helpButton" class="btn btn-default" ><span class="glyphicon glyphicon-info-sign" aria-hidden="true"></span></button>';
          return div;
        }

        onRemove() {
          // nothing
        }
      }

      mapInstance.addControl(new HelpControl(), 'top-right');
    };

    this.addListControl = (mapInstance) => {
      class RouteListControl {
        onAdd(map) {
          let div = document.createElement('div');
          div.className = 'mapboxgl-ctrl info legend';
          div.innerHTML += '<h4>Rutas en mapa</h4>' +
            '<div id="header" style="display: none">' +
            '<div class="form-inline" >' +
            '<button id="timePeriodButton" class="btn alert-warning " ><span class="fa fa-bus" aria-hidden="true"></span> Ver información operacional</button>' + '</div>' +
            '<div class="form-inline" >' +
            '<div class="form-row">' +
            '<div class="form-group col">' +
            '<button class="btn btn-default-disabled btn-sm" ><span class="glyphicon glyphicon-remove" aria-hidden="true"></span></button>' +
            '<button class="btn btn-default-white btn-sm date" >Fecha PO</button>' +
            '<button class="btn btn-default-white btn-sm userRoute"" >Servicio</button>' +
            '<button class="btn btn-default-white btn-sm route" >Servicio TS</button>' +
            '<button class="btn btn-default-disabled btn-sm" ><span class="glyphicon glyphicon-remove" aria-hidden="true"></span></button>' +
            '<button class="btn btn-default-disabled btn-sm" ><span class="glyphicon glyphicon-remove" aria-hidden="true"></span></button>' +
            '<button class="btn btn-default-disabled btn-sm" ><span class="glyphicon glyphicon-remove" aria-hidden="true"></span></button>' +
            '</div>' +
            '</div>' +
            '</div>' +
            '</div>' +
            '<div id="routeListContainer" class="form-inline"</div>';
          return div;
        }

        onRemove() {
          // nothing
        }
      }

      mapInstance.addControl(new RouteListControl(), 'top-left');
    };

    this.loadBaseData = () => {
      $.getJSON(Urls["esapi:shapeBase"](), function (data) {
        // data for selectors
        let currentDate = data.dates[0]
        _self.dates_period_dict = data.dates_periods_dict;
        _self.op_routes_dict = data.op_routes_dict;
        _self.periods = data.periods;
        let userRouteList = (Object.keys(data.op_routes_dict[currentDate]).sort(sortAlphaNum));
        userRouteList = userRouteList.map(e => ({id: e, text: e}));
        let dateList = data.dates.map(e => ({id: e, text: e}));

        // activate add button when data exist
        $("#addRouteButton").click(function () {
          _self.addRow(dateList, userRouteList);
        });
      });

      _self.addTableInfo();
    };

    this.enableEvents = () => {
      $("#helpButton").click(function () {
        $("#helpModal").modal("show");
      });
      $("#timePeriodButton").click(function () {
        let routeSelector = $("#routeListContainer");
        let periodInfoList = [];
        let requestList = [];
        let uniqueInfoSet = new Set();

        routeSelector.children().each(function (index, el) {
          let routeText = $(el).closest(".selectorRow").find(".route option:selected").text();
          let route = routeText.substring(routeText.indexOf("(") + 1, routeText.indexOf(")"))
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

    this.addRow = function (dateList, userRouteList) {
      let newId = selectorId;
      selectorId++;
      let row = '<div class="selectorRow" data-id="' + newId + '">' +
        '<button class="btn btn-danger btn-sm" ><span class="glyphicon glyphicon-remove" aria-hidden="true"></span></button>' +
        `<select id=dateSelect-${newId} class="form-control date"></select>` +
        `<select id=userRouteSelect-${newId} class="form-control userRoute"></select>` +
        `<select id=routeSelect-${newId} class="form-control route"></select>` +
        `<button id=colorSelect-${newId} class="btn btn-default btn-sm color-button" ><span class="glyphicon glyphicon-tint" aria-hidden="true"></span></button>` +
        `<button id=visibilityRoutes-${newId} class="btn btn-success btn-sm visibility-routes" ><span class="glyphicon glyphicon-eye-open" aria-hidden="true"></span></button>` +
        `<button id=visibilityStops-${newId} class="btn btn-success btn-sm visibility-stops" ><span class="glyphicon fa fa-bus" aria-hidden="true"></span></button>` +
        `<button id=visibilityUserStopLabels-${newId} class="btn btn-success btn-sm visibility-user-stops" ><span class="glyphicon glyphicon-user" aria-hidden="true"></span></button>` +
        '</div>';

      $("#routeListContainer").append(row);
      $(`#dateSelect-${newId}`).select2({width: 'element', data: dateList});
      $(`#userRouteSelect-${newId}`).select2({width: 'element', data: userRouteList});
      $(`#routeSelect-${newId}`).select2({width: 'element'});

      _self.refreshControlEvents(newId);
      _self.refreshRemoveButton();
      _self.refreshColorPickerButton();
      _self.refreshVisibilityRoutesButton();
      _self.refreshVisibilityStopsButton();
      _self.refreshVisibilityUserStopLabelsButton();
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
      tileLayer: 'streets',
      onLoad: (_mapInstance, _mapApp) => {
        let img = '/static/trip/img/double-arrow.png';
        _mapInstance.loadImage(img, (err, image) => {
          if (err) {
            console.log(err);
            return;
          }
          _mapInstance.addImage('double-arrow', image, {sdf: true});

          _self.addRouteControl(_mapInstance);
          _self.addHelpControl(_mapInstance);
          _self.addListControl(_mapInstance);

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

    this.sendData = function (e) {
      let selector = $(e).closest(".selectorRow");
      let selectorId = selector.data("id");
      let route = $(`#routeSelect-${selectorId}`).val();
      let date = $(`#dateSelect-${selectorId}`).val();
      let params = {
        route: route,
        operationProgramDate: date
      };
      $.getJSON(Urls['esapi:shapeRoute'](), params, function (data) {
        if (data.status) {
          showMessage(data.status);
          if (!('points' in data)) {
            return;
          }
        }

        // update map data
        let stopsSource = [];
        data.stops.forEach((stop) => {
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

        _self.addLayers(selectorId, stopsSource, shapeSource);

        // update color
        let getRandomColor = function () {
          let letters = "0123456789ABCDEF";
          let color = "#";
          for (let i = 0; i < 6; i++) {
            color += letters[Math.floor(Math.random() * 16)];
          }
          return color;
        };
        let $COLOR_BUTTON = $(`#colorSelect-${selectorId}`);
        let color = getRandomColor();
        $COLOR_BUTTON.colorpicker('setValue', color);
        updateLayerColor(color, selectorId);

        // update routes
        let routesButton = $(`#visibilityRoutes-${selectorId}`);
        let routesSpan = routesButton.find("span");
        let routesActive = routesSpan.hasClass("glyphicon-eye-open");
        updateLayerRoutes(!routesActive, selectorId, routesButton, routesSpan);

        // update stops
        let stopButton = $(`#visibilityStops-${selectorId}`);
        let stopSpan = stopButton.find("span");
        let stopActive = stopButton.hasClass("btn-success");
        updateStopRoutes(!stopActive, selectorId, stopButton, stopSpan);
      });
    };

    this.refreshControlEvents = function (id) {
      // handle user route selector
      let $USER_ROUTE = $(`#userRouteSelect-${id}`);
      $USER_ROUTE.change(function () {
        let selector = $(this).closest(".selectorRow");
        let userRoute = selector.find(".userRoute").first().val();
        let route = selector.find(".route").first();
        let date = selector.find(".date").first().val();

        //update auth route list
        let routeValues = [];
        if (_self.op_routes_dict.hasOwnProperty(date) && _self.op_routes_dict[date].hasOwnProperty(userRoute)) {
          routeValues = _self.op_routes_dict[date][userRoute];
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
        //set value
        let allSelectors = $(".selectorRow");
        let selectorIndex = allSelectors.index(selector);
        if ($(this).data("first") === true) {
          route.val(allSelectors.slice(selectorIndex - 1).find(".route").first().val());
          $(this).data("first", false);
        }
        _self.sendData(this);
      });

      // handle route selector
      let $ROUTE = $(`#routeSelect-${id}`);
      $ROUTE.change(function () {
        _self.sendData(this);
      });

      // handle date selector
      let $DATE = $(`#dateSelect-${id}`);
      $DATE.change(function () {
        let selector = $(this).closest(".selectorRow");
        let date = selector.find(".date").first().val();
        let userRoutes = selector.find(".userRoute").first();

        userRoutes.empty();
        let userRouteDict = _self.op_routes_dict.hasOwnProperty(date) ? _self.op_routes_dict[date] : [];
        let dataList = Object.keys(userRouteDict).sort(sortAlphaNum);
        userRoutes.select2({
          data: dataList.map(e => {
            return {
              id: e,
              text: e
            }
          })
        });
        userRoutes.trigger("change");

        //set value
        if ($(this).data("first") === true) {
          $(this).data("first", false);
        }
      });

      // handle clone selector
      let selector = $(".selectorRow");
      if (selector.length > 1) {
        let lastSelected = selector.slice(-2, -1);
        $DATE.val(lastSelected.find(".date").first().val());
        $DATE.data("first", true);
        $USER_ROUTE.val(lastSelected.find(".userRoute").first().val());
        $USER_ROUTE.data("first", true);

        let color = lastSelected.find(".glyphicon-tint").css("color");
        $(`#colorSelect-${id}`).css("color", color);
        let routesButton = lastSelected.find(".visibility-routes").find("span");
        $(`#visibilityRoutes-${id}`).find("span").removeClass().addClass(routesButton.attr("class"));
        let stopButton = lastSelected.find(".visibility-stops");
        $(`#visibilityStops-${id}`).removeClass().addClass(stopButton.attr("class"));
        let userStopButton = lastSelected.find(".visibility-user-stops");
        $(`#visibilityUserStopLabels-${id}`).removeClass().addClass(userStopButton.attr("class"));
      } else {
        $("#header").css('display', "block");
      }

      $USER_ROUTE.trigger("change");
    };

    this.refreshRemoveButton = function () {
      let $REMOVE_BUTTON = $(".btn-danger");
      let modal = $("#modal");
      $REMOVE_BUTTON.off("click");
      $REMOVE_BUTTON.click(function () {
        let removeButtonRef = $(this);
        modal.off("show.bs.modal");
        modal.on("show.bs.modal", function () {
          modal.off("click", "button.btn-info");
          modal.on("click", "button.btn-info", function () {
            let layerId = removeButtonRef.parent().data("id");
            // update last selected
            _self.removeLayers(layerId);
            removeButtonRef.parent().remove();
          });
        });
        modal.modal("show");
      });
    };

    const updateLayerColor = (color, layerId) => {
      let stopsSource = _mapApp.getMapInstance().getSource(`stops-source-${layerId}`)._data;
      stopsSource.features = stopsSource.features.map(feature => {
        feature.properties.color = color;
        return feature;
      });
      let shapeSource = _mapApp.getMapInstance().getSource(`shape-source-${layerId}`)._data;
      shapeSource.features = shapeSource.features.map(feature => {
        feature.properties.color = color;
        return feature;
      });
      _mapApp.getMapInstance().getSource(`stops-source-${layerId}`).setData(stopsSource);
      _mapApp.getMapInstance().getSource(`shape-source-${layerId}`).setData(shapeSource);
    };

    this.refreshColorPickerButton = function () {
      let $COLOR_BUTTON = $(".selectorRow .btn-default");
      $COLOR_BUTTON.off("changeColor");
      $COLOR_BUTTON.colorpicker({format: "rgb"}).on("changeColor", function (e) {
        let color = e.color.toString("rgba");
        let layerId = $(this).parent().data("id");
        $(this).css("color", color);
        updateLayerColor(color, layerId);
      });
    };

    const updateLayerRoutes = (update, layerId, button, span) => {
      if (update) {
        button.removeClass("btn-success").addClass("btn-warning");
        span.removeClass("glyphicon-eye-open").addClass("glyphicon-eye-close");
        _self.setShapeLayerVisibility(layerId, false);
      } else {
        button.removeClass("btn-warning").addClass("btn-success");
        span.removeClass("glyphicon-eye-close").addClass("glyphicon-eye-open");
        _self.setShapeLayerVisibility(layerId, true);
      }
    };

    this.refreshVisibilityRoutesButton = function () {
      let $VISIBILITY_BUTTON = $(".selectorRow .visibility-routes");
      $VISIBILITY_BUTTON.off("click");
      $VISIBILITY_BUTTON.click(function () {
        let button = $(this);
        let span = button.find("span");
        let layerId = button.parent().data("id");
        let active = span.hasClass("glyphicon-eye-open");
        updateLayerRoutes(active, layerId, button, span);
      });
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
        let layerId = button.parent().data("id");
        let active = button.hasClass("btn-success");
        updateStopRoutes(active, layerId, button, span);
      });
    };

    const updateUserStopLabels = (active, layerId, button, span) => {
      if (active) {
        button.removeClass("btn-success").addClass("btn-warning");
        span.removeClass("glyphicon-user").addClass("glyphicon-user");
        _self.setStopLabelLayerVisibility(layerId, false);
      } else {
        button.removeClass("btn-warning").addClass("btn-success");
        span.removeClass("glyphicon-user").addClass("glyphicon-user");
        _self.setStopLabelLayerVisibility(layerId, true);
      }
    };

    this.refreshVisibilityUserStopLabelsButton = function () {
      let $VISIBILITY_BUTTON = $(".selectorRow .visibility-user-stops");
      $VISIBILITY_BUTTON.off("click");
      $VISIBILITY_BUTTON.click(function () {
        let button = $(this);
        let span = button.find("span");
        let layerId = button.parent().data("id");
        let active = button.hasClass("btn-success");
        updateUserStopLabels(active, layerId, button, span);
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

  let mapShapeApp = new MapShapeApp();
  mapShapeApp.loadBaseData();
  $("#modalList").detach().appendTo($(".main_container")[0]);
  document.activeElement.blur();
});