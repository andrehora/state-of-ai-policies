"""Text patterns that find candidate sentences for each countermeasure against AI slop. Prints matches for reading."""
import json, re, sys, random
exec(open("../collect/human25.py").read().split('if __name__')[0])
M={
 "No autonomous agents or bots": r"\bautonomous\b|fully[- ]automated|unsupervised|(agents?|bots?) (may|must|should|shall|can|are) not\b|(do not|don't) (let|allow|use) (an? )?(AI )?(agents?|bots?)|\bno (AI )?(agents|bots)\b|not (allow|accept)\w* .{0,30}\b(agents?|bots?)\b|without (a )?human (review|involvement|in the loop)",
 "Ban or block repeat offenders": r"\b(be|been|get|getting|being|are|is) (permanently |temporarily |immediately )?(banned|blocked)\b|\bban(ned)? (from|you|the (user|account|contributor))|\bblocked from\b|\bblock(ed)? (you|the account|accounts|users?|contributors?)\b|\brepeat(ed)? (offen|violat)|\bpermanent(ly)? ban",
 "Close without review or notice": r"\bclosed?\b.{0,40}\bwithout (further |any |detailed |prior )?(review|notice|warning|comment|discussion|explanation|reason)|\bclosed? (immediately|on sight|at (our|the maintainers') discretion)|will be (closed|rejected) (immediately|outright)",
 "Restrict newcomers or require vouching": r"(?<!no )\bvouch(ed|ing)?\b(?! for)(?!/etc)|first[- ]time contributors?\b.{0,40}\b(may not|cannot|can't|must|are not|need|should not|will be|only)|(?<!welcome )new contributors?\b(?!, but cannot)(?!, we can't).{0,40}\b(may not|cannot|can't|must|are not|should not|need|will be|only)|(trusted|known|established|existing) contributors? (only|may)|only .{0,30}\b(trusted|known|vouched|existing|core) (contributors|members|collaborators)|(merged|accepted) (PRs|pull requests|contributions) (before|first)",
 "Require an approved issue first": r"(approved|accepted|assigned) issue|\bissue first\b|(open|file|create) an issue (first|before)|discuss(ed|ion)? (it |this |the change )?(first|before (opening|submitting|starting|you))|must (reference|link to|address) (a|an) (\w+ )?(issue|discussion)|without (a |an )?(linked|prior|approved|accepted) (issue|discussion)|no linked,? accepted issue",
 "Cap the number of PRs": r"(at most|no more than|maximum of|limit of|up to|cap of) (\w+ )?(\d+|one|two|three|four|five|ten) (open )?(non-draft )?(PRs|pull requests)\b|pull request limits|\bover the cap\b|\bcap on .{0,30}pull requests|quota of PR|\b(\d+|one|two|three) (open )?(PRs|pull requests) at a time",
 "Automated detection or slop labels": r"(label|tag)\w*.{0,30}\b(ai-slop|slop|ai-unreviewed|llm-generated|AI-generated)\b|\b(ai-slop|ai-unreviewed|llm-generated)\W{0,3}(label|tag)|screened by an automated|automated checks? flag|pr-ai-slop|ai-slop-review|CI labels",
 "Canary or signal for agents": r"\bcanary\b|if you are an? (AI|LLM|agent|language model|coding agent|bot)|note (to|for) (AI|agents|LLMs)|\bAI agents? reading|agents? (must|should) (add|include|put|end|append)|attention (AI|LLM|agents)|🤖🤖🤖",
}
RM={k:re.compile(v,re.I) for k,v in M.items()}
def slop(o):
    out={}
    for s in sents(o["scope"]):
        for k,r in RM.items():
            if k not in out and r.search(s) and len(s)>20: out[k]=s
    return out
if __name__=="__main__":
    S={o["repo"]:slop(o) for o in P}
    from collections import Counter
    c=Counter(k for h in S.values() for k in h); print(c)
    random.seed(11)
    for k in M:
        L=[(r,h[k]) for r,h in S.items() if k in h]
        print("==",k,len(L))
        for r,s in random.sample(L,min(int(sys.argv[1]),len(L))): print(" -",r,"|",s[:150])
