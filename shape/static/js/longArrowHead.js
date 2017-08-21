/**
 * CREATE NEW SYMBOL TO POLYLINE DECORATOR
 */
L.Symbol.LongArrowHead = L.Class.extend({
  isZoomDependant: true,
  options: {
    polygon: true,
    pixelSize: 10,
    headAngle: 60,
    pathOptions: {
      stroke: false,
      weight: 2
    }
  },

  initialize: function (options) {
    L.Util.setOptions(this, options);
    this.options.pathOptions.clickable = false;
  },

  buildSymbol: function(dirPoint, latLngs, map, index, total) {
    var opts = this.options;
    var path;
    if(opts.polygon) {
      path = new L.Polygon(this._buildArrowPath(dirPoint, map), opts.pathOptions);
    } else {
      path = new L.Polyline(this._buildArrowPath(dirPoint, map), opts.pathOptions);
    }
    return path;
  },

  _buildArrowPath: function (dirPoint, map) {
    var d2r = Math.PI / 180;
    var tipPoint = map.project(dirPoint.latLng);
    var direction = (-(dirPoint.heading - 90)) * d2r;
    var radianArrowAngle = this.options.headAngle / 2 * d2r;

    var headAngle1 = direction + radianArrowAngle,
        headAngle2 = direction - radianArrowAngle;
        headAngle3 = direction + 0;
        headAngle4 = direction - 0;
        headAngle5 = direction - radianArrowAngle;
    var arrowHead1 = new L.Point(
      tipPoint.x - this.options.pixelSize * Math.cos(headAngle1),
      tipPoint.y + this.options.pixelSize * Math.sin(headAngle1)),
        arrowHead2 = new L.Point(
      tipPoint.x - this.options.pixelSize * Math.cos(headAngle2),
      tipPoint.y + this.options.pixelSize * Math.sin(headAngle2)),
        arrowBack1 = new L.Point(
      arrowHead1.x - (this.options.pixelSize*1.5) * Math.cos(headAngle3),
      arrowHead1.y + (this.options.pixelSize*1.5) * Math.sin(headAngle3)),
        arrowBack2 = new L.Point(
      arrowHead2.x - (this.options.pixelSize * 1.5) * Math.cos(headAngle4),
      arrowHead2.y + (this.options.pixelSize * 1.5) * Math.sin(headAngle4)),
        arrowBackCenter = new L.Point(
      arrowBack2.x + this.options.pixelSize * Math.cos(headAngle5),
      arrowBack2.y - this.options.pixelSize * Math.sin(headAngle5));

    return [
      map.unproject(arrowBack1),
      map.unproject(arrowHead1),
      dirPoint.latLng,
      map.unproject(arrowHead2),
      map.unproject(arrowBack2),
      map.unproject(arrowBackCenter),
    ];
  }
});

L.Symbol.longArrowHead = function (options) {
  return new L.Symbol.LongArrowHead(options);
};