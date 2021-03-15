/**
 * Opens the URL associated with an edge.
 * (i.e. description of a vulnerability)
 * edge_source is the ColumnDataSource used to populate edges.
 * https://stackoverflow.com/questions/54768696/how-to-open-a-url-with-corresponding-data-of-clicked-edge-of-a-bokeh-graph
 */
function open_url(edge_source, node_source) {
    const selected_edge = edge_source.selected.indices[0];

    // Deselect all that got selected.
    edge_source.selected.indices = [];
    node_source.selected.indices = [];

    const url = edge_source.data.url[selected_edge];
    if (url !== null)
        window.open(url);
}

/** Loads a model uploaded via the Load Model button. */
function load_model() {
    const file_list = document.querySelector("input#load").files;

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
                window.location.href = "/visualiser?id=" + response['id'];
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

/** Returns an object of GET URL parameters. */
function get() {
    let get = {};
    location.search.substr(1).split("&").forEach(function(item) {
        get[item.split("=")[0]] = item.split("=")[1];
    });

    return get;
}

/** Saves the currently loaded model. */
function save_model() {
    let dict = {'cmd': 'save'};
    let get_table = get();
    if ('id' in get_table)
        dict['id'] = get_table['id'];
    console.log(get_table, get_table['id'])
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

/** Opens the currently open model in the editor. */
function edit_model() {
    let url = "/edit";
    let get_table = get();
    if ('id' in get_table)
        url += "?id=" + get_table['id'];

    window.open(url, "_blank");
}

/** Opens an empty model in the editor. */
function new_model() {
    window.open("/edit?id=empty", "_blank");
}

/** Goes to one of the default models (templates). */
function template_change(value) {
    let url = "/visualiser";
    url += "?id=" + value;

    window.location.href = url;
}
