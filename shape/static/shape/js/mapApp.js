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
                '<div id="header" style="display: none">' +
                '<div class="form-inline" >' +
                '<button id="timePeriodButton" class="btn btn-default" ><span class="fa fa-bus" aria-hidden="true"> Ver información operacional </span></button>' + '</div>' +
                '<div class="form-inline" >' +
                '<div class="form-row">' +
                '<div class="form-group col">' +
                '<button class="btn btn-default-disabled btn-sm" ><span class="glyphicon glyphicon-remove" aria-hidden="true"></span></button>' +
                '<button class="btn btn-default-white btn-sm date" >Programa de Operación</button>' +
                '<button class="btn btn-default-white btn-sm userRoute"" >Servicio</button>' +
                '<button class="btn btn-default-white btn-sm route" >Servicio Sonda</button>' +
                '<button class="btn btn-default-disabled btn-sm" ><span class="glyphicon glyphicon-remove" aria-hidden="true"></span></button>' +
                '<button class="btn btn-default-disabled btn-sm" ><span class="glyphicon glyphicon-remove" aria-hidden="true"></span></button>' +
                '<button class="btn btn-default-disabled btn-sm" ><span class="glyphicon glyphicon-remove" aria-hidden="true"></span></button>' +
                '</div>' +
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

        $("#timePeriodButton").click(function () {
            let routeSelector = $("#routeListContainer");
            let periodInfoList = [];
            let requestList = [];
            let uniqueInfoSet = new Set();

            routeSelector.children().each(function (index, el) {
                let route = $(el).closest(".selectorRow").find(".route").val();
                let routeText = $(el).closest(".selectorRow").find(".route option:selected").text();
                let userRoute = $(el).closest(".selectorRow").find(".userRoute").val();
                let date = $(el).closest(".selectorRow").find(".date").val();
                date = date !== null ? [[date]] : [[]];
                let params = {
                    authRouteCode: route,
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
                        $(this).off('shown.bs.modal');
                    });
                }
            );
        });


        L.control.zoom({
            position: 'topright'
        }).addTo(mapInstance);


        var $ROW_CONTAINER = $("#routeListContainer");

        var layers = {};

        var selectorId = 1;

        this.sendData = function (e) {
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

                // update color
                let $COLOR_BUTTON = $(`#colorSelect-${layerId}`);
                let color = $COLOR_BUTTON.css("color");
                updateLayerColor(color, layerId);

                // update routes
                let routesButton = $(`#visibilityRoutes-${layerId}`);
                let routesSpan = routesButton.find("span");
                let routesActive = routesSpan.hasClass("glyphicon-eye-open");
                updateLayerRoutes(!routesActive, layerId, routesButton, routesSpan);

                // update stops
                let stopButton = $(`#visibilityStops-${layerId}`);
                let stopSpan = stopButton.find("span");
                let stopActive = stopButton.hasClass("btn-success");
                updateStopRoutes(!stopActive, layerId, stopButton, stopSpan);

            });
        };

        this.refreshControlEvents = function (id) {

            // handle user route selector
            let $USER_ROUTE = $(`#userRouteSelect-${id}`);
            $USER_ROUTE.off("change");
            $USER_ROUTE.change(function () {
                let selector = $(this).closest(".selectorRow");
                let userRoute = selector.find(".userRoute").first().val();
                let route = selector.find(".route").first();
                let date = selector.find(".date").first().val();

                //update authroute list
                let routeValues = _self.data[date][userRoute];
                route.empty();
                route.select2({
                    data: routeValues.map(e => {
                        let date_dict = _self.op_routes_dict[date] || {};
                        let text = date_dict[e] || e;
                        text = text === e ? e : `${text} (${e})`;
                        return {
                            id: e,
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
            $ROUTE.off("change");
            $ROUTE.change(function () {
                _self.sendData(this);
            });


            // handle date selector
            let $DATE = $(`#dateSelect-${id}`);
            $DATE.off("change");
            $DATE.change(function () {
                let selector = $(this).closest(".selectorRow");
                let date = selector.find(".date").first().val();
                let userRoutes = selector.find(".userRoute").first();

                let params = {
                    "op_program": date
                };
                //get user_routes
                $.getJSON(Urls["esapi:shapeUserRoutes"](), params, function (data) {
                    userRoutes.empty();
                    _self.data[date] = data.user_routes;
                    let dataList = Object.keys(_self.data[date]).sort(sortAlphaNum);
                    userRoutes.select2({
                        data: dataList.map(e => {
                            return {
                                id: e,
                                text: e
                            }
                        })
                    });
                    userRoutes.trigger("change");
                });

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
                console.log(color);
                let routesButton = lastSelected.find(".visibility-routes").find("span");
                $(`#visibilityRoutes-${id}`).find("span").removeClass().addClass(routesButton.attr("class"));
                let stopButton = lastSelected.find(".visibility-stops");
                $(`#visibilityStops-${id}`).removeClass().addClass(stopButton.attr("class"));


            } else {
                $("#header").css('display', "block");
            }$scope.$broadcast('', );
            
            $USER_ROUTE.trigger("change");
            //$DATE.trigger("change");

        };

        this.refreshRemoveButton = function () {
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

        const updateLayerColor = (color, layerId) => {
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
        };

        this.refreshColorPickerButton = function () {
            var $COLOR_BUTTON = $(".selectorRow .btn-default");
            $COLOR_BUTTON.off("changeColor");
            $COLOR_BUTTON.colorpicker({format: "rgb"}).on("changeColor", function (e) {
                var color = e.color.toString("rgba");
                var layerId = $(this).parent().data("id");
                updateLayerColor(color, layerId);
                $(this).css("color", color);
            });
        };

        const updateLayerRoutes = (update, layerId, button, span) => {
            if (update) {
                button.removeClass("btn-success").addClass("btn-warning");
                span.removeClass("glyphicon-eye-open").addClass("glyphicon-eye-close");
                layers[layerId].eachLayer(function (layer) {
                    if (layer instanceof L.Polyline) {
                        mapInstance.removeLayer(layer);
                    } else if (layer instanceof L.PolylineDecorator) {
                        mapInstance.removeLayer(layer);
                    }
                });
            } else {
                button.removeClass("btn-warning").addClass("btn-success");
                span.removeClass("glyphicon-eye-close").addClass("glyphicon-eye-open");
                layers[layerId].eachLayer(function (layer) {
                    if (layer instanceof L.Polyline) {
                        mapInstance.addLayer(layer);
                    } else if (layer instanceof L.PolylineDecorator) {
                        mapInstance.addLayer(layer);
                    }
                });
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
                layers[layerId].eachLayer(function (layer) {
                    if (layer instanceof L.Marker) {
                        mapInstance.removeLayer(layer);
                    }
                });
            } else {
                button.removeClass("btn-warning").addClass("btn-success");
                span.removeClass("fa-bus").addClass("fa-bus");
                layers[layerId].eachLayer(function (layer) {
                    if (layer instanceof L.Marker) {
                        mapInstance.addLayer(layer);
                    }
                });
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


        this.addTableInfo = function () {
            let $TABLE = $('#shapeDetail');
            $TABLE.DataTable({
                language: {
                    url: "//cdn.datatables.net/plug-ins/1.10.13/i18n/Spanish.json",
                    decimal: ",",
                    thousands: "."
                },

                pageLength: 28,
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
                    {title: "Frecuencia [Bus/h]", data: "frecuency", searchable: false},
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

        this.addRow = function (dateList, userRouteList) {
            var newId = selectorId;
            selectorId++;
            var row = '<div class="selectorRow" data-id="' + newId + '">' +
                '<button class="btn btn-danger btn-sm" ><span class="glyphicon glyphicon-remove" aria-hidden="true"></span></button>' +
                `<select id=dateSelect-${newId} class="form-control date">` + dateList + '</select>' +
                `<select id=userRouteSelect-${newId} class="form-control userRoute">` + userRouteList + '</select>' +
                `<select id=routeSelect-${newId} class="form-control route"></select>` +
                `<button id=colorSelect-${newId} class="btn btn-default btn-sm color-button" ><span class="glyphicon glyphicon-tint" aria-hidden="true"></span></button>` +
                `<button id=visibilityRoutes-${newId} class="btn btn-success btn-sm visibility-routes" ><span class="glyphicon glyphicon-eye-open" aria-hidden="true"></span></button>` +
                `<button id=visibilityStops-${newId} class="btn btn-success btn-sm visibility-stops" ><span class="glyphicon fa fa-bus" aria-hidden="true"></span></button>` +
                '</div>';
            $ROW_CONTAINER.append(row);
            _self.refreshControlEvents(newId);
            _self.refreshRemoveButton();
            _self.refreshColorPickerButton();
            _self.refreshVisibilityRoutesButton();
            _self.refreshVisibilityStopsButton();

            layers[newId] = new L.FeatureGroup([]);
            mapInstance.addLayer(layers[newId]);

            //$ROW_CONTAINER.find(".form-control").last().change();
            $(`#dateSelect-${newId}`).select2({width: 'element'});
            $(`#userRouteSelect-${newId}`).select2({width: 'element'});
            $(`#routeSelect-${newId}`).select2({width: 'element'});
        };

        this.loadBaseData = function () {

            $.getJSON(Urls["esapi:shapeBase"](), function (data) {
                // data for selectors
                _self.data = {};
                _self.data[data.dates[data.dates.length - 1]] = data.user_routes;
                _self.dates_period_dict = data.dates_periods_dict;
                _self.op_routes_dict = data.op_routes_dict;
                _self.periods = data.periods;
                let userRouteList = (Object.keys(data.user_routes).sort(sortAlphaNum));
                userRouteList = userRouteList.map(e =>
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

            _self.addTableInfo()
        };
    }

    var mapShapeApp = new MapShapeApp();
    mapShapeApp.loadBaseData();
    $("#modalList").detach().appendTo($(".main_container")[0]);
    document.activeElement.blur();

})
;