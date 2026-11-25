"""List candidate policies: repositories whose CONTRIBUTING.md matches the strict AI-policy pattern, or that have an AI_POLICY.md."""
import json, re, sys
sys.path.insert(0,"/nonexistent")
src=open("../collect/strict.py").read().split("rows=list")[0]; exec(src)   # ESTRITO
pt=open("../collect/policy_text.py").read()
exec(pt.split("LINK=")[0].split("rows=[r")[0]); exec("H=re.compile(r\"^(#{1,6})\\s*(.*)$\", re.M)\n"+pt.split("H=re.compile(r\"^(#{1,6})\\s*(.*)$\", re.M)\n")[1].split("LINK=")[0])
old={r["repo"] for r in json.load(open("repos.json"))}
allr=json.load(open("repos.json"))
extra=json.load(open("extra_policy.json"))
cands=[]
for r in allr:
    if r["repo"] in old: continue
    d=json.load(open("files/"+r["repo"].replace("/","__")+".json"))
    contrib="\n".join(t for p,t in d["arquivos"].items() if p.lower().endswith("contributing.md"))
    pol="\n".join(t for p,t in d["arquivos"].items() if "polic" in p.lower())
    nome=r["repo"].lower(); hit=False
    for mm in ESTRITO.finditer(contrib):
        t=mm.group(0)
        if re.match(r"#+\s*contributing to",t,re.I): continue
        if "copilot" in t.lower() and "copilot" in nome: continue
        hit=True; break
    if hit or pol or r["repo"] in extra:
        cands.append({"repo":r["repo"],"stars":r["stars"],"contrib_hit":hit,"has_policy_file":bool(pol) or r["repo"] in extra,
                      "secao":secao_ia(contrib).strip() if hit else "","ai_policy":pol.strip()})
cands.sort(key=lambda x:-x["stars"])
json.dump(cands,open("cands.json","w"),ensure_ascii=False)
print("candidatos:",len(cands),"| com AI_POLICY:",sum(c["has_policy_file"] for c in cands),"| só policy file:",sum(c["has_policy_file"] and not c["contrib_hit"] for c in cands))
