import sys
import json
import sqlite3

MAPPING = {
    "Command injection": "cmdi",
    "Cross Site Request Forgery": "xss",
    "Weak password": None,
    "Admin interaction": None,
    "Phishing": None,
    "File inclusion (PHP script injection)": "pathtraver",
    "Denial of Service": None,
    "SQL injection": "sqli",
    "Weak session ID": "weakrand",
    "Non-DOM Cross Site Scripting": "xss",
    "Password sniffing": "crypto",
    "Web Server Vulnerabilities & Misconfigurations": None,
    "SSL and authentication vulnerabilities": "crypto",
    "Missing / invalid access control": "trustbound",
    "Network vulnerability": None,
    "Unvalidated redirect / forward": "pathtraver",
}

TOOLS = [
    "OWASP_ZAP_vD-2016-09-05",
    "SonarQube_Java_Plugin_v3.14",
    "FBwFindSecBugs_v1.4.4",
    "FBwFindSecBugs_v1.4.6"
]


def main():
    f = open(sys.argv[1])
    model = json.load(f)
    f.close()

    conn = sqlite3.connect(sys.argv[2])
    c = conn.cursor()

    for edge in model['edges']:
        name = edge['vulnerability']['name']
        if name not in MAPPING:
            print(name + " not in mapping.", file=sys.stderr)
            continue
        if not MAPPING[name]:
            continue

        scores_c = c.execute("SELECT [tool], [true_pos_score] FROM score WHERE category=? AND tool IN (%s)"
                             % ",".join('?' * len(TOOLS)),
                             (MAPPING[name], *TOOLS))
        scores = dict(scores_c.fetchall())

        def proc(x):
            if x > 0.95:
                x = 0.95
            return round(1-x, 2)
        result = [proc(scores[tool]) for tool in TOOLS]
        edge['vulnerability']['controls']['Au'] = {'custom': result}

        # print(MAPPING[name], result)

    new_model = json.dumps(model, indent=2)
    print(new_model)


if __name__ == "__main__":
    main()
