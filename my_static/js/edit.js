const verticesGrid = $("#verticesGrid");
const groupsGrid = $("#groupsGrid");
const levelsGrid = $("#levelsGrid");
const edgesGrid = $("#edgesGrid");

function updateGrid(grid, item) {
    const groups = groupsGrid.jsGrid("option", "data");
    console.log(groups);

    let new_levels = [];
    for (const group of groups) {
        console.log(group);
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

    levelsGrid.jsGrid("option", "data", new_levels);
    console.log(new_levels);
}

verticesGrid.jsGrid({
    width: "100%",
    height: "400px",

    inserting: true,
    editing: true,
    sorting: true,
    paging: false,

    data: vertices,

    fields: [
        { name: "id", title: "ID", type: "number", width: 50, validate: "required" },
        { name: "name", title: "Name", type: "text", width: 150, validate: "required" },
        { type: "control" }
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
        { name: "id", title: "ID", type: "text", width: 50, validate: "required" },
        { name: "name", title: "Name", type: "text", width: 150, validate: "required" },
        { name: "levels", title: "Number of levels", type: "number", width: 50, validate: "required" },
        { type: "control" }
    ]
});


levelsGrid.jsGrid({
    width: "100%",
    height: "400px",

    inserting: false,
    editing: true,
    sorting: true,
    paging: false,

    data: levels;

    fields: [
        { name: "gid", title: "Group ID", type: "text", width: 50, readOnly: true },
        { name: "level", title: "Level", type: "text", width: 50, readOnly: true },
        { name: "name", title: "Name", type: "text", width: 150, validate: "required" },
        { name: "cost", title: "Cost", type: "number", width: 50, validate: "required" },
        { name: "ind_cost", title: "Indirect cost", type: "number", width: 50, validate: "required" },
        { name: "flow", title: "Flow", type: "number", width: 50, validate: "required" },
        { type: "control", deleteButton: false }
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
