let $ = (arg) => document.querySelector(arg);

// Avoids bug #8065 in Bokeh
async function arrow() {
    // noinspection JSJQueryEfficiency
    while (!$('div.bk-tooltip-arrow'))
        await new Promise(r => setTimeout(r, 250));

    // noinspection JSJQueryEfficiency
    let arrow = $('div.bk-tooltip-arrow');
    if (arrow && arrow.parentNode)
        arrow.parentNode.removeChild(arrow);
}


function main() {
    // Resizing plot
    let plotWrapper = $("div#plot-my-wrapper");
    plotWrapper.addEventListener('mouseup', function(e){
        // noinspection JSSuspiciousNameCombination
        plotWrapper.style.height = plotWrapper.style.width;
        Bokeh.index["attack-figure"].resize();
    }, false);

    // Disable for now
    //arrow().then();
}

window.onload = main;
