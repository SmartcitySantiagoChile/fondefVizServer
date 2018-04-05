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
            var $FORM_CONTROLS = $(".form-control");
            $FORM_CONTROLS.off("change");
            $FORM_CONTROLS.change(function () {
                var layerId = $(this).closest(".selectorRow").data("id");
                var route = $(this).closest(".selectorRow").find(".route").first().val();
                var params = {
                    route: route,
                    operationProgramDate: $(this).closest(".selectorRow").find(".date").val()
                };

                $.getJSON(Urls["shape:route"](), params, function (data) {
                    if (data.status) {
                        showMessage(data.status);
                        return;
                    }

                    // update map
                    // clean featureGroup
                    layers[layerId].clearLayers();
                    var layer = layers[layerId];
                    app.addPolyline(layer, data.points, {
                        stops: data.stops,
                        route: route
                    });
                });
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

        this.addRow = function (dateList, authorityRouteList) {
            var newId = $ROW_CONTAINER.children().length + 1;
            var row = '<div class="selectorRow" data-id="' + newId + '">' +
                '<button class="btn btn-danger btn-sm" ><span class="glyphicon glyphicon-remove" aria-hidden="true"></span></button>' +
                '<select class="form-control input-sm date">' + dateList + '</select>' +
                '<select class="form-control input-sm route">' + authorityRouteList + '</select>' +
                '<button class="btn btn-default btn-sm" ><span class="glyphicon glyphicon-tint" aria-hidden="true"></span></button>' +
                '<button class="btn btn-success btn-sm visibility" ><span class="glyphicon glyphicon-eye-open" aria-hidden="true"></span></button>' +
                '<div/>';
            $ROW_CONTAINER.append(row);
            _self.refreshControlEvents();
            _self.refrehRemoveButton();
            _self.refreshColorPickerButton();
            _self.refreshVisibilityButton();

            layers[newId] = new L.FeatureGroup([]);
            mapInstance.addLayer(layers[newId]);

            $ROW_CONTAINER.find(".form-control").last().change();
        };

        this.loadBaseData = function () {
            $.getJSON(Urls["shape:base"](), function (data) {
                // data for selectors
                var authorityRouteList = data.routes.map(function (el) {
                    return "<option>" + el + "</option>";
                }).join("");
                var dateList = data.dates.map(function (el) {
                    return "<option>" + el + "</option>";
                }).join("");

                // activate add button when data exist
                $("#addRouteButton").click(function () {
                    _self.addRow(dateList, authorityRouteList);
                });
            });
        };
    }

    var mapShapeApp = new MapShapeApp();
    mapShapeApp.loadBaseData();
});