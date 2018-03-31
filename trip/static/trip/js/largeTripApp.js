"use strict";
$(document).ready(function () {
    function LargeTripApp() {
        var _self = this;
        var $STAGES_SELECTOR = $(".netapas_checkbox");
        var $DATA_LIMITS = $("#dataLimits");
        var $ORIGIN_OR_DESTINATION_SELECTOR = $("#originOrDestination");

        [$STAGES_SELECTOR, $ORIGIN_OR_DESTINATION_SELECTOR].forEach(function (el) {
            el.each(function (index, html) {
                new Switchery(html, {
                    size: 'small',
                    color: 'rgb(38, 185, 154)'
                });
            });
        });

        $DATA_LIMITS.ionRangeSlider({
            type: "double",
            min: 0,
            max: 1,
            onFinish: function (data) {
                _self.setDataLimits(data.from, data.to);
                _self.updateMap();
            }
        });
        var slider = $DATA_LIMITS.data("ionRangeSlider");
        console.log(slider);
        // data given by server
        var data = null;
        var mapOpts = {
            count: {
                name: 'Cantidad de viajes',
                grades: [1, 10, 20, 30, 40],
                grades_str: ["1", "10", "20", "30", "40"],
                legend_post_str: "",
                map_fn: function (zone) {
                    return zone.doc_count;
                }
            }
        };

        this.getStages = function () {
            return $STAGES_SELECTOR.filter(function (index, el) {
                return el.checked;
            }).map(function (index, el) {
                return el.getAttribute('data-ne-str')
            }).get();
        };

        this.getOriginOrDestination = function () {
            return $ORIGIN_OR_DESTINATION_SELECTOR.get()[0].checked ? "origin" : "destination";
        };

        var getColorScale = function () {
            var checkbox = document.querySelector("#colorscale_checkbox");
            if (checkbox.checked) {
                return "sequential";
            } else {
                return "divergent";
            }
        };

        this.setDataLimits = function (minVal, maxVal) {
            var step = (maxVal - minVal) / 4;
            var expMin = Math.floor(Math.log(minVal) / Math.LN10);
            var expStep = Math.floor(Math.log(step) / Math.LN10);
            var coefMin = Math.floor(2.0 * minVal / Math.pow(10, expMin)) / 2.0;
            var coefStep = Math.floor(10 * step / Math.pow(10, expStep)) / 10.0;
            var roundedMin = coefMin * Math.pow(10, expMin);
            var roundedStep = coefStep * Math.pow(10, expStep);

            var grades = [Math.max(1, roundedMin), roundedMin + roundedStep, roundedMin + 2 * roundedStep, roundedMin + 3 * roundedStep, roundedMin + 4 * roundedStep];

            mapOpts.count.grades = grades;
            mapOpts.count.grades_str = grades.map(function (x) {
                return parseInt(x.toFixed(0)).toLocaleString();
            });
            _self.updateMap();
        };

        var setScaleSwitch = function () {
            var checkbox = document.querySelector("#colorscale_checkbox");
            new Switchery(checkbox, {
                size: "small",
                color: "#777",
                jackColor: "#fff",
                secondaryColor: "#777",
                jackSecondaryColor: "#fff"
            });
            checkbox.onchange = function () {
                var opts = {
                    scale: getColorScale()
                };
                _self.updateMap(opts);
            };
        };
        setScaleSwitch();

        var printAmountOfData = function () {
            var quantity = data.hits.total;
            document.getElementById("visualization_doc_count_txt").innerHTML = quantity === 1 ? "viaje" : "viajes";
            document.getElementById("visualization_doc_count").innerHTML = quantity.toLocaleString();
        };

        this.setData = function (newData) {
            data = newData;
            printAmountOfData();
            var values = newData.aggregations.by_zone.buckets.map(function(el){
                return el.doc_count;
            });
            slider.update({
                min: Math.min(...values),
                max: Math.max(...values)
            });
        };

        this.updateMap = function (opts) {
            opts = opts || {};
            console.log("updateMap method called!");
            var scale = opts.scale || getColorScale();
            var selectedKPI = 'count';
            var legendOpts = {
                grades: mapOpts[selectedKPI].grades,
                grades_str: mapOpts[selectedKPI].grades_str,
                legend_post_str: mapOpts[selectedKPI].legend_post_str
            };
            mapApp.refreshMap([], scale, selectedKPI, legendOpts);
        };

        var opts = {
            getDataZoneById: function (zoneId) {
                if (data === null) {
                    return null;
                }
                var zoneData = data.aggregations.by_zone.buckets;
                var answer = zoneData.filter(function (el) {
                    return el.key === zoneId;
                });
                if (answer.length) {
                    return answer[0];
                }
                return null;
            },
            getZoneValue: function (zone, kpi) {
                return mapOpts[kpi].map_fn(zone);
            },
            getZoneColor: function (value, kpi, colors) {
                // use mapping
                var grades = mapOpts[kpi].grades;
                if (value < grades[0]) {
                    return null;
                }

                for (var i = 1; i < grades.length; i++) {
                    if (value <= grades[i]) {
                        return colors[i - 1];
                    }
                }
                return colors[grades.length - 1];
            }
        };
        var mapApp = new MapApp(opts);

        this.loadLayers = function (readyFunction) {
            mapApp.loadLayers(readyFunction);
        }
    }

    function processData(data, app) {
        if (data.status) {
            return;
        }
        app.setData(data.large);
        app.updateMap();
    }

    // load filters
    (function () {
        loadAvailableDays(Urls["esapi:availableTripDays"]());

        var app = new LargeTripApp();

        var afterCall = function (data) {
            processData(data, app);
        };
        var opts = {
            urlFilterData: Urls["esapi:largeTravelData"](),
            afterCallData: afterCall,
            dataUrlParams: function () {
                return {
                    stages: app.getStages(),
                    originOrDestination: app.getOriginOrDestination()
                }
            }
        };
        var manager = new FilterManager(opts);
        // load first time
        app.loadLayers(function () {
            manager.updateData();
        });
    })();
})
;