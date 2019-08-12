from numbers import Real, Integral
from typing import Sequence, Mapping, Callable, Tuple

from pulp import *
import math

from src.data import Model, Control, Edge


def _optimal_solve(arcs: Sequence[Edge], nodes: Sequence[Integral], sink_nodes: Sequence[Integral],
                   controls: Sequence[Control], control_ind: Mapping[Edge, Sequence[Control]],
                   budget: Real, budget_indirect: Real,
                   pi: Callable[[Edge], Real], p: Callable[[Edge], Real],
                   cost: Callable[[Control], Real], ind_cost: Callable[[Control], Real], eps: Real,
                   selected=None):
    if selected is None:
        selected = []

    model = LpProblem("simple", pulp.LpMinimize)

    # set up optimization variables
    x = LpVariable.dicts("x", controls, lowBound=0, upBound=1, cat=pulp.LpInteger)
    lam = LpVariable.dicts("lam", nodes)

    # eps>0 to impose minimize costs of portfolio
    # ============  OBJECTIVE function: ====== ======
    model += lpSum(-lam[s] + lam[0] for s in sink_nodes) + eps * lpSum(x[c] * cost(c) for c in controls) + eps * lpSum(
        x[c] * ind_cost(c) for c in controls)

    # ===============   CONSTRAINTS  ========
    # Budget CONSTRAINTS:
    model += lpSum(cost(c) * x[c] for c in controls) <= budget  # , 'Budget'
    model += lpSum(ind_cost(c) * x[c] for c in controls) <= budget_indirect  # , 'indirect costs budget'

    for c in controls:  # CONSTRAINTS: select at most one level per control
        if Control(c[0], 2) in controls:  # if the control has more than 1 level
            model += lpSum([x[c1] for c1 in controls if c[0] == c1[0]]) <= 1

    for e in arcs:  # CONSTRAINTS: duality lagrangian
        model += lam[e[0]] - lam[e[1]] >= math.log(pi(e)) + lpSum(x[c] * math.log(p(c, e)) for c in control_ind[e])

    for c in selected:  # CONSTRAINTS: select the selected
        model += x[c] == 1

        # print(model)
    # ============ SOLVE OPTIMIZATION
    #     model.solve(GUROBI_CMD())
    model.solve()
    if not model.status == 1:
        print('STATUS: unsatisfiable, status= ', model.status)
    # print('model.status:', model.status,'\nobjective value',math.exp(model.objective.value()),'\nSolution:\n')
    total_cost, total_ind_cost = 0, 0
    if not model.status == 1:
        return
    for i in controls:
        if x[i].varValue is not None:
            total_cost += cost(i) * x[i].varValue
            total_ind_cost += ind_cost(i) * x[i].varValue
        # if x[i].varValue!=0:
        # print(x[i].name,' '*(20-len(x[i].name)),x[i].varValue)
    # print('\ntotal_cost= ',total_cost,'   total Indirect costs=',total_ind_cost )
    # print((lam[0].name,lam[0].varValue),[(lam[s].name,lam[s].varValue) for s in SINK_NODES])
    return (
        model.status, math.exp(model.objective.value()), [i for i in controls if x[i].varValue != 0],
        total_cost,
        total_ind_cost)


def model_solve(model: Model, budget: float, indirect_budget: float,
                selected=None) -> Sequence[Control]:
    """
    Passes model to  the original optimisation function.
    Returns a sequence of controls to turn on.
    """
    if selected is None:
        selected = []

    nodes = list(range(model.n))

    controls = []
    controls.extend(sum((level for level in model.control_subcategories.values()), []))

    control_ind = {edge: edge.vulnerability.controls for edge in model.edges}
    pi = lambda edge: edge.default_flow
    def p(control, edge):
        if control.id in edge.vulnerability.adjustment:
            adj = edge.vulnerability.adjustment[control.id]
            return min([control.flow * adj[0], adj[1]])
        else:
            return control.flow
    cost = lambda control: control.cost
    ind_cost = lambda control: control.ind_cost

    result = _optimal_solve(model.edges, nodes, model.sink_nodes, controls, control_ind, budget,
                            indirect_budget, pi, p, cost, ind_cost, 0.00001, selected)
    return result


def model_solve_iterate(model: Model, budget: float, indirect_budget: float) -> Sequence[Control]:
    """Iterates over model_solve to spend all the budget."""
    result = (0, 0, [], 0, 0)
    changed = True

    while changed:
        result_new = model_solve(model, budget, indirect_budget, result[2])
        changed = result[2] != result_new[2]
        result = result_new

    return result


def pareto_frontier(model, budget=None, ind_budget=None):
    """
    Return pareto frontier with constant budget for one of the parameters.
    """
    max_level_controls = [group[-1] for group in model.control_subcategories.values()]

    current_ind_budget = 0
    if budget is not None:
        total_ind_cost = sum(control.ind_cost for control in max_level_controls)
    elif ind_budget is not None:
        total_ind_cost = sum(control.cost for control in max_level_controls)
    else:
        raise TypeError("Missing required budget or ind_budget")

    px, py, pz, solution = [], [], [], []
    current_solution = (1, 0)

    while current_ind_budget <= total_ind_cost:
        if budget is not None:
            sol = model_solve(model, budget, current_ind_budget)

            if sol[0] != 1:
                print('SOLUTION INFEASIBLE')

            if (sol[1] < current_solution[0] and sol[4] >= current_solution[1]) or (
                    sol[1] <= current_solution[0] and sol[4] > current_solution[1]):
                solution.append(sol)
                current_solution = (sol[1], sol[4])
                px.append(sol[1])
                py.append(sol[4])
                pz.append(sol[3])
        else:
            sol = model_solve(model, current_ind_budget, ind_budget)

            if sol[0] != 1:
                print('SOLUTION INFEASIBLE')

            if (sol[1] < current_solution[0] and sol[3] >= current_solution[1]) or (
                    sol[1] <= current_solution[0] and sol[3] > current_solution[1]):
                solution.append(sol)
                current_solution = (sol[1], sol[3])
                px.append(sol[1])
                py.append(sol[3])
                pz.append(sol[4])

        current_ind_budget = current_ind_budget + 1
    return px, py, pz, solution
