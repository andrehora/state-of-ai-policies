"""Strict text pattern for AI-policy mentions in CONTRIBUTING.md (first-pass filter before reading)."""
import csv, json, random, re, sys
ESTRITO = re.compile(
    r"\bAI[- ](?:generated|assisted|written|authored|created|produced|tools?|usage|use|policy|contributions?|slop)\b"
    r"|\b(?:use|usage|using|use of|usage of)\s+(?:of\s+)?(?:AI|LLMs?|generative AI|large language models?)\b"
    r"|\bLLM[- ](?:generated|assisted|written|authored|tools?|contributions?)\b"
    r"|\bgenerative AI\b|\bChatGPT\b|\bCopilot\b|\bvibe[- ]cod(?:ed|ing)\b|\bmachine[- ]generated\b"
    r"|^#+\s*.*\b(?:AI|LLMs?)\b.*$",
    re.I | re.M)
rows=list(csv.DictReader(open("resultado.csv")))
hits=[]
for r in rows:
    d=json.load(open("files/"+r["repo"].replace("/","__")+".json"))
    txt="\n".join(t for p,t in d["arquivos"].items() if p.lower().endswith("contributing.md"))
    nome=r["repo"].lower()
    m=None
    for mm in ESTRITO.finditer(txt):
        t=mm.group(0)
        if re.match(r"#+\s*contributing to", t, re.I):  # título com o nome do projeto
            continue
        if "copilot" in t.lower() and "copilot" in nome:
            continue
        m=mm; break
    r["estrito"]=bool(m)
    if m: hits.append((r,txt,m))
print("estrito:", len(hits))
if len(sys.argv)>1:
    random.seed(int(sys.argv[1]))
    for r,txt,m in random.sample(hits,30):
        s=txt[max(0,m.start()-100):m.end()+100].replace("\n"," ")
        print(f"## {r['repo']}\n   ...{s}...\n")
w=csv.DictWriter(open("resultado2.csv","w",newline=""),fieldnames=list(rows[0]))
w.writeheader(); w.writerows(rows)
