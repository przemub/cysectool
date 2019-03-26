'''multi-controls, multi-levels, multiplicative, controls as sets of edges.
Controls' effectiveness varies depending on edge, thinning and multiple sinks'''
# the extended attack graph2:
from src.data import Model, Control, Edge, Vulnerability

'''
===========================   THE HIGH LEVEL MODEL DEFINITION   ================================
CONTROLS:
Sc= Sec   ure configuration: 1. up to date software , 2. Patching, 3. whitelisting
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


class Sample(Model):

    controls = [Control(*control) for control in
                [('Sc', 1), ('Sc', 2), ('Sc', 3), ('N1', 1), ('N1', 2), ('N1', 3), ('N2', 1), ('N2', 2), ('N2', 3),
                 ('Ed', 1), ('Ed', 2), ('Ed', 3),
                 ('Pr', 1), ('Pr', 2), ('A1', 1), ('A1', 2), ('A2', 1), ('Am', 1), ('Ac', 1), ('En', 1)]]

    control_categories = [('Sc', 'Secure configuration', 3), ('N1', 'Network security (external)', 3),
                          ('N2', 'Network security (internal)', 3), ('Ed', 'User education', 3),
                          ('Pr', 'Processes', 2), ('A1', 'Authentication', 2), ('A2', '2FA', 1),
                          ('En', 'Encryption', 1), ('Am', 'Anti-malware', 1)]

    control_subcategories = {
        Control('Sc', 1): "up-to-date software",
        Control('Sc', 2): "patching",
        Control('Sc', 3): "whitelisting",
        Control('N1', 1): "firewall",
        Control('N1', 2): "traffic monitoring",
        Control('N1', 3): "in-depth packet inspection",
        Control('N2', 1): "firewall\u200b",
        Control('N2', 2): "traffic monitoring\u200b",
        Control('N2', 3): "in-depth packet inspection\u200b",
        Control('Ed', 1): "basic training",
        Control('Ed', 2): "active simulated social engineering attacks",
        Control('Ed', 3): "strongly monitored policies",
        Control('Pr', 1): "inventories",
        Control('Pr', 2): "prompt disabling when users leave",
        Control('A1', 1): "strong password policy",
        Control('A1', 2): "regularly change password",
        Control('A2', 1): "2-factor authentication",
        Control('En', 1): "implement encryption",
        Control('Am', 1): "use anti-malware",
        Control('Ac', 1): "access control",
    }


    # controls' data (P below is the surviving flow per edge):
    cost = {key: value for key, value in zip(controls, [1, 3, 4, 1, 4, 7, 2, 5, 8, 3, 5, 6, 2, 3, 1, 4, 7, 2, 2, 3])}
    ind_costs = {key: value for key, value in
                 zip(controls, [1, 1, 6, 4, 5, 6, 3, 4, 5, 2, 5, 10, 2, 4, 3, 7, 8, 1, 1, 2])}
    P0 = {key: value for key, value in
          zip(controls, [.4, .12, .1, .3, .2, .1, .3, .2, .1, .5, .3, .25, .4, .25, .3, .25, .05, .2, .1, .01])}

    def flow(self, c: Control, e: Edge):
        if e == (0, 1, 0) and c[0] == 'Sc':
            return min(2 * self.P0[c], 1)  # twice the flow than default case as many CVEs available on this edge
        if e == (0, 1, 0) and c[0] == 'N1':
            return 0.8 * self.P0[c]  # 0.8 of flow than default as it can hide
        if e == (0, 5, 1) or e == (0, 4, 0) or e == (
                0, 3, 1):  # whaling or watering hole or compromised external systems
            if c[0] == 'N1':
                return min(4 * self.P0[c], 0.999)  # N1 very little effective against social engineering
        return self.P0[c]  # return flow survival default for the control

    edges = [Edge(*edge) for edge in [(0, 1, 0), (0, 5, 0), (0, 5, 1), (0, 3, 0), (0, 3, 1), (0, 4, 0), (1, 2, 0),
                                      (1, 5, 0), (2, 3, 0), (2, 3, 1), (3, 5, 0), (4, 5, 0), (5, 6, 0)]]
    vulnerabilities = {
        Edge(0, 1, 0): Vulnerability("CVE exploit webserver",
                                     {Control('N1', 1), Control('N1', 2), Control('N1', 3),
                                      Control('Sc', 1), Control('Sc', 2), Control('Sc', 3)}),
        Edge(0, 5, 0): Vulnerability("CVE exploit direct",
                                     {Control('N1', 1), Control('N1', 2), Control('N1', 3),
                                      Control('Sc', 1), Control('Sc', 2), Control('Sc', 3)}),
        Edge(0, 5, 1): Vulnerability("whaling",
                                     {Control('N1', 1), Control('N1', 2), Control('N1', 3),
                                      Control('Ed', 1), Control('Ed', 2), Control('Ed', 3)}),
        Edge(0, 3, 0): Vulnerability("phishing",
                                     {Control('N1', 1), Control('N1', 2), Control('N1', 3),
                                      Control('Ed', 1), Control('Ed', 2), Control('Ed', 3)}),
        Edge(0, 3, 1): Vulnerability("compromised external systems",
                                     {Control('N1', 1), Control('N1', 2), Control('N1', 3),
                                      Control('Ed', 1), Control('Ed', 2), Control('Ed', 3),
                                      Control('Pr', 1), Control('Pr', 2)}),
        Edge(0, 4, 0): Vulnerability("watering hole",
                                     {Control('N1', 1), Control('N1', 2), Control('N1', 3),
                                      Control('Ed', 1), Control('Ed', 2), Control('Ed', 3)}),
        Edge(1, 5, 0): Vulnerability("CVE exploit",
                                     {Control('N2', 1), Control('N2', 2), Control('N2', 3),
                                      Control('Sc', 1), Control('Sc', 2), Control('Sc', 3)}),
        Edge(1, 2, 0): Vulnerability("empty step", set()),  # empty step
        Edge(2, 3, 0): Vulnerability("brute force",
                                     {Control('N2', 1), Control('N2', 2), Control('N2', 3),
                                      Control('A1', 1), Control('A1', 2)}),
        Edge(2, 3, 1): Vulnerability("sniff traffic",
                                     {Control('N2', 1), Control('N2', 2), Control('N2', 3), Control('En', 1)}),
        Edge(2, 5, 0): Vulnerability("admin exploit",
                                     {Control('N2', 1), Control('N2', 2), Control('N2', 3),
                                      Control('Pr', 1), Control('Pr', 2)}),
        Edge(3, 5, 0): Vulnerability("log in", {Control('A2', 1)}),  # log in
        Edge(4, 3, 0): Vulnerability("steal credentials", {Control('Ed', 1), Control('Ed', 2), Control('Ed', 3)}),
        Edge(4, 5, 0): Vulnerability("install malware",
                                     {Control('N2', 1), Control('N2', 2), Control('N2', 3),
                                      Control('Sc', 1), Control('Sc', 2), Control('Sc', 3), Control('Am', 1)}),
        Edge(5, 6, 0): Vulnerability("excalate privileges",
                                     {Control('Sc', 1), Control('Sc', 2), Control('Sc', 3),
                                      Control('Ac', 1), Control('A1', 1), Control('A1', 2)})
    }

    n = 6

    vertices = ["start", "webserver", "in LAN", "credentials", "website", "control", "root"]

    pi0 = {key: value for key, value in zip(edges, [1 for _ in range(len(edges))])}  # default thinning flow coefficient

    def default_flow(self, edge: Edge):  # define non-default thinning flow coefficients for specific edges
        if edge == (0, 5, 1) or edge == (0, 5, 0):  # these attack steps are unlikely so thin flow to 1/3
            return self.pi0[edge] * 0.33333
        return self.pi0[edge]

    # controls data:
    B = 40  # total budget
    BI = 40  # indirect costs

    eps = 0.00001
