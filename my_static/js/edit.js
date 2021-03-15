const vertices_grid = $("#verticesGrid");
const groups_grid = $("#groupsGrid");
const levels_grid = $("#levelsGrid");
const edges_grid = $("#edgesGrid");

function update_grid(_grid, _item) {
    const groups = groups_grid.jsGrid("option", "data");

    let new_levels = [];
    for (const group of groups) {
        for (let i = 1; i <= group.levels; i++)
            new_levels.push({
                'gid': group.id,
                'level': i.toString(),
                'name': group.id+" "+i.toString(),
                'cost': 1,
                'ind_cost': 1,
                'flow': 1
            });
    }

    const levels = levels_grid.jsGrid("option", "data");
    // TODO: Do it more efficiently
    for (const level of levels) {
        for (const i in new_levels)
            if (new_levels[i]['gid'] === level['gid'] && new_levels[i]['level'] === level['level'])
                new_levels[i] = level;
    }
    console.log(new_levels);
    console.log(levels);

    levels_grid.jsGrid("option", "data", new_levels);
}

function update_vertices(_grid, _item) {
    const vertices = vertices_grid.jsGrid("option", "data");
    for (const i in vertices)
        vertices[i].id = i;
    vertices_grid.jsGrid("option", "data", vertices);

    // Fill the vertex select with the changed vertices
    const vertex_fields = edges_grid.jsGrid("option", "fields");
    const vertex_names = vertices.map((v) => v.name)

    vertex_fields[0].items = vertex_names;
    vertex_fields[1].items = vertex_names;
    edges_grid.jsGrid("option", "fields", vertex_fields);
}

(function(jsGrid, $) {
    let NumberField = jsGrid.NumberField;

    function DecimalField(config) {
        NumberField.call(this, config);
    }

    DecimalField.prototype = new NumberField({

        step: 0.01,

        filterValue: function() {
            return this.filterControl.val() ? parseFloat(this.filterControl.val()) : undefined;
        },

        insertValue: function() {
            return this.insertControl.val() ? parseFloat(this.insertControl.val()) : undefined;
        },

        editValue: function() {
            return this.editControl.val() ? parseFloat(this.editControl.val()) : undefined;
        },

        _createTextBox: function() {
            return NumberField.prototype._createTextBox.call(this)
                .attr("step", this.step);
        }
    });

    jsGrid.fields.decimal = jsGrid.DecimalField = DecimalField;

}(jsGrid, jQuery));

function clear_edit() {
    vertices_grid.jsGrid("option", "data", []);
    levels_grid.jsGrid("option", "data", []);
    edges_grid.jsGrid("option", "data", []);
    groups_grid.jsGrid("option", "data", []);
}

function model_to_json() {
    const groupsData = groups_grid.jsGrid("option", "data");
    const levelsData = levels_grid.jsGrid("option", "data");
    const verticesData = vertices_grid.jsGrid("option", "data");
    const edgesData = edges_grid.jsGrid("option", "data");

    let controls = {};
    // TODO: Again, efficiency…
    for (const group of groupsData) {
        let group_obj = {
            'name': group.name,
            'level_name': [],
            'cost': [],
            'ind_cost': [],
            'flow': []
        };
        for (const level of levelsData) {
            if (level.gid === group.id) {
                group_obj.level_name.push(level.name);
                group_obj.cost.push(level.cost);
                group_obj.ind_cost.push(level.ind_cost);
                group_obj.flow.push(level.flow);
            }
        }
        controls[group.id] = group_obj;
    }

    let vertices_obj = [];
    for (const vertex of verticesData)
        vertices_obj.push(vertex.name);

    function controlsReprToObj(control) {
        const controls = control.split(";");

        let obj = {};
        const re = /^([a-zA-Z0-9]+)\(([0-9]+\.?[0-9]*),([0-9]+\.?[0-9]*)\)$/;
        const re_custom = /^([a-zA-z0-9]+)\[([0-9.,]+)]$/;
        for (const control of controls) {
            if (!control)
                continue;

            const match = re.exec(control),
                match_custom = re_custom.exec(control);
            if (match !== null)
                obj[match[1]] = {
                    'flow': parseFloat([2]),
                    'max_flow': parseFloat(match[3])
                };
            else if (match_custom !== null)
                obj[match_custom[1]] = {'custom': match_custom[2].split(',').map(parseFloat)};
            else
                obj[control] = {};
        }
        return obj;
    }

    let edges_obj = [];
    for (const edge of edgesData)
        edges_obj.push({
            'source': edge.source, 'target': edge.target,
            'default_flow': edge.default_flow,
            'vulnerability': {
                'name': edge.name,
                'controls': controlsReprToObj(edge.controls)
            },
            'url': edge.url
        });

    let obj = {
        'name': $("#graph_title").val(),
        'controls': controls,
        'vertices': vertices_obj,
        'edges': edges_obj
    };

    return JSON.stringify(obj, null, 2);
}

function save_edit() {
    /**
     * Uploads the model and, if it uploaded correctly, gives a JSON file
     * to download it.
     */
    const json = model_to_json();

    _upload_model(json, function () {
        try {
            JSON.parse(this.responseText);
        } catch (e) {
            alert(this.responseText);
            return
        }

        const blob = new Blob([json]);
        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = $("#graph_title").val() + ".json";
        document.body.appendChild(link);
        link.click();
        window.URL.revokeObjectURL(link.href);
        link.remove();
    });
}

function _upload_model(model, callback) {
    let http = new XMLHttpRequest();
    http.open('POST', "/api", true);
    http.setRequestHeader('Content-Type', 'application/json');
    http.onload = callback;

    http.send(JSON.stringify({'cmd': 'load', 'file': model}))
}

/** Uploads the model and opens it in the visualiser. */
function view_edit() {
    const json = model_to_json();

    _upload_model(json, function () {
        try {
            let response = JSON.parse(this.responseText);
            window.open("/visualiser?id=" + response['id'], "_blank");
        } catch (e) {
            alert(this.responseText);
        }
    });
}

/** Uploads the given model and opens it in the editor. */
function open_edit() {
    const file_list = document.querySelector("input#file").files;
    if (!file_list)
        return;

    const file = file_list[0];
    const reader = new FileReader();
    reader.readAsText(file, "UTF-8");

    reader.onload = function() {
        _upload_model(reader.result, function () {
            try {
                let response = JSON.parse(this.responseText);
                window.open("/edit?id=" + response['id'], "_blank");
            } catch (e) {
                alert(this.responseText);
            }
        });
    }
}

function main() {
    vertices_grid.jsGrid({
        width: "100%",
        height: "400px",

        inserting: true,
        editing: true,
        sorting: true,
        paging: false,

        data: vertices,

        onItemInserted: update_vertices,
        onItemDeleted: update_vertices,

        fields: [
            {name: "id", title: "ID", type: "text", width: 50, readOnly: true},
            {name: "name", title: "Name", type: "text", width: 150, validate: "required"},
            {type: "control"}
        ]
    });


    groups_grid.jsGrid({
        width: "100%",
        height: "400px",

        inserting: true,
        editing: true,
        sorting: true,
        paging: false,

        data: groups,

        onItemInserted: update_grid,
        onItemUpdated: update_grid,

        fields: [
            {name: "id", title: "ID", type: "text", width: 50, validate: "required"},
            {name: "name", title: "Name", type: "text", width: 150, validate: "required"},
            {name: "levels", title: "Number of levels", type: "number", width: 50, validate: "required"},
            {type: "control"}
        ]
    });

    const flowValidator = {
        validator: "range",
        message: "The flow should be between 0 and 1.",
        param: [0, 1]
    }

    levels_grid.jsGrid({
        width: "100%",
        height: "400px",

        inserting: false,
        editing: true,
        sorting: true,
        paging: false,

        data: levels,

        fields: [
            {name: "gid", title: "Group ID", type: "text", width: 50, readOnly: true},
            {name: "level", title: "Level", type: "text", width: 50, readOnly: true},
            {name: "name", title: "Name", type: "text", width: 150, validate: "required"},
            {name: "cost", title: "Cost", type: "number", width: 50, validate: "required"},
            {name: "ind_cost", title: "Indirect cost", type: "number", width: 50, validate: "required"},
            {name: "flow", title: "Flow", type: "decimal", width: 50, validate: flowValidator},
            {type: "control", deleteButton: false}
        ]
    });


    edges_grid.jsGrid({
        width: "100%",
        height: "400px",

        inserting: true,
        editing: true,
        sorting: true,
        paging: false,

        data: edges,

        fields: [
            {name: "source", title: "Source", type: "select", width: 80, validate: "required"},
            {name: "target", title: "Target", type: "select", width: 80, validate: "required"},
            {name: "default_flow", title: "Default flow", type: "decimal", width: 50, validate: flowValidator},
            {name: "name", title: "Vulnerability name", type: "text", width: 150, validate: "required"},
            {name: "controls", title: "Valid controls", type: "text", width: 100},
            {name: "url", title: "URL", type: "text", width: 30},
            {type: "control"}
        ]
    });

    update_vertices();
}

main();
