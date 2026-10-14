# Winning plan

## What the organisers reward (known facts)

- Prize: USD 3,000 in prizes and a **paid contract to integrate the hack into screenpipe's product**, plus a meal with the founders. screenpipe is also looking for 1-2 interns or apprentices.
- screenpipe's own positioning (README, July 2026 relaunch): "finds work worth automating", "map workflows", "power agents' context".
- The official starter's philosophy: observe real work, document it **with exact evidence**, keep a **human approval**, then **replay with fixed code, not AI**; separate exceptions and troubleshooting from the normal process; never claim time saved without measuring.
- Judging criteria are not published yet. They will be presented at the briefing (Friday 19:00).

**Our angle:** a project screenpipe could ship as is. It extends their starter instead of competing with it, follows their evidence-and-approval rules, and solves a painful, recurring, high-value job: explaining variances at month end.

## The five moments that win the room

1. **One number, two stories.** Contract revenue is only -17k, but the agent splits it into Belvedere -45k (slipped to April, email and chat) and Harbour City +28k (rush order).
2. **It heard the meeting.** Temporary labour +14k is explained by a sentence spoken in the 5 March production meeting, found in screenpipe's audio transcript. No email says why.
3. **It remembers.** Timber -12.4k: "Same cause as February: Brightwood +8%. You wrote this on 4 March. Still true? Also, Brightwood announced another +3% from May."
4. **It knows what it doesn't know.** Freight -6.2k: "I found the surcharges in the ledger, but nothing in your mail, chat or meetings explains them. Here is a question for Sofia Lindqvist." No invented cause.
5. **It refuses bad data.** The broken March export (duplicate from the split export, malformed amount) is rejected before any figure is computed. The unmapped account 4020 stops the calculation until someone confirms the mapping.

## Pitch (60 seconds, to the jury)

> Every month, a financial controller explains to the CFO why the numbers moved. The painful part: the explanation has almost always crossed their screen already. A supplier email about a price increase, a chat message about a delayed order, a sentence in a meeting. At month end, they dig for it again.
>
> We built an agent that closes the month with screenpipe as its memory. It watched one close and learned the procedure. The next month, it runs the close: the numbers come from code, never from the model. For each variance, it finds the evidence in your screen and audio history, remembers what you explained last month, and says so when it finds nothing.
>
> Every claim links to its source. Nothing is approved without a human. And it extends screenpipe's own starter: same review desk, same evidence rules.

Dedication (opening or closing line): "Our fictional company is called Pipeline. We named it after the tool that gave it a memory."

## 2-minute submission video (deadline Sunday 15:30)

| Time | Show | Say |
|---|---|---|
| 0:00 | Pipeline Workspace inbox, then the March P&L | The problem: 7 variances to explain, the answers are somewhere in a month of mail, chat and meetings. |
| 0:15 | February session in the review desk | The agent learned the close from one recorded session: steps with evidence, troubleshooting kept out, human approval. |
| 0:40 | Broken export rejected, then valid export | It refuses bad data before computing anything. |
| 0:50 | Variance list computed by code | Numbers come from code, never from the model. |
| 1:00 | Contract revenue split, then temporary labour linked to meeting audio | Moments 1 and 2. |
| 1:25 | Timber with February's explanation | Moment 3: memory. |
| 1:35 | Freight: "no evidence found" + drafted question | Moment 4: honesty. |
| 1:45 | Commentary draft, every sentence with a source link | The controller checks, edits, approves. |
| 1:55 | End card | "The controller stops searching and starts analysing." |

## 3-minute live final (16:40-18:00 for finalists), then 2 minutes of questions

Same story as the video, live, plus:
- the controller corrects one step in the review desk before approving (human in the loop);
- 30 seconds of vision: the April handoff to Ellen (track 3 material), onboarding Owen, a Q2 forecast that already includes Brightwood's +3%.

Keep the pre-recorded video ready if the live demo fails.

## Jury questions to prepare

- **"You record a finance person's whole screen and audio?"** Everything stays local by default. Capture is restricted to chosen apps and windows, passwords are excluded, analytics are off, and each agent only gets the data types its permissions allow (screenpipe enforces these at the system level).
- **"What if the model gets a number wrong?"** It never computes numbers. The variance engine is plain code with tests; the model only retrieves, links and writes.
- **"What if it finds the wrong email?"** Every explanation shows its exact quote and source; the controller approves each line. When evidence is missing, it says so.
- **"Does it work beyond your fictional company?"** The inputs are a standard GL export, a budget and screenpipe's history. The procedure is learned from the user's own session, not hard-coded.
- **"Why is this worth a contract?"** Month-end close happens in every company, every month. It is screenpipe's thesis (find work worth automating, give agents context) applied to a job with a clear owner and a clear deliverable.

## Official schedule (event page, read on 14 October 2026)

| When | What |
|---|---|
| Fri 16, 18:00-18:15 | Check-in |
| Fri 16, 18:15-18:25 | Opening (42 Entrepreneurs) |
| Fri 16, 18:25-19:00 | screenpipe intro and demo (product, API, MCP) |
| Fri 16, 19:00-19:15 | Briefing: tracks, rules, prizes, judging, submission format |
| Fri 16, 19:15-20:00 | Team formation and track choice |
| Fri 16, 20:00 | Hacking starts (continues overnight) |
| Sat 17, 18:00-18:45 | screenpipe technical office hours |
| Sun 18, 15:30 | **Submission deadline**: video of 2 minutes or less, GitHub link, short description |
| Sun 18, 15:30-16:30 | Pre-selection of finalists |
| Sun 18, 16:30 | Finalists announced |
| Sun 18, 16:40-18:00 | Finals: 3-minute demo + 2 minutes of questions |
| Sun 18, 18:25-18:45 | Awards |

Source: https://42entrepreneurs.com/hackathon-screenpipe?tab=schedule

## Team roles (3 to 5 people)

| Role | Owns |
|---|---|
| Capture lead | screenpipe setup, recording the scenes (runbook), API/MCP access, fallback records. |
| Engine | Deterministic variance engine: load export, validate (duplicates, formats, unmapped accounts), compute variances, drill down to entries. Tests against the answer key. |
| Memory and retrieval | Link each variance (counterparty, amount, document, date) to screenpipe evidence; recall past commentary; "insufficient evidence" outcome. |
| Interface | Variance list, evidence panel, commentary draft with source links; reuse the starter's review desk. |
| Story (can be combined) | Pitch, video, live demo, submission text. |

## Build checkpoints

- Fri night: engine passes the answer key on `gl_2026-03.csv` and rejects `gl_2026-03_invalid.csv`. Capture done or fallback records loaded.
- Sat 13:00: retrieval finds the evidence for at least 5 of the 7 variances; freight returns "not found".
- Sat 18:00: bring blockers to screenpipe office hours.
- Sat night: commentary draft with sources; end-to-end run on March.
- Sun 12:00: feature freeze. Rehearse; record the video; submit before 15:30.

## Scoring ourselves against the answer key

For each of the 7 material lines: right cause, right evidence, right "repeats next month" flag. Report the score honestly in the submission (the starter's checklist asks what works and what fails).
