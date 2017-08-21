"use strict";

let App = (function(){
  let Element = function(layer, color, group, name) {
    this.layer = layer;
    this.color = color;
    this.group = group;
    this.name = name;
    this.visible = true;
    this.addToMap = function(map) {
      this.layer.addTo(map);
      this.visible = true;
    };
    this.removeFromMap = function() {
      this.layer.remove();
      this.visible = false;
    };
    this.updateLayer = function(layer, map){
      if(this.visible){
        this.removeFromMap();
        this.layer = layer;
        this.addToMap(map);
      }else{
        this.layer = layer;
      }
    };
    this.isOld = false;
  };

  function getMap(){
    // Set map
    let beauchefLocation = L.latLng(-33.457910, -70.663869);
    let mapid = $(".right_col")[0];
    let map = L.map(mapid, {
      editable: true,
      closePopupOnClick: false
    }).setView(beauchefLocation, 13);

    // mapbox map styles
    let mapboxURL = "https://api.mapbox.com/styles/v1/";
    let token = "pk.eyJ1IjoidHJhbnNhcHAiLCJhIjoiY2lzbjl6MDQzMDRkNzJxbXhyZWZ1aTlocCJ9.-xsBhulirrT0nMom_Ay9Og";
    let blackStyle= mapboxURL + "mapbox/dark-v9/tiles/256/{z}/{x}/{y}?access_token=" + token;
    let grayStyle= mapboxURL + "mapbox/light-v9/tiles/256/{z}/{x}/{y}?access_token=" + token;
    let stopStyle= mapboxURL + "transapp/cj3a8ksvx000t2sqstwxzbc2f/tiles/256/{z}/{x}/{y}?access_token=" + token;
    let attribution = "Map data &copy; <a href='http://openstreetmap.org'>OpenStreetMap</a> contributors, " +
                    "Imagery © <a href='http://mapbox.com'>Mapbox</a>";

    // map layers
    let grayBaseLayerWithStops = L.tileLayer(stopStyle, {attribution: attribution});
    let grayBaseLayer = L.tileLayer(grayStyle, {attribution: attribution});
    // default map
    grayBaseLayer.addTo(map);

    let modalContent =
 '<div class="col-md-12 col-sm-12 col-xs-12">' +
   '<div class="x_panel">' +
     '<div class="x_title">' +
       '<div class="col-md-12 col-sm-12 col-xs-12"><h2><i class="fa fa-filter"></i> Filtro</h2> </div>' +
       '<div class="col-md-6 col-sm-6 col-xs-6"><div class="radio"><label class=""><input id="chkAll" type="radio" class="flat" checked="" name="filter"><small> Marcar todos</small></label></div></div>' +
       '<div class="col-md-6 col-sm-6 col-xs-6"><div class="radio"><label class=""><input id="chkEmpty" type="radio" class="flat"  name="filter"><small> Desmarcar todos</small></label></div></div>' +
       '<div class="clearfix"></div>' +
     '</div>' +
     '<div class="x_content">' +
       '<div class="" id="window" role="tabpanel" data-example-id="togglable-tabs">'+
         '<ul id="filterTab" class="nav nav-tabs bar_tabs" role="tablist">'+
           '<li role="presentation" class="active"><a href="#colorContentPanel" role="tab" id="colorTab" data-toggle="tab" aria-expanded="false">Color</a>'+
           '</li>'+
           '<li role="presentation" class=""><a href="#listContentPanel" id="listTab" role="tab" data-toggle="tab" aria-expanded="true">Ejes</a>'+
           '</li>'+
           '<li role="presentation" class=""><a href="#groupContentPanel" role="tab" id="groupTab" data-toggle="tab" aria-expanded="false">Grupos</a>'+
           '</li>'+
         '</ul>'+
         '<div id="myTabContent" class="tab-content">'+
           '<div role="tabpanel" class="tab-pane fade" id="listContentPanel" aria-labelledby="home-tab">'+
             '<div class="col-md-12 col-sm-12 col-xs-12"><div id="listContent"></div></div>'+
           '</div>'+
           '<div role="tabpanel" class="tab-pane fade" id="groupContentPanel" aria-labelledby="profile-tab">'+
             '<div class="col-md-12 col-sm-12 col-xs-12"><div id="groupContent"></div></div>'+
           '</div>'+
           '<div role="tabpanel" class="tab-pane fade in active" id="colorContentPanel" aria-labelledby="profile2-tab">'+
             '<div class="col-md-12 col-sm-12 col-xs-12"><div id="colorContent"></div></div>'+
           '</div>'+
         '</div>'+
       '</div>'+
     '</div>'+
   '</div>'+
  '</div>';

    let win = L.control.window(map, {
      content: modalContent,
      closeButton: true,
      modal: true,
      position: "top"
    });
    // activate tabs
    $(".nav-tabs a").click(function(e){
      e.preventDefault();
      $(this).tab("show");
    });
    // set all and empty checkbox
    $("input[type='radio'].flat").iCheck({
      labelHover: false,
      cursor: true,
      checkboxClass: "icheckbox_flat-green",
      radioClass: "iradio_flat-green"
    });
    $("input[type=radio][name=filter]").on("ifChanged", function () {
      let id = $("input[name='filter']:checked").attr("id");
      if (id === "chkAll") {
        $("input[type=checkbox]").iCheck("check");
      }
      if (id === "chkEmpty") {
        $("input[type=checkbox]").iCheck("uncheck");
      }
    });

    // DEFINE HOUR CONTROL
    let hourControl = L.control({position: 'topleft'});
    hourControl.onAdd = function (map) {
      let div = L.DomUtil.create("div", "info hour");
      div.innerHTML = '<i class="fa fa-clock-o fa-lg" aria-hdden="true"></i> <span id="hourInfo"></span>';
      return div;
    };
    hourControl.addTo(map);

    // DEFINE DAY TYPE CONTROL
    let dayTypeControl = L.control({position: 'topleft'});
    dayTypeControl.onAdd = function (map) {
      let div = L.DomUtil.create('div', 'info day');
      div.innerHTML = '<i class="fa fa-calendar-o fa-lg" aria-hdden="true"></i> <span id="dayType"></span>';
      return div;
    };
    dayTypeControl.addTo(map);

    let filterControl = L.easyButton({
      position: "topright",
      states: [{
        stateName: "filter",
        icon: "<i id='filterButton' class='fa fa-filter fa-lg'></i>",
        onClick: function(btn, map) {
          win.show();
        }
      }]
    }).addTo(map);

    // DEFINE SWITCH MAP
    let switchMapControl = L.easyButton({
      position: "topright",
      states: [{
        stateName: "map",
        icon: "<i id='switchMap' class='fa fa-map-signs fa-lg'></i>",
        onClick: function(btn, map) {
          map.removeLayer(grayBaseLayer);
          map.addLayer(grayBaseLayerWithStops);
          btn.state("mapWithStops");
        }
      },{
        stateName: "mapWithStops",
        icon: '<i id="switchMap" class="fa fa-map fa-lg"></i>',
        onClick: function(btn, map) {
          map.removeLayer(grayBaseLayerWithStops);
          map.addLayer(grayBaseLayer);
          btn.state("map");
        }
      }]
    }).addTo(map);

    $(window).smartresize(function(){
      map.invalidateSize();
    });
    map.invalidateSize();

    return {
      map: map,
      controls: {
        "switchMap": switchMapControl,
        "filter": filterControl,
        "hourInfo": hourControl,
        "dayTypeInfo": dayTypeControl
      }
    };
  }
/*
  let _wrapper = getMap();
  let defaults = {
     mapControls: {
         showSwitchMapControl: true,
         showFilterControl: true,
         showHourControl: true,
         showDayTypeControl: true
     },
     getMetric: null,
     getColor: null,
     getColorPosition: null,
     getBubbleInfo: null
  };
  function App(options) {
    let _makeBounds = true;
    let map = _wrapper.map;
    // Merge user settings with default, recursively.
    this.options = $.extend(true, {}, defaults, options);
  }
*/
  function App(getMetricFunc, getColorFunc, getColorPositionFunc, getBubbleInfo){
    let _wrapper = getMap();
    let _map = _wrapper.map;
    let _mapControls = _wrapper.controls;
    let _dataSource = {};
    let _getMetric = getMetricFunc;
    let _getColor = getColorFunc;
    let _getColorPosition = getColorPositionFunc;
    let _getBubbleInfo = getBubbleInfo;
    let _makeBounds = true;

    this.setMetric = function(getMetricFunc){
      _getMetric = getMetricFunc;
    };
    this.setStyle = function(getColorFunc, getColorPositionFunc){
      _getColor = getColorFunc;
      _getColorPosition = getColorPositionFunc;
    };
    this.setMapControlVisibility = function(controlName, val){
      let control = _mapControls[controlName];
      _map.removeControl(control);
        if (val){
          _map.addControl(control);
        }
    };
    let _updateElement = function(layer, color, group, name, id) {
      // if id is present in data
      if(_dataSource.hasOwnProperty(id)){
        let el = _dataSource[id];
        el.color = color;
        el.group = group;
        el.name = name;
        el.updateLayer(layer, _map);
      }else {
        _dataSource[id] = new Element(layer, color, group, name);
      }
    };

    // Add control to map
    this.addMapControl = function(control){
      control.addTo(_map);
    };
    // Remove control from map
    this.removeMapControl = function(control){
      _map.removeControl(control);
    };

    /**
     * CREATE OVERLAYS
     */
    this.generateOverlays = function(streetName, sectionName, section) {

      let latLngs = [];
      let id = section.id;
      let metrics = _getMetric(section);
      let group = section.group;
      let points = section.points;

      // order points by distOnRoute
      points.sort(function(a, b) {
        return a.distOnRoute - b.distOnRoute;
      });

      // populate positions
      $.each(points, function(i2, point) {
        latLngs.push([point.latitude, point.longitude]);
      });

      let line = L.polyline(latLngs, {
        color: _getColor(metrics),
        //weight: 6,
      });

      let patternsOpts = [
      // defines a pattern of 10px-wide dashes, repeated every 20px on the line
      {offset: 10,
        endOffset: 5,
        repeat: "5%",
        symbol: L.Symbol.longArrowHead({
          rotate: true,
          pixelSize: 5,
          polygon: true,
          pathOptions: {
            color: _getColor(metrics),
            stroke: false,
            fillColor: _getColor(metrics),
            fillOpacity: 1.0
          }
        })
      }
      ];
      let decorator = L.polylineDecorator(line, {patterns: patternsOpts});

      //********************************************************/
      // set bubble
      let message = _getBubbleInfo(metrics, streetName, section);
      decorator.bindPopup(message);
      line.bindPopup(message);

      //********************************************************/
      // animation
      let arrowOffset = 0;
      patternsOpts[0].repeat = 0;
      let anim = window.setInterval(function() {
        patternsOpts[0].offset = arrowOffset + "%";
        decorator.setPatterns(patternsOpts);
        if(arrowOffset > 100)
          arrowOffset = 0;
        arrowOffset = arrowOffset + 1;
      }, 50);
      //********************************************************/

      // create overlay
      let overlay = L.featureGroup([]);
      overlay.addLayer(line);
      overlay.addLayer(decorator);
      _updateElement(overlay, _getColor(metrics), group, streetName, id);

      console.log("Map updated with polyline decorator");
    };

    this.updateMap = function(hour, dayType) {

      // update map info
      $("#hourInfo").text(hour);
      $("#dayType").text(dayType);

      // update filter
      this.updateFilterWindow();

      let bounds = null;

      // add layers to map and control
      $.each(_dataSource, function(index, element){
        if (element.visible){
          element.addToMap(_map);
          console.log(element);
          if (!bounds) {
            bounds = element.layer.getBounds();
          } else {
            bounds = bounds.extend(element.layer.getBounds());
          }
        }
      });

      if(bounds !== null && _makeBounds){
        _map.fitBounds(bounds);
        _makeBounds = false;
      }
    };

    /**
    * DEFINE FILTER
    */
    let _getAttributeUniqueList = function(attributeName, sortFunction) {
      let dict = $.map(_dataSource, function(element, id){
        return element[attributeName];
      }).reduce(function(x, y){
        if (x.hasOwnProperty(y)) {
          x[y]++;
          return x;
        }
        x[y] = 1;
        return x;
      }, {});

      let orderedList = [];
      $.each(dict, function(attrValue, frecuency){
        orderedList.push({attrValue:attrValue, frecuency:frecuency});
      });
      orderedList.sort(sortFunction);
      return orderedList;
    };

    let _generateGroupList = function(divId, attrName, sortFunction, getLabel) {
      let orderedList = _getAttributeUniqueList(attrName, sortFunction);
      // delete children
      $("#"+divId).children().remove();
      $.each(orderedList, function(index, item){
        let attrValue = item.attrValue;
        let frecuency = item.frecuency;
        let label = getLabel(attrValue, frecuency);

        let checkbox = null;
        let checkboxId = attrValue.replace(/\.|-| |#/g, "");
        let checkboxExists = $("#" + checkboxId).length ? true:false;
        if (checkboxExists){
          checkbox = $("#" + checkboxId);
          checkbox.parent().next().html(label);
          checkbox.off("ifChecked");
          checkbox.off("ifUnchecked");
        } else {
          let html = $("<div class='checkbox'><label>" + label + "</label></div>");
          checkbox = $("<input id='"+checkboxId+"' type='checkbox' class='flat' checked='checked' />");
          html.prepend(checkbox);
          $("#" + divId).append(html);
          checkbox.iCheck({
            labelHover: false,
            cursor: true,
            checkboxClass: "icheckbox_flat-green",
            radioClass: "iradio_flat-green",
          });
        }
        checkbox.on("ifChecked", function(){
          $.each(_dataSource, function(index, element){
            if (attrValue === element[attrName]) {
              element.addToMap(_map);
            }
          });
        });
        checkbox.on("ifUnchecked", function(){
          $.each(_dataSource, function(index, element){
            if (attrValue === element[attrName]) {
              element.removeFromMap();
            }
          });
        });
      });
    };

    this.updateFilterWindow = function(){
      // streets
      _generateGroupList("listContent", "name", function(a, b){
        return a.attrValue.localeCompare(b.attrValue);
      }, function(name, frecuency){
        return " " + name + " (" + frecuency + " tramos)";
      });

      // groups
      _generateGroupList("groupContent", "group", function(a, b){
        return a.attrValue.localeCompare(b.attrValue);
      }, function(group, frecuency){
        return " " + group + " (" + frecuency + " tramos)";
      });

      // colors
      _generateGroupList("colorContent", "color", function(a, b){
        return _getColorPosition(a.attrValue) - _getColorPosition(b.attrValue);
      }, function(color, frecuency){
        return " (" + frecuency + " tramos)<i class='filterColor' style='background:" + color + "'></i>";
      });

      console.log("checkboxs info updated");
    };
  }

  return App;
})();