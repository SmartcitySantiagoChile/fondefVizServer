"use strict";
$(document).ready(function(){

  // define logic to manipulate data
  function Trip(expeditionId,
                route,
                licensePlate,
                busCapacity,
                stopTime,
                stopTimePeriod,
                dayType,
                loadProfile,
                expandedGetIn,
                expandedLanding) {

    this.expeditionId = expeditionId;
    this.route = route;
    this.licensePlate = licensePlate;
    this.busCapacity = busCapacity;
    this.stopTime = stopTime;
    this.stopTimePeriod = stopTimePeriod;
    this.dayType = dayType;
    this.loadProfile = loadProfile;
    this.expandedGetIn = expandedGetIn;
    this.expandedLanding = expandedLanding;
    this.visible = true;
  }

  /*
   * to manage grouped data
   */
  function DataManager(){
    // trips
    var _trips = [];
    // routes list
    var _xAxisData = null;
    // y average data
    var _yAxisData = null;
    // trips used to calculate average profile
    var _tripsUsed = 0;
    var _stopInfo = null;

    this.stopInfo = function(info){
      if(info === undefined){
        return _stopInfo;
      }
      _stopInfo = info;
    };
    this.getDataName = function(){
      if(_stopInfo !== null){
        var dayType = $("#dayTypeFilter").val();
        var period = $("#periodFilter").val();
        dayType = dayType!==null ? "_"+dayType.join("_"):"";
        period = period!==null ? "_"+period.join("_"):"";
        return "Perfil de carga " + _stopInfo["userStopCode"] + "_" + _stopInfo["authorityStopCode"] + dayType + period;
      }
      return "";
    };
    this.trips = function(trips){
      if(trips === undefined){
        return _trips;
      }
      _tripsUsed=0;
      for(var i=0;i<tripIdArray.length; i++){
        if(trips[i]["visible"]){
          _tripsUsed++;
        }
      }
      _trips = trips;
    };
    this.addTrip = function(trip){
      // create trip identifier
      if(trip["visible"]){
        _tripsUsed++;
      }
      trip["id"] = _trips.length;
      _trips.push(trip);
    };
    this.xAxisData = function(data){
      if( data === undefined){
        return _xAxisData;
      }
      _xAxisData = data;
    };
    this.yAxisData = function(data){
      if (data === undefined) {
        return _yAxisData;
      }
      _yAxisData = data;
    };
    this.tripsUsed = function(){
      return _tripsUsed;
    };
    this.cleanData = function(){
      _trips = [];
      _stopInfo = null;
      _xAxisData = null;
      _yAxisData = null;
      _tripsUsed = 0;
    };
    this.setVisibilty = function(tripIdArray, value){
      for(var i=0;i<tripIdArray.length; i++){
       var tripId = tripIdArray[i];
       if(_trips[tripId]["visible"] !== value){
         if(value === false){
           _tripsUsed--;
         }else{
           _tripsUsed++;
         }
       }
       _trips[tripId]["visible"] = value;
      }
    };
    this.checkAllAreAggregate = function(tripIdArray){
      var result = tripIdArray.length;
      for(var i=0;i<tripIdArray.length; i++){
       var tripId = tripIdArray[i];
       if(!_trips[tripId]["visible"]){
         result--;
       }
      }
      return result;
    };
    this.calculateAverage = function(){
      // erase previous visible data
      var xAxisLength = _xAxisData.length;
      var counterByRoute = [];
      var capacityByRoute = [];
      var tripQuantity = _trips.length;

      _yAxisData = {
        "expandedLanding": [],
        "expandedGetIn": [],
        "saturationRateBefore": [],
        "saturationRateAfter": [],
        "saturationDiff": [],
        "positiveSaturationRateAfter": [],
        "negativeSaturationRateAfter": [],
        "averageSaturationRateBefore": [],
        "averageSaturationRateAfter": []
      };

      for(var i=0; i<xAxisLength; i++){
          _yAxisData["expandedGetIn"].push(0);
          _yAxisData["expandedLanding"].push(0);
          _yAxisData["saturationRateBefore"].push(0);
          _yAxisData["saturationRateAfter"].push(0);
          _yAxisData["saturationDiff"].push(0);
          _yAxisData["positiveSaturationRateAfter"].push(0);
          _yAxisData["negativeSaturationRateAfter"].push(0);
          _yAxisData["averageSaturationRateBefore"].push(0);
          _yAxisData["averageSaturationRateAfter"].push(0);

          counterByRoute.push(0);
          capacityByRoute.push(0);
      }

      for(var tripIndex=0; tripIndex<tripQuantity; tripIndex++){
        var trip = _trips[tripIndex];

        if(!trip.visible){
          continue;
        }

        var key = _xAxisData.indexOf(trip.route);

        _yAxisData["expandedLanding"][key]+=trip.expandedLanding;
        _yAxisData["expandedGetIn"][key]+=trip.expandedGetIn;
        _yAxisData["saturationRateBefore"][key]+=trip.loadProfile;
        _yAxisData["saturationDiff"][key]+=trip.expandedGetIn - trip.expandedLanding;

        counterByRoute[key]+=1;
        capacityByRoute[key]+=trip.busCapacity;
      }

      // it calculates average
      for(var routeIndex=0;routeIndex<xAxisLength;routeIndex++){
        var percentageAfter = 0;

        if (counterByRoute[routeIndex] !== 0){
            _yAxisData["expandedLanding"][routeIndex]=_yAxisData["expandedLanding"][routeIndex]/counterByRoute[routeIndex];
            _yAxisData["expandedGetIn"][routeIndex]=_yAxisData["expandedGetIn"][routeIndex]/counterByRoute[routeIndex];

            _yAxisData["averageSaturationRateBefore"][routeIndex]=  _yAxisData["saturationRateBefore"][routeIndex] / counterByRoute[routeIndex];
            _yAxisData["averageSaturationRateAfter"][routeIndex]=(_yAxisData["saturationRateBefore"][routeIndex] + _yAxisData["saturationDiff"][routeIndex]) / counterByRoute[routeIndex];
        } else {
            _yAxisData["expandedLanding"][routeIndex]=0;
            _yAxisData["expandedGetIn"][routeIndex]=0;
            _yAxisData["averageSaturationRateBefore"][routeIndex]=0;
            _yAxisData["averageSaturationRateAfter"][routeIndex]= 0;
        }

        if (capacityByRoute[routeIndex] !== 0) {
            _yAxisData["saturationRateBefore"][routeIndex] = _yAxisData["saturationRateBefore"][routeIndex] / capacityByRoute[routeIndex] * 100;
            percentageAfter = _yAxisData["saturationDiff"][routeIndex] / capacityByRoute[routeIndex] * 100;
        }else {
            _yAxisData["saturationRateBefore"][routeIndex] = 0;
        }

        var incValue = 0;
        var decValue = 0;
        if(percentageAfter > 0){
          incValue = percentageAfter;
        }else if(percentageAfter < 0){
          decValue = percentageAfter*-1;
        }
        _yAxisData["saturationRateAfter"][routeIndex]=_yAxisData["saturationRateBefore"][routeIndex]+percentageAfter;
        _yAxisData["positiveSaturationRateAfter"][routeIndex]= incValue;
        _yAxisData["negativeSaturationRateAfter"][routeIndex]= decValue;
      }
    };
    this.getAttrGroup = function(attrName, formatFunc){
      var values = [];
      var dict = {};
      for(var i in _trips){
        var trip = _trips[i];
        if(!trip.visible){
          continue;
        }
        var attrValue = trip[attrName];
        attrValue = (formatFunc===undefined?attrValue:formatFunc(attrValue));
        if(dict[attrValue]){
          dict[attrValue]++;
        }else{
          dict[attrValue] = 1;
        }
      }
      for (var name in dict) {
          values.push({"name":name, "value": dict[name]});
      }
      return values;
    };
    this.getDatatableData = function(){
      var values = [];
      var max = 0;
      for(var i in _trips){
        var trip = $.extend({}, _trips[i]);
        /*if(!trip.visible){
          continue;
        }*/
        trip["busDetail"] = trip["licensePlate"] + " (" + trip["busCapacity"] + ")";
        values.push(trip);
      }
      return {"rows":values};
    };

    this.getDistributionData = function(){

      var globalMax = 0;
      var trips = [];

      for(var i in _trips){
        var trip = _trips[i];
        var tripData = {};
        if(!trip.visible){
          continue;
        }
        tripData["name"] = trip["stopTime"];

        var loadProfile = [];
        for(var i=0;i<_xAxisData.length;i++){
          var authStopCode = _xAxisData[i]["authCode"];
          var value = trip.yAxisData["loadProfile"][authStopCode];

          if(globalMax<value){
            globalMax = value;
          }
          loadProfile.push(value);
        }
        tripData["loadProfile"] = loadProfile;
        trips.push(tripData);
      }

      var result = {};
      result["globalMax"] = globalMax;
      result["trips"] = trips;

      return result;
    }
  }

  function ExpeditionApp(){
    var _self = this;
    var _dataManager = new DataManager();
    var _barChart = echarts.init(document.getElementById("barChart"), theme);
    var _wordcloudCharts = [
      echarts.init(document.getElementById("wordcloudChart1"), theme),
      echarts.init(document.getElementById("wordcloudChart2"), theme)];
    var _timePeriodChart = echarts.init(document.getElementById("timePeriodChart"), theme);
    var _datatable = $("#expeditionDetail").DataTable({
      lengthMenu: [[10, 25, 50], [10, 25, 50]],
      language: {
        url: "//cdn.datatables.net/plug-ins/1.10.13/i18n/Spanish.json",
        decimal: ",",
        thousands: "."
      },
      columns: [
        {
         targets: 0, searchable: false, orderable: false, className: "text-center", data: "visible",
         render: function (data, type, full, meta){
             return '<input type="checkbox" name="trip' + full.id + '" class="flat" checked>';
         }
        },
        { title: "Servicio-sentido", data: "route",   searchable: true},
        { title: "Patente(capacidad)", data: "busDetail", searchable: true},
        { title: "Período de pasada", data: "stopTimePeriod", searchable: true},
        { title: "Hora de pasada", data: "stopTime", searchable: true},
        { title: "Tipo de día", data: "dayType", searchable: true},
        { title: "Carga al llegar", data: "loadProfile", searchable: true},
        { title: "Subidas", data: "expandedGetIn", searchable: true},
        { title: "Bajadas", data: "expandedLanding", searchable: true},
        { title: "Carga al salir", data: "loadProfile", searchable: true,
          render: function(data, type, row, meta){
            return data + row.expandedGetIn - row.expandedLanding;
          }
        }
      ],
      order: [[3, "asc"]],
      createdRow: function ( row, data, index ) {
        $(row).addClass("success");
      },
      initComplete: function(settings){
        // Handle click on "Select all" control
        var mainCheckbox = $("#checkbox-select-all");
        mainCheckbox.iCheck({
          labelHover: false,
          cursor: true,
          checkboxClass: "icheckbox_flat-green"
        });
        mainCheckbox.on("ifToggled", function(event){
          // Get all rows with search applied
          var rows = _datatable.rows({"search":"applied"}).nodes();
          var addToAggr = false;
          var inputs = $("input.flat", rows);
          if(event.target.checked){
            inputs.prop("checked", true);
            $(rows).addClass("success");
            addToAggr = true;
          } else {
            inputs.prop("checked", false);
            $(rows).removeClass("success");
          }
          $("tbody input.flat").iCheck("update");
          var tripIds = _datatable.rows({"search":"applied"}).data().map(function(el){return el.id});
          _dataManager.setVisibilty(tripIds, addToAggr);
          _self.updateCharts();
        });
      }
    });
    _datatable.on("search.dt", function (event) {

      var el = $("#checkbox-select-all");
      var tripIds = _datatable.rows({"search":"applied"}).data().map(function(el){ return el.id});
      var resultChecked = _dataManager.checkAllAreAggregate(tripIds);

      if(resultChecked === tripIds.length){
        el.prop("checked", true);
      } else if(resultChecked === 0){
        el.prop("checked", false);
      } else {
        el.prop("checked", false);
        el.prop("indeterminate", true);
      }
      el.iCheck("update");
    });

    this.dataManager = function(dataManager){
      if(dataManager === undefined){
        return _dataManager;
      }
      _dataManager = dataManager;
      this.updateCharts();
      this.updateDatatable();
    };

    this.resizeCharts = function() {
        _barChart.resize();
        _timePeriodChart.resize();
        _wordcloudCharts.forEach(function(chart){
            chart.resize();
        });
    };

    var _updateTimePeriodChart = function(){
      var stopTime = _dataManager.getAttrGroup("stopTime", function(attrValue){
        return attrValue.substring(11, 13);
      });
      stopTime = stopTime.sort(function(a, b){
        a = parseInt(a.name);
        b = parseInt(b.name);
        return a-b;
      });
      var hours = stopTime.map(function(el){ return el.name;});
      var values = stopTime.map(function(el, index){ return [index, el.value];});
      var option = {
        tooltip: {
          positon: "top"
        },
        singleAxis: [{
          type: "category",
          boundaryGap: false,
          data: hours,
          top: "10%",
          height: "40%",
          axisLabel: {
            interval: 2
          }
        }],
        series: [{
          singleAxisIndex: 0,
          coordinateSystem: "singleAxis",
          type: "scatter",
          data: values,
          symbolSize: function (dataItem) {
            return [10, dataItem[1]*0.3];
          },
          tooltip: {
            formatter: function(params){
              var value = params.value[1];
              var name = params.name;
              var timePeriod = "[" + name + ":00, " + name + ":59]";
              return value + " expediciones iniciadas entre " + timePeriod;
            }
          }
        }]
      };
      _timePeriodChart.clear();
      _timePeriodChart.setOption(option,{notMerge: true});
    };

    var _updateWordcloudCharts = function(){
      var lpValues = _dataManager.getAttrGroup("licensePlate");
      var dayTypeValues = _dataManager.getAttrGroup("dayType");

      $("#licensePlateNumber").html("(" + lpValues.length + ")");

      var values = [lpValues, dayTypeValues];
      for(var i=0;i<values.length;i++){
        var chart = _wordcloudCharts[i];

        chart.on("click", function(params){
          console.log(params);
        });

        var options = {
          tooltip: {},
          series: [{
            type: "wordCloud",
            shape: "pentagon",
            width: "100%",
            height: "100%",
            sizeRange: [6, 14],
            rotationRange: [0, 0],
            rotationStep: 0,
            gridSize: 8,
            textStyle: {
              normal: {
                color: function () {
                  return "rgb(" + [
                    Math.round(Math.random() * 160),
                    Math.round(Math.random() * 160),
                    Math.round(Math.random() * 160)
                  ].join(",") + ")";
                }
              },
              emphasis: {
                shadowBlur: 10,
                shadowColor: "#169F85"
              }
            },
            data: values[i]
          }]
        };
        chart.clear();
        chart.setOption(options, {notMerge: true});
      }
    };

    var _updateDatatable = function(){
      var dataset = _dataManager.getDatatableData();
      var rows = dataset["rows"];

      _datatable.off("draw");
      _datatable.on("draw", function(oSettings) {
        $("tbody input.flat").iCheck("destroy");
        $("tbody input.flat").iCheck({
          labelHover: false,
          cursor: true,
          checkboxClass: "icheckbox_flat-green"
        });

        // activate iCheck in checkbox
        var dtRows = _datatable.rows().nodes();
        // attach events check and uncheck
        $("input.flat", dtRows).off("ifToggled");
        $("input.flat", dtRows).on("ifToggled", function(event){
          var tr = $(this).parent().parent().parent();
          var addToAggr = false;
          if(event.target.checked){
            tr.addClass("success");
            addToAggr = true;
          }else{
            tr.removeClass("success");
          }

          // updateChart
          var tripId = parseInt($(this).attr("name").replace("trip", ""));
          _dataManager.setVisibilty([tripId], addToAggr);
          _self.updateCharts();
        });
      });
      _datatable.clear();
      _datatable.rows.add(rows);
      _datatable.columns.adjust().draw();
    };

    var _updateBarChart = function(){
      _dataManager.calculateAverage();
      var yAxisData = _dataManager.yAxisData();
      var xAxisData = _dataManager.xAxisData();

      // get out, get in, load profile, percentage ocupation
      var yAxisDataName = ["Subidas promedio", "Bajadas promedio", "% Ocupación promedio a la llegada"];
      var yChartType = ["bar","bar", "bar", "bar", "bar"];
      var yStack = [null, null, "stack", "stack", "stack"];
      var xGridIndex = [1, 1, 0, 0, 0];
      var yGridIndex = [1, 1, 0, 0, 0];
      var dataName = ["expandedGetIn",
                      "expandedLanding",
                      //"saturationRateBefore",
                      "saturationRateAfter",
                      "positiveSaturationRateAfter",
                      "negativeSaturationRateAfter"];
      var positiveItemStyle = {
        normal: {
          color: "#33CC70",
          barBorderRadius: 0,
          label: {
            show: true,
            position: "top",
            formatter: function(p){
              return p.value > 0 ? ("▲" + p.value.toFixed(1) + "%"):"";
            }
          }
        }
      };
      var negativeItemStyle = {
        normal: {
          color: "#C12301",
          barBorderRadius: 0,
          stack: "stack",
          label: {
            show: true,
            position: "top",
            formatter: function(p){
              return p.value > 0 ? ("▼" + p.value.toFixed(1) + "%"):"";
            }
          }
        }
      };

      var yItemStyle = [{}, {}, {}, positiveItemStyle, negativeItemStyle];

      var series = [];
      for (var index=0; index<dataName.length; index++){
        var serie = {
          name: yAxisDataName[index],
          stack: yStack[index],
          type: yChartType[index],
          data: yAxisData[dataName[index]],
          itemStyle: yItemStyle[index],
          xAxisIndex: xGridIndex[index],
          yAxisIndex: yGridIndex[index]
        };
        series.push(serie);
      }

      var title = _dataManager.stopInfo().name;
      var subtitle = "Código de usuario: " + _dataManager.stopInfo().userStopCode + "  Código de Transantiago: " + _dataManager.stopInfo().authorityStopCode;
      var options = {
        title: {
          text: title,
            subtext: subtitle
        },
        legend: {
          data: yAxisDataName,
          right: 0,
          top: "45px"
        },
        axisPointer: {
          link: [{xAxisIndex: "all"}],
          snap: true
        },
        toolbox: {
          show : true,
          itemSize: 20,
          left: "center",
          bottom: "0px",
          feature : {
            mark : {show: false},
            restore : {show: false, title: "restaurar"},
            saveAsImage : {show: true, title: "Guardar imagen", name: _dataManager.getDataName()},
            dataView: {
              show: true,
              title: "Ver datos",
              lang: ["Datos del gráfico", "cerrar", "refrescar"],
              buttonColor: "#169F85",
              readOnly: true,
              optionToContent: function(opt) {
                  var axisData = opt.xAxis[0].data;
                  var series = opt.series;
                  var stopInfo = _dataManager.stopInfo();
                  var yData = _dataManager.yAxisData();

                  var textarea = document.createElement('textarea');
                  textarea.style.cssText = 'width:100%;height:100%;font-family:monospace;font-size:14px;line-height:1.6rem;';
                  textarea.readOnly = "true";

                  var dayTypeFilter = $("#dayTypeFilter").val()!==null?$("#dayTypeFilter").val().join("\t"):["Todos"];
                  var periodFilter = $("#periodFilter").val()!==null?$("#periodFilter").val().join("\t"):["Todos"];
                  var meta = "tipo(s) de día:\t" + dayTypeFilter + "\n";
                  meta += "período(s):\t" + periodFilter + "\n\n";

                  var header = "Código usuario\tCódigo transantiago\tNombre parada\tServicio\tCarga promedio a la llegada\tCarga promedio a la salida";
                  series.forEach(function(el, index){
                      var name = el.name;
                      if (index === 3) {
                        name = "Variación % positiva"
                      } else if (index === 4) {
                        name = "Variación % negativa"
                      }
                      header += "\t" + name;
                  });
                  header += "\n";
                  var body = "";
                  axisData.forEach(function(authorityRouteCode, index){
                      var serieValues = [yData.averageSaturationRateBefore[index], yData.averageSaturationRateAfter[index]];
                      series.forEach(function(serie){
                          serieValues.push(serie.data[index]);
                      });
                      serieValues = serieValues.join("\t").replace(/\./g, ",") + "\n";
                      body += [stopInfo.userStopCode, stopInfo.authorityStopCode, stopInfo.name, authorityRouteCode, serieValues].join("\t");
                  });

                  textarea.value = meta + header + body;
                  return textarea;
              }
            }
          }
        },
        grid: [
          {x: "10px", y:"70px", height: "30%", right:"0px", containLabel: true},
          {x: "30px", y2:"75px", height: "33%", right: "0px", containLabel: true}
        ],
        xAxis: [
          {gridIndex: 0, type: "category", data: xAxisData, axisLabel: { show: false}, axisTick: {interval:0}},
          {gridIndex: 1, type: "category", data: xAxisData, axisLabel: { rotate: 30, interval: 0}}
        ],
        yAxis: [
          {gridIndex: 0, type: "value", name: "Porcentaje", max: 100,
            axisLabel: {formatter: "{value} %"}, nameLocation: "middle", nameGap: 40,
            axisLine: {onZero: false}},
          {gridIndex: 1, type: "value", name: "Pasajeros", position: "left", nameLocation: "middle", nameGap: 30}
        ],
        series: series,
        tooltip: {
          axisPointer: {
            type: "shadow"
          },
          trigger: "axis",
          //alwaysShowContent: true,
          formatter: function(params){
            if (Array.isArray(params)){
              params.sort(function(a,b){return a.seriesIndex>b.seriesIndex});
              var xValue = params[0].dataIndex;
              var head = xAxisData[xValue];
              var info = [];
              info.push(head);
              var ball ="<span style='display:inline-block;margin-right:5px;border-radius:10px;width:9px;height:9px;background-color:{}'></span>";
              for(var i=0;i<params.length-1;i++){
                var el = params[i];
                var serieIndex = el.seriesIndex;
                var name = el.seriesName;
                var value = el.value.toFixed(2);
                if(serieIndex===2){
                  value = yAxisData.saturationRateBefore[xValue].toFixed(1) + "% (" + yAxisData.averageSaturationRateBefore[xValue].toFixed(2) + ")";
                }else if(serieIndex===3){
                  var sign = "▲";
                  if(el.value===0){
                    el = params[i+1];
                    sign = "▼";
                  }
                  name = "Variación";
                  value = sign + el.value.toFixed(1) + "%";
                }
                var colorBall = ball.replace("{}", el.color);
                info.push(colorBall + name + ": " + value);
              }
              // add saturation rate after
              var saturationRateInfo = ball.replace("{}", "#3145f7") + "Tasa ocupación promedio a la salida:" + yAxisData.saturationRateAfter[xValue].toFixed(1)+"% (" + yAxisData.averageSaturationRateAfter[xValue].toFixed(2) + ")";
              info.push(saturationRateInfo);
              return info.join("<br />");
            } else {
              var title = params.data.name;
              var name = params.seriesName;
              var value = params.value.toFixed(2);
              return title + "<br />" + name + ": " + value;
            }
          }
        }
      };

      _barChart.clear();
      _barChart.setOption(options, {
        notMerge: true
      });
    };

    var _updateGlobalStats = function() {
      $("#expeditionNumber").html(_dataManager.tripsUsed());
      $("#expeditionNumber2").html(_dataManager.tripsUsed());
    };

    this.updateCharts = function(){
      _updateBarChart();
      _updateWordcloudCharts();
      _updateTimePeriodChart();
      _updateGlobalStats();
    };
    this.updateDatatable = function(){
      _updateDatatable();
    };
    this.showLoadingAnimationCharts = function(){
      var loadingText = "Cargando...";
      _barChart.showLoading(null, {text: loadingText});
      _timePeriodChart.showLoading(null, {text: loadingText});
      for(var i=0;i<_wordcloudCharts.length;i++){
        _wordcloudCharts[i].showLoading(null, {text: loadingText});
      }
    };
    this.hideLoadingAnimationCharts = function(){
      _barChart.hideLoading();
      _timePeriodChart.hideLoading();
      for(var i=0;i<_wordcloudCharts.length;i++){
        _wordcloudCharts[i].hideLoading();
      }
    };
  }

  function processData(dataSource, app){
    console.log(dataSource);

    if(dataSource["status"]){
      var status = dataSource["status"];
      showMessage(status);
      return;
    }

    var stopInfo = dataSource.info;
    var trips = dataSource.trips;
    var dataManager = new DataManager();
    var tripGroupXAxisData = [];

    for(var expeditionId in trips){
      var trip = trips[expeditionId];

      // trip info
      var capacity = trip["capacity"];
      var licensePlate = trip["licensePlate"];
      var route = trip["route"];
      var stopTime = trip["stopTime"];
      var stopTimePeriod = trip["stopTimePeriod"];
      var dayType = trip["dayType"];
      //var distOnPath = trip["distOnPath"];

      var loadProfile = trip["loadProfile"];
      var expandedGetIn = trip["expandedGetIn"];
      var expandedLanding = trip["expandedLanding"];
      //var saturationRate = trip["loadProfile"]/capacity*100;

      trip = new Trip(expeditionId, route, licensePlate, capacity, stopTime,
                      stopTimePeriod, dayType, loadProfile, expandedGetIn, expandedLanding);
      dataManager.addTrip(trip);
    }

    dataManager.stopInfo(stopInfo);
    var xAxisData = dataManager.getAttrGroup("route").map(function(el){ return el.name;});
    dataManager.xAxisData(xAxisData);
    app.dataManager(dataManager);
  }

  // load filters
  (function (){
    // set locale
    moment.locale("es");

    $("#dayFilter").select2();
    $("#stopFilter").select2({
        ajax: {
            delay: 500, // milliseconds
            url: Urls["profile:getStopList"](),
            dataType: "json",
            data: function (params) {
                return {
                    term: params.term
                }
            },
            processResults: function (data, params) {
                return {
                    results: data.items
                }
            },
            cache: true
        },
        minimumInputLength: 3,
        language: {
          inputTooShort: function () {
            return "Ingresar 3 o más caracteres";
          }
        }
    });
    $("#dayTypeFilter").select2({placeholder: "Todos"});
    $("#periodFilter").select2({placeholder: "Todos"});
    $("#minutePeriodFilter").select2({placeholder: "Todos"});

    var app = new ExpeditionApp();
    var makeAjaxCall = true;
    $("#btnUpdateChart").click(function(){
      var day = $("#dayFilter").val();
      var stopCode = $("#stopFilter").val();
      var dayType = $("#dayTypeFilter").val();
      var period = $("#periodFilter").val();
      var minutes = $("#minutePeriodFilter").val();

      var params = {
        day: day
      };
      if (stopCode) {
        params["stopCode"] = stopCode;
      }
      if (dayType) {
        params["dayType"] = dayType;
      }
      if (period) {
        params["period"] = period;
      }
      if (minutes) {
          params["halfHour"] = minutes;
      }

      if (makeAjaxCall) {
          makeAjaxCall = false;
          app.showLoadingAnimationCharts();
          var loadingIcon = " <i class='fa fa-cog fa-spin fa-2x fa-fw'>";
          var previousMessage = $(this).html();
          var button = $(this).append(loadingIcon);
          $.getJSON(Urls["profile:getStopData"](), params, function (data) {
              processData(data, app);
          }).always(function () {
              makeAjaxCall = true;
              button.html(previousMessage);
              app.hideLoadingAnimationCharts();
          });
      }
    });
    $(window).resize(function() {
      app.resizeCharts();
    });
    $("#menu_toggle").click(function() {
      app.resizeCharts();
    });
  })();
});