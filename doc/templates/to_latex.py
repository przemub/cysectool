#!/usr/bin/python3

import json
import sys


def main():
    a = None
    with open(sys.argv[1], "r") as f:
        a = json.load(f)

    def e(num):
        return a['vertices'][num]

    print(r"\begin{table}[ht]")
    print(r"\begin{tabular}{c c p{14em} c c c}")
    print(r"Control ID & Control name & Level name & Cost & Ind. cost & Flow reduction \\")
    print(r"\hline")
    for id_, control in a['controls'].items():
        print(f"\\multirow{{{len(control['level_name'])}}}{{*}}{{{id_}}} & ", end="")
        print(f"\\multirow{{{len(control['level_name'])}}}{{*}}{{{control['name']}}}", end="")
        for level in range(len(control['level_name'])):
            if level > 0:
                print("& ", end="")
            control['level_name'][level] = control['level_name'][level].replace("%", r"\%")
            print(f"& {control['level_name'][level]} & {control['cost'][level]} & {control['ind_cost'][level]} & "
                  f"{control['flow'][level]} \\\\")
        print(r"\hline")
    print(r"\end{tabular}")
    print(r"\caption{Control groups and levels.}")
    print(r"\label{tab:appendix_controls}")
    print(r"\end{table}")

    print(r"\begin{table}[ht]")
    print(r"\begin{tabular}{c c p{14em} c c}")
    print(r"Source & Target & Vulnerability & Default flow & Controls \\")
    for edge in a['edges']:
        controls = ", ".join(key + (f"[{','.join(str(v) for v in value['custom'])}]" if 'custom' in value else "")
                             for key, value in edge['vulnerability']['controls'].items())
        edge['vulnerability']['name'] = edge['vulnerability']['name'].replace("&", r"\&")
        print(f"{e(edge['source'])} & {e(edge['target'])} & {edge['vulnerability']['name']}"
              f" & {edge['default_flow']} & {controls} \\\\")
    print(r"\end{tabular}")
    print(r"\caption{Edges. Numbers in brackets specify flow reductions for the Application security levels. "
          r"These can be further reduced by pen-testing. For the other controls, flow reductions are always "
          r"as specified in Table \ref{tab:appendix_controls}.}")
    print(r"\end{table}")


if __name__ == "__main__":
    main()
