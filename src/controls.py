"""multi-controls, multi-levels, multiplicative, controls as sets of edges.
Controls' effectiveness varies depending on edge, thinning and multiple sinks"""
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

    edges = [Edge(*edge) for edge in [(0, 1, 0), (0, 5, 0, 0.33333), (0, 5, 1, 0.33333), (0, 3, 0), (0, 3, 1),
                                      (0, 4, 0), (1, 2, 0), (1, 5, 0), (2, 3, 0), (2, 3, 1), (3, 5, 0),
                                      (4, 5, 0), (5, 6, 0)]]
    vulnerabilities = {
        Edge(0, 1, 0): Vulnerability("CVE exploit webserver",
                                     {*Model.adjust_flows_by_factor(control_subcategories['Sc'], 2, 1),
                                      *Model.adjust_flows_by_factor(control_subcategories['N1'], 0.8, 1)}),
        Edge(0, 5, 0): Vulnerability("CVE exploit direct",
                                     {*control_subcategories['N1'],
                                      *control_subcategories['Sc']}),
        Edge(0, 5, 1): Vulnerability("whaling",
                                     {*Model.adjust_flows_by_factor(control_subcategories['N1'], 4, 0.999),
                                      *control_subcategories['Ed']}),
        Edge(0, 3, 0): Vulnerability("phishing",
                                     {*control_subcategories['N1'],
                                      *control_subcategories['Ed']}),
        Edge(0, 3, 1): Vulnerability("compromised external systems",
                                     {*Model.adjust_flows_by_factor(control_subcategories['N1'], 4, 0.999),
                                      *control_subcategories['Ed'],
                                      *control_subcategories['Pr']}),
        Edge(0, 4, 0): Vulnerability("watering hole",
                                     {*Model.adjust_flows_by_factor(control_subcategories['N1'], 4, 0.999),
                                      *control_subcategories['Ed']}),
        Edge(1, 5, 0): Vulnerability("CVE exploit",
                                     {*control_subcategories['N2'],
                                      *control_subcategories['Sc']}),
        Edge(1, 2, 0): Vulnerability("empty step", set()),  # empty step
        Edge(2, 3, 0): Vulnerability("brute force",
                                     {*control_subcategories['N2'],
                                      *control_subcategories['A1']}),
        Edge(2, 3, 1): Vulnerability("sniff traffic",
                                     {*control_subcategories['N2'],
                                      *control_subcategories['En']}),
        Edge(2, 5, 0): Vulnerability("admin exploit",
                                     {*control_subcategories['N2'],
                                      *control_subcategories['Pr']}),
        Edge(3, 5, 0): Vulnerability("log in", {*control_subcategories['A2']}),  # log in
        Edge(4, 3, 0): Vulnerability("steal credentials", {*control_subcategories['Ed']}),
        Edge(4, 5, 0): Vulnerability("install malware",
                                     {*control_subcategories['N2'],
                                      *control_subcategories['Sc']}),
        Edge(5, 6, 0): Vulnerability("escalate privileges",
                                     {*control_subcategories['A1'],
                                      *control_subcategories['Sc']}),
    }

    n = 6

    vertices = ["start", "webserver", "in LAN", "credentials", "website", "control", "root"]
