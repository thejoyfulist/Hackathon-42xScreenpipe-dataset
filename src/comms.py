"""Fictional emails, chat messages, meetings and documents for Pipeline.

IDs are stable and referenced by the answer key (scenario.MARCH_DRIVERS):
E = email, C = chat message, M = meeting, D = document.
Dates are story dates (2026). screenpipe will timestamp captures with the real
date of recording, so agents must read the date shown inside the content.
"""

EMAILS = [
    {
        "id": "E01", "date": "2026-01-28 10:12", "from": "brightwood", "to": ["niamh"], "cc": ["claire"],
        "subject": "Brightwood Timber - 2026 price list (effective 1 February)",
        "attachments": ["D01"],
        "body": """Dear Niamh,

Please find attached our updated price list. Because of higher kiln-drying and transport costs, prices for oak and birch veneer panels will increase by 8% for all deliveries from 1 February 2026.

Current orders delivered before 1 February keep the 2025 prices.

Kind regards,
Gareth Moss
Account Manager, Brightwood Timber Ltd""",
    },
    {
        "id": "E02", "date": "2026-01-29 09:03", "from": "niamh", "to": ["claire"], "cc": ["tom"],
        "subject": "FW: Brightwood Timber - 2026 price list (effective 1 February)",
        "body": """Claire,

FYI, Brightwood is putting prices up 8% from 1 February. At our usual volume (about EUR 150k a month with them) that is roughly EUR 12k a month more on timber.

I'm asking them for a volume rebate. No answer yet, I'll keep you posted.

Niamh""",
    },
    {
        "id": "E03", "date": "2026-02-05 17:40", "from": "tom", "to": ["claire"],
        "subject": "January pack - feedback",
        "body": """Claire,

Thanks for the January pack, clear and on time.

For February onwards, keep the threshold at EUR 5,000 per line: comment every line above it, nothing below. The board wants the cause and whether it will repeat next month.

Tom""",
    },
    {
        "id": "E04", "date": "2026-02-27 16:05", "from": "mark", "to": ["claire", "ellen"],
        "subject": "ERP - GL detail export timing out",
        "body": """Hi both,

Heads-up for month end: the GL detail export is timing out for full-month ranges (known issue, ticket open with the ERP vendor).

Workaround: export 1-14 and 15-end of month separately and merge the two files. Make sure you don't paste the boundary day twice.

Mark""",
    },
    {
        "id": "E05", "date": "2026-03-04 18:22", "from": "claire", "to": ["tom"],
        "subject": "February management pack",
        "attachments": ["P02"],
        "body": """Tom,

February pack attached. EBITDA EUR 312.8k vs budget EUR 324.0k (-11.2k).

Only one line above the EUR 5k threshold: Timber & panels -11.6k. Brightwood's +8% price list applies from 1 February (letter of 28 January). It will repeat every month until Niamh gets the rebate or we change supplier.

Claire""",
    },
    {
        "id": "E06", "date": "2026-03-09 11:47", "from": "belvedere", "to": ["raj"],
        "subject": "Order BHG-2291 - change of delivery date",
        "attachments": ["D02"],
        "body": """Hello Raj,

Our refurbishment works at the Cork property are running late. Please postpone the delivery of order BHG-2291 (lobby and meeting room furniture, EUR 45,000) to 14 April 2026.

Invoice on delivery as agreed.

Best regards,
Anna Ross
Procurement, Belvedere Hotel Group""",
    },
    {
        "id": "E07", "date": "2026-03-06 14:30", "from": "staffbridge", "to": ["pieter"],
        "subject": "Booking confirmation - 3 operatives from 9 March",
        "body": """Hi Pieter,

As discussed on the phone, we confirm 3 temporary operatives for your workshop from Monday 9 March to Friday 27 March (3 weeks), at the agreed daily rate. Total estimate EUR 14,000, invoiced at the end of the assignment.

Lisa Grant
StaffBridge Recruitment""",
    },
    {
        "id": "E08", "date": "2026-03-18 09:15", "from": "brightwood", "to": ["niamh"],
        "subject": "Price review - further adjustment from 1 May",
        "body": """Dear Niamh,

Following our call, we are unable to offer a volume rebate this year. Please also note a further 3% increase on veneer panels for deliveries from 1 May 2026.

Kind regards,
Gareth Moss""",
    },
    {
        "id": "E09", "date": "2026-03-21 08:50", "from": "celtic", "to": ["ellen"],
        "subject": "Credit note CN-55821",
        "attachments": ["D03"],
        "body": """Dear customer,

Following the meter reading correction for October to December 2025, please find attached credit note CN-55821 for EUR 5,600.00. It will be deducted from your next payment.

This is a one-off correction. Your monthly invoices are not affected.

Celtic Energy Supply - Billing""",
    },
    {
        "id": "E10", "date": "2026-03-24 12:05", "from": "tom", "to": ["kpc"], "cc": ["claire"],
        "subject": "ERP phase 2 - start two weeks early",
        "body": """Dara,

We're happy to start phase 2 two weeks early, on 30 March, so the kickoff workshop happens before Easter. Please invoice the kickoff as per the proposal.

Claire: this moves the EUR 8k kickoff from April to March.

Tom""",
    },
    {
        "id": "E11", "date": "2026-03-27 15:40", "from": "kpc", "to": ["ellen"], "cc": ["tom"],
        "subject": "Invoice KPC-2026-031 - ERP phase 2 kickoff",
        "attachments": ["D04"],
        "body": """Hello Ellen,

Please find attached invoice KPC-2026-031 for EUR 8,000.00 (ERP phase 2 - kickoff workshop and design), as agreed with Tom.

Dara Quinn
KPC Advisory""",
    },
    {
        "id": "E12", "date": "2026-03-30 10:20", "from": "harbour", "to": ["raj"],
        "subject": "Thank you - order HCC-0457",
        "body": """Raj,

Many thanks to you and the workshop for delivering the school furniture order HCC-0457 (EUR 28,000) in three weeks. The schools reopen on time.

Brian Doyle
Facilities, Harbour City Council""",
    },
    {
        "id": "E13", "date": "2026-04-02 09:30", "from": "ellen", "to": ["claire"],
        "subject": "March GL export + new account 4020",
        "body": """Claire,

The March GL export is in the shared folder (gl_2026-03.csv). I had to use Mark's split-export workaround again.

Note: IT opened account 4020 "Sales - online web shop" on 1 March for the new web shop. It's not in the mapping tab of the closing workbook yet. About EUR 6.4k of sales in March.

Ellen""",
    },
    {
        "id": "E14", "date": "2026-04-01 07:55", "from": "atlantic", "to": ["ellen"],
        "subject": "Statement March 2026",
        "body": """Dear customer,

Your March 2026 statement is available. Total charges: EUR 50,200.00, including surcharges as itemised on invoices AFS-0326-A, AFS-0326-B and AFS-0326-C.

Atlantic Freight Services - Accounts""",
    },
    {
        "id": "E15", "date": "2026-04-07 08:40", "from": "tom", "to": ["claire"],
        "subject": "March pack by Thursday",
        "body": """Claire,

Can I have the March pack by Thursday? EBITDA looks well below budget and the board will want the reasons line by line.

Tom""",
    },
    {
        "id": "E16", "date": "2026-04-10 16:10", "from": "claire", "to": ["ellen"], "cc": ["tom", "owen"],
        "subject": "Leave 20 April - 8 May: April close",
        "body": """Ellen,

As agreed, you'll run the April close while I'm on leave (20 April to 8 May). I'll write up the handoff notes on Tuesday. Owen will shadow you.

Claire""",
    },
    # Noise
    {"id": "E17", "date": "2026-03-03 07:30", "from": "mark", "to": ["claire"], "subject": "Password expires in 5 days", "body": "Your Pipeline password expires in 5 days. Change it from the self-service portal.\n\nIT"},
    {"id": "E18", "date": "2026-03-12 12:00", "from": "pieter", "to": ["claire", "ellen", "raj", "niamh", "sofia"], "subject": "Friday lunch - workshop 10 years", "body": "Pizza in the workshop canteen on Friday at 12:30 to celebrate 10 years in the Cork building. All welcome!\n\nPieter"},
    {"id": "E19", "date": "2026-03-17 09:00", "from": "tom", "to": ["claire", "ellen", "owen"], "subject": "Welcome Owen", "body": "Please welcome Owen Kelly, who joins finance as junior analyst. Claire, please include him in the March close.\n\nTom"},
]

CHANNELS = {
    "finance-close": "Month-end close coordination",
    "sales-ops": "Sales operations",
    "production": "Workshop and production",
    "dm-claire-niamh": "Direct messages: Claire / Niamh",
    "dm-claire-raj": "Direct messages: Claire / Raj",
}

CHATS = [
    {"id": "C01", "channel": "finance-close", "date": "2026-02-02 08:45", "author": "claire", "text": "Starting the January close today. Order as usual: ERP export, workbook, mapping check, variances, commentary, pack."},
    {"id": "C02", "channel": "finance-close", "date": "2026-03-04 18:30", "author": "claire", "text": "February close done, pack sent to Tom. Only material line: timber (Brightwood +8%)."},
    {"id": "C03", "channel": "sales-ops", "date": "2026-03-10 09:12", "author": "raj", "text": "Heads-up: Belvedere pushed BHG-2291 (EUR 45k) from March to 14 April, their refurbishment is late. Nothing we can do, the order stays firm."},
    {"id": "C04", "channel": "production", "date": "2026-03-11 16:02", "author": "pieter", "text": "Harbour City rush order is on track for delivery on 27 March. Busy weeks ahead in the workshop."},
    {"id": "C05", "channel": "dm-claire-niamh", "date": "2026-03-19 10:31", "author": "niamh", "text": "Bad news on Brightwood: no rebate, and another +3% from 1 May. I'm getting quotes from Oakfield and Nordboard."},
    {"id": "C06", "channel": "finance-close", "date": "2026-04-02 09:34", "author": "ellen", "text": "March GL export is in the shared folder. New account 4020 (online web shop) since 1 March, not mapped yet."},
    {"id": "C07", "channel": "finance-close", "date": "2026-03-31 17:10", "author": "ellen", "text": "Atlantic Freight March invoices posted, EUR 50.2k in total."},
    {"id": "C08", "channel": "dm-claire-raj", "date": "2026-04-03 11:20", "author": "claire", "text": "Raj, is BHG-2291 still confirmed for 14 April? I want to say so in the March commentary."},
    {"id": "C09", "channel": "dm-claire-raj", "date": "2026-04-03 11:26", "author": "raj", "text": "Yes, confirmed this morning with Anna Ross. Delivery 14 April, invoice same day."},
    {"id": "C10", "channel": "finance-close", "date": "2026-04-14 15:00", "author": "claire", "text": "April close handoff notes are in the close folder (handoff_2026-04.md). Ellen leads, Owen shadows. Ping me only if something is blocking."},
    # Noise
    {"id": "C11", "channel": "production", "date": "2026-03-13 12:40", "author": "pieter", "text": "Thanks all for coming to the lunch!"},
    {"id": "C12", "channel": "sales-ops", "date": "2026-03-25 14:05", "author": "raj", "text": "Quayside Co-working wants a quote for 40 more desks, I'm on it."},
]

# Meetings: transcripts are written to be read aloud by the team while
# screenpipe records audio. Decision:/Action (Owner): lines follow the
# hackathon starter's meeting parser format.
MEETINGS = [
    {
        "id": "M01", "date": "2026-03-05 09:00", "title": "Weekly production meeting",
        "attendees": ["pieter", "raj", "niamh", "sofia"],
        "lines": [
            ("pieter", "Morning everyone. First topic, the Harbour City order."),
            ("raj", "Harbour City Council confirmed order HCC-0457 yesterday. School furniture, twenty-eight thousand euros, and they need it before the schools reopen at the end of March."),
            ("pieter", "That's a rush on top of the normal plan. With the current team we can't do it in three weeks."),
            ("pieter", "I'll bring in three temporary operatives from StaffBridge for three weeks, from Monday the ninth. That's about fourteen thousand euros."),
            ("niamh", "Panels are fine, I can get the extra boards from Oakfield."),
            ("sofia", "Delivery to the schools is standard road freight, no problem."),
            ("pieter", "Decision: three StaffBridge operatives from 9 to 27 March for the Harbour City rush order."),
            ("pieter", "Action (Pieter): book the three operatives with StaffBridge today."),
            ("raj", "Action (Raj): confirm the delivery date to Harbour City."),
        ],
    },
    {
        "id": "M02", "date": "2026-03-18 14:00", "title": "Purchasing review",
        "attendees": ["niamh", "tom", "claire"],
        "lines": [
            ("niamh", "Brightwood answered this morning. No volume rebate, and a further three percent from the first of May."),
            ("tom", "So the eight percent is permanent. Claire, what does that cost us?"),
            ("claire", "About twelve thousand a month on timber since February. With three percent more from May, around sixteen to seventeen thousand a month."),
            ("tom", "Decision: we look for a second supplier for veneer panels before May."),
            ("tom", "Action (Niamh): get quotes from Oakfield and Nordboard by the end of April."),
            ("tom", "Action (Claire): include the May increase in the Q2 forecast."),
        ],
    },
    {
        "id": "M03", "date": "2026-04-14 11:00", "title": "April close handoff",
        "attendees": ["claire", "ellen", "owen"],
        "lines": [
            ("claire", "Ellen, you'll run the April close, Owen shadows you. Threshold stays at five thousand per line."),
            ("claire", "Three things carry over from March. First, the Belvedere order of forty-five thousand should be invoiced on the fourteenth of April."),
            ("claire", "Second, the KPC kickoff of eight thousand was invoiced in March but budgeted in April, so April fees will look favourable. That's timing, not a saving."),
            ("claire", "Third, I never found why Atlantic Freight charged express surcharges in March. Six thousand two hundred."),
            ("ellen", "Who would know?"),
            ("claire", "Sofia in logistics. I haven't asked her yet."),
            ("claire", "Decision: Ellen leads the April close, Claire is on leave from 20 April to 8 May."),
            ("claire", "Action (Ellen): ask Sofia which shipments used service code EXP in March."),
            ("claire", "Action (Owen): note every question you have during the April close."),
        ],
    },
]

# Documents shown on screen (rendered to HTML).
DOCUMENTS = [
    {
        "id": "D01", "date": "2026-01-28", "title": "Brightwood Timber - Price list 2026 (effective 1 February 2026)", "party": "brightwood",
        "rows": [("Item", "2025 price (EUR/m2)", "2026 price (EUR/m2)", "Change"),
                 ("Oak veneer panel 18 mm", "42.50", "45.90", "+8%"),
                 ("Birch veneer panel 18 mm", "31.25", "33.75", "+8%"),
                 ("Oak veneer panel 25 mm", "55.00", "59.40", "+8%")],
        "note": "Applies to all deliveries from 1 February 2026.",
    },
    {
        "id": "D02", "date": "2026-03-09", "title": "Belvedere Hotel Group - Purchase order BHG-2291 (amended)", "party": "belvedere",
        "rows": [("Field", "Before", "After"),
                 ("Delivery date", "20 March 2026", "14 April 2026"),
                 ("Amount (EUR, excl. VAT)", "45,000.00", "45,000.00"),
                 ("Status", "Confirmed", "Confirmed - delivery postponed")],
        "note": "Reason: refurbishment works delayed at the Cork property.",
    },
    {
        "id": "D03", "date": "2026-03-21", "title": "Celtic Energy Supply - Credit note CN-55821", "party": "celtic",
        "rows": [("Description", "Period", "Amount (EUR)"),
                 ("Meter reading correction", "October - December 2025", "-5,600.00")],
        "note": "One-off correction. Deducted from the next payment.",
    },
    {
        "id": "D04", "date": "2026-03-27", "title": "KPC Advisory - Invoice KPC-2026-031", "party": "kpc",
        "rows": [("Description", "Amount (EUR)"),
                 ("ERP phase 2 - kickoff workshop and design", "8,000.00")],
        "note": "Phase 2 start moved from 13 April to 30 March at the client's request.",
    },
    {
        "id": "D05", "date": "2026-03-31", "title": "StaffBridge Recruitment - Invoice SB-7781", "party": "staffbridge",
        "rows": [("Description", "Days", "Amount (EUR)"),
                 ("3 temporary operatives, production, 9-27 March", "45", "14,000.00")],
        "note": "",
    },
]
