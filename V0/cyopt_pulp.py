import numpy as np
import pandas as pd
from pulp import *
from os.path import abspath

# INITIALIZATIONS: 
controls_table = pd.read_csv(abspath('data/ConCosts_file.csv'))
CONTROLS = controls_table.Row
CONTROLS_WITHOUT_LEVELS = dict(zip(CONTROLS, CONTROLS.apply(lambda x: x.split('-')[0])))
# the distinct controls (irrespective of the implementation level):
CONTROLS_SET = set(CONTROLS_WITHOUT_LEVELS.values())
# controls extended with zero levels explicitly:
CONTROLS_ZERO_LEVELS = pd.DataFrame([x+'-0' for x in CONTROLS_SET])
EXT_CONTROLS = CONTROLS.append(CONTROLS_ZERO_LEVELS)
EXT_CONTROLS = EXT_CONTROLS.iloc[:,0]

Indir_Costs = dict(zip(CONTROLS,controls_table.IndirC))
Indir_Cost_Step = min(Indir_Costs.values())
Dir_Costs = dict(zip(CONTROLS,controls_table.DirC))
vulnerability_table = pd.read_csv(abspath('data/Vul_file.csv'),index_col='Row')
VULNERABILITIES = vulnerability_table.index.tolist()
Vul_Impact = vulnerability_table.Vul_I.to_dict()
Vul_P = vulnerability_table.Vul_P.to_dict()
Eff_CV = pd.read_csv(abspath('data/Eff_CV_file.csv'), index_col='Row')

def Additive_Passive(Budget, Indir_Costs_Max, Indir_Costs_Min):
    
    prob = LpProblem("Additive Passive Pareto-Front", LpMinimize)
    x = LpVariable.dicts("X", CONTROLS, 
                         lowBound = 0, 
                         upBound = 1, 
                         cat = LpBinary)
    y = LpVariable.dicts("Y", VULNERABILITIES, 0, 1)

    # additive effectiveness (together with positivity ensures remain below 100%)
    for v in VULNERABILITIES:
        prob += y[v] >= 1 - lpSum(Eff_CV.loc[c,v] * x[c] for c in CONTROLS)

    # the total budget constsraiint
    prob += lpSum(Dir_Costs[c] * x[c] for c in CONTROLS) <= Budget

    # only one level per each control
    for CON in CONTROLS_SET:
        prob += lpSum(x[c] for c in CONTROLS if  CONTROLS_WITHOUT_LEVELS[c] == CON) <= 1

    # The objective function
    small_delta = min(Indir_Costs.values())/1000 # to break the ties in favour of lower direct costs
    prob += small_delta * lpSum(Dir_Costs[c] * x[c] for c in CONTROLS) \
        + lpSum(Vul_P[v] * Vul_Impact[v] * y[v] for v in VULNERABILITIES)
        
    Indir_Costs_Caps = np.arange(Indir_Costs_Max, Indir_Costs_Min, -Indir_Cost_Step)
    Plan = {key:[] for key in ['DirectCost', 'IndirectCost', 'PassiveSecCost', 'ReactiveSecCost',
        'PassiveVulProfile', 'ReactiveVulProfile','OptimalControls']} 
    old_security_cost = -1
    for epsil in Indir_Costs_Caps:
        # the total indirect costs being less than a sliding epsilon
        prob += lpSum(Indir_Costs[c] * x[c] for c in CONTROLS) <= epsil 
        if prob.solve():
            new_security_cost = np.round(sum(Vul_P[v] * Vul_Impact[v] * y[v].varValue for v in VULNERABILITIES), 2)
            if np.abs(new_security_cost - old_security_cost) > 0.01: # to smooth away computation precision errors
                Plan['PassiveSecCost'].append(new_security_cost)
                Plan['IndirectCost'].append(np.round(sum(Indir_Costs[c] * x[c].varValue for c in CONTROLS), 2))
                Plan['DirectCost'].append(np.round(sum(Dir_Costs[c] * x[c].varValue for c in CONTROLS), 2))
                Passive_Profile = np.round([Vul_Impact[v]*Vul_P[v]*y[v].varValue for v in VULNERABILITIES] , 2)
                Reactive_Profile = np.round([Vul_Impact[v]*y[v].varValue for v in VULNERABILITIES], 2)
                Plan['PassiveVulProfile'].append(Passive_Profile)
                Plan['ReactiveVulProfile'].append(Reactive_Profile)
                Plan['ReactiveSecCost'].append(max(Reactive_Profile))
                Plan['OptimalControls'].append([c for c in CONTROLS if x[c].varValue>0.5])
                old_security_cost = new_security_cost
        else:
            print('Infeasible Problem Encountered!')
    return Plan


def Additive_Reactive(Budget, Indir_Costs_Max, Indir_Costs_Min):

    prob = LpProblem("Additive Reactive Pareto Front", LpMinimize)
    x = LpVariable.dicts("X", CONTROLS, 
                         lowBound = 0, 
                         upBound = 1, 
                         cat = LpBinary)
    z = LpVariable("Z", 0, max(Vul_Impact.values()))

    # additive effectiveness and the reactive threat(together with positivity ensures remain below 100%)
    for v in VULNERABILITIES:
        prob += z >= Vul_Impact[v]*(1 - lpSum(Eff_CV.loc[c,v] * x[c] for c in CONTROLS))

    # the total budget constsraiint
    prob += lpSum(Dir_Costs[c] * x[c] for c in CONTROLS) <= Budget

    # only one level per each control
    CONTROLS_WITHOUT_LEVELS = dict(zip(CONTROLS, CONTROLS.apply(lambda x: x.split('-')[0])))
    CONTROLS_SET = set(CONTROLS_WITHOUT_LEVELS.values())
    for CON in CONTROLS_SET:
        prob += lpSum(x[c] for c in CONTROLS if  CONTROLS_WITHOUT_LEVELS[c] == CON) <= 1

    # The objective function
    small_delta = min(Indir_Costs.values())/1000  
     # to break the ties in favour of lower direct costs
    prob += small_delta * lpSum(Dir_Costs[c] * x[c] for c in CONTROLS) + z
        
    Plan = {key:[] for key in ['DirectCost', 'IndirectCost', 'PassiveSecCost', 'ReactiveSecCost',
        'PassiveVulProfile', 'ReactiveVulProfile','OptimalControls']}  
    Indir_Costs_Caps = np.arange(Indir_Costs_Max, Indir_Costs_Min, -Indir_Cost_Step)
    old_security_cost = -1
    for epsil in Indir_Costs_Caps:
        # the total indirect costs being less than a sliding epsilon
        prob += lpSum(Indir_Costs[c] * x[c] for c in CONTROLS) <= epsil 
        if prob.solve():
            new_security_cost = np.round(z.varValue , 2)
            if np.abs(new_security_cost - old_security_cost) > 0.01:
                Plan['ReactiveSecCost'].append(new_security_cost)
                Plan['IndirectCost'].append(np.round(sum(Indir_Costs[c] * x[c].varValue for c in CONTROLS), 2))
                Plan['DirectCost'].append(np.round(sum(Dir_Costs[c] * x[c].varValue for c in CONTROLS), 2))
                Selected_plan = [c for c in CONTROLS if x[c].varValue>0.5]
                Success_per_vulnerabilities = {v:max(1-sum(Eff_CV.loc[c,v]*x[c].varValue for c in CONTROLS),0) for v in VULNERABILITIES}
                Passive_Profile = np.round([Vul_Impact[v]*Vul_P[v]*Success_per_vulnerabilities[v] for v in VULNERABILITIES], 2)
                Reactive_Profile = np.round([Vul_Impact[v]*Success_per_vulnerabilities[v] for v in VULNERABILITIES], 2)
                Plan['PassiveVulProfile'].append(Passive_Profile)
                Plan['ReactiveVulProfile'].append(Reactive_Profile)
                Plan['PassiveSecCost'].append(sum(Passive_Profile))
                Plan['OptimalControls'].append(Selected_plan)
                old_security_cost = new_security_cost
        else:
            print('Infeasible Problem Encountered!')
    return Plan


def sectool(combination='additive', threat='passive', \
                            Budget=10, Indir_Costs_Max=7.5,  Indir_Costs_Min=0.0):
    
    combination = combination.lower()
    threat = threat.lower()
    
    if (combination == 'additive' and threat == 'passive'):
        return Additive_Passive(Budget, Indir_Costs_Max, Indir_Costs_Min)
    elif (combination == 'additive' and threat == 'reactive'):
        return Additive_Reactive(Budget, Indir_Costs_Max,  Indir_Costs_Min)
    else:
        print('Selection {}-{} not valid or not implemented yet!'.format(combination, threat))
        return 0
