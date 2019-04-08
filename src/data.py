import abc
import json
from io import IOBase

import networkx
from abc import ABC
from typing import Tuple, NamedTuple, Sequence, Set, Mapping


class Control(NamedTuple):
    """
    Represents a control.
    Attributes:
        id - category id (like Sc, A1, etc.)
        level - control level (from 0 upwards)
        cost - cost in budget
        ind_cost - individual cost
        flow - default flow reduction coefficient.
               can be overridden in an edge.
    """
    id: str
    level: int
    level_name: str = ""
    cost: float = 0
    ind_cost: float = 0
    flow: float = 1

    def __hash__(self):
        val: int = pow(self.level, 1.7)
        for i, letter in enumerate(self.id):
            val *= pow(ord(letter), 2.1 + 0.47 * i)
            val = hash(val)
        return val

    def __eq__(self, other):
        return self.id == other.id and self.level == other.level

    def __ne__(self, other):
        return not self.__eq__(other)


class Vulnerability(NamedTuple):
    """
    Represents a vulnerability resulting in changing state.
    Attributes:
        name - human-readable name of the attack
        controls - set of controls that change the probability of exploiting the vulnerability
    """
    name: str
    controls: Set[Control]


class Edge(NamedTuple):
    """
    Represents an edge in a graph.
    Attributes:
        source, target: vertices connected by the edge
        multiplicity: id of the edge among multiple edges
        default_flow: flow when this edge has no applied controls
    """
    source: int
    target: int
    multiplicity: int
    default_flow: float = 1.0

    def __hash__(self):
        val = hash(pow(self.source + 1, 1.3) * pow(self.target + 1, 1.8) * pow(self.multiplicity + 1, 2.57))
        return val

    def __eq__(self, other):
        return self.source, self.target, self.multiplicity == other.source, other.target, other.multiplicity

    def __ne__(self, other):
        return not self.__eq__(other)


class Model(metaclass=abc.ABCMeta):
    """
    Superclass documenting properties required to define a model.

    Attributes (controls):
        control_categories: Mapping[str, Tuple[str, int] - specification of categories (mapping of category ids
                                                           on category full name and number of levels)
        control_subcategories: Mapping[str, Sequence[Control] - mapping of control ids to a sequence of their levels
        edges: Sequence[Edge] - all edges in the graph
        vulnerabilities: Mapping[Edge, Vulnerability - mapping of vulnerabilities to the edges
    """

    name: str

    # Defining controls
    control_categories: Mapping[str, Tuple[str, int]]
    control_subcategories: Mapping[str, Sequence[Control]]

    # Defining a graph
    n: int
    edges: Sequence[Edge]
    vertices: Sequence[str]
    vulnerabilities: Mapping[Edge, Vulnerability]

    # Simulation results
    edge_flow: Mapping[Edge, float]
    vertex_flow: Mapping[int, float]
    tree_flow: Mapping[Edge, float]

    @staticmethod
    def adjust_flows_by_factor(c: Sequence[Control], factor: float, max_value: float = 1):
        """
        Helper method that adjust flows in a list of controls to min(control.flow*factor, max_value).
        """
        result = []
        for control in c:
            obj = [*control]
            obj[5] = min(control.flow * factor, max_value)
            new = Control(*obj)
            result.append(new)
        return result

    def reflow(self, controls: Sequence[Control]) -> Mapping[Edge, float]:
        """
        Recalculates the flow, saves it in cached_flow and returns it.
        Assumes that the graph is a directed acyclic graph, sorts it topologically and calculates the maximum flow.
        """
        edge_flow = {}
        for edge in self.edges:
            flow = edge.default_flow
            for control in self.vulnerabilities[edge].controls:
                if control not in controls:
                    continue
                flow *= control.flow
            edge_flow[edge] = flow
        self.edge_flow = edge_flow

        topological_sort = list(networkx.topological_sort(self.graph))
        vertex_flow = {topological_sort[0]: 1}
        for vertex in topological_sort[1:]:
            flow = 0
            for edge in self.graph.in_edges(vertex, data="multiplicity"):
                flow = max(flow, edge_flow[Edge(*edge)] * vertex_flow[edge[0]])
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
                       possible_controls=possible_controls)

        return g

    def __init__(self):
        self.graph: networkx.MultiDiGraph = self.to_networkx()
        self.reflow([])


class JSONModel(Model, ABC):
    @classmethod
    def create(cls, file):
        if isinstance(file, IOBase):
            d = json.load(file)
        else:
            d = json.loads(file)

        control_categories = {control[0]: (control[1]['name'], len(control[1]['level_name']))
                              for control in d['controls'].items()}
        control_subcategories = {}
        for category_id, category in control_categories.items():
            control_subcategories[category_id] = []
            for level in range(category[1]):
                control = d['controls'][category_id]
                control_subcategories[category_id].append(Control(category_id, level + 1,
                                                                  control['level_name'][level], control['cost'][level],
                                                                  control['ind_cost'][level], control['flow'][level]))

        obj = {'name': d['name'],
               'control_categories': control_categories,
               'control_subcategories': control_subcategories,
               'n': len(d['vertices']),
               'edges': [Edge(edge['from'], edge['to'], edge['multiplicity'],
                              edge['default_flow'] if 'default_flow' in edge else 1)
                         for edge in d['edges']],
               'vertices': d['vertices'],
               'vulnerabilities': {
                   Edge(edge['from'], edge['to'], edge['multiplicity']): Vulnerability(edge['vulnerability']['name'],
                                                                                       set())
                   for edge in d['edges']
               }}

        for edge in d['edges']:
            edge_obj = Edge(edge['from'], edge['to'], edge['multiplicity'])
            for control_id, control_settings in edge['vulnerability']['controls'].items():
                for level in range(obj['control_categories'][control_id][1]):
                    control = Model.adjust_flows_by_factor([obj['control_subcategories'][control_id][level]],
                                                           control_settings['flow']
                                                           if 'flow' in control_settings else 1,
                                                           control_settings['max_flow']
                                                           if 'max_flow' in control_settings else 1)[0]
                    obj['vulnerabilities'][edge_obj].controls.add(control)

        result = type(d['name'], (JSONModel,), obj)
        return result
