"use strict";

/**
 * Calendar to show available days (dates with data)
 * */
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
    });
    $("#menu_toggle").click(function () {
        dateRangeChart.resize();
    });
    $("#dateRangeModal").on('shown.bs.modal', function () {
        dateRangeChart.resize();
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


    // return selected day
    function singleSelectionDate(selected_date, params){
        var value = params.data[0];
        var indexf = [];
        for (var i = 0; i < selected_date.length; i++){
            var index = selected_date[i].indexOf(value);
            if (index != -1){
                indexf = [i, index];
            }
        }
        if (indexf.length == 0) {
            selected_date.push([value]);
            dateRangeChart.dispatchAction({
                type: 'highlight',
                seriesIndex: params.seriesIndex,
                seriesName: params.seriesName,
                dataIndex: params.dataIndex,
            })
        } else {
            if (selected_date[indexf[0]].length == 1){
                selected_date.splice(indexf[0], 1);
            } else {
                selected_date[indexf[0]].splice(indexf[1], 1);
            }
            dateRangeChart.dispatchAction({
                type: 'downplay',
                seriesIndex: params.seriesIndex,
                seriesName: params.seriesName,
                dataIndex: params.dataIndex,
            })
        }
        return selected_date
    }

    // return selected days in a range todo: iluminar/cambiar color
    function rangeSelectionDate(range_selection){
        var selected_date = [];
        range_selection.forEach(element => selected_date.push(element));
        var allData = dateRangeChart.getOption().series[0].data;
        var selected_days = [];
        allData.forEach(function(e){
            if (e > range_selection[0] && e < range_selection[1]){
                selected_days.push(e[0]);
            }
        });
        selected_days.push(range_selection[1]);
        return selected_days;
    }

    // Decide to add or delete selected days
    function manageRangeDate(range_selection, selected_days){
        if (range_selection.length == 1){
            var index = selected_days.indexOf(range_selection[0]);
            console.log(index)
        }


    }

    //filter selection
    // check selection type
    var selectedDate = [];
    var rangeSelectionCheck = false;
    var rangeSelection = [];
    $("#dateRangeOn").click(function() {
        rangeSelectionCheck = this.checked;
    });

    //click event
    dateRangeChart.on('click', function (params) {
        if (!rangeSelectionCheck){
            selectedDate = singleSelectionDate(selectedDate, params);

        } else {
            if (rangeSelection.length < 2) {
                rangeSelection.push(params.data[0]);
            } else {
                rangeSelection = [];
                rangeSelection.push(params.data[0]);
            }
            if (rangeSelection.length == 2) {
                selectedDate.push(rangeSelectionDate(rangeSelection.sort()));
                rangeSelection = []
            }
        }

        //update the selection date list
        var $ul = $('<ul>', {class: "mylist"}).append(
            selectedDate.map(fecha =>
                $("<li>").append($("<a>").text(fecha))
            )
        );
        $('#daysSelectedList').empty().append($ul);
    });
}