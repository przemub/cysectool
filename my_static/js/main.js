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

arrow().then();

