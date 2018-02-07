moment.locale('es');

var optionDateRangePicker = {
    startDate: moment().subtract(1, "months"),
    endDate: moment(),
    alwaysShowCalendars: true,
    showCustomRangeLabel: false,
    showDropdowns: false,
    showWeekNumbers: false,
    timePicker: false,
    timePickerIncrement: 1, // minutes
    timePicker12Hour: true,
    ranges: {
        "Hoy": [moment(), moment()],
        "Ayer": [moment().subtract(1, "days"), moment().subtract(1, "days")],
        "Últimos 7 días": [moment().subtract(6, "days"), moment()],
        "Últimos 30 Días": [moment().subtract(29, "days"), moment()],
        "Este mes": [moment().startOf("month"), moment().endOf("month")],
        "Mes anterior": [moment().subtract(1, "month").startOf("month"), moment().subtract(1, "month").endOf("month")]
    },
    opens: "right",
    buttonClasses: ["btn btn-default"],
    applyClass: "btn-sm btn-success",
    cancelClass: "btn-sm",
    format: "DD/MM/YYYY",
    separator: " to ",
    locale: {
        applyLabel: "Aceptar",
        cancelLabel: "Cancelar",
        fromLabel: "Desde",
        toLabel: "A",
        customRangeLabel: "Elegir",
        daysOfWeek: ["Do", "Lu", "Ma", "Mi", "Ju", "Vi", "Sa"],
        monthNames: ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
        firstDay: 1
    }
};