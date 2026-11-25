"""Rebuild every table of the State of AI Contribution Policies report.

Inputs (in data/input/):
  repos_top25k.csv  the 25,000 most-starred repositories, with language and whether a CONTRIBUTING.md exists
  policies.csv      the 1,284 repositories with an AI contribution policy and their classification
  evidence.json     for each policy, the sentences that support each human duty, countermeasure,
                    disclosure item and git-trailer label (every one was read; false matches removed)

Outputs: data/report/*.csv (the tables the report charts read) and
data/ai-policies_<date>.csv (the full table of policies, as downloaded from the report).

Usage: python3 src/build_report.py
"""
import base64, csv, json, os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
SNAPSHOT = "2026-11-25"
ROOT = os.path.dirname(HERE)
D, O = os.path.join(ROOT, "data", "input"), os.path.join(ROOT, "data", "report")
os.makedirs(O, exist_ok=True)

def read(name):
    with open(os.path.join(D, name), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def write(name, rows):
    with open(os.path.join(O, name), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

def pct(a, b, nd=1):
    return round(100 * a / b, nd) if b else 0

repos = read("repos_top25k.csv")
pol = read("policies.csv")
ev = json.load(open(os.path.join(D, "evidence.json"), encoding="utf-8"))
N = len(pol)
FAVOR = ("In favor, no condition", "In favor, with conditions")
AGAINST = ("Against, with exceptions", "Against")

# Funnel (section 01)
TOTAL = len(repos)
fun = [("Analyzed (top 25k by stars)", TOTAL),
       ("Have CONTRIBUTING.md", sum(int(r["has_contributing"]) for r in repos)),
       ("Have CONTRIBUTING.md with AI policy", sum(int(p["in_contributing"]) for p in pol)),
       ("Have AI_POLICY.md", sum(int(p["in_ai_policy_file"]) for p in pol)),
       ("Have any AI policy", N)]
write("funnel.csv", [{"stage": s, "repos": n, "pct_of_total": pct(n, TOTAL)} for s, n in fun])

# Popularity tiers
TIERS = [(1, 1000, "Top 1–1,000"), (1001, 5000, "1,001–5,000"), (5001, 10000, "5,001–10,000"), (10001, 25000, "10,001–25,000")]
rows = []
for a, b, name in TIERS:
    S = [p for p in pol if a <= int(p["rank"]) <= b]
    c = Counter(p["ai_allowance"] for p in S)
    fav, ag = sum(c[k] for k in FAVOR), sum(c[k] for k in AGAINST)
    size = b - a + 1
    rows.append({"tier": name, "repos": size, "with_policy": len(S), "pct_with_policy": pct(len(S), size),
                 "in_favor": fav, "against": ag, "neutral": c["Neutral"], "undetermined": c["Undetermined"],
                 "pct_in_favor": pct(fav, len(S)), "pct_against": pct(ag, len(S))})
write("tiers.csv", rows)

# Languages (programming languages with at least 300 repos; HTML and Jupyter Notebook left out)
lang_all = Counter(r["language"] for r in repos if r["downloaded"] == "1" and r["language"])
lang_pol = Counter(p["language"] for p in pol)
icons = json.load(open(os.path.join(HERE, "icons", "map.json")))
def icon(l):
    f = icons.get(l)
    if not f or not os.path.exists(os.path.join(HERE, "icons", f)): return ""
    return "data:image/svg+xml;base64," + base64.b64encode(open(os.path.join(HERE, "icons", f), "rb").read()).decode()
rows = [{"language": l, "repos": n, "with_policy": lang_pol[l], "pct_with_policy": pct(lang_pol[l], n), "icon": icon(l)}
        for l, n in lang_all.items() if n >= 300 and l not in ("HTML", "Jupyter Notebook")]
rows.sort(key=lambda r: -r["pct_with_policy"])
write("languages.csv", rows)

# AI allowance (section 02) and human duties (section 03)
ORDER = ["In favor, no condition", "In favor, with conditions", "Neutral", "Against, with exceptions", "Against", "Undetermined"]
c = Counter(p["ai_allowance"] for p in pol)
hum = Counter(p["ai_allowance"] for p in pol if p["ai_allowance"] in FAVOR and ev[p["repo"]].get("human_duties"))
write("stance.csv", [{"stance": k, "policies": c[k], "pct": pct(c[k], N), "mentions_human": hum[k]} for k in ORDER])
DUTIES = ["Understand and explain the change", "Take responsibility for it", "Review the AI output", "Test and verify it", "Write your own words"]
fav = [p for p in pol if p["ai_allowance"] in FAVOR]
write("human.csv", [{"requirement": k, "policies": sum(1 for p in fav if k in ev[p["repo"]].get("human_duties", {})),
                     "pct": round(pct(sum(1 for p in fav if k in ev[p["repo"]].get("human_duties", {})), len(fav), 0))} for k in DUTIES])

# Disclosure (section 04)
dq = [p for p in pol if p["disclosure_strength"]]
WHERE = ["PR description", "Not specified", "Commit trailer", "PR template", "Mark the generated passage", "PR description and commit trailer"]
LABEL = {"PR description": "Free text in the PR description", "Not specified": "Doesn't say where", "Commit trailer": "Commit trailer",
         "PR template": "PR template section or checkbox", "Mark the generated passage": "Mark the generated passage",
         "PR description and commit trailer": "PR description and commit trailer"}
rows = []
for k in WHERE:
    req = sum(1 for p in dq if p["disclosure_where"] == k and p["disclosure_strength"] == "Required")
    rec = sum(1 for p in dq if p["disclosure_where"] == k and p["disclosure_strength"] == "Recommended")
    rows.append({"format": LABEL[k], "required": req, "recommended": rec, "total": req + rec})
rows.sort(key=lambda r: -r["total"])
write("disclose_where.csv", rows)
ITEMS = ["Tool name", "Extent / which parts", "Model and version", "Prompts or chat log", "How the result was verified"]
cnt = Counter(k for p in dq for k in ev[p["repo"]].get("disclosure_content", {}))
write("disclose_info.csv", [{"item": k, "policies": cnt[k], "pct_of_requests": round(pct(cnt[k], len(dq), 0))} for k in ITEMS])
rows = []
for t in ["Assisted-by", "Co-authored-by", "Generated-by"]:
    L = [ev[p["repo"]]["trailers"][t]["label"] for p in pol if t in ev[p["repo"]].get("trailers", {})]
    rows.append({"trailer": t + ":", "mentioned": len(L), "asked_or_allowed": L.count("asked or allowed"), "forbidden": L.count("forbidden")})
write("trailers.csv", rows)

# Countermeasures (section 05)
MECH = [("Must disclose AI use", "Human accountability"), ("No autonomous agents or bots", "Human accountability"),
        ("Close without review or notice", "Enforcement"), ("Ban or block repeat offenders", "Enforcement"),
        ("Require an approved issue first", "Barriers to entry"), ("Restrict newcomers or require vouching", "Barriers to entry"),
        ("Cap the number of PRs", "Barriers to entry"), ("Canary or signal for agents", "Automation and traps"),
        ("Automated detection or slop labels", "Automation and traps")]
rows = []
for k, g in MECH:
    n = len(dq) if k == "Must disclose AI use" else sum(1 for p in pol if k in ev[p["repo"]].get("countermeasures", {}))
    rows.append({"mechanism": k, "group": g, "policies": n, "pct": round(pct(n, N, 0))})
groups = [g for _, g in MECH]
rows.sort(key=lambda r: (groups.index(r["group"]), -r["policies"]))
write("antislop.csv", rows)
n = sum(1 for p in pol if ev[p["repo"]].get("countermeasures"))
write("slop_summary.csv", [{"policies_with_countermeasure": n, "policies": N, "pct": round(pct(n, N, 0))}])

# Explore table (section 06)
import re
def trunc(s, n=140):
    s = re.sub(r"[*_`>#|]+", " ", re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s))
    s = " ".join(s.split())
    return s if len(s) <= n else s[:n].rsplit(" ", 1)[0].rstrip(",;:.(") + " [...]"
rows = []
for p in sorted(pol, key=lambda p: -int(p["stars"])):
    h = ev[p["repo"]].get("human_duties", {})
    first = next((k for k in DUTIES if k in h), None)
    rows.append({"repo": p["repo"], "stars": p["stars"], "language": p["language"], "stance": p["ai_allowance"],
                 "policy_file": p["policy_file"], "policy_url": p["policy_url"], "snippet": p["policy_excerpt"],
                 "disclosure": p["disclosure_strength"] or "No", "disclosure_excerpt": p["disclosure_excerpt"],
                 "human": ("Yes" if h else "No") if p["ai_allowance"] in FAVOR else "—",
                 "human_duties": "; ".join(k for k in DUTIES if k in h), "human_excerpt": trunc(h[first]) if first else "",
                 "url": "https://github.com/" + p["repo"]})
# The table to download: same rows, dated, at the top of data/
with open(os.path.join(ROOT, "data", f"ai-policies_{SNAPSHOT}.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print("Wrote", len(os.listdir(O)), "tables to", O)
