let our_tooltip: HTMLElement;

function on_tap(): void {
    // Find the tooltip
    let tooltip: HTMLElement = $('div.bk-tooltip');
    if (!tooltip)
        return;

    // Clone it
    let clone = <HTMLElement>tooltip.cloneNode(true);
    clone.style['left'] = "50px";
    clone.style['top'] = null;
    clone.style['bottom'] = "50px";

    // Remove the old one and add the new one
    if (our_tooltip)
        our_tooltip.parentNode.removeChild(our_tooltip);
    our_tooltip = tooltip.parentNode.appendChild(clone);
}

on_tap();
