"""Extend a repository list to N repositories, continuing the star-ordered search."""
import json, subprocess, sys, time
N=int(sys.argv[1]); base=sys.argv[2]; out=sys.argv[3]
repos={r["repo"]:r for r in json.load(open(base))}
teto=min(r["stars"] for r in repos.values())
def gh(path):
    for t in range(8):
        r=subprocess.run(["gh","api",path],capture_output=True,text=True)
        if r.returncode==0: return json.loads(r.stdout)
        print("erro:",(r.stderr+r.stdout)[:160],file=sys.stderr,flush=True); time.sleep(20*(t+1))
    raise SystemExit("falhou "+path)
while len(repos)<N:
    q=f"stars:1000..{teto}"; ultimo=None; novos=0
    for page in range(1,11):
        d=gh(f"search/repositories?q={q}&sort=stars&order=desc&per_page=100&page={page}")
        it=d.get("items",[])
        for x in it:
            if x["full_name"] not in repos:
                repos[x["full_name"]]={"repo":x["full_name"],"stars":x["stargazers_count"],"branch":x["default_branch"],"archived":x["archived"],"language":x["language"]}; novos+=1
            ultimo=x["stargazers_count"]
        time.sleep(2.1)
        if len(it)<100: break
    print(len(repos),"repos; faixa até",teto,"último",ultimo,file=sys.stderr,flush=True)
    json.dump(list(repos.values()),open(out+".parcial","w"))
    if novos==0 or ultimo is None: break
    teto=ultimo
lista=sorted(repos.values(),key=lambda r:-r["stars"])[:N]
json.dump(lista,open(out,"w"))
print("salvos",len(lista),"menor:",lista[-1]["stars"],file=sys.stderr)
