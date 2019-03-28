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
// noinspection JSUnusedGlobalSymbols
function load_model() {
    var file_list = $("input#load").files;
    if (!file_list)
        return;
    var file = file_list[0];
    var reader = new FileReader();
    reader.readAsText(file, "UTF-8");
    reader.onload = function () {
        var content = reader.result;
        console.log(content);
    };
    reader.onerror = function () {
        alert("Failed to load the model!");
    };
}
//# sourceMappingURL=callbacks.js.map