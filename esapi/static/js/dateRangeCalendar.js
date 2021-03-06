"use strict";

/**
 * Group dates array in a range of dates array
 * */
function groupByDates(dates) {
    let parseDate = function (input) {
        var parts = input.match(/(\d+)/g);
        return new Date(parts[0], parts[1] - 1, parts[2], 0); // months are 0-based
    };
    let sortedArray = Array.from(dates).sort();
    let dateArray = [];
    sortedArray.map(e => dateArray.push(parseDate(e[0])));
    let selection_by_range = [];
    let aux_selector = [];
    for (let i = 0; i < dateArray.length; i++) {
        aux_selector.push(sortedArray[i]);
        let next_day = new Date(dateArray[i]);
        next_day.setDate(dateArray[i].getDate() + 1);
        const index = dateArray.findIndex(function (x) {
            return x.toISOString().slice(0, 10) === next_day.toISOString().slice(0, 10);
        });
        if (index === -1) {
            selection_by_range.push(aux_selector);
            aux_selector = [];
        }
    }
    return selection_by_range
}

/**
 * Message to display when days are selected
 * */
const dayMessageHandler = days => {
    if (days === 0) {
        return "Ningún día seleccionado";
    } else if (days === 1) {
        return "1 día seleccionado";
    } else {
        return days + " días seleccionados";
    }
};

/**
 * Group elements by key arg
 * */
const groupBy = keys => array =>
    array.reduce((objectsByKeyValue, obj) => {
        const value = keys.map(key => obj[key]).join('-');
        objectsByKeyValue[value] = (objectsByKeyValue[value] || []).concat(obj);
        return objectsByKeyValue;
    }, {});

/**
 * Calendar to show available days (dates with data)
 * Filter to select multiple range of dates.
 * */
function loadRangeCalendar(data_url, calendar_opts) {
    // set variables
    let urlKey = window.location.pathname;
    var tempSelectedDates = new Set();
    var selectedDates = new Set(JSON.parse(window.localStorage.getItem(urlKey + 'dayFilter')) || []);
    var tempDeleted = new Set();
    if (selectedDates.size === 0) {
        window.localStorage.setItem(urlKey + 'dayFilter', JSON.stringify([]));
    }
    let $dayFilter = $('#dayFilter');
    let divId = "dateRangeCalendar";
    let dateRangeChart = echarts.init(document.getElementById(divId), theme);

    let calendarYearTemplate = {
        orient: "horizontal",
        range: null,
        dayLabel: {
            firstDay: 1,
            nameMap: ["D", "L", "M", "M", "J", "V", "S"]
        },
        monthLabel: {
            nameMap: []
        },
        left: "50",
        right: "20",
        cellSize: ["auto", 9]
    };

    let serieTemplate = {
        type: "heatmap",
        coordinateSystem: "calendar",
        calendarIndex: 0,
        data: []
    };

    var opts = {
        tooltip: {
            position: "top",
            formatter: function (p) {
                return echarts.format.formatTime("dd/MM/yyyy", p.data[0]);
            }
        },
        visualMap: {
            min: 0,
            max: 1000,
            calculable: true,
            orient: "vertical",
            left: "0",
            top: "center",
            show: false,
        },
        calendar: [],
        series: [],
        legend: [],
        dataRange: []
    };

    // show loading
    var loadingText = "Cargando ...";
    dateRangeChart.showLoading(null, {text: loadingText});
    $.get(data_url, function (data) {
        dateRangeChart.hideLoading();
        //get years
        const days_by_years = e => {
            let year_dict = {};
            e.map(f => {
                let year = f.split("-")[0];
                if (year in year_dict) {
                    year_dict[f.split("-")[0]].push([f, 1]);
                } else {
                    year_dict[f.split("-")[0]] = [[f, 1]];
                }
            });
            return year_dict;
        };
        let availableDaysByYear = days_by_years(data.availableDays);
        let years = Object.keys(availableDaysByYear);


        //get colors
        const groupByColor = groupBy(["color"]);
        let descriptionDayList = groupByColor(data.info);
        descriptionDayList = Object.values(descriptionDayList);

        //delete keys
        descriptionDayList = descriptionDayList.map(e => {
            return e.map(f => Object.values(f));
        });

        let noDataDay = [["", "#FFFFFF", "Sin datos"]];
        descriptionDayList.push(noDataDay);

        if (years.length > 0) {
            let newOpts = $.extend({}, opts);
            let top = 50;
            let legendData = [];
            years.map((year, index) => {
                let calendarYear = JSON.parse(JSON.stringify($.extend({}, calendarYearTemplate)));
                let serie = $.extend({}, serieTemplate);
                if (index === 0) calendarYear.monthLabel.nameMap = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago",
                    "Sep", "Oct", "Nov", "Dic"];
                if (index === years.length - 1) calendarYear.bottom = '2%';
                calendarYear.range = year;
                calendarYear.top = top;
                top += 84;
                serie.calendarIndex = index;

                serie.data = availableDaysByYear[year];
                serie.emphasis = {
                    itemStyle: {
                        color: 'green'
                    }
                };
                serie.itemStyle = {
                    color: "#97b58d"
                };
                newOpts.calendar.push(calendarYear);
                newOpts.series.push(serie);

                //year-date dictionary
                let dataObject = {};
                availableDaysByYear[year].map(e => {
                    dataObject[e[0]] = 1;
                });

                descriptionDayList.map(date => {
                    let descriptionSerie = $.extend({}, serieTemplate);

                    descriptionSerie.name = date[0][2];
                    let dataAux = [];
                    date.forEach(function (e) {
                        const index = e[0] in dataObject;
                        if (index) {
                            dataAux.push(e);
                        }
                    });
                    descriptionSerie.data = dataAux.map(e => [e[0], 1]);
                    legendData.push(descriptionSerie.name);
                    descriptionSerie.itemStyle = {
                        color: date[0][1],
                        shadowBlur: 2,
                        shadowColor: "#333"
                    };
                    descriptionSerie.emphasis = {
                        itemStyle: {
                            color: 'green'
                        }
                    };
                    descriptionSerie.color = "black";
                    descriptionSerie.showEffectOn = "render";
                    descriptionSerie.rippleEffect = {
                        brushType: "stroke"
                    };
                    descriptionSerie.hoverAnimation = true;
                    descriptionSerie.zlevel = 3;
                    newOpts.series.push(descriptionSerie);
                    descriptionSerie.calendarIndex = index;
                    descriptionSerie.tooltip = {
                        position: "top",
                        formatter: function (p) {
                            let date = echarts.format.formatTime("dd/MM/yyyy", p.data[0]);
                            return date + "<br />" + descriptionSerie.name;
                        }
                    }
                });
            });

            newOpts.legend = {
                top: "0",
                left: "0",
                data: legendData,
                selectedMode: false,
                itemStyle: {
                    borderColor: "black",
                    borderWidth: 1
                }
            };

            $("#" + divId).height(top - 20);
            dateRangeChart.setOption(newOpts, {notMerge: true});
            dateRangeChart.resize();

        }

    });


    // optional configuration when singleDatePicker = True
    let singleDatePicker = calendar_opts.singleDatePicker || false;
    if (singleDatePicker) {
        let arrayToSave = Array.from(selectedDates);
        selectedDates = new Set([arrayToSave[0]]);
        if (arrayToSave.length > 0) {
            $dayFilter.val(reverse_date(arrayToSave[0][0]));
        } else {
            selectedDates = new Set([]);
            $dayFilter.val("Ningún día seleccionado");
        }
        window.localStorage.setItem(urlKey + "dayFilter", JSON.stringify(Array.from(selectedDates)));
        $('#group-button').hide();
        $('#option3').attr("checked", false);
        $('#option1').attr("checked", true);
        $('#selectedDaysTitle').text("Día seleccionado:");
        //$('#deleteSelection').hide();
    } else {
        $dayFilter.val(dayMessageHandler(selectedDates.size));
    }


    // modal activation
    $("#dateRangeModal").on('shown.bs.modal', function () {
        dateRangeChart.resize();
        deleteSelection();
        reprintSelection();
        var $ul = createSelectionUl(selectedDates);
        $('#daysSelectedList').empty().append($ul);
        if (selectedDates.size === 0) {
            tempSelectedDates = new Set([]);
        } else {
            tempSelectedDates = new Set(selectedDates);
        }
    });

    // popove activation
    $dayFilter.attr("data-trigger", "hover");
    $dayFilter.attr("data-toggle", "popover");
    $dayFilter.attr("data-content", "");
    $dayFilter.attr("data-placement", "top");
    $dayFilter.attr("data-original-title", "Días seleccionados:");
    if (selectedDates.size !== 0 && !singleDatePicker) {
        $dayFilter.popover({
            html: true,
            content: function () {
                return $('#popover-content').html();

            }
        });
    }
    $dayFilter.attr("data-content", "");
    $('#popover-content').empty().append(createSelectionUl(selectedDates));


    //reprint only dates selected
    function reprintSelection(auxiliar = false, global = true) {
        let seriesLength = dateRangeChart.getOption().series.length;
        for (var j = 0; j < seriesLength; j++) {
            var allDates = dateRangeChart.getOption().series[j].data;
            for (var i = 0; i < allDates.length; i++) {
                dateRangeChart.dispatchAction({
                    type: 'downplay',
                    dataIndex: i,
                    seriesIndex: j
                });
            }
            if (auxiliar) {
                tempSelectedDates.forEach(function (e) {
                    dateRangeChart.dispatchAction({
                        type: 'highlight',
                        dataIndex: e[1],
                        seriesIndex: e[2]

                    });
                });
            }

            if (global) {
                selectedDates.forEach(function (e) {
                    dateRangeChart.dispatchAction({
                        type: 'highlight',
                        dataIndex: e[1],
                        seriesIndex: e[2]
                    });
                });
            }
        }
    }

    //downplay all dates selected
    function deleteSelection() {
        tempSelectedDates.forEach(function (e) {
            dateRangeChart.dispatchAction({
                type: 'downplay',
                dataIndex: e[1],
                seriesIndex: e[2]
            });
        });
        tempSelectedDates = new Set([]);
        //update the selection date list
        var $ul = createSelectionUl(tempSelectedDates);
        $("#daysSelectedList").empty().append($ul);
    }

    //add single date
    function singleSelectionDate(selected_date, value, data_index, series_index) {
        dateRangeChart.dispatchAction({
            type: 'highlight',
            dataIndex: data_index,
            seriesIndex: series_index

        });
        let this_day_exist = false;
        selected_date.forEach(function (e) {
            if (e[0] === value) {
                if (e[2] !== series_index) {
                    selected_date.delete(e);
                } else {
                    this_day_exist = true;
                }
            }
        });
        if (!this_day_exist) {
            selected_date.add([value, data_index, series_index]);
        }
    }

    //delete single date
    function singleDeleteDate(selected_date, value, data_index, series_index) {
        dateRangeChart.dispatchAction({
            type: 'downplay',
            dataIndex: data_index,
            seriesIndex: series_index

        });

        selected_date.forEach(function (e) {
            if (e[0] === value) {
                selected_date.delete(e);
            }
        });
    }

    //add dates range
    function rangeSelectionDate(selected_date, range_selection) {
        range_selection.forEach(e => singleSelectionDate(selected_date, e.data[0], e.dataIndex, e.seriesIndex));
        let rs_sort = [range_selection[0].data[0], range_selection[1].data[0]];
        rs_sort.sort();
        let seriesLength = dateRangeChart.getOption().series.length;
        for (let j = 0; j < seriesLength; j++) {
            let allData = dateRangeChart.getOption().series[j].data;
            for (let i = 0; i < allData.length; i++) {
                if (allData[i][0] > rs_sort[0] && allData[i][0] < rs_sort[1]) {
                    singleSelectionDate(selected_date, allData[i][0], i, j);
                }
            }
        }
    }

    //delete dates range
    function rangeDeleteDate(selected_date, range_selection, series_index) {
        range_selection.forEach(e => singleDeleteDate(selected_date, e.data[0], e.dataIndex, e.seriesIndex));
        var rs_sort = [range_selection[0].data[0], range_selection[1].data[0]];
        rs_sort.sort();
        let seriesLength = dateRangeChart.getOption().series.length;
        for (var j = 0; j < seriesLength; j++) {
            var allData = dateRangeChart.getOption().series[j].data;
            for (var i = 0; i < allData.length; i++) {
                if (allData[i][0] > rs_sort[0] && allData[i][0] < rs_sort[1]) {
                    singleDeleteDate(selected_date, allData[i][0], i, j);
                }
            }
        }
    }

    //create dates list
    function createSelectionUl(selection_date) {
        let selection_by_range = groupByDates(selection_date);
        const ul = $('<ul>', {class: "mylist"});
        selection_by_range.forEach(function (e) {
            if (e.length === 1) {
                ul.append($("<li>").append($("<a>").text(reverse_date(e[0][0]))));
            } else {
                ul.append($("<li>").append($("<a>").text("Desde " + reverse_date(e[0][0]) + " hasta "
                    + reverse_date(e[e.length - 1][0]))));
            }
        });
        return ul;
    }

    function reverse_date(date) {
        return date.toString().split("-").reverse().join("-")
    }


    function downplay_date(params) {
        dateRangeChart.dispatchAction({
            type: 'downplay',
            seriesIndex: params.seriesIndex,
            seriesName: params.seriesName,
            dataIndex: params.dataIndex,
        });
    }

    //filter selection
    var selectedRangeDate = [];
    var deletedRangeDate = [];
    //over event
    dateRangeChart.on("mouseover", function (params) {
        dateRangeChart.dispatchAction({
            type: 'highlight',
            seriesIndex: params.seriesIndex,
            seriesName: params.seriesName,
            dataIndex: params.dataIndex,
        });

        if (selectedRangeDate.length !== 0) {

            let seriesLength = dateRangeChart.getOption().series.length;
            for (var j = 0; j < seriesLength; j++) {
                let allData = dateRangeChart.getOption().series[j].data;
                let rs_sort = [selectedRangeDate[0].data[0], params.data[0]].sort();
                for (let i = 0; i < allData.length; i++) {
                    if (allData[i][0] >= rs_sort[0] && allData[i][0] <= rs_sort[1]) {
                        dateRangeChart.dispatchAction({
                            type: 'highlight',
                            dataIndex: i,
                            seriesIndex: j,

                        });
                    } else {
                        dateRangeChart.dispatchAction({
                            type: 'downplay',
                            dataIndex: i,
                            seriesIndex: j,

                        });
                    }
                }
            }

            tempSelectedDates.forEach(function (e) {
                dateRangeChart.dispatchAction({
                    type: 'highlight',
                    dataIndex: e[1],
                    seriesIndex: e[2],

                });
            });
        }

        if (deletedRangeDate.length !== 0) {
            let seriesLength = dateRangeChart.getOption().series.length;
            for (j = 0; j < seriesLength; j++) {
                let allData = dateRangeChart.getOption().series[j].data;
                let rs_sort = [deletedRangeDate[0].data[0], params.data[0]].sort();
                tempDeleted = new Set([]);
                for (let i = 0; i < allData.length; i++) {
                    if (allData[i][0] >= rs_sort[0] && allData[i][0] <= rs_sort[1]) {
                        tempDeleted.add([[allData[i][0]], i]);
                        dateRangeChart.dispatchAction({
                            type: 'downplay',
                            dataIndex: i,
                            seriesIndex: j
                        });
                    }
                }
            }
        }
    });

    //out event
    dateRangeChart.on("mouseout", function (params) {
        var is_date = false;
        tempSelectedDates.forEach(function (e) {
            if (e[0] === params.data[0]) {
                is_date = true;
            }
        });
        selectedRangeDate.forEach(function (e) {
            if (e.data[0] === params.data[0]) {
                is_date = true;
            }
        });
        if (!is_date) {
            dateRangeChart.dispatchAction({
                type: 'downplay',
                seriesIndex: params.seriesIndex,
                seriesName: params.seriesName,
                dataIndex: params.dataIndex,
            });
        }

    });


    //click event
    dateRangeChart.on('click', function (params) {
        if (singleDatePicker) {
            deleteSelection();
        }
        if ($("#option1").is(":checked")) {
            selectedRangeDate = [];
            deletedRangeDate = [];
            singleSelectionDate(tempSelectedDates, params.data[0], params.dataIndex, params.seriesIndex);
        } else if ($("#option2").is(":checked")) {
            selectedRangeDate = [];
            deletedRangeDate = [];
            singleDeleteDate(tempSelectedDates, params.data[0], params.dataIndex, params.seriesIndex);
            reprintSelection(true, false);

        } else if ($("#option3").is(":checked")) {
            deletedRangeDate = [];
            selectedRangeDate.push(params);
            if (selectedRangeDate.length === 2) {
                rangeSelectionDate(tempSelectedDates, selectedRangeDate);
                selectedRangeDate = [];
            }
            reprintSelection(true, false);

        } else if ($("#option4").is(":checked")) {
            selectedRangeDate = [];
            deletedRangeDate.push(params);
            if (deletedRangeDate.length === 2) {
                rangeDeleteDate(tempSelectedDates, deletedRangeDate);
                deletedRangeDate = [];
            }
            reprintSelection(true, false);

        }
        //update the selection date list
        var $ul = createSelectionUl(tempSelectedDates);
        $("#daysSelectedList").empty().append($ul);
    });


    //update storage and popover
    $('#saveButton').click(function () {
        selectedDates = tempSelectedDates;
        var datesSize = selectedDates.size;
        if (datesSize !== 0 && !singleDatePicker) {
            $('#dayFilter').popover({
                html: true,
                content: function () {
                    return $('#popover-content').html();
                }
            });
            $('#dayFilter').popover('enable');
        } else {
            $('#dayFilter').popover('disable');
        }

        if (!singleDatePicker) {
            $dayFilter.val(dayMessageHandler(datesSize));
            $dayFilter.attr("data-content", "");
            $('#popover-content').empty().append(createSelectionUl(tempSelectedDates));
        } else {
            if (datesSize !== 0) {
                $dayFilter.val(reverse_date(Array.from(tempSelectedDates)[0][0]));
            } else {
                $dayFilter.val("Ningún día seleccionado");
            }
        }
        window.localStorage.setItem(urlKey + "dayFilter", JSON.stringify(Array.from(tempSelectedDates)));
        $('#dayFilter').trigger('change');
    });

    //delete all selection
    $('#deleteSelection').click(function () {
        deleteSelection();
    });

    // downplay when global out
    dateRangeChart.on("globalout", function (params) {
        reprintSelection(true, false);
        if (selectedRangeDate.length !== 0) {
            downplay_date(selectedRangeDate[0]);
            selectedRangeDate = [];
        } else {
            deletedRangeDate = [];
        }

    });


    $(window).resize(() => {
        dateRangeChart.resize();
        reprintSelection();
    });

    $("#menu_toggle").click(() => {
        dateRangeChart.resize();
        reprintSelection();
    });


}