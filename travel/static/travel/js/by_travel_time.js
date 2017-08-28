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

$(document).ready(function () {

    var map;
    var geojson;

    // http://colorbrewer2.org/#type=sequential&scheme=GnBu&n=5
    function getColorByTViaje(time_min) {
        return time_min > 75 ? '#0868ac' :
               time_min > 60  ? '#43a2ca' :
               time_min > 45  ? '#7bccc4' :
               time_min > 30  ? '#bae4bc' :
                          '#f0f9e8';
    }

    function getTViajeById() {
        return 50;
    }

    function styleFunction(feature) {
        return {
            fillColor: getColorByTViaje(getTViajeById(feature.properties.id)),
            weight: 2,
            opacity: 1,
            color: 'white',
            dashArray: '3',
            fillOpacity: 0.7
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
        this._div.innerHTML = '<h4>Zonificación</h4>' +  (props ?
            '<b>' + props.comuna + '</b><br />id: ' + props.id + ''
            : 'Pon el ratón sobre una zona');
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

        return div;
    };

    function createMap() {
        var santiagoLocation = L.latLng(-33.459229, -70.645348);
        map = L.map("mapChart").setView(santiagoLocation, 10);

        L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/light-v9/tiles/256/{z}/{x}/{y}?access_token={accessToken}', {
            attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, Imagery © <a href="http://mapbox.com">Mapbox</a>',
            maxZoom: 18,
            accessToken: "pk.eyJ1IjoidHJhbnNhcHB2aXMiLCJhIjoiY2l0bG9qd3ppMDBiNjJ6bXBpY3J0bm40cCJ9.ajifidV4ypi0cXgiGQwR-A"
        }).addTo(map);
        
        // load zonas
        $.ajax({
            'global': false,
            // 'url': '/static/travel/data/sectores.geojson',
            // 'url': '/static/travel/data/lineasMetro.geojson',
            'url': '/static/travel/data/zonificacion777.geojson',
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

    function processData(response) {
        console.log(response);
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
        $('#periodFilter').select2({placeholder: 'Todos'});

        // $('#communeFilter').select2({placeholder: 'comuna'});
        // $('#halfhourFilter').select2({placeholder: 'media hora'});

        // Update Charts from filters
        $('#btnUpdateChart').click(function () {
            // TODO: enforce fromDate < toDate.

            var fromDate = $('#dateFromFilter').val();
            var toDate = $('#dateToFilter').val();
            var dayTypes = $('#dayTypeFilter').val();
            var periods = $('#periodFilter').val();

            console.log("--- update charts ---");
            console.log("from date: " + fromDate);
            console.log("to date: " + toDate);
            console.log("day types: " + dayTypes);
            console.log("periods: " + periods);
            console.log("-- -- -- -- -- -- -- ");

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

        });
    })() // end filters

});