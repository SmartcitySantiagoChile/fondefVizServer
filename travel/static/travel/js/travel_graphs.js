"use strict";

$(document).ready(function () {

    // Forms
    setupDateForm();
    setupDayTypeAndTSPeriodForm(_allDaytypes, _dayTypes, _dayTypes_reversed);
    setupVisualizationForm();

});