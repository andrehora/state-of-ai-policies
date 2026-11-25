"""Text patterns that find candidate sentences for each human duty. Prints matches for reading: human25.py "<duty>" <n>"""
import json, re, sys, random
P=json.load(open("policies.json"))
CAT={
 "Understand and explain the change": r"\b(understand|comprehend)(s|ing)?\b(?! (the |a |an |existing |new )?(codebase|existing code|code ?base|project))(?!ing (the |a |an |existing )?(codebase|code))(?! that).{0,80}\b(code|changes?|contribution|submi\w*|every (line|part)|diff|what (you|it|the AI)|it|them)\b|\b(explain|defend)\w*\b.{0,60}\b(code|changes?|it|them|every|your|each|why)\b",
 "Review the AI output": r"\b(you|contributors?|authors?|submitters?|humans?|a person)\b( \w+){0,3} (personally |carefully |thoroughly |manually |fully )?review(ed)?\b(?! (questions?|comments?|feedback|process))|^[-*\d.\s\[\]x]*(please )?(\*\*)?(carefully |thoroughly |personally |always |manually )?review\b(?! (questions?|comments?|feedback|process|time|more))|\bhave (personally |carefully |thoroughly |fully )?reviewed\b|\b(make sure|ensure|be sure)\b.{0,25}\breview|\breview(ed)? (it|them|the (code|output|changes?|diff|generated \w+)|all|every|any|each|AI[- ]generated \w+|generated \w+)\b.{0,40}\b(yourself|before|carefully|thoroughly|personally)|\bread (every|each|the|all)( \w+)? (line|diff|code|changes?|output)\b|\bline[- ]by[- ]line\b|\bmust (be )?(first )?(be )?reviewed by (a|the) (human|contributor|author|submitter)",
 "Test and verify it": r"\btest(ed)?\b.{0,25}\b(it|them|locally|yourself|thoroughly|before (submitting|opening|you)|every|all|the (code|changes?)|your (code|changes?)|generated|output)\b|\bverif(y|ied)\b.{0,30}\b(works?|correct\w*|code|changes?|output|claims?|result|generated|it|everything|every)\b|\brun (it|the code|the tests|all tests|the test suite)\b",
 "Take responsibility for it": r"(?<!maintainers are )(?<!maintainers remain )\b(responsib(le|ility)|accountab(le|ility))\b(?! for any code that is published)(?!, (and|or) )|\bown(s|ership)? (it|the (change|code|contribution|result|work))\b|\byou are (still )?the author\b|\bstands? behind\b",
 "Write your own words": r"\bown words\b|\b(answer|respond|reply|replies|responses?|comments?|descriptions?|communicat\w*)\b.{0,60}\b(yourself|written by (you|a human)|not .{0,20}(AI|LLM)|without (using )?(AI|LLM))|(do not|don't|never|avoid) (copy|paste|forward|relay|post)\w*.{0,40}\b(AI|LLM)|\b(AI|LLM)\b.{0,30}\b(speak for you|to (communicate|reply|respond|answer|write (comments|descriptions|replies)))|never let an? (LLM|AI) speak",
}
EXCL=re.compile(r"\bAI\b.{0,20}\b(review|reviews) your\b|reading this|read more|\b(we|our|maintainers?|reviewers?) (have to|need to|will|may|must|do|are|remain)\b|^(#|\|)|e\.g\.,? ?\"?I ",re.I)
R={k:re.compile(v,re.I) for k,v in CAT.items()}
AIW=re.compile(r"\b(AI|LLMs?|GenAI|generative|ChatGPT|Copilot|Claude|Cursor|Codex|agents?|agentic|vibe[- ]cod\w*|machine[- ]generated|language models?|generated|tools?)\b|人工智能",re.I)
def sents(t):
    t=re.sub(r"<!--.*?-->","",t,flags=re.S); out=[]; head=""
    for para in re.split(r"\n\s*\n",t):
        m=re.match(r"\s*#+\s*(.*)",para)
        if m: head=m.group(1)
        if not (AIW.search(para) or AIW.search(head)): continue
        out+= [re.sub(r"\s+"," ",x).strip() for x in re.split(r"(?<=[.!?。])\s+|\n",para)]
    return out
AIK=re.compile(r"\b(AI|LLMs?|GenAI|generative|ChatGPT|Copilot|Claude|agents?|agentic|tools?|generated|vibe|model)\b",re.I)
def hits(o):
    out={}
    ss=sents(o["scope"])
    for k,r in R.items():
        for s in ss:
            if r.search(s) and not EXCL.search(s) and len(s)>20: out[k]=s; break
    return out
if __name__=="__main__":
    fav=[o for o in P if o["stance"] in("A","AR")]
    H={o["repo"]:hits(o) for o in fav}
    k=sys.argv[1]; n=int(sys.argv[2]); random.seed(7)
    L=[(r,h[k]) for r,h in H.items() if k in h]
    print(k,len(L),"of",len(fav))
    for r,s in random.sample(L,min(n,len(L))): print(" -",r,"|",s[:200])
