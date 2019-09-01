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

def main():
    f = open(sys.argv[1])
    model = json.load(f)
    f.close()

    conn = sqlite3.connect(sys.argv[2])
    c = conn.cursor()

    for edge in model['edges']:
        name = edge['vulnerability']['name']
        if name not in MAPPING:
            print(name + " not in mapping.")
            continue
        if not MAPPING[name]:
            continue

        scores_c = c.execute("SELECT [tool], [true_pos_score] FROM score WHERE category=?", (MAPPING[name],))
        scores = scores_c.fetchall()
        print(scores)



if __name__ == "__main__":
    main()
