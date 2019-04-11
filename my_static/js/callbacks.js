let our_tooltip;

// noinspection JSUnusedGlobalSymbols
function on_tap() {
    // Find the tooltip
    const tooltip = $('div.bk-tooltip');
    if (!tooltip)
        return;

    // Clone it
    const clone = tooltip.cloneNode(true);
    clone.style['left'] = "50px";
    clone.style['top'] = null;
    clone.style['bottom'] = "50px";

    // Remove the old one and add the new one
    if (our_tooltip)
        our_tooltip.parentNode.removeChild(our_tooltip);
    our_tooltip = tooltip.parentNode.appendChild(clone);
}

function load_model() {
    const file_list = $("input#load").files;

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
            try {
                let response = JSON.parse(this.responseText);
                window.location.href = "/visualiser?id=" + response['uid'];
            } catch (e) {
                alert(this.responseText);
            }
        };

        http.send(JSON.stringify({'cmd': 'load', 'file': content}))
    };

    reader.onerror = function() {
        alert("Failed to load the model!");
    };
}

function get() {
    let get = {};
    location.search.substr(1).split("&").forEach(function(item) {
        get[item.split("=")[0]] = item.split("=")[1];
    });

    return get;
}

function save_model() {
    let dict = {'cmd': 'save'};
    let get_table = get();
    if ('uid' in get_table)
        dict['uid'] = get_table['uid'];
    let json = JSON.stringify(dict);

    let http = new XMLHttpRequest();
    http.open('POST', "/api", true);
    http.setRequestHeader('Content-Type', 'application/json');

    http.onload = function () {
        let blob = new Blob([this.responseText]);
        let link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = "model.json";
        document.body.appendChild(link);
        link.click();
        window.URL.revokeObjectURL(link.href);
        link.remove();
    };

    http.send(json);
}

function edit_model() {
    let url = "/edit";
    let get_table = get();
    if ('id' in get_table)
        url += "?uid=" + get_table['id'];

    window.open(url, "_blank");
}

function new_model() {
    window.open("/edit?uid=empty", "_blank");
}