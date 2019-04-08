from pulp import *
import math

from src.data import Model


def optimal_solve(arcs, nodes, sink_nodes, controls, control_ind, budget, budget_indirect, pi, P, cost, ind_costs, eps):
    model = LpProblem("simple", pulp.LpMinimize)

    # set up optimization variables
    x = LpVariable.dicts("x", controls, lowBound=0, upBound=1, cat=pulp.LpInteger)
    lam = LpVariable.dicts("lam", nodes)

    # eps>0 to impose minimize costs of portfolio
    # ============  OBJECTIVE function: ====== ======
    model += lpSum(-lam[s] + lam[0] for s in sink_nodes) + eps * lpSum(x[c] * cost[c] for c in controls) + eps * lpSum(
        x[c] * ind_costs[c] for c in controls)

    # ===============   CONSTRAINTS  ========
    # Budget CONSTRAINTS:
    model += lpSum(cost[c] * x[c] for c in controls) <= budget  # , 'Budget'
    model += lpSum(ind_costs[c] * x[c] for c in controls) <= budget_indirect  # , 'indirect costs budget'

    for c in controls:  # CONSTRAINTS: select at most one level per control
        if (c[0], 2) in controls:  # if the control has more than 1 level
            model += lpSum([x[c1] for c1 in controls if c[0] == c1[0]]) <= 1

    for e in arcs:  # CONSTRAINTS: duality lagrangian
        model += lam[e[0]] - lam[e[1]] >= math.log(pi(e)) + lpSum(x[c] * math.log(P(c, e)) for c in control_ind[e])

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
        total_cost += cost[i] * x[i].varValue
        total_ind_cost += ind_costs[i] * x[i].varValue
        # if x[i].varValue!=0:
        # print(x[i].name,' '*(20-len(x[i].name)),x[i].varValue)
    # print('\ntotal_cost= ',total_cost,'   total Indirect costs=',total_ind_cost )
    # print((lam[0].name,lam[0].varValue),[(lam[s].name,lam[s].varValue) for s in SINK_NODES])
    return (
        model.status, math.exp(model.objective.value()), [x[i].name for i in controls if x[i].varValue != 0],
        total_cost,
        total_ind_cost)


def model_solve(model: Model, budget: float, indirect_budget: float):
    arcs = [(edge.source, edge.target, edge.multiplicity) for edge in model.edges]
    nodes = [i for i in range(model.n)]
    sink_nodes = [model.n - 1]
    controls = sum((level for level in model.control_subcategories), [])
    control_ind = {edge: vuln.controls for edge, vuln in model.vulnerabilities.items()}
    pi = lambda edge: edge.default_flow
    p = lambda control, edge: control.flow
