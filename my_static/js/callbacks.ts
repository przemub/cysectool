let our_tooltip: HTMLElement;

// noinspection JSUnusedGlobalSymbols
function on_tap(): void {
    // Find the tooltip
    const tooltip: HTMLElement = $('div.bk-tooltip');
    if (!tooltip)
        return;

    // Clone it
    const clone = <HTMLElement>tooltip.cloneNode(true);
    clone.style['left'] = "50px";
    clone.style['top'] = null;
    clone.style['bottom'] = "50px";

    // Remove the old one and add the new one
    if (our_tooltip)
        our_tooltip.parentNode.removeChild(our_tooltip);
    our_tooltip = tooltip.parentNode.appendChild(clone);
}

function load_model(): void {
    const file_list = (<HTMLInputElement> $("input#load")).files;

    if (!file_list)
        return;

    const file = file_list[0];

    const reader = new FileReader();
    reader.readAsText(file, "UTF-8");

    reader.onload = function() {
        const content = reader.result;

        let http = new XMLHttpRequest();
        http.open('POST', "/api", true);
        http.setRequestHeader('Content-Type', 'application/json');

        http.onload = function () {
            let response = JSON.parse(this.responseText);
            window.location.href = "/visualiser?id=" + response['uid'];
        };

        http.send(JSON.stringify({'cmd': 'load', 'file': content}))
    };

    reader.onerror = function() {
        alert("Failed to load the model!");
    };
}