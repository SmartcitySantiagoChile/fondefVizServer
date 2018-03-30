"use strict";
$(document).ready(function () {
    function LargeTripApp() {
        var _self = this;
        var $STAGES_SELECTOR = $(".netapas_checkbox");
        var $DATA_LIMITS = $("#dataLimits");

        $STAGES_SELECTOR.each(function (index, html) {
            console.log(html);
            new Switchery(html, {
                size: 'small',
                color: 'rgb(38, 185, 154)'
            });
        });

        $DATA_LIMITS.ionRangeSlider({
            type: "double",
            min: 0,
            max: 1,
            from: 0,
            to: 1,
            onFinish: function (data) {
                _self.setDataLimits(data.from, data.to);
                redraw(options);
                updateMapDocCount(options);
            }
        });

        // data given by server
        var data = null;

        this.getStages = function(){
            var stages = $STAGES_SELECTOR.filter(function(index, el){
                return el.checked;
            }).map(function(index, el){
                return el.getAttribute('data-ne-str')
            }).get();
            console.log(stages);
            return stages;
        };

        var getColorScale = function () {
            var checkbox = document.querySelector("#colorscale_checkbox");
            if (checkbox.checked) {
                return "sequential";
            } else {
                return "divergent";
            }
        };

        var grades = null;
        var gradesStr = null;

        this.setDataLimits = function (minVal, maxVal) {
            var visibleLimits = [minVal, maxVal];
            var step = (maxVal - minVal) / 4;
            var expMin = Math.floor(Math.log(minVal) / Math.LN10);
            var expStep = Math.floor(Math.log(step) / Math.LN10);
            var coefMin = Math.floor(2.0 * minVal / Math.pow(10, expMin)) / 2.0;
            var coefStep = Math.floor(10 * step / Math.pow(10, expStep)) / 10.0;
            var roundedMin = coefMin * Math.pow(10, expMin);
            var roundedStep = coefStep * Math.pow(10, expStep);

            grades = [Math.max(1, roundedMin), roundedMin + roundedStep, roundedMin + 2 * roundedStep, roundedMin + 3 * roundedStep, roundedMin + 4 * roundedStep];
            gradesStr = grades.map(function (x) {
                return parseInt(x.toFixed(0)).toLocaleString();
            });
            _self.updateMap({
                visibleLimits: visibleLimits
            });
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
            document.getElementById("visualization_doc_count_txt").innerHTML = quantity === 1 ? "dato" : "datos";
            document.getElementById("visualization_doc_count").innerHTML = quantity.toLocaleString();
        };

        this.setData = function (newData) {
            data = newData;
            printAmountOfData();
        };

        this.updateMap = function (opts) {
            console.log("updateMap method called!");
            var scale = opts.scale || getColorScale();

            var legendOpts = {
                grades: grades,
                grades_str: gradesStr,
                legend_post_str: "hola"
            };
            mapApp.refreshMap(destinationZoneIds, scale, selectedKPI, legendOpts);
        };

        var opts = {
            getDataZoneById: function (zoneId) {
                if (data === null) {
                    return null;
                }
                var zoneData = data.aggregations[$SECTOR_SELECTOR.val()].by_zone.buckets;
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
        app.setData(data.large);
        app.updateMap({});
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
                    stages: app.getStages()
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