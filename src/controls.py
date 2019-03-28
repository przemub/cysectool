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
    control_categories = {'Sc': ('Secure configuration', 3), 'N1': ('(Network security (external)', 3),
                          'N2': ('Network security (internal)', 3), 'Ed': ('User education', 3),
                          'Pr': ('Processes', 2), 'A1': ('Authentication', 2), 'A2': ('2FA', 1),
                          'En': ('Encryption', 1), 'Am': ('Anti-malware', 1)}

    control_subcategories = {
        'Sc': [Control('Sc', 1, "up-to-date software", 1, 1, .4), Control('Sc', 2, "patching", 3, 1, .12),
               Control('Sc', 3, "whitelisting", 4, 6, .1)],
        'N1': [Control('N1', 1, "firewall", 1, 4, .3), Control('N1', 2, "traffic monitoring", 4, 5, .2),
               Control('N1', 3, "in-depth packet inspection", 7, 6, .1)],
        'N2': [Control('N2', 1, "firewall", 2, 3, .3), Control('N2', 2, "traffic monitoring", 5, 4, .2),
               Control('N2', 3, "in-depth packet inspection", 8, 5, .1)],
        'Ed': [Control('Ed', 1, "basic training", 3, 2, .5),
               Control('Ed', 2, "active simulated social engineering attacks", 5, 5, .3),
               Control('Ed', 3, "strongly monitored policies", 6, 10, .25)],
        'Pr': [Control('Pr', 1, "inventories", 2, 2, .4),
               Control('Pr', 2, "prompt disabling when users leave", 3, 4, .25)],
        'A1': [Control('A1', 1, "strong password policy", 1, 3, .3),
               Control('A1', 2, "regularly change password", 4, 7, .25)],
        'A2': [Control('A2', 1, "2-factor authentication", 7, 8, .05)],
        'En': [Control('En', 1, "implement encryption", 2, 1, .2)],
        'Am': [Control('Am', 1, "use anti-malware", 2, 1, .1)],
        'Ac': [Control('Ac', 1, "access control", 3, 2, 0.01)]
    }

    def flow(self, c: Control, e: Edge):
        if e == (0, 1, 0) and c[0] == 'Sc':
            return min(2 * c.flow, 1)  # twice the flow than default case as many CVEs available on this edge
        if e == (0, 1, 0) and c[0] == 'N1':
            return 0.8 * c.flow  # 0.8 of flow than default as it can hide
        if e == (0, 5, 1) or e == (0, 4, 0) or e == (
                0, 3, 1):  # whaling or watering hole or compromised external systems
            if c[0] == 'N1':
                return min(4 * c.flow, 0.999)  # N1 very little effective against social engineering
        return c.flow  # return flow survival default for the control

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
        Edge(5, 6, 0): Vulnerability("escalate privileges",
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
