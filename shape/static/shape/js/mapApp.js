"use strict";
$(document).ready(function () {

    function MapShapeApp() {
        var _self = this;
        var mapOpts = {
            mapId: $(".right_col")[0],
            maxZoom: 18
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

        this.refreshControlEvents = function () {

            //handle send data
            let sendData = e => {
                let layerId = $(e).closest(".selectorRow").data("id");
                let route = $(e).closest(".selectorRow").find(".route").val();
                let params = {
                    route: route,
                    operationProgramDate: $(e).closest(".selectorRow").find(".date").val()
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

            let $USER_ROUTE = $(".userRoute");
            $USER_ROUTE.off("change");
            $USER_ROUTE.change(function () {
                let userRoute = $(this).closest(".selectorRow").find(".userRoute").first().val();
                let route = $(this).closest(".selectorRow").find(".route");
                //update authroute list
                if (userRoute !== null) {
                    let routeValues = _self.data[userRoute];
                    route.empty();
                    route.append('<option value="" disabled selected> Ruta Transantiago </option>');
                    route.append(routeValues.map(e => '<option>' + e + '</option>').join(""));
                }
            });

            let $ROUTE = $(".route");
            $ROUTE.off("change");
            $ROUTE.change(function () {
                sendData(this);
            });

            let $DATE = $(".date");
            $DATE.off("change");
            $DATE.change(function () {
                if ($ROUTE.val() != null) {
                    sendData(this);
                }
            });
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

        this.refreshVisibilityButton = function () {
            var $VISIBILITY_BUTTON = $(".selectorRow .visibility");
            $VISIBILITY_BUTTON.off("click");
            $VISIBILITY_BUTTON.click(function () {
                var button = $(this);
                var span = button.find("span");
                var layerId = button.parent().data("id");

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
            let $TABLE = $('#shape_info');
            let thead = $TABLE.find("thead").find("tr");
            thead.empty();
            let head = ["Periodo Transantiago", "Inicio de periodo", "Fin de periodo", "Frecuencia", "Capacidad", "Distancia", "Velocidad"];
            let headRow = head.map(e => "<th>" + e + "</th>").join("");
            thead.append(headRow);
            let tbody = $TABLE.find("tbody");
            tbody.empty();
            let keys = Object.keys(data[0]);
            data.forEach(e => {
                    let tr = $("<tr></tr>");
                    tbody.append(tr);
                    let tds = keys.map(f => {
                        let value = e[f];
                        value = (typeof (value) === "number" && value % 1 !== 0) ? value.toFixed(3) : value;
                        return "<td>" + value + "</td>";
                    });
                    tr.append(tds);
                }
            );
        };

        this.refreshInfoButton = function () {
            let $INFO_BUTTON = $(".selectorRow .showInfo");
            $INFO_BUTTON.off("click");
            $INFO_BUTTON.click(function () {
                    let route = $(this).closest(".selectorRow").find(".route").val();
                    let date = $(this).closest(".selectorRow").find(".date").val();
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
                        _self.addTableInfo(data.data);
                        $("#shape_info").modal("show");

                    });
                }
            );
        };

        this.addRow = function (dateList, userRouteList) {
            var newId = $ROW_CONTAINER.children().length + 1;
            var row = '<div class="selectorRow" data-id="' + newId + '">' +
                '<button class="btn btn-danger btn-sm" ><span class="glyphicon glyphicon-remove" aria-hidden="true"></span></button>' +
                '<select class="form-control input-sm date"><option value="" disabled selected>Programa de Operación</option>' + dateList + '</select>' +
                '<select class="form-control input-sm userRoute"><option value="" disabled selected>Ruta Usuario</option>' + userRouteList + '</select>' +
                '<select class="form-control input-sm route"><option value="" disabled selected>Ruta Transantiago</option></select>' +
                '<button class="btn btn-default btn-sm" ><span class="glyphicon glyphicon-tint" aria-hidden="true"></span></button>' +
                '<button class="btn btn-success btn-sm visibility" ><span class="glyphicon glyphicon-eye-open" aria-hidden="true"></span></button>' +
                '<button class="btn btn-success btn-sm showInfo" ><span class="glyphicon glyphicon-info-sign" aria-hidden="true"></span></button>' +
                '<div/>';
            $ROW_CONTAINER.append(row);
            _self.refreshControlEvents();
            _self.refrehRemoveButton();
            _self.refreshColorPickerButton();
            _self.refreshVisibilityButton();
            _self.refreshInfoButton();

            layers[newId] = new L.FeatureGroup([]);
            mapInstance.addLayer(layers[newId]);

//            $ROW_CONTAINER.find(".form-control").last().change();
            $(".form-control").select2();
        };

        this.loadBaseData = function () {

            $.getJSON(Urls["esapi:shapeBase"](), function (data) {
                // data for selectors
                _self.data = data.user_routes;
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
})
;