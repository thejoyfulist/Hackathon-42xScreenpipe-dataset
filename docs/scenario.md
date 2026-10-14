# Scenario

## The company

**Pipeline Furniture Ltd** (fictional) designs and manufactures office and hospitality furniture in Cork, Ireland. 96 staff, about EUR 15.6M budgeted revenue for 2026, currency EUR. Management accounts are closed every month and compared with the budget. Every P&L line with a variance of **EUR 5,000 or more** must be explained to the CFO: the cause, and whether it repeats next month.

## The cast

| Person | Role | Part in the story |
|---|---|---|
| **Claire Donnelly** | Financial Controller | The user. screenpipe records her screen. |
| Tom Avery | CFO | Sets the EUR 5k rule, approves the early KPC start. |
| Ellen Walsh | Senior Accountant | Posts invoices, spots the new account 4020, takes over the April close. |
| Owen Kelly | Junior Finance Analyst | Joins in March, shadows the April close (onboarding). |
| Niamh Brennan | Purchasing Manager | Handles the Brightwood price increase. |
| Raj Mehta | Key Account Sales Manager | Belvedere delay, Harbour City rush order. |
| Pieter de Vries | Production Manager | Books temporary operatives, decided in a meeting. |
| Sofia Lindqvist | Logistics Coordinator | The only person who could explain the freight surcharges. Nobody asked her. |
| Mark Fallon | IT and ERP Administrator | ERP export timeout and its workaround. |

## Timeline

| Date (2026) | Event | Evidence |
|---|---|---|
| 28 Jan | Brightwood Timber announces +8% on veneer panels from 1 Feb | E01, D01 |
| 29 Jan | Niamh: about EUR 12k a month, asks for a rebate | E02 |
| 5 Feb | CFO: comment every line above EUR 5k, nothing below | E03 |
| 27 Feb | IT: GL export times out, split it 1-14 / 15-end, never paste the boundary day twice | E04 |
| 2-4 Mar | **February close** (recorded session `feb-close-session.json`), pack sent | E05, C02 |
| 5 Mar | Production meeting: 3 temporary operatives for the Harbour City rush order (**said aloud only**) | M01 |
| 6 Mar | StaffBridge confirms 3 operatives "as discussed on the phone" (no reason given) | E07 |
| 9-10 Mar | Belvedere postpones order BHG-2291 (EUR 45k) to 14 April | E06, D02, C03 |
| 18 Mar | Brightwood: no rebate, another +3% from 1 May. Purchasing review | E08, M02, C05 |
| 21 Mar | Celtic Energy credit note EUR 5,600 (one-off meter correction) | E09, D03 |
| 24-27 Mar | CFO approves early start of ERP phase 2; KPC invoices EUR 8k in March | E10, E11, D04 |
| 30 Mar | Harbour City thanks Raj for the EUR 28k rush order | E12 |
| 1 Apr | Atlantic Freight statement EUR 50.2k "including surcharges" (no reason) | E14, C07 |
| 2 Apr | New account 4020 (online web shop) is not in the mapping | E13, C06 |
| 2-3 Apr | **March close** (recorded session `mar-close-session.json`) | |
| 14 Apr | Handoff meeting: Ellen runs April, Claire on leave | M03, C10, E16 |

## Results

| Month | EBITDA actual | Budget | Variance | Lines above EUR 5k |
|---|---|---|---|---|
| January | 317,000 | 324,000 | -7,000 | none |
| February | 312,800 | 324,000 | -11,200 | Timber & panels |
| **March** | **276,900** | **324,000** | **-47,100** | **7 lines** |

## The seven March variances (the demo)

Variance sign: positive = favourable, negative = adverse.

| Line | Variance | Real cause | Where the agent finds it | What it tests |
|---|---|---|---|---|
| Revenue - Contract | -17,000 | Belvedere -45,000 slipped to April **and** Harbour City +28,000 rush order | E06, C03 / M01, E12, GL SI-260388 | One net number hides two stories |
| Revenue - Online | +6,400 | New web shop, account 4020, unmapped and not budgeted | E13, C06 | Stop before calculating when the mapping is incomplete |
| Timber & panels | -12,400 | Brightwood +8% (-12,000), same as February; small volume effect (-400) | E01, E02, February commentary | **Memory** from one month to the next |
| Temporary labour | -14,000 | 3 operatives for the Harbour City rush order | **M01 (meeting audio only)**, E07, GL SB-7781 | Information that was only spoken |
| Freight out | -6,200 | Express surcharges, service code EXP | **Nowhere**: GL and statement only (E14) | The agent must say "not found" and ask Sofia |
| Energy | +5,600 | Credit note, meter correction for Q4 2025 | E09, D03 | One-off, will not repeat |
| Professional fees | -8,000 | KPC kickoff invoiced in March, budgeted in April | E10, E11, D04 | Timing, reverses in April |

The full answer key with evidence IDs is in `dataset/answer-key/march_2026_variances.json`.

## Traps built in

- **Unmapped account**: `closing_workbook_2026-03.xlsx` still has February's mapping. Account 4020 shows `UNMAPPED` and the P&L shows `FIX MAPPING`.
- **Broken export**: `gl_2026-03_invalid.csv` contains a duplicated entry on 14 March (the split-export boundary day, see E04) and an amount written in European format (`4.818,78`). A good procedure rejects the file before computing anything.
- **Noise**: unrelated emails (password expiry, lunch, welcome), unrelated chat, unrelated browsing in the recorded session (f12), and a free-text line in the handoff records.
- **Dates**: story dates are in 2026; screenpipe stamps captures with the real recording date. The agent must read the date shown in the content.

## Months after March

- April: Belvedere EUR 45k should be invoiced on 14 April; April fees will look favourable by EUR 8k (KPC timing). Ellen runs the close.
- May: Brightwood +3% on top of +8%, about EUR 16.9k a month in total versus budget.
