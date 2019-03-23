import math
import sys
from collections import defaultdict, OrderedDict
from typing import List, Tuple, Dict

import networkx
from bokeh.models import Arrow, Circle, HoverTool, TapTool, BoxSelectTool, NodesAndLinkedEdges, \
    EdgesAndLinkedNodes, VeeHead, MultiLine
# noinspection PyProtectedMember
from bokeh.models.graphs import from_networkx
from bokeh.plotting import figure, curdoc
from bokeh.palettes import Spectral8

from data import sample


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


def tree_layout(graph_data, root, width=1.5, vert_gap=0.5, vert_loc=0, xcenter=0):
    """g: the graph
       root: the root node of current branch
       width: horizontal space allocated for this branch - avoids overlap with other branches
       vert_gap: gap between levels of hierarchy
       vert_loc: vertical location of root
       xcenter: horizontal location of root
    """

    _, depth = bfs(graph_data, root)

    def h_recur(local_root, local_width, local_vert_loc, local_xcenter,
                pos=None, parsed=None, level=0):
        if parsed is None:
            parsed = []
        if local_root not in parsed:
            parsed.append(local_root)
            if pos is None:
                pos = {local_root: (local_xcenter, local_vert_loc)}
            else:
                pos[local_root] = (local_xcenter, local_vert_loc)

            neighbors = graph_data.neighbors(local_root)
            neighbors = list(filter(lambda x: depth[x] == level+1, neighbors))

            if len(neighbors) != 0:
                dx = local_width / len(neighbors)
                nextx = local_xcenter - local_width / 2 - dx / 2
                for neighbor in neighbors:
                    nextx += dx
                    # noinspection PyTypeChecker
                    pos = h_recur(neighbor, local_width=dx,
                                  local_vert_loc=local_vert_loc - vert_gap, local_xcenter=nextx, pos=pos,
                                  parsed=parsed, level=level+1)
        return pos

    return h_recur(root, local_width=width, local_vert_loc=vert_loc, local_xcenter=xcenter)


CIRCLE_SIZE = 15
ARROW_PADDING = CIRCLE_SIZE / 670
BEZIER_CONTROL = 0.1
BEZIER_STEPS = 20


def main():
    # Create a plot
    plot = figure(title="Attack Vector Graph", plot_width=800, plot_height=800, x_range=(-1.1, 1.1), y_range=(-2.1, 0.1))
    plot.add_tools(HoverTool(tooltips=None), TapTool(), BoxSelectTool())

    # Create a layout
    graph_data = sample()
    n = max(graph_data.nodes) + 1
    levels, depth = bfs(graph_data, 0)

    # Create a bokeh graph
    layout = tree_layout(graph_data, 0)
    graph = from_networkx(graph_data, layout)

    # Add colours and glyphs
    graph.node_renderer.data_source.add([Spectral8[0], *(Spectral8[3] for _ in range(n - 2)), Spectral8[7]], 'color')
    graph.node_renderer.glyph = Circle(size=CIRCLE_SIZE, fill_color='color')
    graph.node_renderer.selection_glyph = Circle(size=CIRCLE_SIZE, fill_color=Spectral8[5])
    graph.node_renderer.hover_glyph = Circle(size=CIRCLE_SIZE, fill_color=Spectral8[4])

    graph.edge_renderer.glyph = MultiLine(line_color="#000000", line_alpha=0.8, line_width=3)
    graph.edge_renderer.selection_glyph = MultiLine(line_color=Spectral8[4], line_width=3)
    graph.edge_renderer.hover_glyph = MultiLine(line_color=Spectral8[1], line_width=3)

    graph.selection_policy = NodesAndLinkedEdges()
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

    def quadratic_bezier(t: float, p0: Tuple[float, float], p1: Tuple[float, float],
                         p2: Tuple[float, float]) -> Tuple[float, float]:
        # https://en.wikipedia.org/wiki/B%C3%A9zier_curve#Quadratic_B%C3%A9zier_curves
        tx = (1 - t) * ((1 - t) * p0[0] + t * p1[0]) + t * ((1 - t) * p1[0] + t * p2[0])
        ty = (1 - t) * ((1 - t) * p0[1] + t * p1[1]) + t * ((1 - t) * p1[1] + t * p2[1])
        return tx, ty

    for x, y in bokeh_edges:
        start_x, start_y = graph.layout_provider.graph_layout[x]
        end_x, end_y = graph.layout_provider.graph_layout[y]
        if multiplicity[x][y] == 1 and \
                (depth[x] != depth[y] or abs(levels[depth[x]].index(x)-levels[depth[y]].index(y)) != 1):
            xs.append((start_x, end_x))
            ys.append((start_y, end_y))
            graph_data[x][y][0]['edge_curve'] = -1
            continue

        angle = math.atan2(start_x - end_x, start_y - end_y)
        distance = math.hypot(start_x - end_x, start_y - end_y) // 0.4
        for z in range(multiplicity[x][y]):
            graph_data[x][y][z]['edge_curve'] = z

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

    graph.edge_renderer.data_source.data['xs'] = xs
    graph.edge_renderer.data_source.data['ys'] = ys

    # Draw arrows
    # Bokeh does not support drawing directed graphs, hence we add arrows manually.
    for x in graph_data:
        for y in graph_data[x]:
            for z in graph_data[x][y]:
                start_x, start_y = graph.layout_provider.graph_layout[x]
                end_x_orig, end_y_orig = graph.layout_provider.graph_layout[y]
                angle = math.atan2(start_x - end_x_orig, start_y - end_y_orig)
                distance = math.hypot(start_x - end_x_orig, start_y - end_y_orig) // 0.4

                # Account for the vertex glyph…
                end_x = end_x_orig + ARROW_PADDING * math.sin(angle)
                end_y = end_y_orig + ARROW_PADDING * math.cos(angle)

                # …and for curved edges
                if graph_data[x][y][z]['edge_curve'] != -1:
                    mid_x = (start_x + end_x) / 2 + BEZIER_CONTROL * distance * math.cos(angle) * \
                            (1 if z % 2 else -1) * (z // 2 + 1)
                    mid_y = (start_y + end_y) / 2 + BEZIER_CONTROL * distance * math.sin(angle) * \
                            (1 if z % 2 else -1) * (z // 2 + 1)

                    end_x, end_y = quadratic_bezier(0.995+0.001*distance, (start_x, start_y), (mid_x, mid_y), (end_x, end_y))
                else:
                    mid_x, mid_y = start_x, start_y
                """sin = math.cos(graph_data[x][y][z]['edge_curve_angle'])
                cos = math.cos(graph_data[x][y][z]['edge_curve_angle'])

                end_x = (end_x - end_x_orig) * cos - (end_y - end_y_orig) * sin + end_x_orig
                end_y = (end_x - end_x_orig) * sin + (end_y - end_y_orig) * cos + end_y_orig"""

                # start_x = (start_x - end_x) * cos - (start_y - end_y) * sin + end_x
                # start_y = (start_x - end_x) * sin + (start_y - end_y) * cos + end_y

                plot.add_layout(Arrow(end=VeeHead(fill_color="orange", size=10),
                                      x_start=mid_x, y_start=mid_y, x_end=end_x, y_end=end_y, line_alpha=0))
    # Add the graph to the plot and the plot to the doc
    plot.renderers.append(graph)
    curdoc().add_root(plot)


if __name__.startswith("bk_"):
    main()
