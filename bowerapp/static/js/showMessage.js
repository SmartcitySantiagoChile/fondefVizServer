"use strict";
/**
 *  Use Pnotify library to show floating bubble with info message
 * */
function showMessage(status) {
    var message = status.message;
    var title = status.title;
    var type = status.type;

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
