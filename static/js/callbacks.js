"use strict";
var our_tooltip;
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
on_tap();
//# sourceMappingURL=callbacks.js.map