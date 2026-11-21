# Component view

Status: design draft, written before any agent code.
Model choices and their free-tier limits are recorded in ADR-006.

```mermaid
flowchart LR
    E([Issue event<br/>label or /autose]) --> G[Gate job<br/>trusted user,<br/>one run per issue]
    G --> P[Planner agent<br/>stages 1-2]
    P --> B[Builder agent<br/>stages 3-4]
    B --> R[Release step<br/>stage 5, plain code]
    R --> V[Reviewer agent<br/>stage 6, read-only]
    V --> H([Human maintainer<br/>merge or close])

    B -. tests fail: retry .-> B
    V -. code issue .-> B
    V -. approach issue .-> P

    classDef agent fill:#eff6ff,stroke:#1d4ed8,color:#0f172a;
    classDef code fill:#f1f5f9,stroke:#64748b,color:#0f172a;
    classDef review fill:#fef3c7,stroke:#b45309,color:#0f172a;
    class P,B agent;
    class E,G,R,H code;
    class V review;
```

Solid arrows are forward flow. Dashed arrows send work back and are limited
by budgets (ADR-002, ADR-009).

## Components

| Component | Stages | Tools | Model | Can write to GitHub? |
| --- | --- | --- | --- | --- |
| Gate job | trigger check | none | none | no |
| Planner agent | 1 Requirements, 2 Design | read repo, write `spec.md` and `design.md` | Gemini (Flash-class) | no |
| Builder agent | 3 Implementation, 4 Testing | read, edit `src/` and `tests/`, run tests | Groq gpt-oss-120b | no |
| Release step | 5 Release | `git push`, `gh pr create` (plain code) | none | yes |
| Reviewer agent | 6 Review | read, run code and tests | Groq qwen3.8-27b (third family) | no (a separate posting step publishes the review) |

## Reading guide
- Checks between stages are deterministic code, not a model (ADR-007).
- Artifacts (`spec.md`, `design.md`, `diff.patch`, `test_report.md`, `pr.md`,
  `review.md`, `run_state.json`) are stored as workflow artifacts (ADR-004).
- Agents hold no GitHub token; only the Release and posting steps can write
  (ADR-005).
- The Reviewer receives only the issue, the diff and the repository at the PR
  head commit (ADR-003, ADR-008).
- A human makes the merge decision; no component merges.
