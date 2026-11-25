# State of AI Contribution Policies

Data and code behind the report *AI contribution policies in the top 25,000 GitHub repositories* (November 2026).

https://andrehora.github.io/state-of-ai-policies/

## Repository layout

```
data/
  ai-policies_2026-11-25.csv          every policy, as in the report's Explore table
  input/
    repos_top25k.csv                  the 25,000 most-starred repositories
    policies.csv                      the 1,284 policies and their classification
    evidence.json                     supporting sentences for each count
  report/                             the tables the report's charts read
docs/
  index.html                          the report page (served with GitHub Pages)
src/
  build_report.py                     rebuilds data/report/ and data/ai-policies_<date>.csv
  collect/                            scripts used to collect data and find candidate sentences
  icons/                              language logos from Devicon
```

| File | What it holds |
|---|---|
| `data/ai-policies_2026-11-25.csv` | One row per policy: repository, stars, main language, AI allowance, permalink to the policy, policy excerpt, AI disclosure (with excerpt) and human duties (with excerpt). |
| `data/input/repos_top25k.csv` | Rank, stars, primary language, and whether a CONTRIBUTING.md was found, for the 25,000 most-starred public repositories (forks excluded, at least 2,736 stars). |
| `data/input/policies.csv` | The 1,284 policies: AI allowance, disclosure strength and place, where the policy lives, permalink and excerpts. |
| `data/input/evidence.json` | For each policy, the sentence that supports each human duty, countermeasure, disclosure item and git-trailer label. |

## Categories

**AI allowance** (one per policy):

- *In favor, no condition*: accepts AI with no extra request.
- *In favor, with conditions*: accepts AI but asks for anything at all, even only understanding the code.
- *Neutral*: regulates only PR text, volume or attribution.
- *Against, with exceptions*: bans or discourages AI but allows narrow uses such as translation.
- *Against*: bans AI.
- *Undetermined*: the linked policy could not be found.

**Human duties** (policies that accept AI only): understand and explain the change, take responsibility for it, review the AI output, test and verify it, write your own words.

**Disclosure**: required or recommended, and where (PR description, PR template, commit trailer, both, marking the generated passage, or not specified).

**Countermeasures against AI slop**: no autonomous agents, close without review, ban repeat offenders, require an approved issue first, restrict newcomers or require vouching, cap the number of PRs, canaries for agents, automated slop labels.

## Method

1. `src/collect/top_repos.py` and `src/collect/top_repos_ext.py` list the most-starred repositories with the GitHub search API (via the `gh` CLI).
2. `src/collect/fetch_files.py` downloads CONTRIBUTING.md (root, `.github/`, `docs/`) and AI_POLICY.md files from raw.githubusercontent.com.
3. `src/collect/strict.py` and `src/collect/new_candidates.py` find candidate policies with a strict text pattern. `src/collect/policy_text.py` extracts the AI section.
4. Every candidate was read, and false positives were removed. Each policy was then classified, and policies that only link elsewhere were read at the linked page.
5. `src/collect/human25.py` and `src/collect/slop25.py` find candidate sentences for human duties and countermeasures. Every candidate sentence was read, and false matches were removed. The results are in `data/input/evidence.json`.
6. `src/collect/links25.py` and `src/collect/findline.py` build permalinks pinned to a commit.

**Classification.** Claude Opus 5.5 was used to classify the policies. Policies with unusual wording may be missed, so counts of human duties, countermeasures, disclosure items and trailers are a lower bound. An AI model can misread or misclassify a policy, so treat the figures as estimates

## References

1. Hora, A., Robbes, R. and Zacchiroli, S. "We Permit the Use of AI, but [...]": The Landscape of AI Policies in Popular Open Source Projects. [arXiv:2609.07542](https://arxiv.org/abs/2609.07542).
2. Hora, A. and Robbes, R. AI Policy, Disclosure, and Human in the Loop: How Are Contribution Guidelines Adapting to GenAI? International Conference on Software Maintenance and Evolution (ICSME), 2026. [arXiv:2605.16706](https://arxiv.org/abs/2605.16706v2).
