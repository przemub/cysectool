import networkx

from controls import Sample


def sample() -> networkx.MultiDiGraph:
    g = networkx.MultiDiGraph()

    for arc in Sample.arcs:
        g.add_edge(arc[0], arc[1], multiplicity=arc[2])

    return g
