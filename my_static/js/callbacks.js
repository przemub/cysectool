"use strict";
var our_tooltip;
// noinspection JSUnusedGlobalSymbols
function on_tap() {
    // Find the tooltip
    var tooltip = $('div.bk-tooltip');
    if (!tooltip)
        return;
    // Clone it
    var clone = tooltip.cloneNode(true);
    clone.style['left'] = "50px";
    clone.style['top'] = null;
    clone.style['bottom'] = "50px";
    // Remove the old one and add the new one
    if (our_tooltip)
        our_tooltip.parentNode.removeChild(our_tooltip);
    our_tooltip = tooltip.parentNode.appendChild(clone);
}
function load_model() {
    var file_list = $("input#load").files;
    if (!file_list)
        return;
    var file = file_list[0];
    var reader = new FileReader();
    reader.readAsText(file, "UTF-8");
    reader.onload = function () {
        var content = reader.result;
        var http = new XMLHttpRequest();
        http.open('POST', "/api", true);
        http.setRequestHeader('Content-Type', 'application/json');
        http.onload = function () {
            var response = JSON.parse(this.responseText);
            window.location.href = "/visualiser?id=" + response['uid'];
        };
        http.send(JSON.stringify({ 'cmd': 'load', 'file': content }));
    };
    reader.onerror = function () {
        alert("Failed to load the model!");
    };
}
function save_model() {
    var get = {};
    location.search.substr(1).split("&").forEach(function (item) {
        get[item.split("=")[0]] = item.split("=")[1];
    });
    var dict = { 'cmd': 'save' };
    if ('uid' in get)
        dict['uid'] = get['uid'];
    var json = JSON.stringify(dict);
    var http = new XMLHttpRequest();
    http.open('POST', "/api", true);
    http.setRequestHeader('Content-Type', 'application/json');
    http.onload = function () {
        var blob = new Blob([this.responseText]);
        var link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = "model.json";
        document.body.appendChild(link);
        link.click();
        window.URL.revokeObjectURL(link.href);
        link.remove();
    };
    http.send(json);
}
//# sourceMappingURL=callbacks.js.map