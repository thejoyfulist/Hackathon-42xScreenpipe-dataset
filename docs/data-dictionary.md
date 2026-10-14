# Data dictionary

## Conventions

- Currency: EUR. Amounts in CSV use a dot decimal separator and two decimals (except the deliberate error in `gl_2026-03_invalid.csv`).
- Variance = (actual - budget) x sign, where sign is +1 for revenue and -1 for costs. **Positive = favourable.**
- Commentary threshold: absolute variance of EUR 5,000 or more.
- Story dates are 2026. Records use ISO timestamps in UTC (`2026-03-05T09:00:00Z`).
- IDs: `E` email, `C` chat message, `M` meeting, `D` document, `P` presentation, `JE-YYYYMM-NNNN` GL entry, `GL:<document_ref>` and `COMMENTARY:<month>` in the answer key.

## GL export (`erp-exports/gl_YYYY-MM.csv`)

| Column | Meaning |
|---|---|
| entry_id | Unique entry ID, `JE-202603-0023` |
| posting_date | ISO date |
| period | `YYYY-MM` |
| journal | SAL sales, PUR purchases, PAY payroll |
| account | GL account (see `budget/chart_of_accounts.csv`) |
| account_name | Account label |
| cost_centre | SALES, PROD, LOG, ADMIN |
| counterparty | Customer or supplier (empty for payroll, rent, overheads) |
| document_ref | Invoice, credit note or payroll reference |
| description | Free text |
| debit, credit | Amounts. Revenue is a credit, costs are debits, a credit note on a cost is a credit. |

The export contains P&L accounts only (4000-6999). Sum of (credit - debit) x sign per line equals the actuals in `answer-key/pnl_by_month.csv`.

## P&L lines

| Code | Name | Account |
|---|---|---|
| REV_CONTRACT | Revenue - Contract | 4000 |
| REV_DEALER | Revenue - Dealers | 4010 |
| REV_ONLINE | Revenue - Online | 4020 (opened 1 March 2026) |
| MAT_TIMBER | Timber & panels | 5000 |
| MAT_FITTINGS | Metal fittings & hardware | 5010 |
| LAB_DIRECT | Direct labour | 5100 |
| LAB_TEMP | Temporary labour | 5110 |
| FREIGHT | Freight out | 5200 |
| ENERGY | Energy | 6000 |
| FEES | Professional fees | 6100 |
| RENT | Rent & facilities | 6200 |
| OTHER | Other overheads | 6300 |
| LAB_ADMIN | Salaries - admin & sales | 6400 |

## Closing workbook (`workbooks/closing_workbook_YYYY-MM.xlsx`)

Tabs: `README` (procedure), `GL_import` (export + formulas: column M line via the Mapping tab, column N net = credit - debit), `Mapping`, `PnL_vs_Budget` (SUMIFS formulas, `UNMAPPED` row, EBITDA, "comment needed"), `Commentary`. Values are formulas: open the file in Excel or LibreOffice to see them computed. The March workbook still has February's mapping and an empty Commentary tab.

## screenpipe-style records (`screenpipe-records/*.json`)

Arrays of `{ "id", "timestamp", "app", "text" }`, the normalized shape used by the hackathon starter.

| File | Used by (starter) | Content |
|---|---|---|
| workspace-memory.json | `search`, your agent | Every email, chat message, meeting, document and validated commentary |
| feb-close-session.json | `sop` | February close as observed on screen |
| mar-close-session.json | `sop` | March close as observed on screen |
| task-runs.json | `repetition` | `Task:` / `Run:` / `Minutes:` annotations |
| meetings.json | `meeting` | Transcripts with `Decision:` and `Action (Owner):` lines |
| handoff.json | `handoff` | `Decision:` / `Blocker:` / `Action (Owner):` lines |
| escalation.json | `escalation` | `Symptom:` / `Attempt:` / `Result:` / `Question:` / `Action (Owner):` lines |
| procedures/*.json | review desk, `onboarding`, `changes` | Curated procedure candidates (not approved) |
| replay/*.csv | your replay adapter | Valid February and March exports, broken March export |

## Rebuilding

`src/scenario.py` (company, accounts, budget, actuals, named transactions, answer key) and `src/comms.py` (emails, chat, meetings, documents) are the single source of truth. `src/build.py` regenerates `dataset/`; `src/validate.py` re-reads the files and checks that the ledger reconciles to the actuals, that every variance driver adds up and that every piece of evidence exists.
