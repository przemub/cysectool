const verticesGrid = $("#verticesGrid");
const groupsGrid = $("#groupsGrid");
const levelsGrid = $("#levelsGrid");
const edgesGrid = $("#edgesGrid");

function updateGrid(grid, item) {
    const groups = groupsGrid.jsGrid("option", "data");

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

    const levels = levelsGrid.jsGrid("option", "data");
    // TODO: Do it more efficiently
    for (const level of levels) {
        for (const i in new_levels)
            if (new_levels[i]['gid'] === level['gid'] && new_levels[i]['level'] === level['level'])
                new_levels[i] = level;
    }
    console.log(new_levels);
    console.log(levels);

    levelsGrid.jsGrid("option", "data", new_levels);
}

function setVertexId(grid, item) {
    const vertices = verticesGrid.jsGrid("option", "data");
    for (const i in vertices)
        vertices[i].id = i;
    verticesGrid.jsGrid("option", "data", vertices);
}

(function(jsGrid, $) {
    var NumberField = jsGrid.NumberField;

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

function main() {
    verticesGrid.jsGrid({
        width: "100%",
        height: "400px",

        inserting: true,
        editing: true,
        sorting: true,
        paging: false,

        data: vertices,

        onItemInserted: setVertexId,
        onItemDeleted: setVertexId,

        fields: [
            {name: "id", title: "ID", type: "text", width: 50, readOnly: true},
            {name: "name", title: "Name", type: "text", width: 150, validate: "required"},
            {type: "control"}
        ]
    });


    groupsGrid.jsGrid({
        width: "100%",
        height: "400px",

        inserting: true,
        editing: true,
        sorting: true,
        paging: false,

        data: groups,

        onItemInserted: updateGrid,
        onItemUpdated: updateGrid,

        fields: [
            {name: "id", title: "ID", type: "text", width: 50, validate: "required"},
            {name: "name", title: "Name", type: "text", width: 150, validate: "required"},
            {name: "levels", title: "Number of levels", type: "number", width: 50, validate: "required"},
            {type: "control"}
        ]
    });


    levelsGrid.jsGrid({
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
            {name: "flow", title: "Flow", type: "decimal", width: 50},
            {type: "control", deleteButton: false}
        ]
    });


    edgesGrid.jsGrid({
        width: "100%",
        height: "400px",

        inserting: true,
        editing: true,
        sorting: true,
        paging: false,

        data: edges,

        fields: [
            {name: "source", title: "Source", type: "number", width: 50, validate: "required"},
            {name: "target", title: "Target", type: "number", width: 50, validate: "required"},
            {name: "name", title: "Vulnerability name", type: "text", width: 150, validate: "required"},
            {name: "controls", title: "Valid controls", type: "text", width: 100, validate: "required"},
            {type: "control"}
        ]
    });

    setVertexId();
}

main();
