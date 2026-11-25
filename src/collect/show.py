"""Print key AI sentences of policies for reading: show.py <stances|ids> <from> <to> <width>"""
import json, re, sys
P=json.load(open("policies_f.json"))
for i,o in enumerate(P): o["i"]=i
sel=sys.argv[1]; a,b,w=int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4])
L=[o for o in P if o["stance"] in sel.split(",")] if not sel[0].isdigit() else [P[int(x)] for x in sel.split(",")]
L.sort(key=lambda o:-o["stars"])
K=re.compile(r"\b(AI|LLMs?|GenAI|generative|ChatGPT|Copilot|Claude|agents?|agentic|machine[- ]generated|vibe|automated|bots?|language models?)\b|人工智能|生成|AI",re.I)
NEG=re.compile(r"\b(not|no|never|ban|forbid|prohibit|reject|allow|permit|welcome|fine|accept|okay|ok|encourage|may|must|only|except|unless|discourag|disclos|translat|review|responsib|understand)\w*",re.I)
for o in L[a:b]:
    t=re.sub(r"<!--.*?-->","",o["text"],flags=re.S); t=re.sub(r"\[([^\]]*)\]\([^)]*\)",r"\1",t)
    fs=[re.sub(r"[*_`#>|]+"," ",re.sub(r"\s+"," ",f)).strip() for f in re.split(r"(?<=[.!?。])\s+|\n",t)]
    fs=[f for f in fs if K.search(f) and NEG.search(f) and len(f)>15]
    s=" | ".join(dict.fromkeys(fs))
    print(f"{o['i']}|{o['repo']}|{o['stance']}|{s[:w]}")
