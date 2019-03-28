import math
import sys
from collections import defaultdict, OrderedDict

import colorcet
import networkx
from bokeh.layouts import widgetbox, row
from bokeh.models import Arrow, HoverTool, TapTool, BoxSelectTool, EdgesAndLinkedNodes, VeeHead, MultiLine, \
    Select, LogColorMapper, ColorBar, FixedTicker, CustomJS, Rect
# noinspection PyProtectedMember
from bokeh.models.graphs import from_networkx
from bokeh.palettes import Spectral8
from bokeh.plotting import figure, curdoc
from typing import List, Tuple, Dict

from src.controls import Sample
from src.data import Edge, Control


def bfs(graph: networkx.Graph, start: int) -> Tuple[Tuple[List[int], ...], List[int]]:
    depth = [-1 for _ in range(max(graph.nodes) + 1)]

    queue = [(start, 0)]
    while len(queue) > 0:
        x, cur_depth = queue[0]
        del queue[0]

        if depth[x] != -1:
            continue
        depth[x] = cur_depth

        for y in graph[x]:
            queue.append((y, cur_depth + 1))

    if -1 in depth:
        print("The graph is not connected!")
        sys.exit(-1)

    result = tuple(list() for _ in range(max(depth) + 1))
    for x, x_depth in enumerate(depth):
        result[x_depth].append(x)

    return result, depth


def tree_layout(graph_data: networkx.DiGraph, root: int, depth: List[int], width: float = 1.5, vert_gap: float = 0.5,
                vert_loc: float = 0, x_center: float = 0):
    """graph_data: the networkx graph
       root: the root node of current branch
       depth: tree layers
       width: horizontal space allocated for this branch - avoids overlap with other branches
       vert_gap: gap between levels of hierarchy
       vert_loc: vertical location of root
       x_center: horizontal location of root
    """

    def h_recur(local_root, local_width, local_vert_loc, local_x_center,
                pos=None, parsed=None, level=0):
        if parsed is None:
            parsed = []
        if local_root not in parsed:
            parsed.append(local_root)
            if pos is None:
                pos = {local_root: (local_x_center, local_vert_loc)}
            else:
                pos[local_root] = (local_x_center, local_vert_loc)

            neighbors = graph_data.neighbors(local_root)
            neighbors = list(filter(lambda x: depth[x] == level + 1, neighbors))

            if len(neighbors) != 0:
                dx = local_width / len(neighbors)
                next_x = local_x_center - local_width / 2 - dx / 2
                for neighbor in neighbors:
                    next_x += dx
                    pos = h_recur(neighbor, local_width=dx, local_vert_loc=local_vert_loc - vert_gap,
                                  local_x_center=next_x, pos=pos, parsed=parsed, level=level + 1)
        return pos

    return h_recur(root, local_width=width, local_vert_loc=vert_loc, local_x_center=x_center)


CIRCLE_SIZE = 15
ARROW_PADDING = CIRCLE_SIZE / 670
BEZIER_CONTROL = 0.1
BEZIER_STEPS = 20
PALETTE: List[str] = colorcet.b_diverging_gkr_60_10_c40
BAR_MAX, BAR_MIN = 0, -3  # 10**value
GLYPH_WIDTH: float = 0.25  # in pixels
GLYPH_HEIGHT: float = 0.05  # in axis units


def map_color(value: float) -> str:
    """
    Bug in Bokeh makes log mapper work as a linear mapper when used as a data column.
    In the meantime, log mapper is implemented here for this use.
    """

    log = math.log10(value)
    if log > BAR_MAX:
        log = BAR_MAX
    if log < BAR_MIN:
        log = BAR_MIN

    log -= BAR_MIN
    threshold = int((log / int(BAR_MAX - BAR_MIN)) * 255)

    return PALETTE[threshold]


def typescript(name: str) -> CustomJS:
    return CustomJS(code="%s();" % name)


def main():
    # Create a plot
    plot = figure(title="Attack Vector Graph", plot_width=800, plot_height=800,
                  x_range=(-1.1, 1.1), y_range=(-2.1, 0.1))

    hover = HoverTool()
    hover.tooltips = [
        ("flow", "@flow{0.0[0000]}"),
        ("flow reduction", "@edge_flow{0.0[0000]}"),
        ("vulnerability", "@vuln_name"),
        ("controls", "@possible_controls")
    ]

    tap = TapTool()
    tap.callback = typescript("on_tap")

    plot.add_tools(hover, tap, BoxSelectTool())

    # Import a model and a graph
    model = Sample()
    graph_data = model.graph
    n = max(graph_data.nodes) + 1
    levels, depth = bfs(graph_data, 0)

    # Create a bokeh graph
    layout = tree_layout(graph_data, 0, depth)
    graph = from_networkx(graph_data, layout)

    # Add colours and glyphs
    graph.node_renderer.data_source.add([Spectral8[0], *(Spectral8[3] for _ in range(n - 2)), Spectral8[7]], 'color')
    graph.node_renderer.glyph = Rect(height=GLYPH_HEIGHT, width=GLYPH_WIDTH, fill_color='color')
    graph.node_renderer.selection_glyph = Rect(height=GLYPH_HEIGHT, width=GLYPH_WIDTH, fill_color=Spectral8[5])
    graph.node_renderer.hover_glyph = Rect(height=GLYPH_HEIGHT, width=GLYPH_WIDTH, fill_color=Spectral8[4])

    mapper = LogColorMapper(palette=PALETTE, low=10 ** BAR_MIN, high=10 ** BAR_MAX)
    graph.edge_renderer.glyph = MultiLine(line_color='color',
                                          line_alpha=0.8, line_width=3)
    graph.edge_renderer.selection_glyph = MultiLine(line_color=Spectral8[4], line_width=3)
    graph.edge_renderer.hover_glyph = MultiLine(line_color=Spectral8[1], line_width=3)

    graph.selection_policy = EdgesAndLinkedNodes()
    graph.inspection_policy = EdgesAndLinkedNodes()

    # Drawing edges
    # Support drawing 1) multiple edges, 3) edges circumventing vertices
    multiplicity = defaultdict(lambda: defaultdict(int))
    for x in graph_data:
        for y in graph_data[x]:
            for _ in graph_data[x][y]:
                multiplicity[x][y] += 1

    xs, ys = [], []
    bokeh_edges = graph.edge_renderer.data_source.data
    bokeh_edges = list(OrderedDict.fromkeys(zip(bokeh_edges['start'], bokeh_edges['end'])))

    def quadratic_bezier(step: float, p0: Tuple[float, float], p1: Tuple[float, float],
                         p2: Tuple[float, float]) -> Tuple[float, float]:
        # https://en.wikipedia.org/wiki/B%C3%A9zier_curve#Quadratic_B%C3%A9zier_curves
        tx = (1 - step) * ((1 - step) * p0[0] + step * p1[0]) + step * ((1 - step) * p1[0] + step * p2[0])
        ty = (1 - step) * ((1 - step) * p0[1] + step * p1[1]) + step * ((1 - step) * p1[1] + step * p2[1])
        return tx, ty

    for x, y in bokeh_edges:
        if multiplicity[x][y] == 1 and \
                (depth[x] != depth[y] or abs(levels[depth[x]].index(x) - levels[depth[y]].index(y)) != 1):
            cur_xs = []
            cur_ys = []

            start_x, start_y = graph.layout_provider.graph_layout[x]
            end_x, end_y = graph.layout_provider.graph_layout[y]

            # Account for the glyph
            if start_y > end_y:
                start_y -= GLYPH_HEIGHT/2
                end_y += GLYPH_HEIGHT/2
            elif start_y < end_y:
                start_y += GLYPH_HEIGHT/2
                end_y -= GLYPH_HEIGHT/2
            elif start_x < end_x:
                start_x += GLYPH_WIDTH/2
                end_x -= GLYPH_WIDTH/2
            elif start_x > end_x:
                start_x -= GLYPH_WIDTH/2
                end_x += GLYPH_WIDTH/2

            # Generate multiple points along the line so HoverTool can display close to the mouse,
            # not next to an end-point
            for i in range(BEZIER_STEPS + 1):
                t = i * (1 / BEZIER_STEPS)
                bx, by = quadratic_bezier(t, (start_x, start_y), (start_x, start_y), (end_x, end_y))
                cur_xs.append(bx)
                cur_ys.append(by)
            xs.append(cur_xs)
            ys.append(cur_ys)

            graph_data[x][y][0]['edge_ends'] = (start_x, end_x, start_y, end_y)
            graph_data[x][y][0]['edge_curve'] = -1
            continue
        for z in range(multiplicity[x][y]):
            start_x, start_y = graph.layout_provider.graph_layout[x]
            end_x, end_y = graph.layout_provider.graph_layout[y]
            angle = math.atan2(start_x - end_x, start_y - end_y)
            distance = math.hypot(start_x - end_x, start_y - end_y) // 0.4

            # Account for the glyph
            if start_y > end_y:
                start_y -= GLYPH_HEIGHT/2
                end_y += GLYPH_HEIGHT/2
            elif start_y < end_y:
                start_y += GLYPH_HEIGHT/2
                end_y -= GLYPH_HEIGHT/2
            else:
                start_y -= GLYPH_HEIGHT/2
                end_y -= GLYPH_HEIGHT/2

            mid_x = (start_x + end_x) / 2 + BEZIER_CONTROL * distance * math.cos(angle) * \
                    (1 if z % 2 else -1) * (z // 2 + 1)
            mid_y = (start_y + end_y) / 2 + BEZIER_CONTROL * distance * math.sin(angle) * \
                    (1 if z % 2 else -1) * (z // 2 + 1)

            cur_xs = []
            cur_ys = []
            for i in range(BEZIER_STEPS + 1):
                t = i * (1 / BEZIER_STEPS)
                bx, by = quadratic_bezier(t, (start_x, start_y), (mid_x, mid_y), (end_x, end_y))
                cur_xs.append(bx)
                cur_ys.append(by)

            xs.append(cur_xs)
            ys.append(cur_ys)

            graph_data[x][y][z]['edge_ends'] = (start_x, end_x, start_y, end_y)
            graph_data[x][y][z]['edge_curve'] = z

    graph.edge_renderer.data_source.data['xs'] = xs
    graph.edge_renderer.data_source.data['ys'] = ys

    # Draw arrows
    # Bokeh does not support drawing directed graphs, hence we add arrows manually.

    for x in graph_data:
        for y in graph_data[x]:
            for z in graph_data[x][y]:
                start_x, end_x, start_y, end_y = graph_data[x][y][z]['edge_ends']

                angle = math.atan2(start_x - end_x, start_y - end_y)
                distance = math.hypot(start_x - end_x, start_y - end_y) // 0.4

                # Account for the curves
                if graph_data[x][y][z]['edge_curve'] > -1:
                    mid_x = (start_x + end_x) / 2 + BEZIER_CONTROL * distance * math.cos(angle) * \
                            (1 if z % 2 else -1) * (z // 2 + 1)
                    mid_y = (start_y + end_y) / 2 + BEZIER_CONTROL * distance * math.sin(angle) * \
                            (1 if z % 2 else -1) * (z // 2 + 1)
                else:
                    mid_x, mid_y = start_x, start_y

                plot.add_layout(Arrow(end=VeeHead(fill_color="orange", size=10),
                                      x_start=mid_x, y_start=mid_y, x_end=end_x, y_end=end_y, line_alpha=0))

    # Add the graph to the plot and the plot to the doc
    plot.renderers.append(graph)

    # Controls
    control_levels: Dict[str, int] = {category: 0 for category in model.control_categories.keys()}

    def flow_to_bokeh():
        flow = []
        edge_flow = []
        color = []
        for _x, _y in bokeh_edges:
            for _z in range(multiplicity[_x][_y]):
                flow.append(model.tree_flow[Edge(_x, _y, _z)])
                edge_flow.append(model.edge_flow[Edge(_x, _y, _z)])
                color.append(map_color(flow[-1]))

        graph.edge_renderer.data_source.data['flow'] = flow
        graph.edge_renderer.data_source.data['edge_flow'] = edge_flow
        graph.edge_renderer.data_source.data['color'] = color

    flow_to_bokeh()

    def change_security(category: str):
        def _change(_attr, _old, new):
            if new == "None":
                control_levels[category] = 0
            else:
                control_levels[category] = int(new[:new.find(")")])

            print(control_levels)
            model.reflow([model.control_subcategories[item[0]][item[1]-1] for item in control_levels.items() if item[1] > 0])
            flow_to_bokeh()

        return _change

    selects = []
    for category_id, category in model.control_categories.items():
        select = Select(title=category[0], value="None", options=["None"] +
                                                                 ["%d) " % level.level + level.level_name
                                                                  for level in model.control_subcategories[category_id]])
        select.on_change('value', change_security(category_id))
        selects.append(select)
    box = widgetbox(selects, width=380)

    color_bar = ColorBar(color_mapper=mapper, orientation='vertical',
                         location=(0, 0), ticker=FixedTicker(ticks=[1, 0.6, 0.4, 0.2, 0.1, 0.05, 0.01]))
    plot.add_layout(color_bar, 'right')

    # Add labels
    plot.text(x=[graph.layout_provider.graph_layout[v][0] for v in range(n)],
              y=[graph.layout_provider.graph_layout[v][1] for v in range(n)],
              text=model.vertices,
              text_baseline="middle", text_align="center",
              text_font_size="0.7em")

    # Layout
    main_row = row([plot, box])
    curdoc().add_root(main_row)
