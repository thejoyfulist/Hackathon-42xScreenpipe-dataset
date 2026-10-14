# Capture runbook: recording the scenes with screenpipe

Goal: build a realistic screenpipe history from the fictional dataset, so the agent can search it during the demo. Total recording time: about 45 minutes. Do it once before the demo, and keep the ready-made JSON records as a fallback.

## 0. Before recording

1. Install screenpipe on **macOS or Windows** (Linux capture depends on the distribution). Use the 30-day Business access given to participants (Discord `#hackathon-access`).
2. **Turn analytics off**: Settings > Privacy > Analytics, then apply.
3. Use local transcription (Whisper) and, if possible, a local AI provider.
4. Restrict capture to the apps used below (browser, spreadsheet, presentation app, video call app) with screenpipe's app filters. Close personal mail, messaging and password managers.
5. Check the API: `screenpipe auth token`, then
   `curl -H "Authorization: Bearer $TOKEN" "http://localhost:3030/search?q=test&content_type=all&limit=5"`.
   (The hackathon starter's `bun run doctor` does the same check.)

Open the workspace:

```sh
python3 -m http.server 8000 -d dataset
# browser: http://localhost:8000/viewer/
```

Deep links: `#mail/E06`, `#chat/sales-ops`, `#meetings/M01`, `#documents`, `#ledger/2026-03/5200`.

Read each item for a few seconds and scroll to the end, so screenpipe captures the whole text. screenpipe captures on events (clicks, typing pauses, scrolling, app switches), not continuously.

## Scene 1 - January and February mail (10 min)

Open in this order: E01, D01 (attachment link), E02, E03, E04, E05, then chat `#finance-close`.

## Scene 2 - The February close (10 min)

Follow `dataset/screenpipe-records/feb-close-session.json` step by step:

1. Ledger tab, period 2026-02, then account 5000, filter "Brightwood".
2. Open `workbooks/closing_workbook_2026-02.xlsx` in Excel or LibreOffice: tabs GL_import, Mapping, PnL_vs_Budget, Commentary.
3. Mail: search "Brightwood".
4. Open `commentary/commentary_2026-02.md` and `presentations/management_pack_2026-02.pptx`.

## Scene 3 - Meetings, recorded as audio (10 min)

The temporary labour explanation exists **only** in meeting M01. It must be spoken.

1. Start a video call between two laptops (Meet, Zoom or Teams), with screenpipe recording on at least one of them.
2. Read `meetings/M01_weekly-production-meeting.md` aloud, one person per role. Then M02. Keep M03 for the track 3 demo.
3. Say the names and the numbers clearly ("fourteen thousand euros", "three operatives").

## Scene 4 - March mail and chat (10 min)

Open E06, D02, C03 (`#sales-ops`), E07, C04 (`#production`), E08, C05 (DM Niamh), E09, D03, E10, E11, D04, E12, E14, C07, E13, C06, E15. Also open the noise items (E17, E18, E19, C11, C12): the agent must ignore them.

Do **not** open anything that explains the freight surcharges: nothing does, by design.

## Scene 5 - The March close starts (5 min)

1. Ledger tab, period 2026-03.
2. Open `workbooks/closing_workbook_2026-03.xlsx`: filter GL_import column M on `UNMAPPED` (account 4020), look at PnL_vs_Budget (`FIX MAPPING`).
3. Stop there. The agent does the rest in the demo.

## Check what was captured

```sh
curl -H "Authorization: Bearer $TOKEN" "http://localhost:3030/search?q=Belvedere&content_type=all&limit=10"
curl -H "Authorization: Bearer $TOKEN" "http://localhost:3030/search?q=StaffBridge&content_type=audio&limit=10"
```

With the starter: `bun run capture --start <ISO> --end <ISO>` saves at most 20 records per call to `local-data/records.json` (add `--type audio` for transcripts).

Things to check early, and to ask at the screenpipe office hours on Saturday 18:00 if needed:
- Are spreadsheet cell values captured, or only what is visible on screen?
- Are both voices transcribed on the call, with speakers separated?

## Fallback

If capture fails or is incomplete, use `dataset/screenpipe-records/workspace-memory.json`. It holds every email, chat message, meeting transcript, document and past commentary as records with the same shape as the starter's captures.
