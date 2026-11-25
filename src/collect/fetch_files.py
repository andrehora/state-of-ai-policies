"""Download CONTRIBUTING.md and AI_POLICY.md for each repository from the usual paths.

Paths are tried directly on raw.githubusercontent.com. Resumable: repositories already saved are skipped.
Usage: python3 fetch_files.py repos.json files/
"""
import json, os, sys, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

repos = json.load(open(sys.argv[1]))
outdir = sys.argv[2]
os.makedirs(outdir, exist_ok=True)

CAMINHOS = [
    "CONTRIBUTING.md", ".github/CONTRIBUTING.md", "docs/CONTRIBUTING.md",
    "contributing.md", "Contributing.md", ".github/contributing.md",
    "AI_POLICY.md", ".github/AI_POLICY.md", "docs/AI_POLICY.md",
    "ai_policy.md", "AI-POLICY.md",
]

def raw(repo, branch, path):
    url = f"https://raw.githubusercontent.com/{repo}/{branch}/{path}"
    for tent in range(4):
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(5 * (tent + 1))
        except Exception:
            time.sleep(5 * (tent + 1))
    return "ERRO"

def processa(r):
    dest = os.path.join(outdir, r["repo"].replace("/", "__") + ".json")
    if os.path.exists(dest):
        return
    achados = {}
    vistos = set()
    for p in CAMINHOS:
        txt = raw(r["repo"], r["branch"], p)
        if txt == "ERRO":
            return  # tenta de novo na próxima execução
        if txt is not None and txt not in vistos:  # raw não diferencia redirecionamentos
            vistos.add(txt)
            achados[p] = txt
    json.dump({**r, "arquivos": achados}, open(dest, "w"))

with ThreadPoolExecutor(32) as ex:
    for i, _ in enumerate(ex.map(processa, repos), 1):
        if i % 250 == 0:
            print(i, flush=True)
print("fim", flush=True)
