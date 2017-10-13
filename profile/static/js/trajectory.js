"use strict";
$(document).ready(function(){

  // define logic to manipulate data
  function Trip(expeditionId,
                route,
                licensePlate,
                busCapacity,
                timeTripInit,
                timeTripEnd,
                authTimePeriod,
                dayType,
                data) {
    this.expeditionId = expeditionId;
    this.route = route;
    this.licensePlate = licensePlate;
    this.busCapacity = busCapacity;
    this.timeTripInit = timeTripInit;
    this.timeTripEnd = timeTripEnd;
    this.authTimePeriod = authTimePeriod;
    this.dayType = dayType;
    this.data = data;
    this.visible = true;
  }

  /*
   * to manage grouped data
   */
  function DataManager(){
    // trips
    var _trips = [];
    // trips are visible
    var _visibleTrips = 0;
    var _yAxisData = [];
    this.getDataName = function(){
      const FILE_NAME = 'Trayectorias con perfil de carga ';
      if(_trips.length>0){
        return FILE_NAME + _trips[0]['route'];
      }
      return '';
    };
    this.trips = function(trips){
      if(trips === undefined){
        return _trips;
      }
      _visibleTrips=0;
      for(var i=0;i<tripIdArray.length; i++){
        if(trips[i]['visible']){
          _visibleTrips++;
        }
      }
      _trips = trips;
    };
    this.addTrip = function(trip){
      // create trip identifier
      if(trip['visible']){
        _visibleTrips++;
      }
      trip['id'] = _trips.length;
      _trips.push(trip);
    };
    this.tripsUsed = function(){
      return _visibleTrips;
    };
    this.yAxisData = function(data){
      if(data === undefined){
        return _yAxisData;
      }
      _yAxisData = data;
    };
    this.cleanData = function(){
      _trips = [];
      _visibleTrips = 0;
    };
    this.setVisibility = function(tripIdArray, value){
      for(var i=0;i<tripIdArray.length; i++){
       var tripId = tripIdArray[i];
       if(_trips[tripId]['visible'] !== value){
         if(value === false){
           _visibleTrips--;
         }else{
           _visibleTrips++;
         }
       }
       _trips[tripId]['visible'] = value;
      }
    };
    this.checkAllAreAggregate = function(tripIdArray){
      var result = tripIdArray.length;
      for(var i=0;i<tripIdArray.length; i++){
       var tripId = tripIdArray[i];
       if(!_trips[tripId]['visible']){
         result--;
       }
      }
      return result;
    };
    this.getAttrGroup = function(attrName, formatFunc=undefined){
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
      for(var name in dict) {
        values.push({'name':name, 'value': dict[name]});
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
        trip['busDetail'] = trip['licensePlate'] + ' (' + trip['busCapacity'] + ')';
        var loadProfile = [];
        var hasNegativeValue = false;
        for(var i=0;i<trip.data.length;i++){
          var value = trip.data[i][2];
          if(value !== undefined && value<0){
            hasNegativeValue = true;
          }
          if(max<value){
            max = value;
          }
          loadProfile.push(value);
        }
        trip['sparkLoadProfile'] = loadProfile;
        trip['hasNegativeValue'] = hasNegativeValue;
        values.push(trip);
      }
      return {
        rows: values,
        maxHeight: max
      };
    }
  }

  function ExpeditionApp(){
    var _self = this;
    var _dataManager = new DataManager();
    var _barChart = echarts.init(document.getElementById('barChart'), theme);
    var _datatable = $('#expeditionDetail').DataTable({
      lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "Todos"]],
      language: {
        url: '//cdn.datatables.net/plug-ins/1.10.13/i18n/Spanish.json'
      },
      columns: [
        {
         'targets': 0, 'searchable': false, 'orderable': false, 'className': 'text-center', 'data': 'visible',
         'render': function (data, type, full, meta){
             return '<input type="checkbox" name="trip' + full.id + '" class="flat" checked>';
         }
        },
        { title: 'Perfil de carga', data: 'sparkLoadProfile', searchable: false,
          render: function(data, type, row){
            return '<i class="spark">' + data.join(',') + '</i>';
          }
        },
        //{ title: 'Servicio-sentido', data: 'route',   searchable: true},
        { title: 'Patente(capacidad)', data: 'busDetail', searchable: true},
        { title: 'Período inicio expedición', data: 'authTimePeriod', searchable: true},
        { title: 'Hora de inicio', data: 'timeTripInit', searchable: true},
        { title: 'Hora de fin', data: 'timeTripEnd', searchable: true},
        { title: 'Tipo de día', data: 'dayType', searchable: true}
      ],
      order: [[4, 'asc']],
      createdRow: function ( row, data, index ) {
        $(row).addClass('success');
      },
      initComplete: function(settings){
        // Handle click on "Select all" control
        var mainCheckbox = $('#checkbox-select-all');
        mainCheckbox.iCheck({
          labelHover: false,
          cursor: true,
          checkboxClass: 'icheckbox_flat-green'
        });
        mainCheckbox.on('ifToggled', function(event){
          // Get all rows with search applied
          var rows = _datatable.rows({'search':'applied'}).nodes();
          var addToAggr = false;
          var inputs = $('input.flat', rows);
          if(event.target.checked){
            inputs.prop('checked', true);
            $(rows).addClass('success');
            addToAggr = true;
          } else {
            inputs.prop('checked', false);
            $(rows).removeClass('success');
          }
          $('tbody input.flat').iCheck('update');
          var tripIds = _datatable.rows({'search':'applied'}).data().map(function(el){return el.id});
          _dataManager.setVisibility(tripIds, addToAggr);
          _self.updateCharts();
        });
      }
    });
    _datatable.on('search.dt', function (event) {

      var el = $('#checkbox-select-all');
      var tripIds = _datatable.rows({'search':'applied'}).data().map(function(el){ return el.id});
      var resultChecked = _dataManager.checkAllAreAggregate(tripIds);

      if(resultChecked === tripIds.length){
        el.prop('checked', true);
      } else if(resultChecked === 0){
        el.prop('checked', false);
      } else {
        el.prop('checked', false);
        el.prop('indeterminate', true);
      }
      el.iCheck('update');
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
    };

    var _updateDatatable = function(){
      var dataset = _dataManager.getDatatableData();
      var rows = dataset['rows'];
      var maxHeight = dataset['maxHeight'];

      _datatable.off('draw');
      _datatable.on('draw', function(oSettings) {
        $('.spark:not(:has(canvas))').sparkline('html', {
          type: 'bar',
          barColor: '#169f85',
          negBarColor: 'red',
          chartRangeMax: maxHeight
        });

        $('tbody input.flat').iCheck('destroy');
        $('tbody input.flat').iCheck({
          labelHover: false,
          cursor: true,
          checkboxClass: 'icheckbox_flat-green'
        });

        // activate iCheck in checkbox
        var dtRows = _datatable.rows().nodes();
        // attach events check and uncheck
        $('input.flat', dtRows).off('ifToggled');
        $('input.flat', dtRows).on('ifToggled', function(event){
          var tr = $(this).parent().parent().parent();
          var addToAggr = false;
          if(event.target.checked){
            tr.addClass('success');
            addToAggr = true;
          }else{
            tr.removeClass('success');
          }

          // updateChart
          var tripId = parseInt($(this).attr('name').replace('trip', ''));
          _dataManager.setVisibility([tripId], addToAggr);
          _self.updateCharts();
        });
      });
      _datatable.clear();
      _datatable.rows.add(rows);
      _datatable.columns.adjust().draw();

      // attach to attach event
      $('#detail-tab').off('shown.bs.tab');
      $('#detail-tab').on('shown.bs.tab', function(event){
        $('.spark:not(:has(canvas))').sparkline('html', {
          type: 'bar',
          barColor: '#169f85',
          negBarColor: 'red',
          chartRangeMax: maxHeight
        });
      })
    };

    var _updateBarChart = function(){

      var trips = _dataManager.trips();
      var series = [];
      var visualMaps = [];
      var scatterData = [];
      var seriesIndex = -1;
      for (var index=0; index<trips.length; index++){
        var trip = trips[index];
        if(!trip.visible){
          continue;
        }
        seriesIndex++;

        var serie = {
          name: trip.licensePlate,
          type: 'line', data: trip.data,
          showSymbol: true, symbol: 'pin', symbolSize: 6,
          lineStyle: { normal: { width: 1}}
        };
        var visualMap = {
          show: false,
          type: 'piecewise',
          pieces:[],
          dimension: 0,
          seriesIndex: seriesIndex,
          outOfRange: {
            color: 'blue'
          }
        };
        var colors = ['#0008fc', '#d3d352', '#db9500', '#ff0707'];
        var previousPiece = null;
        for (var i=1; i<trip.data.length; i++){
          var value = trip.data[i][3];
          var color = value<=25?colors[0]:value<=50?colors[1]:value<=75?colors[2]:value<=100?colors[3]:null;

          if(trip.data[i-1][0] !== "" && trip.data[i][0] !== ""){
            var piece = {
                gte: (new Date(trip.data[i-1][0])).getTime(),
                lte: (new Date(trip.data[i][0])).getTime(),
                color: color
            };

            if(previousPiece === null){
              previousPiece = piece;
            }else if(previousPiece.color === piece.color){
              previousPiece.lte = piece.lte;
            }else{
              visualMap.pieces.push(previousPiece);
              previousPiece = piece;
            }
          }

          if(i+1 === trip.data.length){
            visualMap.pieces.push(previousPiece);
          }
        }
        series.push(serie);
        visualMaps.push(visualMap);
        scatterData = scatterData.concat(trip.data);
      }

      var scatterSerie = {
        type: 'scatter',
        symbolSize: function(el){
          return el[5]*0.3;
        },
        itemStyle: {
          normal: {
            color: 'red'
          }
        },
        data: scatterData
      };
      //generates markLine
      var markLines = [];
      var yMax = 0;
      _dataManager.yAxisData().forEach(function(item){
        if(item.value > yMax){
          yMax = item.value;
        }
        var markLine = {
          yAxis: item.value,
          name: item.name
        };
        markLines.push(markLine);
      });
      scatterSerie.markLine = {
        data: markLines,
        silent: true,
        symbol: ['pin', null],
        label: {
          normal: {
            formatter: '{b} - {c}     ',
            textStyle: {
              fontSize: 9, color: '#000'
            },
            position: 'left'
          }
        },
        lineStyle: {
          normal: {
            type: 'solid',
            opacity: 0.2,
            color: '#000'
          }
        }
      };
      //scatterSerie.data = null;
      series.push(scatterSerie);
      console.log(series);
      console.log(visualMaps);

      var options = {
        animation: false,
        series: series,
        visualMap: visualMaps,
        dataZoom: [{
          show: true, type: 'slider', xAxisIndex: 0, start: 0, end: 100
        },{
          show: true, type: 'slider', yAxisIndex: 0, start: 0, end: 100
        },{
          //show: true, type: 'inside', xAxisIndex: 0, start: 0, end: 100
        },{
          //show: true, type: 'inside', yAxisIndex: 0, start: 0, end: 100
        }],
        xAxis:{
          type: 'time', name: 'Hora', boundaryGap: false, splitNumber: 15, splitLine:{ show: false}
        },
        yAxis: {
          type: 'value', name: 'Distancia en Ruta', splitLine:{ show: false}, splitArea: {show: false},
          axisLabel: {show: false}, axisTick: {show: false},
          max: yMax
        },
        tooltip: {
          show:true,
          trigger: 'item',
          formatter: function(params){
            console.log(params);
            var row = [];
            if(params.componentType === "series"){
              row.push(params.marker);
              if(params.componentSubType === "line"){
                var time = params.data[0];
                var loadProfile = params.data[2];
                var getOut = params.data[4];
                var getIn = params.data[5];

                row.push('Tiempo: ' + time);
                row.push('Carga: ' + loadProfile);
                row.push('Bajadas: ' + getOut);
                row.push('Subidas: ' + getIn);
              }else if(params.componentSubType === "scatter"){
                var getIn = params.data[5];
                row.push('Subidas: ' + getIn);
              }
            }
            return row.join('<br />');
          }
        },
        grid: {
          left: '200px',
          bottom: '80px',
          containLabel: true
        },
        toolbox: {
          show : true,
          itemSize: 20,
          left: 'center',
          top: 'top',
          feature : {
            mark : {show: false},
            restore : {show: false, title: "restaurar"},
            saveAsImage : {show: true, title: "Guardar imagen", name: _dataManager.getDataName()},
            dataView: {
              show: true,
              title: 'Ver datos',
              lang: ['Datos del gráfico', 'cerrar', 'refrescar'],
              buttonColor: '#169F85',
              readOnly: true
            },
            dataZoom: {
              show: true, title: {
                zoom: 'Seleccionar área',
                back: 'Restablecer vista'
              }
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
      $('#expeditionNumber').html(_dataManager.tripsUsed());
      $('#expeditionNumber2').html(_dataManager.tripsUsed());
    };

    this.updateCharts = function(){
      _updateBarChart();
      _updateGlobalStats();
    };
    this.updateDatatable = function(){
      _updateDatatable();
    };
    this.showLoadingAnimationCharts = function(){
      const LOADING_TEXT = 'Cargando...';
      _barChart.showLoading(null, {text: LOADING_TEXT});
    };
    this.hideLoadingAnimationCharts = function(){
      _barChart.hideLoading();
    };
  }

  function processData(dataSource, app){
    console.log(dataSource);

    if(dataSource['status']){
      var status = dataSource['status'];
      showMessage(status);
      return;
    }

    var trips = dataSource.trips;
    var dataManager = new DataManager();
    var globalYAxis = [];
    var updateGlobalYAxis = false;

    for(var expeditionId in trips){
      var trip = trips[expeditionId];

      // trip info
      var capacity = trip['info']['capacity'];
      var licensePlate = trip['info']['licensePlate'];
      var route = trip['info']['route'];
      var timeTripInit = trip['info']['timeTripInit'];
      var timeTripEnd = trip['info']['timeTripEnd'];
      var authTimePeriod = trip['info']['authTimePeriod'];
      var dayType = trip['info']['dayType'];

      var stopQuantity = trip['stops'].length;

      if(stopQuantity > globalYAxis.length){
        globalYAxis = [];
        updateGlobalYAxis = true;
      }else{
        updateGlobalYAxis = false;
      }

      var data = [];
      for(var stopIndex=0; stopIndex<stopQuantity; stopIndex++){
        var stopInfo = trip['stops'][stopIndex];
        var authStopCode = stopInfo['authStopCode'];
        var userStopCode = stopInfo['userStopCode'];
        var order = stopInfo['order'];
        var name = stopInfo['name'];
        var distOnPath = stopInfo['distOnPath'];

        if(updateGlobalYAxis){
          var yPoint = {
            'value': distOnPath,
            'name': name,
            'authStopCode': authStopCode,
            'userStopCode': userStopCode
          };
          globalYAxis.push(yPoint);
        }
        var row = [];
        var stopTime = stopInfo['stopTime'];
        row.push(stopTime);
        row.push(stopInfo['distOnPath']);
        row.push(stopInfo['loadProfile']);
        row.push(stopInfo['loadProfile']/capacity*100);
        row.push(stopInfo['expandedGetOut']);
        row.push(stopInfo['expandedGetIn']);
        data.push(row);
      }

      trip = new Trip(expeditionId, route, licensePlate, capacity, timeTripInit,
                      timeTripEnd, authTimePeriod, dayType, data);
      dataManager.addTrip(trip);
    }
    dataManager.yAxisData(globalYAxis);
    app.dataManager(dataManager);
  }

  // load filters
  (function (){
    // set locale
    moment.locale('es');

    $('#dayFilter').select2({placeholder: 'Todos'});
    $('#dayTypeFilter').select2({placeholder: 'Todos'});
    $('#periodFilter').select2({placeholder: 'Todos'});
    $('#routeFilter').select2({placeholder: 'Servicio'});//, allowClear: true});
    $("#minutePeriodFilter").select2({placeholder: "Todos"});

    var app = new ExpeditionApp();
    var makeAjaxCall = true;
    $('#btnUpdateChart').click(function(){
      var day = $('#dayFilter').val();
      var route = $('#routeFilter').val();
      var dayType = $('#dayTypeFilter').val();
      var period = $('#periodFilter').val();
      var minutes = $("#minutePeriodFilter").val();

      var params = {
        day: day
      };
      if (route) {
        params['route'] = route;
      }
      if (dayType) {
        params['dayType'] = dayType;
      }
      if (period) {
        params['period'] = period;
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
          $.getJSON(Urls["profile:getExpeditionData"](), params, function (data) {
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
  })()
});