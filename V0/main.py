from os.path import abspath
import cyopt_pulp as cs
from math import pi
# import numpy as np
import pandas as pd
# from pprint import pprint

# bokeh imports
from bokeh.plotting import Figure
from bokeh.models import ColumnDataSource, HBox, HoverTool, TapTool, Circle, VBox, CustomJS, CategoricalTickFormatter
from bokeh.models.widgets import RadioButtonGroup, Slider, TableColumn, DataTable, Toggle
from bokeh.io import curdoc
from bokeh.models.widgets.markups import Paragraph

# setting up some useful mappings:
Threats = {0:'passive', 1:'reactive'}
Combinations = {0:'additive', 1:'multiplicative', 2:'best-of'}
x_labelz = [str(i) for i in range(1,38)]

# # # # # # # # # #
# PARETO-FIGURE #
# # # # # # # # # #

# set up the data source for the pareto figure:
pareto_source = ColumnDataSource(
    data=dict(
        IndirCost = [],
        PassiveSecCost = [],
        DirCost = [],
        y = [],
        ReactiveSecCost = [],
        )
    )
pareto_hover = HoverTool(
    line_policy = "nearest",
    point_policy = "snap_to_data",
        tooltips = [
            ("Organisational Burden (x)", "@IndirCost"),
            ("Passive Sec. Damage", "@PassiveSecCost"),
            ("Reactive Sec. Damage","@ReactiveSecCost"),
            ("Direct Cost", "@DirCost"),        
        ]
    )
pareto_tap = TapTool()

# set up (create and style) the pareto figure:
Pareto_fig = Figure(
    plot_height = 450,
    plot_width = 450,
    tools = [pareto_hover,pareto_tap],
    title = "Pareto-Optimal Plans",
    y_range = (0, 9), 
    x_range = (0, 7),
    x_axis_label = 'organisational burden (Indirect cost)',
    y_axis_label = 'security damage')
Pareto_fig.title.text_color = "olive"
Pareto_fig.title.text_font = "Palatino"
Pareto_fig.axis.axis_label_text_font = "Palatino"
Pareto_fig.axis.axis_label_text_color = "indigo"
Pareto_fig.min_border = 25

# add the plot renderer for pareto-optimal plans to the Pareto_fig:
pareto_circle = Pareto_fig.circle(x='IndirCost', y='y', size=9, source=pareto_source,\
                                    legend="", fill_color="navy", alpha=0.5, name="best_plans")
#
## custom coloring of the active plan:
selected_plan = Circle(fill_alpha=1.0, fill_color="red", line_color="firebrick", line_width=3)
nonselected_plans= Circle(fill_alpha=0.4,  fill_color="navy", line_color="none")
#pareto_circle.selection_glyph = selected_plan
#pareto_circle.nonselection_glyph = nonselected_plans

# # # # # # # # # # # # # # #
#  PASSIVE-PROFILE-FIGURE  #
# # # # # # # # # # # # # # #

vul_names = pd.read_table(abspath('data/vulnerabilities.txt'), sep=',', header=0, usecols=['name'])
Passive_fig = Figure(
    plot_height = 200,
    plot_width = 600,
    tools = "save,reset",
    title = "Passive Vulnerability Profile",
    x_range = x_labelz,
    y_range = (0, 0.5),
    x_axis_label = 'Vulnerability ID',
    y_axis_label = 'Exp. Impact')
Passive_fig.title.text_color = "olive"
Passive_fig.title.text_font = "Palatino"
Passive_fig.axis.axis_label_text_font = "Palatino"
Passive_fig.axis.axis_label_text_color = "indigo"
Passive_fig.xgrid.grid_line_alpha = 0.0
Passive_fig.ygrid.grid_line_alpha = 0.5
Passive_fig.min_border = 25
Passive_fig.axis[0].major_label_orientation = pi/3
##Passive_fig.axis[0].major_label_text_font_size='10'
Passive_fig.axis[0].formatter = CategoricalTickFormatter()

# add the plot renderer for passive profile figure:
passive_profiles_fountain = ColumnDataSource(data = dict(y=[], h=[]))
initilizer_raw_data = cs.sectool("additive", "passive", Budget=0, Indir_Costs_Max=0.25)
initial_passive_unmitigated = initilizer_raw_data["PassiveVulProfile"][0]
passive_profile_source = ColumnDataSource(
    data = dict(
        xs = x_labelz,
        vulnerability_names = vul_names,
        ys = initial_passive_unmitigated*0.5,
        heights = initial_passive_unmitigated,
        backgound_ys = initial_passive_unmitigated*0.5,
        background_heights = initial_passive_unmitigated,
        )
    )
passive_bar_background = Passive_fig.rect(x = 'xs', y ='backgound_ys', height = 'background_heights',\
                                        source = passive_profile_source, width = 0.5, color = "grey",\
                                        line_color = 'grey',\
                                        line_alpha=0.2, alpha=0.2)
passive_bar = Passive_fig.rect(x = 'xs', y = 'ys', height = 'heights',\
                                source = passive_profile_source,\
                                width = 0.5, color = 'red', line_color = 'red')
passive_profile_hover = HoverTool(
    renderers = [passive_bar_background],
    tooltips = [
        ("Vulnerability", "@vulnerability_names"),
        ("Unmitigated (leftover) Impact (red)", "@heights"),
        ("Potential Impact (grey)", "@background_heights"),
        ]
    )
##passive_profile_BG_hover = HoverTool(
##    renderers=[passive_bar_background],
##    tooltips=[
##        ("Vulnerability (x)", "@vulnerability_name"),
##        ]
##    )
Passive_fig.add_tools(passive_profile_hover)
##Passive_fig.add_tools(passive_profile_BG_hover)

# # # # # # # # # # # # # # #
#  REACTIVE-PROFILE-FIGURE  #
# # # # # # # # # # # # # # #

Reactive_fig = Figure(
    plot_height = 200,
    plot_width = 600,
    tools = "save,reset",
    title = "Reactive Vulnerability Profile",
    y_range = (0, 10),
    x_range = x_labelz,
    x_axis_label = 'Vulnerability ID',
    y_axis_label = 'Exp. Impact')
Reactive_fig.title.text_color = "olive"
Reactive_fig.title.text_font = "Palatino"
Reactive_fig.axis.axis_label_text_font = "Palatino"
Reactive_fig.axis.axis_label_text_color = "indigo"
Reactive_fig.xgrid.grid_line_alpha = 0.0
Reactive_fig.ygrid.grid_line_alpha = 0.5
Reactive_fig.min_border = 25

# add the plot renderer for REACTIVE profile figure:
reactive_profiles_fountain = ColumnDataSource(data = dict(y = [], h = []))
initial_reactive_unmitigated = initilizer_raw_data["ReactiveVulProfile"][0]
reactive_profile_source = ColumnDataSource(
    data=dict(
        vulnerability_names = vul_names,
        xs = x_labelz,
        ys = initial_reactive_unmitigated*0.5,
        heights = initial_reactive_unmitigated,
        background_ys = initial_reactive_unmitigated*0.5,
        background_hs = initial_reactive_unmitigated,
        )
    )
reactive_bar_background = Reactive_fig.rect(x = 'xs', y = 'background_ys', height = 'background_hs', \
                                            source = reactive_profile_source, width = 0.5, color = "grey",\
                                            line_alpha = 0.2, alpha = 0.2)
reactive_bar = Reactive_fig.rect(x = 'xs', y = 'ys', height = 'heights', source = reactive_profile_source,\
                                    width = 0.5, color = "red")
reactive_profile_hover = HoverTool(
    renderers = [reactive_bar_background],
    tooltips = [
        ("Vulnerability", "@vulnerability_names"),
        ("Unmitigated (leftover) Impact (red)", "@heights"),
        ("Potential Impact (grey)", "@background_hs"),
        ]
    )
Reactive_fig.add_tools(reactive_profile_hover)
Reactive_fig.axis[0].major_label_orientation = pi/3

###Reactive_fig.axis[0].major_label_text_font_size='10'

# # # # # # # # # # # # # # # # # #
#   SELECTED OPTIMAL PLAN TABLE   #
# # # # # # # # # # # # # # # # # #

selected_controls_fountain = ColumnDataSource(data = dict(controls = []))
controls_table_all = pd.read_table(abspath('data/cysectable.txt'), sep = ',', header = 0)
# control_to_index_source = ColumnDataSource(data = dict(zip(controls_table_all.index, range(len(controls_table_all.index)))))
controls_table_all_source = ColumnDataSource(data = controls_table_all.to_dict('list'))

#pprint(controls_table_all_source.data)
selected_controls_table_source = ColumnDataSource(data = {k:[] for k in controls_table_all.columns.values})
table_columns = [
        TableColumn(field = "Control", title = "Control", width = 300),
        TableColumn(field = "Level", title = "Implementation Level", width = 180),
        TableColumn(field = "Level_of_Max", title = "Level No./Max No.", width = 120),
    ]
selected_plan_table = DataTable(source = selected_controls_table_source, columns = table_columns, width = 600)
# selected_plan_table.disabled = True
selected_plan_table.row_headers = False
selected_plan_table.columns[2].formatter.text_align = 'center'


# # # # # # # 
#  WIDGETS  #
# # # # # # # 

# create a radio-button group for threat type
threat_type_radio_button_group = RadioButtonGroup(
        labels = ["Passive", "Reactive"], active=0, width=280)
threat_type_radio_button_group_text = Paragraph(text = 'Threat Type:', width=280)

# create a radio-button group for combination type
combination_type_radio_button_group = RadioButtonGroup(
        labels = ["Additive", "Multiplicative", "Best-of"], active = 0, width=280)
combination_type_radio_button_group_text = Paragraph(text = 'Efficacy Combination Type:', width=280)

# create a slider for the budget
budget_slider = Slider(start = 0, end = 15, value = 5, step = 0.25, title = "Cybersec Budget",  width=280)
budget_slider_text = Paragraph(text = 'Total Cybersec Budget:', width=280)


# # # # # # # # # # # # # # # #
#   MAIN (COMPUTE) CALL-BACK  #
# # # # # # # # # # # # # # # #

def update_everything(attrname, old, new):
    # signalling wait!
    Pareto_fig.title.text = 'Please wait, computing...!'
    Pareto_fig.background_fill_color = 'grey'
    Pareto_fig.background_fill_alpha = 0.2
    Passive_fig.title.text = 'Please wait, computing...!'
    Passive_fig.background_fill_color = 'grey'
    Passive_fig.background_fill_alpha = 0.2
    Reactive_fig.title.text = 'Please wait, computing...!'    
    Reactive_fig.background_fill_color = 'grey'
    Reactive_fig.background_fill_alpha = 0.2     
    # reading the inputs:
    selected_threat = Threats[threat_type_radio_button_group.active]
    selected_combination = Combinations[combination_type_radio_button_group.active]
    # computing the data by calling the optimization function:
    rawdata = cs.sectool(selected_combination, selected_threat, float(budget_slider.value))
    # signalling the end of wait!
    Pareto_fig.background_fill_color = 'white'
    Pareto_fig.background_fill_alpha = 1.0
    Pareto_fig.title.text = 'Pareto-Optimal Plans'
    Passive_fig.background_fill_color = 'white'
    Passive_fig.background_fill_alpha = 1.0
    Passive_fig.title.text = 'Passive Vulnerability Profile'
    Reactive_fig.background_fill_color = 'white'
    Reactive_fig.background_fill_alpha = 1.0
    Reactive_fig.title.text = 'Reactive Vulnerability Profile'     
    # updating the parteo plot
    pareto_source.data["DirCost"] = rawdata["DirectCost"]
    pareto_source.data["IndirCost"] = rawdata["IndirectCost"]
    pareto_source.data["PassiveSecCost"] = rawdata["PassiveSecCost"]
    pareto_source.data["ReactiveSecCost"] = rawdata["ReactiveSecCost"]
    if selected_threat == 'passive':
        pareto_source.data["y"] = rawdata["PassiveSecCost"]
    elif selected_threat == 'reactive':
        pareto_source.data["y"] = rawdata["ReactiveSecCost"]
    # updating the sources for the taptool interaction with the pareto plot:
    # 1- updating the source for passive vulnerability profile plot
    passive_profiles_fountain.data['h'] = rawdata["PassiveVulProfile"]  
    # 2- updating the reactive vulnerability profile plot
    reactive_profiles_fountain.data['h'] = rawdata["ReactiveVulProfile"]
    # 3- updating the sources for the table of controls:
    selected_controls_fountain.data['controls'] = rawdata["OptimalControls"]

compute_button = Toggle(label = "Compute", width=150)
compute_button.on_change('active', update_everything)


# # # # # # # # # # # #  
#   TAP-TOOL CALLBACK #
# # # # # # # # # # # #

pareto_tap.callback = CustomJS(args = dict(mytable = selected_plan_table,\
                                myrawsource = controls_table_all_source,\
                                mytablefountain = selected_controls_fountain,\
                                mypassivesource = passive_profile_source,\
                                mypassivefountain = passive_profiles_fountain,\
                                myreactivesource = reactive_profile_source,\
                                myreactivefountain = reactive_profiles_fountain),\
                                code="""
var selected_ind = cb_obj.get('selected')['1d'].indices;
if (selected_ind.length==1){
    //
    // UPDATING THE SELECTED CONTROLS TABLE
    var mytabledata = mytable.get('source').get('data');
    var mycontrols = mytablefountain.get('data')['controls'][selected_ind];
    var cols = mytable.get('source').get('column_names');
    var col;
    var control_index;
    var processed_col = [];
    var k = 0;
    for (var i=0; i<cols.length-1, col=cols[i]; ++i){
        for (var j = 0; j < mycontrols.length; ++j){
            while (myrawsource.get('data')['Row'][k] != mycontrols[j]){
                ++k;
            }
            processed_col.push(myrawsource.get('data')[col][k]);
        }
        k = 0;
        mytabledata[col] = processed_col;
        processed_col=[];
    }
    mytable.trigger('change');
    //
    // UPDATING THE PASSIVE VULNERABILITY PROFILE FIGURE:
    var mypassivedata = mypassivesource.get('data');
    mypassivedata['ys'] = mypassivefountain.get('data')['h'][selected_ind].map(function(x) {return x * 0.5;});
    mypassivedata['heights'] = mypassivefountain.get('data')['h'][selected_ind];
    mypassivesource.trigger('change');
    // 
    // UPDATING THE REACTIVE VULNERABILITY PROFILE FIGURE:
    var myreactivedata = myreactivesource.get('data');
    myreactivedata['ys'] = myreactivefountain.get('data')['h'][selected_ind].map(function(x) {return x * 0.5;});
    myreactivedata['heights'] = myreactivefountain.get('data')['h'][selected_ind];
    myreactivesource.trigger('change');
}
""")

## static info about the case study: 
#controls_table_source = ColumnDataSource(data=raw_table_data)
#controls_table_columns = [
#        TableColumn(field = "Control", title = "Control", width = 300),
#        TableColumn(field = "Level", title = "Implementation Level", width = 180),
#        TableColumn(field = "LevelofMax", title = "Level No./Max No.", width = 120),
#    ]
#controls_table = DataTable(source = controls_table_source, columns = controls_table_columns, width = 600)
#selected_plan_table.disabled=True
#controls_table.row_headers = False

# Set up layouts and add to document:
#test_button_form = WidgetBox(children = [])
threat_type_radio_button_group_with_text = VBox(children = [threat_type_radio_button_group_text,\
                                                    threat_type_radio_button_group])
combination_type_radio_button_group_with_text = VBox(children = [combination_type_radio_button_group_text,\
                                                    combination_type_radio_button_group])
budget_slider_with_text = VBox(children = [budget_slider_text, budget_slider])
inputs_layout = VBox(children = [HBox(children = [threat_type_radio_button_group_with_text,\
                                        combination_type_radio_button_group_with_text]),\
                                        HBox(children = [budget_slider, compute_button])])
#inputs_layout_2 = widgetbox(threat_type_radio_button_group, 
#                            combination_type_radio_button_group, 
#                            budget_slider, 
#                            compute_button, width=600)                                        
##inputs_panel=Panel(title='Inputs',child=inputs_layout)
##secondline_layout=HBox(children=[budget_slider,test_button_form],width=400)
##inputs_layout=HBox(children=[radioinputs,secondline_layout])
plan_layout = VBox(children = [Passive_fig, Reactive_fig, selected_plan_table])
left_layout = VBox(children = [inputs_layout, Pareto_fig])
all_layout = HBox(children = [left_layout, plan_layout])
##tab1 = Panel(child=all_layout, title="Interface")
##tab2 = Panel(child=controls_table, title="Controls")
##tabs = Tabs(tabs=[ tab1, tab2 ])
curdoc().title = 'MULTI-OBJECTIVE CYBERSEC PLANNER'
curdoc().add_root(all_layout)

