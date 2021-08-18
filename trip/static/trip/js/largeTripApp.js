"use strict";
$(document).ready(function () {
  function LargeTripApp() {
    let _self = this;
    let $STAGES_SELECTOR = $(".netapas_checkbox");
    let $DATA_LIMITS = $("#dataLimits");
    let $ORIGIN_OR_DESTINATION_SELECTOR = $("#originOrDestination");

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
    let slider = $DATA_LIMITS.data("ionRangeSlider");

    // data given by server
    let data = null;
    let mapOpts = {
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

    let getColorScale = function () {
      let checkbox = document.querySelector("#colorscale_checkbox");
      if (checkbox.checked) {
        return "sequential";
      } else {
        return "divergent";
      }
    };

    this.setDataLimits = function (minVal, maxVal) {
      let step = (maxVal - minVal) / 4;
      let expMin = Math.floor(Math.log(minVal) / Math.LN10);
      let expStep = Math.floor(Math.log(step) / Math.LN10);
      let coefMin = Math.floor(2.0 * minVal / Math.pow(10, expMin)) / 2.0;
      let coefStep = Math.floor(10 * step / Math.pow(10, expStep)) / 10.0;
      let roundedMin = coefMin * Math.pow(10, expMin);
      let roundedStep = coefStep * Math.pow(10, expStep);

      let grades = [Math.max(1, roundedMin), roundedMin + roundedStep, roundedMin + 2 * roundedStep, roundedMin + 3 * roundedStep, roundedMin + 4 * roundedStep];

      mapOpts.count.grades = grades;
      mapOpts.count.grades_str = grades.map(function (x) {
        return parseInt(x.toFixed(0)).toLocaleString();
      });
      _self.updateMap();
    };

    let setScaleSwitch = function () {
      let checkbox = document.querySelector("#colorscale_checkbox");
      new Switchery(checkbox, {
        size: "small",
        color: "#777",
        jackColor: "#fff",
        secondaryColor: "#777",
        jackSecondaryColor: "#fff"
      });
      checkbox.onchange = function () {
        let opts = {
          scale: getColorScale()
        };
        _self.updateMap(opts);
      };
    };
    setScaleSwitch();

    let printAmountOfData = function () {
      let tripQuantity = data.aggregations.sum_expansion_factor.value;
      let dataQuantity = data.hits.total;
      document.getElementById("tripTotalNumberLabel").innerHTML = tripQuantity === 1 ? "viaje" : "viajes";
      document.getElementById("tripTotalNumberValue").innerHTML = tripQuantity.toLocaleString();

      document.getElementById("dataTotalNumberLabel").innerHTML = dataQuantity === 1 ? "dato" : "datos";
      document.getElementById("dataTotalNumberValue").innerHTML = dataQuantity.toLocaleString();
    };

    this.setData = function (newData) {
      data = newData;
      printAmountOfData();
      let values = newData.aggregations.by_zone.buckets.map(function (el) {
        return parseFloat(el.expansion_factor.value.toFixed(2));
      });
      let min = Math.min(...values);
      let max = Math.max(...values);
      slider.update({
        min: min,
        max: max,
        from: min,
        to: max
      });
      _self.setDataLimits(min, max);
    };

    this.updateMap = function (opts) {
      opts = opts || {};
      console.log("updateMap method called!");
      let scale = opts.scale || getColorScale();
      let selectedKPI = 'count';
      let legendOpts = mapOpts[selectedKPI];
      mapApp.refreshMap([], scale, selectedKPI, legendOpts);
    };

    let opts = {
      getDataZoneById: function (zoneId) {
        if (data === null) {
          return null;
        }
        let zoneData = data.aggregations.by_zone.buckets;
        let answer = zoneData.filter(function (el) {
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
        let grades = mapOpts[kpi].grades;
        if (value < grades[0]) {
          return null;
        }

        for (let i = 1; i < grades.length; i++) {
          if (value <= grades[i]) {
            return colors[i - 1];
          }
        }
        return colors[grades.length - 1];
      }
    };
    let mapApp = new MapApp(opts);

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
    loadRangeCalendar(Urls["esapi:availableTripDays"](), {});


    let app = new LargeTripApp();

    let afterCall = function (data, status) {
      if (status) {
        processData(data, app);
      }
    };
    let opts = {
      urlFilterData: Urls["esapi:largeTravelData"](),
      afterCallData: afterCall,
      dataUrlParams: function () {
        return {
          stages: app.getStages(),
          originOrDestination: app.getOriginOrDestination()
        }
      }
    };
    let manager = new FilterManager(opts);
    // load first time
    app.loadLayers(function () {
      manager.updateData();
    });
  })();
})
;