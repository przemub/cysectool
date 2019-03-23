'''multi-controls, multi-levels, multiplicative, controls as sets of edges.
Controls' effectiveness varies depending on edge, thinning and multiple sinks'''
# the extended attack graph2:
'''
===========================   THE HIGH LEVEL MODEL DEFINITION   ================================
CONTROLS:
Sc= Secure configuration: 1. up to date software , 2. Patching, 3. whitelisting
N1= Network security (external): 1. Firewall, 2. traffic monitoring, 3. In depth packet inspection
N2= Network security (internal): 1. Firewall, 2. traffic monitoring, 3. In depth packet inspection
Ed= User education: 1. basic training, 2. Active simulated social eng attacks, 3. Strongly monitored policies
Pr= Processes: 1. inventories, 2. Prompt disabling when users leave
A1= Authentication: 1. Strong password policy, 2. regularly change password
A2= 2-factors authentication
En= Encryption: 1. implement Encryption
Am= anti-malware: 1. use anti-malware
Ac= access control
'''


class Sample:
    controls = [('Sc', 1), ('Sc', 2), ('Sc', 3), ('N1', 1), ('N1', 2), ('N1', 3), ('N2', 1), ('N2', 2), ('N2', 3),
                ('Ed', 1), ('Ed', 2), ('Ed', 3),
                ('Pr', 1), ('Pr', 2), ('A1', 1), ('A1', 2), ('A2', 1), ('Am', 1), ('Ac', 1), ('enc', 1)]

    # controls' data (P below is the surviving flow per edge):
    cost = {key: value for key, value in zip(controls, [1, 3, 4, 1, 4, 7, 2, 5, 8, 3, 5, 6, 2, 3, 1, 4, 7, 2, 2, 3])}
    ind_costs = {key: value for key, value in
                 zip(controls, [1, 1, 6, 4, 5, 6, 3, 4, 5, 2, 5, 10, 2, 4, 3, 7, 8, 1, 1, 2])}
    P0 = {key: value for key, value in
          zip(controls, [.4, .12, .1, .3, .2, .1, .3, .2, .1, .5, .3, .25, .4, .25, .3, .25, .05, .2, .1, .01])}

    def P(self, c, e):  # this function returns how much a flow survives a control c applied to an edge e
        if e == (0, 1, 0) and c[0] == 'Sc':
            return min(2 * self.P0[c], 1)  # twice the flow than default case as many CVEs available on this edge
        if e == (0, 1, 0) and c[0] == 'N1':
            return 0.8 * self.P0[c]  # 0.8 of flow than default as it can hide
        if e == (0, 5, 1) or e == (0, 4, 0) or e == (
        0, 3, 1):  # whaling or watering hole or compromised external systems
            if c[0] == 'N1':
                return min(4 * self.P0[c], 0.999)  # N1 very little effective against social engineering
        return self.P0[c]  # return flow survival default for the control

    arcs = [(0, 1, 0), (0, 5, 0), (0, 5, 1), (0, 3, 0), (0, 3, 1), (0, 4, 0), (1, 2, 0), (1, 5, 0), (2, 3, 0),
            (2, 3, 1),
            (3, 5, 0), (4, 5, 0), (5, 6, 0)]
    control_ind = {(0, 1, 0): [('N1', 1), ('N1', 2), ('N1', 3), ('Sc', 1), ('Sc', 2), ('Sc', 3)],
                   # CVE exploit webserver
                   (0, 5, 0): [('N1', 1), ('N1', 2), ('N1', 3), ('Sc', 1), ('Sc', 2), ('Sc', 3)],  # CVE exploit direct
                   (0, 5, 1): [('N1', 1), ('N1', 2), ('N1', 3), ('Ed', 1), ('Ed', 2), ('Ed', 3)],  # whaling
                   (0, 3, 0): [('N1', 1), ('N1', 2), ('N1', 3), ('Ed', 1), ('Ed', 2), ('Ed', 3)],  # phishing
                   (0, 3, 1): [('N1', 1), ('N1', 2), ('N1', 3), ('Ed', 1), ('Ed', 2), ('Ed', 3), ('Pr', 1), ('Pr', 2)],
                   # compromised external sys
                   (0, 4, 0): [('N1', 1), ('N1', 2), ('N1', 3), ('Ed', 1), ('Ed', 2), ('Ed', 3)],  # watering hole
                   (1, 5, 0): [('N2', 1), ('N2', 2), ('N2', 3), ('Sc', 1), ('Sc', 2), ('Sc', 3)],  # cve exploit
                   (1, 2, 0): [],  # empty step
                   (2, 3, 0): [('N2', 1), ('N2', 2), ('N2', 3), ('A1', 1), ('A1', 2)],  # brute force
                   (2, 3, 1): [('N2', 1), ('N2', 2), ('N2', 3), ('enc', 1)],  # sniff traffic
                   (2, 5, 0): [('N2', 1), ('N2', 2), ('N2', 3), ('Pr', 1), ('Pr', 2)],  # admin exploit
                   (3, 5, 0): [('A2', 1)],  # log in
                   (4, 3, 0): [('Ed', 1), ('Ed', 2), ('Ed', 3)],  # steal credentials
                   (4, 5, 0): [('N2', 1), ('N2', 2), ('N2', 3), ('Sc', 1), ('Sc', 2), ('Sc', 3), ('Am', 1)],
                   # install malware
                   (5, 6, 0): [('Sc', 1), ('Sc', 2), ('Sc', 3), ('Ac', 1), ('A1', 1), ('A1', 2)]  # escale priviliges
                   }
    nodes = [0, 1, 2, 3, 4, 5, 6]
    SINK_NODES = {6}

    pi0 = {key: value for key, value in zip(arcs, [1 for _ in range(len(arcs))])}  # default thinning flow coefficient

    def pi(self, e):  # define non-default thinning flow coefficients for specific edges
        if e == (0, 5, 1) or e == (0, 5, 0):  # these attack steps are unlikely so thin flow to 1/3
            return self.pi0[e] * 0.33333
        return self.pi0[e]

    # controls data:
    B = 40  # total budget
    BI = 40  # indirect costs

    eps = 0.00001
