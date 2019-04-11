import abc
import json
from collections import defaultdict
from io import IOBase
from itertools import chain

import networkx
from abc import ABC
from typing import Tuple, NamedTuple, Sequence, Set, Mapping, MutableMapping


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

    class Adjustment(NamedTuple):
        flow: float
        max_flow: float

    adjustment: MutableMapping[str, Adjustment]

    def controls_repr(self):
        controls = {}
        for control in self.controls:
            result = "(%s,%s)" % (self.adjustment[control.id].flow,
                                  self.adjustment[control.id].max_flow) \
                if control.id in self.adjustment else ""
            controls[control.id] = result
        return ";".join(key+value for key, value in controls.items())


Adjustment = Vulnerability.Adjustment


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
    vulnerability: Vulnerability = None

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
    """

    name: str

    # Defining controls
    control_categories: Mapping[str, Tuple[str, int]]
    control_subcategories: Mapping[str, Sequence[Control]]

    # Defining a graph
    n: int
    edges: Sequence[Edge]
    vertices: Sequence[str]

    # Simulation results
    edge_flow: Mapping[Edge, float]
    vertex_flow: Mapping[int, float]
    tree_flow: Mapping[Edge, float]

    def reflow(self, controls: Sequence[Control]) -> Mapping[Edge, float]:
        """
        Recalculates the flow, saves it in cached_flow and returns it.
        Assumes that the graph is a directed acyclic graph, sorts it topologically and calculates the maximum flow.
        """
        edge_flow = {}
        for edge in self.edges:
            flow = edge.default_flow
            for control in edge.vulnerability.controls:
                if control not in controls:
                    continue
                if control.id in edge.vulnerability.adjustment:
                    adj = edge.vulnerability.adjustment[control.id]
                    flow *= min([control.flow * adj[0], adj[1]])
                else:
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
            possible_controls = ", ".join(set(control.id for control in edge.vulnerability.controls))

            g.add_edge(edge.source, edge.target,
                       multiplicity=edge.multiplicity, vuln_name=edge.vulnerability.name,
                       possible_controls=possible_controls)

        return g

    def __init__(self):
        self.graph: networkx.MultiDiGraph = self.to_networkx()
        self.reflow([])

    @classmethod
    def save(cls) -> str:
        def control_settings(edge, control):
            if control.id not in edge.vulnerability.adjustment:
                return {}
            return {'flow': edge.vulnerability.adjustment[control.id].flow,
                    'max_flow': edge.vulnerability.adjustment[control.id].max_flow}

        obj = {
            'name': cls.name,
            'controls': {
                category: {
                    'name': spec[0],
                    'level_name': [control.level_name for control in cls.control_subcategories[category]],
                    'cost': [control.cost for control in cls.control_subcategories[category]],
                    'ind_cost': [control.ind_cost for control in cls.control_subcategories[category]],
                    'flow': [control.flow for control in cls.control_subcategories[category]]
                }
                for category, spec in cls.control_categories.items()
            },
            'vertices': cls.vertices,
            'edges': [
                {
                    'source': edge.source,
                    'target': edge.target,
                    'multiplicity': edge.multiplicity,
                    'vulnerability': {
                        'name': edge.vulnerability.name,
                        'controls': {
                            control.id: control_settings(edge, control)
                            for control in edge.vulnerability.controls
                        }
                    }
                }
                for edge in cls.edges
            ]
        }

        return json.dumps(obj, indent=2)


class JSONModel(Model, ABC):
    class JSONError(Exception):
        pass

    @classmethod
    def create(cls, file):
        if isinstance(file, IOBase):
            d = json.load(file)
        else:
            d = json.loads(file)

        try:
            control_categories = {control[0]: (control[1]['name'], len(control[1]['level_name']))
                                  for control in d.get('controls', {}).items()}
            control_subcategories = {}
            for category_id, category in control_categories.items():
                control_subcategories[category_id] = []
                for level in range(category[1]):
                    control = d.get('controls', {})[category_id]
                    control_subcategories[category_id].append(Control(category_id, level + 1,
                                                                      control['level_name'][level],
                                                                      control['cost'][level],
                                                                      control['ind_cost'][level],
                                                                      control['flow'][level]))
        except KeyError as ke:
            raise cls.JSONError("Invalid specification of control.") from ke

        edges = []
        multiplicity = defaultdict(lambda: 0)
        for edge in d.get('edges', []):
            try:
                edge_obj = Edge(edge['source'], edge['target'], multiplicity[edge['source'], edge['target']],
                                edge['default_flow'] if 'default_flow' in edge else 1,
                                Vulnerability(edge['vulnerability']['name'], set(), {}))
                multiplicity[edge['source'], edge['target']] += 1
                for control_id, control_settings in edge['vulnerability']['controls'].items():
                    if 'flow' in control_settings:
                        edge_obj.vulnerability.adjustment[control_id] = Adjustment(control_settings['flow'],
                                                                                   control_settings.get('max_flow', 1))
                    for level in range(control_categories[control_id][1]):
                        try:
                            control = control_subcategories[control_id][level]
                        except KeyError as ke:
                            raise cls.JSONError("Control id: %s lvl: %s does not exist." % (control_id, level)) from ke
                        edge_obj.vulnerability.controls.add(control)
                edges.append(edge_obj)
            except KeyError as ke:
                raise cls.JSONError("Invalid specification of edge %s." % edge) from ke

        obj = {'name': d['name'],
               'control_categories': control_categories,
               'control_subcategories': control_subcategories,
               'n': len(d['vertices']),
               'vertices': d['vertices'],
               'edges': edges
               }

        # Checking
        if max(chain((edge.source for edge in edges), (edge.target for edge in edges))) >= len(d['vertices']):
            raise cls.JSONError("An edge exists from/to a non-existent vertex.")

        result = type(d['name'], (JSONModel,), obj)
        return result
