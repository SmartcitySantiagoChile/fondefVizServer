"use strict";
$(document).ready(function () {
    function MapShapeApp() {
        var _self = this;
        var mapOpts = {
            mapId: $(".right_col")[0],
            maxZoom: 18,
            zoomControl: false
        };
        var app = new MapApp(mapOpts);
        var mapInstance = app.getMapInstance();

        var addRouteControl = L.control({position: "topleft"});
        addRouteControl.onAdd = function (map) {
            var div = L.DomUtil.create("div", "info legend");
            div.innerHTML += '<button id="addRouteButton" class="btn btn-default btn-sm" >' +
                '<span class="glyphicon glyphicon-plus" aria-hidden="true"></span> Agregar ruta' +
                '</button>';
            L.DomEvent.disableClickPropagation(div);
            return div;
        };
        addRouteControl.addTo(mapInstance);

        var routeListControl = L.control({position: "topleft"});
        routeListControl.onAdd = function (map) {
            var div = L.DomUtil.create("div", "info legend");
            div.innerHTML += '<h4>Rutas en mapa</h4>' +
                '<div id="header" class="form-inline" style="display: none">' +
                '<div class="form-row">' +
                '<div class="form-group col">' +
                '<button class="btn btn-default-disabled btn-sm" ><span class="glyphicon glyphicon-remove" aria-hidden="true"></span></button>' +
                '<button class="btn btn-default-white btn-sm date" >Programa de Operación</button>' +
                '<button class="btn btn-default-white btn-sm userRoute"" >Servicio</button>' +
                '<button class="btn btn-default-white btn-sm route" >Servicio Sonda</button>' +
                '<button class="btn btn-default-disabled btn-sm" ><span class="glyphicon glyphicon-remove" aria-hidden="true"></span></button>' +
                '<button class="btn btn-default-disabled btn-sm" ><span class="glyphicon glyphicon-remove" aria-hidden="true"></span></button>' +
                '<button class="btn btn-default-disabled btn-sm" ><span class="glyphicon glyphicon-remove" aria-hidden="true"></span></button>' +
                '<button class="btn btn-default-white btn-sm period" >Periodo</button>' +
                '</div>' +
                '</div>' +
                '</div>' +
                '<div id="routeListContainer" class="form-inline"</div>';
            L.DomEvent.disableClickPropagation(div);
            return div;
        };
        routeListControl.addTo(mapInstance);

        var helpControl = L.control({position: "topright"});
        helpControl.onAdd = function (map) {
            var div = L.DomUtil.create("div", "info legend");
            div.innerHTML += '<button id="helpButton" class="btn btn-default" ><span class="glyphicon glyphicon-info-sign" aria-hidden="true"></span></button>';
            L.DomEvent.disableClickPropagation(div);
            return div;
        };
        helpControl.addTo(mapInstance);
        $("#helpButton").click(function () {
            $("#helpModal").modal("show");
        });

        var $ROW_CONTAINER = $("#routeListContainer");

        var layers = {};

        var selectorId = 1;

        this.refreshControlEvents = function (id) {

            //handle send data
            let sendData = e => {
                let selector = $(e).closest(".selectorRow");
                let layerId = selector.data("id");
                let route = $(`#routeSelect-${layerId}`).val();
                let date = $(`#dateSelect-${layerId}`).val();
                let params = {
                    route: route,
                    operationProgramDate: date
                };

                $.getJSON(Urls["esapi:shapeRoute"](), params, function (data) {
                    if (data.status) {
                        showMessage(data.status);
                        if (!("points" in data)) {
                            layers[layerId].clearLayers();
                            return;
                        }
                    }
                    // update map
                    // clean featureGroup
                    layers[layerId].clearLayers();
                    let layer = layers[layerId];
                    app.addPolyline(layer, data.points, {
                        stops: data.stops,
                        route: route
                    });
                });
            };

            // handle user route selector
            let $USER_ROUTE = $(`#userRouteSelect-${id}`);
            $USER_ROUTE.off("change");
            $USER_ROUTE.change(function () {
                let selector = $(this).closest(".selectorRow");
                let userRoute = selector.find(".userRoute").first().val();
                let route = selector.find(".route").first();

                //update authroute list
                let routeValues = _self.data[userRoute];
                route.empty();
                route.append(routeValues.map(e => '<option>' + e + '</option>').join(""));

                //set value
                let allSelectors = $(".selectorRow");
                let selectorIndex = allSelectors.index(selector);
                if ($(this).data("first") === true) {
                    route.val(allSelectors.slice(selectorIndex - 1).find(".route").first().val());
                    $(this).data("first", false);
                }
                if ($PERIOD.val() != null) {
                    sendData(this);
                }
            });

            // handle route selector
            let $ROUTE = $(`#routeSelect-${id}`);
            $ROUTE.off("change");
            $ROUTE.change(function () {
                sendData(this);
            });


            let $PERIOD = $(`#periodSelect-${id}`);
            $PERIOD.off("change");

            // handle date selector
            let $DATE = $(`#dateSelect-${id}`);
            $DATE.off("change");
            $DATE.change(function () {
                let selector = $(this).closest(".selectorRow");
                let date = selector.find(".date").first().val();
                let periods = selector.find(".period").first();

                //update periods list
                let periodValues = _self.periods[_self.dates_period_dict[date]];
                periods.empty();
                periods.append(periodValues.map(e => `<option value=${e.value}>` + e.item + '</option>').join(""));

                //set value
                let allSelectors = $(".selectorRow");
                let selectorIndex = allSelectors.index(selector);
                if ($(this).data("first") === true) {
                    periods.val(allSelectors.slice(selectorIndex - 1).find(".period").first().val());
                    $(this).data("first", false);
                }

                if ($ROUTE.val() != null) {
                    sendData(this);
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

            } else{
                $("#header").css('display', "block");
            }
            $USER_ROUTE.trigger("change");
            $DATE.trigger("change");

        };

        this.refrehRemoveButton = function () {
            var $REMOVE_BUTTON = $(".btn-danger");
            var modal = $("#modal");
            $REMOVE_BUTTON.off("click");
            $REMOVE_BUTTON.click(function () {
                var removeButtonRef = $(this);
                modal.off("show.bs.modal");
                modal.on("show.bs.modal", function () {
                    modal.off("click", "button.btn-info");
                    modal.on("click", "button.btn-info", function () {
                        var layerId = removeButtonRef.parent().data("id");
                        // update last selected
                        mapInstance.removeLayer(layers[layerId]);
                        delete layers[layerId];
                        removeButtonRef.parent().remove();
                    });
                });
                modal.modal("show");
            });
        };

        this.refreshColorPickerButton = function () {
            var $COLOR_BUTTON = $(".selectorRow .btn-default");
            $COLOR_BUTTON.off("changeColor");
            $COLOR_BUTTON.colorpicker({format: "rgb"}).on("changeColor", function (e) {
                var color = e.color.toString("rgba");
                var layerId = $(this).parent().data("id");
                layers[layerId].eachLayer(function (layer) {
                    if (layer instanceof L.Marker) {
                        var iconOpts = layer.options.icon.options;
                        iconOpts.borderColor = color;
                        iconOpts.textColor = color;
                        var newIcon = L.BeautifyIcon.icon(iconOpts);
                        layer.setIcon(newIcon);
                        // console.log("bus stop");
                    } else if (layer instanceof L.Polyline) {
                        // console.log("polyline");
                        layer.setStyle({color: color});
                    } else if (layer instanceof L.PolylineDecorator) {
                        // console.log("polylinedecorator");
                        layer.setStyle({color: color});
                        layer.options.patterns[0].symbol.options.pathOptions.color = color;
                    }
                });
                $(this).css("color", color);
            });
        };

        this.refreshVisibilityRoutesButton = function () {
            var $VISIBILITY_BUTTON = $(".selectorRow .visibility-routes");
            $VISIBILITY_BUTTON.off("click");
            $VISIBILITY_BUTTON.click(function () {
                var button = $(this);
                var span = button.find("span");
                var layerId = button.parent().data("id");
                console.log(layers[layerId]);

                if (span.hasClass("glyphicon-eye-open")) {
                    button.removeClass("btn-success").addClass("btn-warning");
                    span.removeClass("glyphicon-eye-open").addClass("glyphicon-eye-close");
                    mapInstance.removeLayer(layers[layerId]);
                } else {
                    button.removeClass("btn-warning").addClass("btn-success");
                    span.removeClass("glyphicon-eye-close").addClass("glyphicon-eye-open");
                    mapInstance.addLayer(layers[layerId]);
                }
            });
        };


        this.addTableInfo = function (data) {
            let $TABLE = $('#shapeDetail');
            $TABLE.DataTable({
                language: {
                    url: "//cdn.datatables.net/plug-ins/1.10.13/i18n/Spanish.json",
                    decimal: ",",
                    thousands: "."
                },
                retrieve: true,
                data: data,
                orderable: false,
                dom: 'Brt',
                buttons: [
                    {
                        extend: "excelHtml5",
                        text: "Exportar a excel",
                        className: "buttons-excel buttons-html5 btn btn-success",
                        exportOptions: {
                            columns: [1, 2, 3, 4, 5, 6]
                        }
                    },
                    {
                        extend: 'copy',
                        text: "Copiar datos",
                        className: "buttons-excel buttons-html5 btn btn-default",
                    }
                ],
                columns: [
                    {title: "Periodo Transantiago", data: "timePeriod", searchable: false},
                    {title: "Inicio", data: "startPeriodTime", searchable: false},
                    {title: "Fin", data: "endPeriodTime", searchable: false},
                    {title: "Frecuencia [Bus/h]", data: "frecuency", searchable: false},
                    {title: "Capacidad [Plazas/h]", data: "capacity", searchable: false},
                    {title: "Distancia [km]", data: "distance", searchable: false},
                    {title: "Velocidad [km/h]", data: "speed", searchable: false},
                ]
            });
        };

        this.refreshInfoButton = function () {
            let $INFO_BUTTON = $(".selectorRow .showInfo");
            $INFO_BUTTON.off("click");
            $INFO_BUTTON.click(function () {
                    let route = $(this).closest(".selectorRow").find(".route").val();
                    let date = $(this).closest(".selectorRow").find(".date").val();
                    let period = $(this).closest(".selectorRow").find(".period").val();
                    date = date !== null ? [[date]] : [[]];
                    let params = {
                        authRouteCode: route,
                        dates: JSON.stringify(date)
                    };
                    $.getJSON(Urls["esapi:opdataAuthRoute"](), params, function (data) {
                        if (data.status) {
                            showMessage(data.status);
                            return;
                        }
                        $INFO_BUTTON.blur();
                        let $INFOMODAL = $("#shape_info");
                        $INFOMODAL.modal("show");
                        $INFOMODAL.on('shown.bs.modal', function () {
                            $INFOMODAL.trigger('focus');
                            _self.addTableInfo([data.data[period]]);
                        })
                    });
                }
            );
        };

        this.addRow = function (dateList, userRouteList) {
            var newId = selectorId;
            selectorId++;
            var row = '<div class="selectorRow" data-id="' + newId + '">' +
                '<button class="btn btn-danger btn-sm" ><span class="glyphicon glyphicon-remove" aria-hidden="true"></span></button>' +
                `<select id=dateSelect-${newId} class="form-control date">` + dateList + '</select>' +
                `<select id=userRouteSelect-${newId} class="form-control userRoute">` + userRouteList + '</select>' +
                `<select id=routeSelect-${newId} class="form-control route"></select>` +
                '<button class="btn btn-default btn-sm" ><span class="glyphicon glyphicon-tint" aria-hidden="true"></span></button>' +
                '<button class="btn btn-success btn-sm visibility-routes" ><span class="glyphicon glyphicon-eye-open" aria-hidden="true"></span></button>' +
                '<button class="btn btn-success btn-sm visibility-stops" ><span class="glyphicon fa fa-bus" aria-hidden="true"></span></button>' +
                `<select id=periodSelect-${newId} class="form-control period"></select>` +
                '<button class="btn btn-success btn-sm showInfo" ><span class="glyphicon glyphicon-info-sign" aria-hidden="true"></span></button>' +
                '</div>';
            $ROW_CONTAINER.append(row);
            _self.refreshControlEvents(newId);
            _self.refrehRemoveButton();
            _self.refreshColorPickerButton();
            _self.refreshVisibilityRoutesButton();
            _self.refreshInfoButton();

            layers[newId] = new L.FeatureGroup([]);
            mapInstance.addLayer(layers[newId]);

//            $ROW_CONTAINER.find(".form-control").last().change();
            $(".form-control").select2({width: 'element'});
        };

        this.loadBaseData = function () {

            $.getJSON(Urls["esapi:shapeBase"](), function (data) {
                // data for selectors
                _self.data = data.user_routes;
                _self.dates_period_dict = data.dates_periods_dict;
                _self.periods = data.periods;
                let userRouteList = Object.keys(data.user_routes).map(e =>
                    "<option>" + e + "</option>"
                ).join("");
                let dateList = data.dates.reverse().map(function (el) {
                    return "<option>" + el + "</option>";
                }).join("");

                // activate add button when data exist
                $("#addRouteButton").click(function () {
                    _self.addRow(dateList, userRouteList);
                });
            });
        };

    }

    var mapShapeApp = new MapShapeApp();
    mapShapeApp.loadBaseData();
    var elements = document.querySelectorAll(".leaflet-control a");
    for (var i = 0; i < elements.length; ++i) {
        elements[i].setAttribute("tabindex", "-1");
    }
    document.activeElement.blur();

})
;