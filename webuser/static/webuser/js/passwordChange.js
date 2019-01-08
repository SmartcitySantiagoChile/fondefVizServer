"use strict";
$(document).ready(function () {
    $("#update").click(function (e) {
        var params = $("#form").serializeArray();
        $.post(window.location.pathname, params, function (data) {
            if (data.status) {
                showMessage(data.status);
                if (data.status.code === 205) {
                    $("#id_old_password").val("");
                    $("#id_new_password1").val("");
                    $("#id_new_password2").val("");
                }
            }
        });
    });
});