import math
from typing import Tuple, List

import colorcet
import networkx
from bokeh.models import CustomJS

BEZIER_STEPS = 200
BAR_MAX, BAR_MIN = 0, -3  # 10**value
GLYPH_WIDTH: float = 0.25  # in pixels
GLYPH_HEIGHT: float = 0.05  # in axis units
PALETTE: List[str] = colorcet.b_diverging_gkr_60_10_c40


def quadratic_bezier_curve(p0: Tuple[float, float], p1: Tuple[float, float],
                           p2: Tuple[float, float]) -> Tuple[List[float], List[float]]:
    def quadratic_bezier_step(step: float) -> Tuple[float, float]:
        # https://en.wikipedia.org/wiki/B%C3%A9zier_curve#Quadratic_B%C3%A9zier_curves
        tx = (1 - step) * ((1 - step) * p0[0] + step * p1[0]) + step * ((1 - step) * p1[0] + step * p2[0])
        ty = (1 - step) * ((1 - step) * p0[1] + step * p1[1]) + step * ((1 - step) * p1[1] + step * p2[1])
        return tx, ty

    curve_xs, curve_ys = [], []

    for i in range(BEZIER_STEPS + 1):
        t = i * (1 / BEZIER_STEPS)
        bx, by = quadratic_bezier_step(t)
        curve_xs.append(bx)
        curve_ys.append(by)

    return curve_xs, curve_ys


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
            root_local_width = max((local_width, (len(neighbors) + 1) * GLYPH_WIDTH))

            if len(neighbors) != 0:
                dx = root_local_width / len(neighbors)
                next_x = local_x_center - root_local_width / 2 - dx / 2
                for neighbor in neighbors:
                    next_x += dx
                    pos = h_recur(neighbor, local_width=dx, local_vert_loc=local_vert_loc - vert_gap,
                                  local_x_center=next_x, pos=pos, parsed=parsed, level=level + 1)
        return pos

    return h_recur(root, local_width=width, local_vert_loc=vert_loc, local_x_center=x_center)


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


def javascript(name: str, args=None, code_args="") -> CustomJS:
    if args is None:
        args = {}
    return CustomJS(code="%s(%s);" % (name, code_args), args=args)
