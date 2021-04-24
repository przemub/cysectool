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


/**
 * Make sure that the server has not been restarted (and the view invalidated)
 * in the meantime.
 */
async function check_connection() {
    let xhr = new XMLHttpRequest();
    xhr.open("GET", "/ping", true);

    function failed() {
        alert("Lost connection with the server. Press OK to refresh.");
        window.location.href = "/";
    }

    xhr.onload = async function () {
        if (this.responseText === "PONG") {
            await new Promise(r => setTimeout(r, 1000));
            await check_connection();
        }
        else
            failed();
    }
    xhr.onerror = failed;

    xhr.send();
}


function main() {
    // Resizing plot
    let plotWrapper = $("div#plot-my-wrapper");
    plotWrapper.addEventListener('mouseup', function(e){
        // noinspection JSSuspiciousNameCombination
        plotWrapper.style.height = plotWrapper.style.width + 20;

        if ('resize' in Bokeh.index["attack-figure"])
            Bokeh.index["attack-figure"].resize(); // Bokeh < 1.1
        else
            Bokeh.index["attack-figure"].resize_layout(); // Bokeh >= 1.1
    }, false);

    // arrow().then();
    check_connection().then();
}

window.onload = main;
