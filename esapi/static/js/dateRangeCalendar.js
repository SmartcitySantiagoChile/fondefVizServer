"use strict";

/**
 * Calendar to show available days (dates with data)
 * */
var selectedDate = new Set();
var selectedDateAux = new Set();

$('#dayFilter').attr("data-trigger", "hover");
$('#dayFilter').attr("data-toggle", "popover");
$('#dayFilter').attr("data-content", "");
$('#dayFilter').attr("data-placement", "top");
$('#dayFilter').attr("data-original-title", "Días seleccionados");
$('#dayFilter').popover({
    html: true,
    content: function() {
        return $('#popover-content').html();
    }
});



function loadRangeCalendar(data_url) {
    var divId = "dateRangeCalendar";
    var dateRangeChart = echarts.init(document.getElementById(divId), theme);

    var calendarYearTemplate = {
        orient: "horizontal",
        range: null,
        dayLabel: {
            firstDay: 1,
            nameMap: ["D", "L", "M", "M", "J", "V", "S"]
        },
        monthLabel: {
            nameMap: ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        },
        top: 20,
        left: "50",
        right: "0",
        cellSize: ["auto", 9]
    };

    var serieTemplate = {
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
        series: []
    };

    $(window).resize(function () {
        dateRangeChart.resize();
        mark_date_selected();
    });
    $("#menu_toggle").click(function () {
        dateRangeChart.resize();
        mark_date_selected();
    });
    $("#dateRangeModal").on('shown.bs.modal', function () {
        dateRangeChart.resize();
        mark_date_selected();
        var $ul = createSelectionUl(selectedDateAux);
        $('#daysSelectedList').empty().append($ul);
        if (selectedDateAux.size === 0){
            selectedDate = new Set([]);
        } else {
            selectedDate = new Set(selectedDateAux);
        }
    });

    // show loading
    var loadingText = "Cargando ...";
    dateRangeChart.showLoading(null, {text: loadingText});

    $.get(data_url, function (data) {
        dateRangeChart.hideLoading();
        var years = data.availableDays.map(function (el) {
            return el.split("-")[0];
        }).filter(function (el, index, self) {
            return self.indexOf(el) === index;
        });
        data = data.availableDays.map(function (el) {
            return [el, 1];
        });
        if (data.length > 0) {
            var newOpts = $.extend({}, opts);
            var top = 20;
            years.forEach(function (year, index) {
                var calendarYear = $.extend({}, calendarYearTemplate);
                var serie = $.extend({}, serieTemplate);

                calendarYear.range = year;
                calendarYear.top = top;
                top += 100;
                serie.calendarIndex = index;
                serie.data = data;
                serie.emphasis = {
                    itemStyle: {
                        color: 'green'
                    }
                };

                newOpts.calendar.push(calendarYear);
                newOpts.series.push(serie);

            });

            $("#" + divId).height(top - 20);
            dateRangeChart.setOption(newOpts, {notMerge: true});
            dateRangeChart.resize();
        }

    });

    function mark_date_selected(){
        var allData = dateRangeChart.getOption().series[0].data;
        for (var i = 0; i < allData.length; i++){
            dateRangeChart.dispatchAction({
                type: 'downplay',
                dataIndex: allData[i][1],
            });
        }

        selectedDateAux.forEach(function (e) {
            dateRangeChart.dispatchAction({
                type: 'highlight',
                dataIndex: e[1],
            });
        })
    }

    function singleSelectionDate(selected_date, value, data_index){
        dateRangeChart.dispatchAction({
            type: 'highlight',
            dataIndex: data_index,
        });
        var exist = false;
        selected_date.forEach(function(e){
          if (e[0] === value) {
            exist = true;
          }
        });

        if (!exist){
            selected_date.add([value, data_index]);
        }
    }

    function singleDeleteDate(selected_date, value, data_index){
        dateRangeChart.dispatchAction({
            type: 'downplay',
            dataIndex: data_index,
        });

        selected_date.forEach(function(e){
          if (e[0] === value) {
            selected_date.delete(e);
          }
        });
    }

    function rangeSelectionDate(selected_date, range_selection){
        range_selection.forEach(e => singleSelectionDate(selected_date, e.data[0], e.dataIndex ));
        var rs_sort = [range_selection[0].data[0], range_selection[1].data[0]];
        rs_sort.sort();
        var allData = dateRangeChart.getOption().series[0].data;
        for (var i = 0; i < allData.length; i++){
            if (allData[i][0] > rs_sort[0] && allData[i][0] < rs_sort[1]){
                singleSelectionDate(selected_date, allData[i][0], i);
            }
        }
    }

    function rangeDeleteDate(selected_date, range_selection){
        range_selection.forEach(e => singleDeleteDate(selected_date, e.data[0], e.dataIndex ));
        var rs_sort = [range_selection[0].data[0], range_selection[1].data[0]];
        rs_sort.sort();
        var allData = dateRangeChart.getOption().series[0].data;
        for (var i = 0; i < allData.length; i++){
            if (allData[i][0] > rs_sort[0] && allData[i][0] < rs_sort[1]){
                singleDeleteDate(selected_date, allData[i][0], i);
            }
        }
    }

    function createSelectionUl(selection_date){
        let sortedArray = Array.from(selection_date).sort();
        let dateArray = [];
        sortedArray.map(e => dateArray.push(new Date(e[0])));
        let selection_by_range = [];
        let aux_selector = [];
        for (let i = 0; i < dateArray.length; i++) {
            aux_selector.push(sortedArray[i]);
            let next_day = new Date(dateArray[i]);
            next_day.setDate(dateArray[i].getDate() + 1);
            var index = dateArray.findIndex(function (x) {
                return x.valueOf() === next_day.valueOf();
            });
            if (index === -1) {
                selection_by_range.push(aux_selector);
                aux_selector = [];
            }
        }
        var ul = $('<ul>', {class: "mylist"});
        selection_by_range.forEach(function (e) {
            if (e.length === 1){
                ul.append($("<li>").append($("<a>").text(reverse_date(e[0][0]))));
            } else {
                ul.append($("<li>").append($("<a>").text("Desde " + reverse_date(e[0][0]) + " hasta "
                    + reverse_date(e[e.length - 1][0]))));
            }
        });
        return ul;
    }

    function reverse_date(date){
        return date.toString().split("-").reverse().join("-")
    }

    //filter selection
    var selectedRangeDate = [];
    var deletedRangeDate = [];

    //over event
    dateRangeChart.on("mouseover", function(params){
        dateRangeChart.dispatchAction({
            type: 'highlight',
            seriesIndex: params.seriesIndex,
            seriesName: params.seriesName,
            dataIndex: params.dataIndex,
        });
    });

    //out event
    dateRangeChart.on("mouseout", function(params){
        var is_date = false;
        selectedDate.forEach(function(e){
          if (e[0] === params.data[0]) {
            is_date = true;
          }
        });
        selectedRangeDate.forEach(function(e){
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
        if ($("#option1").is(":checked")){
            selectedRangeDate = [];
            deletedRangeDate = [];
            singleSelectionDate(selectedDate, params.data[0], params.dataIndex);
        } else if ($("#option2").is(":checked")){
            selectedRangeDate = [];
            deletedRangeDate = [];
            singleDeleteDate(selectedDate, params.data[0], params.dataIndex);
        } else if ($("#option3").is(":checked")){
            deletedRangeDate = [];
            selectedRangeDate.push(params);
            if (selectedRangeDate.length  === 2) {
                rangeSelectionDate(selectedDate, selectedRangeDate);
                selectedRangeDate = [];
            }
        } else if ($("#option4").is(":checked")){
            selectedRangeDate = [];
            deletedRangeDate.push(params);
            if (deletedRangeDate.length  === 2) {
                rangeDeleteDate(selectedDate, deletedRangeDate);
                deletedRangeDate = [];
            }
        }
        //update the selection date list
        var $ul = createSelectionUl(selectedDate);
        $('#daysSelectedList').empty().append($ul);
    });

    //update storage
    $('#saveButton').click(function () {
        selectedDateAux = selectedDate;
        $('#dayFilter').val(selectedDateAux.size + " dias seleccionados");
        $('#dayFilter').attr("data-content", "");
        $('#popover-content').empty().append(createSelectionUl(selectedDate));

    })



}