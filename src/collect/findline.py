"""Find the line of a sentence in a policy file at its pinned commit, to build permalinks."""
import json, urllib.request, sys, time
L=json.load(open("links.json"))
def find(repo,needle,path=None):
    f,u=L[repo]; 
    if "/blob/" not in u: return None
    sha=u.split("/blob/")[1].split("/")[0]; path=path or f.split(":")[0]
    for k in range(3):
        try: t=urllib.request.urlopen(f"https://raw.githubusercontent.com/{repo}/{sha}/{path}",timeout=30).read().decode("utf-8","replace"); break
        except Exception as e: time.sleep(3); t=""
    for i,l in enumerate(t.splitlines()):
        if needle.lower() in l.lower(): return f"https://github.com/{repo}/blob/{sha}/{path}?plain=1#L{i+1}", f"{path}:{i+1}"
    return None
Q=[("kubernetes-sigs/kueue","AI Tool Usage Policy"),("chthollyphile/folia-major","AI 工具与提交责任"),("obsidianmd/pele","neither encouraged nor prohibited"),("longbridge/nsh","100% of the code"),
   ("tashfeenahmed/freellmapi","Test it for real"),("Homebrew/brew","answer all maintainer questions"),("Taiko2k/Tauon","what model you used"),("PriorLabs/TabPFN","AI-assistance box"),
   ("libkrun/libkrun","Assisted-by: Cursor"),("floci-io/floci","Do not include `Co-Authored-By`"),("pybind/pybind11","at most two open PRs"),("Pennyw0rth/NetExec","accepted issues"),("yt-dlp/yt-dlp","If you are an LLM agent")]
for r,n in Q: print(r,find(r,n))
