"use strict";

var _dayTypes = {
    0: "Laboral",
    1: "Sábado",
    2: "Domingo"
};

var _dayTypes_reversed = {
    "Laboral": 0,
    "Sábado": 1,
    "Domingo": 2
};

var _selected_day_type_ids = [];
var _map_data = null;
var _sector = null;


$(document).ready(function () {

    var map;
    var geojson;

    // http://colorbrewer2.org/#type=sequential&scheme=GnBu&n=5
    function getColorByTViaje(time_min) {
        if (time_min === null) return "#cccccc";
        return time_min > 75 ? "#bd0026" :
            time_min > 60 ? "#f03b20" :
            time_min > 45 ? "#fd8d3c" :
            time_min > 30 ? "#fecc5c" :
                    "#ffffb2";
    }

    function getMapDataByZoneId(zone_id) {
        if (_map_data === null) {
            return null;
        }
        if (_sector === null) {
            return null;
        }
        if (!(_sector in _map_data.aggregations)) {
            return null;
        }
        if (!(zone_id in _map_data.aggregations[_sector].by_zone.buckets)) {
            return null
        }
        return _map_data.aggregations[_sector].by_zone.buckets[zone_id];
    }

    function getTViajeById(zone_id) {
        var zone = getMapDataByZoneId(zone_id);
        if (zone === null) return null;
        return zone.tviaje.value;
        // console.log("ERROR. zona inexistente de id: " + zone_id + " para sector: " + _sector)
    }

    function styleFunction(feature) {
        if (_map_data === null) {
            return {
                weight: 2,
                opacity: 0.1,
                color: 'white',
                dashArray: '3',
                fillOpacity: 0.1
            };
        }

        var hovered = false; // TODO

        var is_sector = _sector !== null && _sector.toUpperCase() === feature.properties.comuna.toUpperCase();
        if (is_sector) {
            return {
                fillColor: "green",
                weight: 2, // TODO: draw this on a top layer.. which can be deactivated on hover.. avoid dissapearing margins
                opacity: 1,
                color: 'green',
                dashArray: '0',
                fillOpacity: 0.5
            };
        }

        return {
            fillColor: getColorByTViaje(getTViajeById(feature.properties.id)),
            weight: 1,
            opacity: 1,
            color: 'white',
            dashArray: '3',
            fillOpacity: 0.8
        };
    }

    var info = L.control();

    function highlightFeatureForZone(e) {
        var layer = e.target;

        layer.setStyle({
            weight: 5,
            color: '#666',
            dashArray: '',
            fillOpacity: 0.7
        });

        if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
            layer.bringToFront();
        }
        info.update(layer.feature.properties);
    }
    function resetHighlight(e) {
        // resets style to default
        geojson.resetStyle(e.target);
        info.update();
    }

    function zoomToFeature(e) {
        map.fitBounds(e.target.getBounds());
    }

    function onEachFeature(feature, layer) {
        layer.on({
            mouseover: highlightFeatureForZone,
            mouseout: resetHighlight,
            click: zoomToFeature
        });
    }


    info.onAdd = function (map) {
        this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
        this.update();
        return this._div;
    };

    // method that we will use to update the control based on feature properties passed
    info.update = function (props) {
        this._div.innerHTML = '<h4>Zonificación 777</h4>';
        if (props) {
            this._div.innerHTML += '<b>' + props.comuna + '</b> (' + props.id + ')';

            var zone = getMapDataByZoneId(props.id);
            if (zone != null) {
                // console.log(zone)
                this._div.innerHTML += 
                    '<br/> - # Datos: ' + zone.doc_count +
                    '<br/> - # Etapas: ' + zone.n_etapas.value.toFixed(2) +
                    '<br/> - Duración: ' + zone.tviaje.value.toFixed(1) + ' [min]' +
                    '<br/> - Distancia (en ruta): ' + (zone.distancia_ruta.value / 1000.0).toFixed(2) + ' [km]' +
                    '<br/> - Distancia (euclideana): ' + (zone.distancia_eucl.value / 1000.0).toFixed(2) + ' [km]';
            } else {
                this._div.innerHTML += 
                    '<br/> Sin información para los filtros'
                    + '<br/> seleccionados';
            }
            
        } else {
            this._div.innerHTML += 'Pon el ratón sobre una zona';
        }
    };

    var legend = L.control({position: 'bottomright'});

    legend.onAdd = function (map) {

        var div = L.DomUtil.create('div', 'info legend'),
            grades = [0, 30, 45, 60, 75],
            labels = [];

        // loop through our density intervals and generate a label with a colored square for each interval
        for (var i = 0; i < grades.length; i++) {
            div.innerHTML +=
                '<i style="background:' + getColorByTViaje(grades[i] + 1) + '"></i> ' +
                grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
        }
        div.innerHTML +=
            '<br> <i style="background:' + getColorByTViaje(null) + '"></i>Sin Datos<br>';

        return div;
    };

    function createMap() {
        var santiagoLocation = L.latLng(-33.459229, -70.645348);
        map = L.map("mapChart").setView(santiagoLocation, 8);

        L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/light-v9/tiles/256/{z}/{x}/{y}?access_token={accessToken}', {
            attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, Imagery © <a href="http://mapbox.com">Mapbox</a>',
            minZoom: 8,
            maxZoom: 15,
            accessToken: "pk.eyJ1IjoidHJhbnNhcHB2aXMiLCJhIjoiY2l0bG9qd3ppMDBiNjJ6bXBpY3J0bm40cCJ9.ajifidV4ypi0cXgiGQwR-A"
        }).addTo(map);

        map.setMaxBounds(map.getBounds());
        map.setView(santiagoLocation, 11);
        
        // load zonas
        $.ajax({
            'global': false,
            // 'url': '/static/travel/data/sectores.geojson',
            // 'url': '/static/travel/data/lineasMetro.geojson',
            'url': '/static/js/data/zonificacion777.geojson',
            'dataType': "json",
            'success': function (data) {
                // sets a default style
                geojson = L.geoJson(data, {
                    style: styleFunction,
                    onEachFeature: onEachFeature
                }).addTo(map);
                info.addTo(map);
                legend.addTo(map);
            }
        });
    }

    function redraw() {
        geojson.setStyle(styleFunction);
    }

    function processData(response) {
        _map_data = response.map;
        updateAvailableSectors();
        redraw();
    }

    function updateTSPeriods(dayTypes) {
        // avoid when dayType has not changed.

        var periodSelect = document.getElementById('periodFilter');

        // remove all values
        while (periodSelect.firstChild) {
            periodSelect.removeChild(periodSelect.firstChild);
        }
        // clear list! and return
        if (dayTypes === null) {
            _selected_day_type_ids = [];
            return;
        }
        // TODO: do not delete already selected values!.. PS. keep the list sorted by id.
        _selected_day_type_ids = dayTypes;

        // required days as string
        var dayTypes_str = dayTypes.map(function(item) {
            return _dayTypes[item];
        });

        // put new ones
        for (var i=0, l=_allPeriods.length; i<l; i++) {
            var this_period = _allPeriods[i];
            if ( dayTypes_str.indexOf( this_period.fields.dayType ) !== -1 ) {
                var option = document.createElement("option");
                option.setAttribute("value", this_period.pk);
                option.appendChild(document.createTextNode(this_period.fields.transantiagoPeriod));
                periodSelect.appendChild(option);
            }
        }
    }

    function updateAvailableSectors() {
        
        function toTitleCase(str) {
            return str.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
        }

        // avoid processing when there is no data
        if (_map_data === null) {
            return;
        }
        var sectorSelect = document.getElementById('sectorSelector');
        var last_value = sectorSelect.value;

        // remove all values
        while (sectorSelect.firstChild) {
            sectorSelect.removeChild(sectorSelect.firstChild);
        }
        
        // update
        for (var sector_key in _map_data.aggregations) {
            var option = document.createElement("option");
            var sector_text = toTitleCase(sector_key);

            option.setAttribute("value", sector_key.toUpperCase());
            option.appendChild(document.createTextNode(sector_text));
            sectorSelect.appendChild(option);
        }

        var curr_value = sectorSelect.value;
        var selected;
        if (last_value == "") {
            // do nothing
            // console.log("last is empty");
            // selected = curr_value;
            selected = "SANTIAGO"; // DEFAULT

        } else if (last_value != curr_value) {
            // keep last
            // console.log("last is: '" + last_value + "'");
            // console.log("current is: '" + curr_value + "'");
            selected = last_value;
            
        } else {
            // use current
            // console.log("current: '" + curr_value + "'");
            selected = curr_value;
        }

        for (var i=0, l=sectorSelect.options.length, curr; i<l; i++)
        {
            curr = sectorSelect.options[i];
            curr.selected = false;
            if ( curr.value == selected ) {
                curr.selected = true;
            }
        }
        updateSelectedSector(selected);

    }

    function updateSelectedSector(selected) {
        _sector = selected;
        redraw();
    }

    createMap();

    // ========================================================================
    // FILTERS
    // ========================================================================
    (function () {

        // set locale
        moment.locale('es');

        var today = new Date();
        var tomorrow = new Date(today.getTime() + 24 * 60 * 60 * 1000);

        // datetime pickers
        $('#dateFromFilter').daterangepicker({
            singleDatePicker: true,
            language: "es",
            "minDate": "01/01/2015",
            "maxDate": tomorrow,
            "startDate": "13/03/2016"
             // "startDate": today,
        });
        $('#dateToFilter').daterangepicker({
            singleDatePicker: true,
            language: 'es',
            "minDate": "01/01/2015",
            "maxDate": tomorrow,
            "startDate": "15/03/2016"
            // "startDate": today,
        });

        
        var dayTypeSelect = document.getElementById('dayTypeFilter');

        // fill daytypes
        for (var i=0, l=_allDaytypes.length; i<l; i++)
        {
            var daytype = _allDaytypes[i];
            var option = document.createElement("option");
            option.setAttribute("value", daytype.pk);
            option.appendChild(document.createTextNode(daytype.name));
            dayTypeSelect.appendChild(option);
        }


        // set default day as LABORAL
        for (var i=0, l=dayTypeSelect.options.length, curr; i<l; i++)
        {
            curr = dayTypeSelect.options[i];
            if ( curr.text === "Laboral" ) {
                curr.selected = true;
            }
        }
        updateTSPeriods([_dayTypes_reversed["Laboral"]]);


        // day type and period filters
        $('#dayTypeFilter')
            .select2({placeholder: 'Cualquiera'})
            .on("select2:select select2:unselect", function(e) {
                var selection_ids = $(this).val();
                updateTSPeriods(selection_ids);
            });
        $('#periodFilter')
            .select2({placeholder: 'Todos'});
        $('#sectorSelector')
            .select2({
                placeholder: "Seleccione un sector",
                allowClear: true,
                minimumResultsForSearch: Infinity // hide search box
            })
            .on("select2:select", function(e) {
                var selected = $(this).val();
                updateSelectedSector(selected);
            })
            .on("select2:unselect", function(e) {
                updateSelectedSector(null);  
            });

        // $('#communeFilter').select2({placeholder: 'comuna'});
        // $('#halfhourFilter').select2({placeholder: 'media hora'});

        // Update Charts from filters
        function updateServerData() {
            // TODO: enforce fromDate < toDate.

            var fromDate = $('#dateFromFilter').val();
            var toDate = $('#dateToFilter').val();
            var dayTypes = $('#dayTypeFilter').val();
            var periods = $('#periodFilter').val();

            // console.log("--- update charts ---");
            // console.log("from date: " + fromDate);
            // console.log("to date: " + toDate);
            // console.log("day types: " + dayTypes);
            // console.log("periods: " + periods);
            // console.log("-- -- -- -- -- -- -- ");

            var request = {
                from: fromDate,
                to: toDate,
                daytypes: dayTypes,
                periods: periods
            };

            var update_button = $(this);
            var loading_text = update_button.html() + " <i class='fa fa-cog fa-spin fa-2x fa-fw'>";
            update_button.html(loading_text);
            $.getJSON('getDataByTime', request, processData).always(function(){
                update_button.html('Actualizar Datos')
            });

        }
        $('#btnUpdateChart').click(updateServerData());
        updateServerData();
    })() // end filters

});