"""Build a permalink (pinned commit + line) to the start of the AI rules in each policy file."""
import csv, json, re, subprocess, urllib.request, time
from concurrent.futures import ThreadPoolExecutor
P=json.load(open("policies.json"))
POL=re.compile(r"\bAI[- ](?:generated|assisted|written|authored|created|tools?|usage|use|policy|contributions?|slop)\b|\b(?:use|usage|using|use of)\s+(?:of\s+)?(?:AI|LLMs?|generative AI)\b|\bLLMs?\b|\bgenerative AI\b|\bChatGPT\b|\bCopilot\b|\bvibe[- ]cod|^#+\s.*\b(?:AI|LLMs?)\b",re.I)
def get(u):
    for k in range(4):
        try: return urllib.request.urlopen(u,timeout=30).read().decode("utf-8","replace")
        except urllib.error.HTTPError as e:
            if e.code==429: time.sleep(5*(k+1)); continue
            return None
        except Exception: time.sleep(2)
    return None
def one(o):
    repo=o["repo"]
    d=json.load(open(f"files/{repo.replace('/','__')}.json")); arq=d["arquivos"]
    pol=[p for p in arq if "polic" in p.lower()]; con=[p for p in arq if p.lower().endswith("contributing.md")]
    try: sha=subprocess.run(["git","ls-remote",f"https://github.com/{repo}","HEAD"],capture_output=True,text=True,timeout=40).stdout.split()[0]
    except Exception: return repo,"(repository)",f"https://github.com/{repo}"
    order=(con+pol) if o["in_contrib"] else (pol+con)
    for path in order:
        txt=get(f"https://raw.githubusercontent.com/{repo}/{sha}/{path}")
        if not txt: continue
        ln=next((i+1 for i,l in enumerate(txt.splitlines()) if POL.search(l)),None)
        if ln or path in pol: return repo,path+(f":{ln}" if ln else ""),f"https://github.com/{repo}/blob/{sha}/{path}?plain=1"+(f"#L{ln}" if ln else "")
    return repo,"(repository)",f"https://github.com/{repo}"
with ThreadPoolExecutor(16) as ex: res=list(ex.map(one,P))
json.dump({r:(f,u) for r,f,u in res},open("links.json","w"))
print(sum(1 for r,f,u in res if f!="(repository)"),"de",len(res))
