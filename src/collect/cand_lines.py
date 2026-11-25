"""Print condensed AI sentences of candidate policies for reading: cand_lines.py <from> <to> <width>"""
import json, re, sys
C=json.load(open("cands.json"))
KEY=re.compile(r"\bAI\b|LLM|agent|Copilot|ChatGPT|Claude|generat|vibe|slop",re.I)
STR=re.compile(r"allow|permit|welcome|fine|accept|encourag|forbid|prohibit|ban|reject|clos|must|disclos|declar|responsib|understand|review|not|don'?t|avoid|strict|label|trailer|assisted",re.I)
def fr(t):
    t=re.sub(r"<!--.*?-->","",t,flags=re.S); t=re.sub(r"\[([^\]]*)\]\([^)]*\)",r"\1",t); t=re.sub(r"[#>*`_|]+"," ",t)
    return [re.sub(r"\s+"," ",f).strip() for f in re.split(r"(?<=[.!?])\s+|\n+",t) if f.strip()]
a,b,w=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3])
for i,c in enumerate(C[a:b],a):
    fs=fr(c["secao"]+"\n"+c["ai_policy"])
    sel=[f for f in fs if KEY.search(f) and STR.search(f)] or [f for f in fs if KEY.search(f)] or fs
    tag=("POL " if c["has_policy_file"] else "")
    print(f"{i}|{c['repo']}|{tag}{' | '.join(sel)[:w]}")
