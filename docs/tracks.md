# What the dataset gives each track

A project enters **one** track (chosen on Friday at 19:15). The dataset supports all three, so the team can decide on site.

Official track definitions (event page):
1. **Find what to automate**: use screenpipe history to find repetitive tasks; build an interface that helps someone understand the steps and decide what to automate.
2. **Teach an agent your workflow**: turn recorded work into an automation; show it completing a real task from start to finish.
3. **Make it work for a team**: turn a personal workflow into an automation others can use, with the setup, approvals and shared tools they need.

## Track 1 - Find what to automate

| Need | In the dataset |
|---|---|
| Repeated work across sessions | Three monthly closes with the same steps (`task-runs.json`: 6 tasks x 3 runs, one one-off audit request, one duplicate capture). |
| Raw observations | `feb-close-session.json`, `mar-close-session.json`. |
| Where the time goes | Variance investigation grows from 35 to 230 minutes as the month gets messier: the best automation candidate. |
| Evidence search | `workspace-memory.json` (all mail, chat, meetings, documents, past commentary). |

Starter: `repetition`, `search`, `sop`. Pitch angle: "the slowest step of the close is searching for explanations that already crossed your screen".

Note: task minutes are fictional annotations. The starter asks to claim savings only after measuring a comparable task.

## Track 2 - Teach an agent your workflow (recommended)

| Need | In the dataset |
|---|---|
| A recorded workflow | February close session (17 records, including troubleshooting and noise). |
| A reviewed procedure | `procedures/feb-close-procedure.json`: steps classified normal / troubleshooting / unclassified, with exact quotes and open questions. Loads in the review desk (`bun start --draft ...`). |
| A real task to complete | The March close: 7 variances to explain with sources, one unmapped account, one unexplained line. |
| Fresh input and a failure case | `gl_2026-03.csv` (valid) and `gl_2026-03_invalid.csv` (duplicate entry and malformed amount). |
| Ground truth | `answer-key/march_2026_variances.json`. |

Demo: the agent learns from February, then closes March on its own: computes variances with code, finds each cause in the captured history, recalls February's timber explanation, admits it cannot explain freight, rejects the broken export, drafts the commentary with sources.

## Track 3 - Make it work for a team

| Need | In the dataset |
|---|---|
| Handoff | Claire goes on leave, Ellen runs April: `handoff.json` (decisions, blockers, actions), meeting M03, E16, C10. |
| Onboarding | Owen joined in March: `bun run onboarding --input procedures/feb-close-procedure.json`. |
| Approvals and procedure changes | `procedures/mar-close-procedure-rev2.json` (revision 2: duplicate check, stop on unmapped accounts, rule for unexplained variances). `bun run changes` compares the two. |
| Shared incident | ERP export timeout: `escalation.json`. |

Note: screenpipe Business does not share context between teammates; sharing must be built by the team.
