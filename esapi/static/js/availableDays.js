"use strict";

/**
 * Calendar to show available days (dates with data)
 * */
function loadAvailableDays(data_url) {
    var divId = "availableDays";
    var availableDaysChart = echarts.init(document.getElementById(divId), theme);

    var calendarYearTemplate = {
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
        series: [],
        legend: [],
        dataRange: []
    };

    $(window).resize(function () {
        availableDaysChart.resize();
    });
    $("#menu_toggle").click(function () {
        availableDaysChart.resize();
    });

    // show loading
    var loadingText = "Cargando ...";
    availableDaysChart.showLoading(null, {text: loadingText});

    $.get(data_url, function (data) {
        availableDaysChart.hideLoading();
        var years = data.availableDays.map(function (el) {
            return el.split("-")[0];
        }).filter(function (el, index, self) {
            return self.indexOf(el) === index;
        });

        const groupBy = keys => array =>
            array.reduce((objectsByKeyValue, obj) => {
                const value = keys.map(key => obj[key]).join('-');
                objectsByKeyValue[value] = (objectsByKeyValue[value] || []).concat(obj);
                return objectsByKeyValue;
            }, {});

        const groupByColor = groupBy(["color"]);
        let descriptionDayList = groupByColor(data.info);
        descriptionDayList = Object.values(descriptionDayList);
        let auxDescriptionDayList = [];
        descriptionDayList.forEach(function (e) {
            let aux_array = [];
            e.forEach(function (f) {
                aux_array.push(Object.values(f));
            });
            auxDescriptionDayList.push(aux_array);
        });
        descriptionDayList = auxDescriptionDayList;
        data = data.availableDays.map(function (el) {
            return [el, 1];
        });
        if (data.length > 0) {
            var newOpts = $.extend({}, opts);
            var top = 50;
            let legendData = [];
            years.forEach(function (year, index) {
                let calendarYear = JSON.parse(JSON.stringify($.extend({}, calendarYearTemplate)));
                var serie = $.extend({}, serieTemplate);
                if (index === 0) {
                    calendarYear.monthLabel.nameMap = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago",
                        "Sep", "Oct", "Nov", "Dic"];
                }
                if (index === years.length - 1) {
                    calendarYear.bottom = '1%'
                }
                calendarYear.range = year;
                calendarYear.top = top;
                top += 84;
                serie.calendarIndex = index;
                serie.data = data;
                serie.itemStyle = {
                    color: "#97b58d",
                };
                serie.zlevel = 3;
                newOpts.calendar.push(calendarYear);
                newOpts.series.push(serie);
                //year-date dictionary
                let dataObject = {};
                data.forEach(function (e) {
                    dataObject[e[0]] = 1;
                });
                let noDataDay = [["", "#FFFFFF", "Sin datos"]];
                descriptionDayList.push(noDataDay);
                descriptionDayList.forEach(function (date) {
                    let descriptionSerie = $.extend({}, serieTemplate);
                    descriptionSerie.name = date[0][2];
                    let dataAux = [];
                    date.forEach(function (e) {
                        const index = e[0] in dataObject;
                        if (index) {
                            dataAux.push(e);
                        }
                    });
                    descriptionSerie.data = dataAux.map(function (e) {
                        return [e[0], 1];
                    });
                    legendData.push({
                        name: descriptionSerie.name,
                    });
                    descriptionSerie.itemStyle = {
                        color: date[0][1],
                    };

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
                itemStyle: {
                    borderColor: "black",
                    borderWidth: 1
                }

            };
            $("#" + divId).height(top - 20);
            availableDaysChart.setOption(newOpts, {notMerge: true});
            availableDaysChart.resize();

        }
    });
}