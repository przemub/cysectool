import abc
from typing import Tuple, Dict, NamedTuple, Sequence, Set, Mapping

import networkx


class Control(NamedTuple):
    """
    Represents a control.
    Attributes:
        id - category id (like Sc, A1, etc.)
        level - control level (from 0 upwards)
    """
    id: str
    level: int


class Edge(NamedTuple):
    """
    Represents an edge in a graph.
    """
    source: int
    target: int
    multiplicity: int


class Vulnerability(NamedTuple):
    """
    Represents a vulnerability resulting in changing state.
    Attributes:
        name: str - human-readable name of the attack
        controls: Set[control] - set of controls that change the probability of exploiting the vulnerability
    """
    name: str
    controls: Set[Control]


class Model(metaclass=abc.ABCMeta):
    """
    Superclass documenting properties and methods required to define a model.

    Attributes (controls):
        controls: List[Control] - controls available as keys to control_subcategories
        control_categories: List[Tuple[str, str, int]] - specification of categories (tuples of category id,
                                                         category name and number of levels)
        control_subcategories: Mapping[Control, str] - mapping of controls to their descriptions
        edges: Sequence[Edge] - all edges in the graph
        vulnerabilities: Mapping[Edge, Vulnerability - mapping of vulnerabilities to the edges
    """

    # Defining controls
    controls: Sequence[Control]
    control_categories: Sequence[Tuple[str, str, int]]
    control_subcategories: Mapping[Control, str]

    # Defining a graph
    n: int
    edges: Sequence[Edge]
    vertices: Sequence[str]
    vulnerabilities: Mapping[Edge, Vulnerability]

    # Simulation results
    edge_flow: Mapping[Edge, float]
    vertex_flow: Mapping[int, float]
    tree_flow: Mapping[Edge, float]

    @abc.abstractmethod
    def flow(self, control: Control, edge: Edge) -> float:
        """
        Returns surviving flow (0.0-1.0) after applying a control to the edge.
        """
        return 1.0

    @abc.abstractmethod
    def default_flow(self, edge: Edge) -> float:
        """
        Returns default (with no controls applied) flow (0.0-1.0) on the edge.
        """
        return 1.0

    def reflow(self, controls: Sequence[Control]) -> Mapping[Edge, float]:
        """
        Recalculates the flow, saves it in cached_flow and returns it.
        Assumes that the graph is a directed acyclic graph, sorts it topologically and calculates the maximum flow.
        """
        edge_flow = {}
        for edge in self.edges:
            flow = self.default_flow(edge)
            for control in controls:
                if control not in self.vulnerabilities[edge].controls:
                    continue
                flow *= self.flow(control, edge)
            edge_flow[edge] = flow
        self.edge_flow = edge_flow

        topological_sort = list(networkx.topological_sort(self.graph))
        vertex_flow = {topological_sort[0]: 1}
        for vertex in topological_sort[1:]:
            flow = 0
            for edge in self.graph.in_edges(vertex, data="multiplicity"):
                flow = max(flow, edge_flow[edge] * vertex_flow[edge[0]])
            vertex_flow[vertex] = flow
        self.vertex_flow = vertex_flow

        tree_flow = {}
        for edge in self.edges:
            tree_flow[edge] = vertex_flow[edge[0]] * edge_flow[edge]
        self.tree_flow = tree_flow

        return tree_flow

    def to_networkx(self) -> networkx.MultiDiGraph:
        g = networkx.MultiDiGraph()

        for edge in self.edges:
            possible_controls = ", ".join(set(control.id for control in self.vulnerabilities[edge].controls))

            g.add_edge(edge.source, edge.target,
                       multiplicity=edge.multiplicity, vuln_name=self.vulnerabilities[edge].name,
                       from_state=self.vertices[edge.source], to_state=self.vertices[edge.target],
                       possible_controls=possible_controls)

        return g

    def __init__(self):
        self.control_subcategories_inverted: Dict[str, Control] = {v: k for k, v in self.control_subcategories.items()}
        self.graph: networkx.MultiDiGraph = self.to_networkx()
        self.reflow([])
