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

        if ('resize' in Bokeh.index["attack-figure"])
            Bokeh.index["attack-figure"].resize(); // Bokeh < 1.1
        else
            Bokeh.index["attack-figure"].resize_layout(); // Bokeh >= 1.1
    }, false);

    // Disable for now
    //arrow().then();
}

window.onload = main;
