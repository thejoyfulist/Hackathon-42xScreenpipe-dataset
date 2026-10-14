# Pipeline Furniture - fictional finance dataset for "Build Agents That Remember"

Dataset and playbook for the 42 Paris x screenpipe hackathon (16-18 October 2026).

**Everything here is fictional.** Pipeline Furniture Ltd, its staff, suppliers, customers, emails, chats, meetings and figures are invented. Any resemblance to a real company or person is coincidental. Email domains use the reserved `.example` suffix.

## The idea in one sentence

A financial controller closes the books every month. The explanation of each budget variance has usually already crossed their screen during the month (an email, a chat message, a meeting). This dataset lets an agent with screenpipe memory find that explanation, remember it from one month to the next, and say so when it finds nothing.

## The tracks

A project enters **one** track, chosen on Friday 16 October at 19:15 (official event page).

| Track | Official definition | What it means for us |
|---|---|---|
| 1. Find what to automate | Use screenpipe history to find repetitive tasks. Build an interface that helps someone understand the steps and decide what to automate. | Show that the slowest step of the close is searching for explanations that already crossed the screen. |
| **2. Teach an agent your workflow** (our choice) | Turn recorded work into an automation. Show it completing a real task from start to finish. | The agent watches the February close, learns the procedure, then closes March on its own: variances computed by code, causes found in screenpipe history, commentary drafted with sources. |
| 3. Make it work for a team | Turn a personal workflow into an automation others can use, with the setup, approvals and shared tools they need. | The controller goes on leave; a colleague runs the April close with the approved procedure and a sourced handoff. |

Why track 2: it is exactly our demo; track 1 would compete with screenpipe's own "map workflows" feature; track 3 needs teammate sharing that screenpipe Business does not include, so we would have to build it in 48 hours. Points from tracks 1 and 3 become the product vision.

## The pain points, and where we can answer

A financial controller's monthly close, pain by pain. **Status**: *Demo* = shown live and in the video; *Data ready* = the dataset supports it, we show it only if time allows; *Vision* = on the closing slide only.

| # | Pain point | Track | How the agent answers with screenpipe | Status | Where in the dataset |
|---|---|---|---|---|---|
| 1 | The explanation of a variance crossed the screen during the month, but must be dug up again at month end | 1 | Starts from the variance (counterparty, amount, date), finds the email, chat or meeting, proposes the cause with its source; says when it finds nothing | **Demo** | `workspace-memory.json`, March answer key |
| 2 | The same variances come back every month and are researched from scratch | 1 | "Same cause as February: Brightwood +8%. Still true?" | **Demo** | `commentary/commentary_2026-02.md`, E01, E02 |
| 3 | Some information is only said in meetings | 1 | Finds the decision in the audio transcript and links it to the right P&L line | **Demo** | Meeting M01 (temporary labour) |
| 4 | Exports and spreadsheet work repeated every month | 1, 2 | Measures where time goes; replays the approved steps with fixed code on next month's export, rejecting bad data | **Demo** | `task-runs.json`, `gl_2026-03.csv`, `gl_2026-03_invalid.csv` |
| 5 | The close procedure only exists in the controller's head | 2 | Drafts the procedure from one observed close, each step with its evidence, troubleshooting kept out; the controller approves | **Demo** | `procedures/feb-close-procedure.json` |
| 6 | Controls get skipped under time pressure | 2 | Compares this month's close with the approved procedure and flags missing steps (duplicate check, unmapped account) | Data ready | `procedures/mar-close-procedure-rev2.json`, workbook March (`UNMAPPED`) |
| 7 | Chasing colleagues for answers they already gave | 2 | Looks for the answer in history first; otherwise drafts the exact question; sending stays a human decision | Data ready | Freight surcharges: no evidence, question to Sofia |
| 8 | The monthly commentary starts from a blank page | 2 | First draft where every sentence links to its variance and source | **Demo** | March draft pack, answer key |
| 9 | "Where does this number come from?" weeks later | 1 | Rebuilds the trail: which file, which day, which email or meeting | Vision | GL document references, evidence IDs |
| 10 | Leave or departure: the replacement is lost | 3 | Sourced handoff file and a guide a colleague can follow alone | Vision | `handoff.json`, meeting M03, E16 |
| 11 | The procedure goes out of date (new account, new entity) | 3 | Proposes changes with evidence; the approved version stays frozen until re-approved | Vision | `procedures/` rev 1 vs rev 2, `bun run changes` |

**What we do not promise:** posting entries in the ERP, sending emails without a human, year-end forecasting (calculation, not memory), "hours saved" without a real measurement.

## What is inside

| Folder | Content |
|---|---|
| `dataset/viewer/` | **Pipeline Workspace**, a static web app (mail, chat, meeting transcripts, documents, ledger). Open it on screen while screenpipe records. |
| `dataset/erp-exports/` | GL detail exports for January, February and March 2026, plus a deliberately broken March export. |
| `dataset/budget/` | Budget 2026 (CSV and XLSX) and chart of accounts. |
| `dataset/workbooks/` | The controller's closing workbooks: January and February closed, March in progress (new unmapped account, empty commentary). |
| `dataset/presentations/` | Budget 2026 deck, January and February management packs, March draft pack. |
| `dataset/mail/` | 19 emails as `.eml` files. |
| `dataset/chat/` | 12 chat messages (CSV). |
| `dataset/meetings/` | 3 meeting scripts to read aloud while screenpipe records audio. |
| `dataset/documents/` | Supplier and customer documents (price list, purchase order, credit note, invoices). |
| `dataset/commentary/` | Validated monthly commentary for January and February (the agent's "memory" of past explanations). |
| `dataset/screenpipe-records/` | Ready-made records in the format of the official [hackathon starter](https://github.com/screenpipe/hackathon-starter), for every starter project, plus two curated procedures. |
| `dataset/answer-key/` | Expected March analysis: every variance, its drivers and their evidence. Do not give it to the agent. |
| `docs/` | Pitch deck (PowerPoint), scenario, capture runbook, track guide, winning plan, data dictionary. |

## Quick start

```sh
# Look at the data
python3 -m http.server 8000 -d dataset   # then open http://localhost:8000/viewer/
# (opening dataset/viewer/index.html directly also works)

# Rebuild everything from the scenario, then check consistency
uv run python src/build.py
uv run python src/pitch_deck.py   # docs/pitch-deck.pptx
uv run python src/validate.py
```

Use the records with the official starter (Bun 1.3+):

```sh
git clone https://github.com/screenpipe/hackathon-starter.git && cd hackathon-starter
R=../hackathon-42x-screenpipe-dataset/dataset/screenpipe-records
bun run search --input $R/workspace-memory.json --query "Belvedere"
bun run repetition --input $R/task-runs.json
bun run meeting --input $R/meetings.json
bun run handoff --input $R/handoff.json
bun run escalation --input $R/escalation.json
bun start --draft $R/procedures/feb-close-procedure.json
bun run changes --before $R/procedures/feb-close-procedure.json --after $R/procedures/mar-close-procedure-rev2.json
bun run onboarding --input $R/procedures/feb-close-procedure.json
```

All these commands were run against this dataset on 14 October 2026 and accept it.

## Read next

0. [docs/pitch-deck.pptx](docs/pitch-deck.pptx) - the 12-slide pitch for the jury, with speaker notes.
1. [docs/scenario.md](docs/scenario.md) - the story, the cast and the seven March variances.
2. [docs/winning-plan.md](docs/winning-plan.md) - pitch, demo scripts, jury questions, schedule, roles.
3. [docs/capture-runbook.md](docs/capture-runbook.md) - how to record the scenes with screenpipe.
4. [docs/tracks.md](docs/tracks.md) - what the dataset gives each of the three tracks.
5. [docs/data-dictionary.md](docs/data-dictionary.md) - files, columns, IDs and conventions.

## Rules we follow

- Fictional data only. Nothing from anyone's real job.
- Figures are computed by code, never by a language model.
- Confirm at the Friday briefing that bringing a prepared fictional dataset is allowed. The product code is written on site.
