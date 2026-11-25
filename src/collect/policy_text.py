"""Extract the AI-related section of CONTRIBUTING.md plus any AI_POLICY.md, for each repository with a policy."""
import csv, json, re, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

rows=[r for r in csv.DictReader(open("candidates_top10k.csv")) if r["tem_politica_de_ia"]=="True"]
H=re.compile(r"^(#{1,6})\s*(.*)$", re.M)
AIH=re.compile(r"\b(AI|A\.I\.|LLMs?|[Gg]enerative|[Aa]gents?|[Vv]ibe|[Mm]achine[- ][Gg]enerated|[Aa]utomated|Copilot|ChatGPT|[Aa]rtificial|生成|AI)\b|AI|LLM|人工智能", re.I)
TERMO=re.compile(r"\bAI\b|LLM|generative|ChatGPT|Copilot|vibe|agent|machine[- ]generated", re.I)

def secao_ia(txt):
    # seções markdown cujo título fala de IA
    hs=list(H.finditer(txt)); out=[]
    for k,h in enumerate(hs):
        if AIH.search(h.group(2)) and not re.match(r"\s*(contributing|table of contents)", h.group(2), re.I):
            nivel=len(h.group(1)); fim=len(txt)
            for h2 in hs[k+1:]:
                if len(h2.group(1))<=nivel: fim=h2.start(); break
            out.append(txt[h.start():fim])
    if not out:  # sem título: parágrafos que mencionam IA
        out=[p for p in re.split(r"\n\s*\n", txt) if TERMO.search(p)][:4]
    return "\n".join(out)

LINK=re.compile(r"https://github\.com/([\w.-]+/[\w.-]+)/blob/([\w./-]+?)/([\w./-]*?(?:AI|ai|LLM|llm)[\w./-]*\.md)")
def raw(repo, ref, path):
    try:
        return urllib.request.urlopen(f"https://raw.githubusercontent.com/{repo}/{ref}/{path}", timeout=30).read().decode("utf-8","replace")
    except Exception:
        return None

def monta(r):
    d=json.load(open("files/"+r["repo"].replace("/","__")+".json"))
    contrib="\n".join(t for p,t in d["arquivos"].items() if p.lower().endswith("contributing.md"))
    pol="\n".join(t for p,t in d["arquivos"].items() if "polic" in p.lower())
    sec=secao_ia(contrib) if r["contributing_tem_politica_de_ia"]=="True" else ""
    extra=""
    if not pol:
        # política linkada em outro arquivo do repo ou em outro repo do GitHub
        for m in LINK.finditer(sec or contrib):
            t=raw(m.group(1), m.group(2), m.group(3))
            if t: extra=t; break
        if not extra:
            for m in re.finditer(r"\]\((?:\./|/)?([\w./-]*(?:AI|ai|LLM|llm)[\w./-]*\.md)", sec):
                t=raw(r["repo"], d["branch"], m.group(1).lstrip("/"))
                if t: extra=t; break
    if r["repo"] in json.load(open("extra_policy.json")) and not pol:
        t=raw(r["repo"], d["branch"], "AI_USAGE_POLICY.md")
        if t: pol=t
    return {"repo":r["repo"],"stars":int(r["estrelas"]),"secao":sec.strip(),"ai_policy":(pol or extra).strip(),
            "fonte_politica":"AI_POLICY local" if pol else ("link" if extra else "")}

with ThreadPoolExecutor(16) as ex: out=list(ex.map(monta, rows))
out.sort(key=lambda x:-x["stars"])
json.dump(out, open("politicas.json","w"), ensure_ascii=False)
import collections
print(len(out), collections.Counter(x["fonte_politica"] for x in out))
curtos=[x for x in out if len(x["secao"])+len(x["ai_policy"])<400]
print("textos curtos (<400 chars):", len(curtos))
print("só link, sem texto de política:", sum(1 for x in out if not x["ai_policy"] and len(x["secao"])<350))
