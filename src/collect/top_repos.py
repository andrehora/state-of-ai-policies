"""List the N most-starred repositories (forks excluded) with the GitHub REST search API, through the gh CLI."""
import json, subprocess, sys, time

N = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
out = sys.argv[2] if len(sys.argv) > 2 else "repos.json"

def gh(path):
    for tent in range(6):
        r = subprocess.run(["gh", "api", "-H", "Accept: application/vnd.github+json", path],
                           capture_output=True, text=True)
        if r.returncode == 0:
            return json.loads(r.stdout)
        msg = r.stderr + r.stdout
        print("erro:", msg[:200], file=sys.stderr)
        time.sleep(20 * (tent + 1))
    raise SystemExit("falhou: " + path)

repos = {}
teto = None  # estrelas máximas da faixa atual
while len(repos) < N:
    q = "stars:>=50" if teto is None else f"stars:50..{teto}"
    ultimo = None
    novos = 0
    for page in range(1, 11):
        d = gh(f"search/repositories?q={q}&sort=stars&order=desc&per_page=100&page={page}")
        items = d.get("items", [])
        for it in items:
            if it["full_name"] not in repos:
                repos[it["full_name"]] = {
                    "repo": it["full_name"], "stars": it["stargazers_count"],
                    "branch": it["default_branch"], "archived": it["archived"],
                    "language": it["language"],
                }
                novos += 1
            ultimo = it["stargazers_count"]
        time.sleep(2.1)  # limite de 30 buscas por minuto
        if len(items) < 100:
            break
    print(f"{len(repos)} repos, faixa até {teto}, último {ultimo}", file=sys.stderr, flush=True)
    json.dump(list(repos.values()), open(out + ".parcial", "w"))
    if novos == 0 or ultimo is None:
        break
    teto = ultimo  # repete a fronteira; duplicados são descartados
    if teto == (ultimo if novos else None):
        pass

lista = sorted(repos.values(), key=lambda r: -r["stars"])[:N]
json.dump(lista, open(out, "w"), indent=0)
print(f"salvos {len(lista)}; menor número de estrelas: {lista[-1]['stars']}", file=sys.stderr)
