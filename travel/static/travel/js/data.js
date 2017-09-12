"use strict";


// ============================================================================
// MAP DATA
// ============================================================================

function getMapZoneById(data, zone_id, options) {
    // missing data
    if (data === null) return null;
    if (zone_id === undefined || zone_id === null) return null;
    if (options === undefined || options === null) return null;
    if (options.curr_sector === null) return null;

    // unknown sector or zone
    if (!(options.curr_sector in data.aggregations)) return null;
    if (!(zone_id in data.aggregations[options.curr_sector].by_zone.buckets)) return null;

    return data.aggregations[options.curr_sector].by_zone.buckets[zone_id];
}

function getZoneValue(zone, options) {
    // missing data
    if (zone === undefined || zone === null) return null;
    if (options === undefined || options === null) return null;
    if (options.curr_sector === null) return null;
    if (options.curr_visualization_type === null) return null;
    if (!(options.curr_visualization_type in options.visualization_mappings)) return null;

    return options.visualization_mappings[options.curr_visualization_type].map_fn(zone);
}

function processData(response) {
    _map_data = response.map;
    updateAvailableSectors(options);
    redraw(options);
    updateMapDocCount(options);
}

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

    // put loading spinner
    var update_button = $(this);
    var loading_text = "Actualizar Datos <i class='fa fa-cog fa-spin fa-2x fa-fw'>";
    update_button.html(loading_text);

    // load data and remove spinner
    $.getJSON('getMapData', request, processData).always(function(){
        update_button.html('Actualizar Datos')
    });

}