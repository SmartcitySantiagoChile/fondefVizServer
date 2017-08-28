"use strict";
/**
 *  Use Pnotify library to show floating bubble with info message
 * */
function showMessage(status) {
    let message = status["message"];
    let title = status["title"];
    let type = status["type"];

    new PNotify({
        title: title,
        type: type,
        text: message,
        nonblock: {
            nonblock: true
        },
        styling: "bootstrap3",
        mouse_reset: false
    }).get().click(function () {
        this.remove();
    });
}
