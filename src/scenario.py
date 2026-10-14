"""Single source of truth for the fictional Pipeline Furniture dataset.

Every name, number and message here is invented for the 42 Paris x screenpipe
hackathon. Any resemblance to a real company or person is coincidental.
All generated files (CSV, XLSX, PPTX, HTML, JSON) are derived from this module.
"""

COMPANY = {
    "name": "Pipeline Furniture Ltd",
    "short": "Pipeline",
    "domain": "pipeline-furniture.example",
    "city": "Cork, Ireland (fictional company)",
    "activity": "Designs and manufactures office and hospitality furniture",
    "headcount": 96,
    "currency": "EUR",
    "erp": "Pipeline ERP (fictional)",
    "fiscal_year": "January to December 2026",
    "variance_threshold": 5000,
}

# id -> person. "user" is the person whose screen screenpipe records.
PEOPLE = {
    "claire": {"name": "Claire Donnelly", "role": "Financial Controller", "email": "claire.donnelly", "user": True},
    "tom": {"name": "Tom Avery", "role": "Chief Financial Officer", "email": "tom.avery"},
    "ellen": {"name": "Ellen Walsh", "role": "Senior Accountant (GL and payables)", "email": "ellen.walsh"},
    "owen": {"name": "Owen Kelly", "role": "Junior Finance Analyst (joined March 2026)", "email": "owen.kelly"},
    "niamh": {"name": "Niamh Brennan", "role": "Purchasing Manager", "email": "niamh.brennan"},
    "raj": {"name": "Raj Mehta", "role": "Key Account Sales Manager", "email": "raj.mehta"},
    "pieter": {"name": "Pieter de Vries", "role": "Production Manager", "email": "pieter.devries"},
    "sofia": {"name": "Sofia Lindqvist", "role": "Logistics Coordinator", "email": "sofia.lindqvist"},
    "mark": {"name": "Mark Fallon", "role": "IT and ERP Administrator", "email": "mark.fallon"},
}

# External (fictional) parties.
PARTIES = {
    "brightwood": {"name": "Brightwood Timber Ltd", "type": "supplier", "contact": "Gareth Moss", "email": "gareth.moss@brightwood-timber.example"},
    "oakfield": {"name": "Oakfield Panels", "type": "supplier"},
    "nordboard": {"name": "Nordboard Supplies", "type": "supplier"},
    "halvorsen": {"name": "Halvorsen Fittings", "type": "supplier"},
    "staffbridge": {"name": "StaffBridge Recruitment", "type": "supplier", "contact": "Lisa Grant", "email": "lisa.grant@staffbridge.example"},
    "atlantic": {"name": "Atlantic Freight Services", "type": "supplier", "contact": "Accounts team", "email": "accounts@atlantic-freight.example"},
    "celtic": {"name": "Celtic Energy Supply", "type": "supplier", "contact": "Billing team", "email": "billing@celtic-energy.example"},
    "kpc": {"name": "KPC Advisory", "type": "supplier", "contact": "Dara Quinn", "email": "dara.quinn@kpc-advisory.example"},
    "harrowgate": {"name": "Harrowgate Audit & Tax", "type": "supplier"},
    "quaylaw": {"name": "Quay Legal LLP", "type": "supplier"},
    "belvedere": {"name": "Belvedere Hotel Group", "type": "customer", "contact": "Anna Ross", "email": "anna.ross@belvedere-hotels.example"},
    "harbour": {"name": "Harbour City Council", "type": "customer", "contact": "Brian Doyle", "email": "brian.doyle@harbourcity-council.example"},
    "quayside": {"name": "Quayside Co-working", "type": "customer"},
    "meridian": {"name": "Meridian Insurance", "type": "customer"},
    "lough": {"name": "Lough Valley University", "type": "customer"},
    "deskworks": {"name": "DeskWorks Dealers", "type": "dealer"},
    "officeline": {"name": "OfficeLine Distribution", "type": "dealer"},
    "workspace_hub": {"name": "Workspace Hub Retail", "type": "dealer"},
}

# Management P&L lines, in display order. sign = +1 revenue, -1 cost.
LINES = [
    ("REV_CONTRACT", "Revenue - Contract", 1),
    ("REV_DEALER", "Revenue - Dealers", 1),
    ("REV_ONLINE", "Revenue - Online", 1),
    ("MAT_TIMBER", "Timber & panels", -1),
    ("MAT_FITTINGS", "Metal fittings & hardware", -1),
    ("LAB_DIRECT", "Direct labour", -1),
    ("LAB_TEMP", "Temporary labour", -1),
    ("FREIGHT", "Freight out", -1),
    ("ENERGY", "Energy", -1),
    ("FEES", "Professional fees", -1),
    ("RENT", "Rent & facilities", -1),
    ("OTHER", "Other overheads", -1),
    ("LAB_ADMIN", "Salaries - admin & sales", -1),
]
LINE_NAME = {k: n for k, n, _ in LINES}
LINE_SIGN = {k: s for k, _, s in LINES}

# GL accounts. "since" = first period the account exists.
ACCOUNTS = {
    "4000": ("Sales - contract customers", "REV_CONTRACT", "2026-01"),
    "4010": ("Sales - dealers", "REV_DEALER", "2026-01"),
    "4020": ("Sales - online web shop", "REV_ONLINE", "2026-03"),
    "5000": ("Purchases - timber and panels", "MAT_TIMBER", "2026-01"),
    "5010": ("Purchases - metal fittings", "MAT_FITTINGS", "2026-01"),
    "5100": ("Wages - production", "LAB_DIRECT", "2026-01"),
    "5110": ("Temporary staff", "LAB_TEMP", "2026-01"),
    "5200": ("Carriage outwards", "FREIGHT", "2026-01"),
    "6000": ("Electricity and gas", "ENERGY", "2026-01"),
    "6100": ("Audit, legal and consulting fees", "FEES", "2026-01"),
    "6200": ("Rent and service charges", "RENT", "2026-01"),
    "6300": ("Other overheads", "OTHER", "2026-01"),
    "6400": ("Salaries - administration and sales", "LAB_ADMIN", "2026-01"),
}
# The mapping table in the January and February workbooks predates account 4020.
MAPPING_BEFORE_MARCH = {a: v[1] for a, v in ACCOUNTS.items() if a != "4020"}

MONTHS = ["2026-01", "2026-02", "2026-03"]
BUDGET_MONTHS = [f"2026-{m:02d}" for m in range(1, 13)]

# Monthly budget (EUR, positive amounts). The online web shop was not budgeted.
_BASE_BUDGET = {
    "REV_CONTRACT": 820000, "REV_DEALER": 480000, "REV_ONLINE": 0,
    "MAT_TIMBER": 290000, "MAT_FITTINGS": 115000, "LAB_DIRECT": 255000,
    "LAB_TEMP": 8000, "FREIGHT": 44000, "ENERGY": 31000, "FEES": 15000,
    "RENT": 40000, "OTHER": 58000, "LAB_ADMIN": 120000,
}
BUDGET = {m: dict(_BASE_BUDGET) for m in BUDGET_MONTHS}
# KPC Advisory ERP phase 2 kickoff (EUR 8,000) was budgeted in April.
BUDGET["2026-04"]["FEES"] = 23000
# Budget assumptions presented in December 2025 (used in the budget deck).
BUDGET_ASSUMPTIONS = [
    "Timber prices flat versus 2025 (Brightwood Timber about EUR 150k per month at 2025 price list).",
    "Belvedere Hotel Group order BHG-2291 (EUR 45k) delivered and invoiced in March 2026.",
    "Temporary labour limited to EUR 8k per month (holiday cover only).",
    "Online web shop launch not budgeted (pilot, upside only).",
    "KPC Advisory ERP phase 2 starts in April 2026 (EUR 8k kickoff invoice).",
    "Variance threshold for commentary: EUR 5,000 per P&L line per month.",
]

# Actuals per month and line (EUR, positive amounts).
ACTUALS = {
    "2026-01": {
        "REV_CONTRACT": 818500, "REV_DEALER": 478900, "REV_ONLINE": 0,
        "MAT_TIMBER": 291200, "MAT_FITTINGS": 114300, "LAB_DIRECT": 254800,
        "LAB_TEMP": 7600, "FREIGHT": 46900, "ENERGY": 33200, "FEES": 15000,
        "RENT": 40000, "OTHER": 57400, "LAB_ADMIN": 120000,
    },
    "2026-02": {
        "REV_CONTRACT": 823100, "REV_DEALER": 481200, "REV_ONLINE": 0,
        "MAT_TIMBER": 301600, "MAT_FITTINGS": 115900, "LAB_DIRECT": 255600,
        "LAB_TEMP": 8200, "FREIGHT": 44600, "ENERGY": 31900, "FEES": 15000,
        "RENT": 40000, "OTHER": 58700, "LAB_ADMIN": 120000,
    },
    "2026-03": {
        "REV_CONTRACT": 803000, "REV_DEALER": 482500, "REV_ONLINE": 6400,
        "MAT_TIMBER": 302400, "MAT_FITTINGS": 116100, "LAB_DIRECT": 256200,
        "LAB_TEMP": 22000, "FREIGHT": 50200, "ENERGY": 25400, "FEES": 23000,
        "RENT": 40000, "OTHER": 59300, "LAB_ADMIN": 120400,
    },
}

# Named ("story") GL transactions. Amount is positive; the side follows the
# account (revenue = credit, cost = debit) unless "credit_note" is True, which
# posts a credit on a cost account. The rest of each line is generated filler.
STORY_TX = [
    # January: Brightwood at the 2025 price list.
    {"month": "2026-01", "date": "2026-01-09", "account": "5000", "party": "brightwood", "doc": "BW-INV-10412", "desc": "Oak and birch veneer panels - price list 2025", "amount": 50000},
    {"month": "2026-01", "date": "2026-01-19", "account": "5000", "party": "brightwood", "doc": "BW-INV-10467", "desc": "Oak and birch veneer panels - price list 2025", "amount": 50000},
    {"month": "2026-01", "date": "2026-01-28", "account": "5000", "party": "brightwood", "doc": "BW-INV-10519", "desc": "Oak and birch veneer panels - price list 2025", "amount": 50000},
    # February: +8% price list from 1 February (145k volume at old prices = 156.6k).
    {"month": "2026-02", "date": "2026-02-06", "account": "5000", "party": "brightwood", "doc": "BW-INV-10588", "desc": "Oak and birch veneer panels - price list 2026-02", "amount": 52200},
    {"month": "2026-02", "date": "2026-02-16", "account": "5000", "party": "brightwood", "doc": "BW-INV-10631", "desc": "Oak and birch veneer panels - price list 2026-02", "amount": 52200},
    {"month": "2026-02", "date": "2026-02-25", "account": "5000", "party": "brightwood", "doc": "BW-INV-10690", "desc": "Oak and birch veneer panels - price list 2026-02", "amount": 52200},
    # March: 150k volume at +8% = 162k.
    {"month": "2026-03", "date": "2026-03-06", "account": "5000", "party": "brightwood", "doc": "BW-INV-10744", "desc": "Oak and birch veneer panels - price list 2026-02", "amount": 54000},
    {"month": "2026-03", "date": "2026-03-16", "account": "5000", "party": "brightwood", "doc": "BW-INV-10802", "desc": "Oak and birch veneer panels - price list 2026-02", "amount": 54000},
    {"month": "2026-03", "date": "2026-03-26", "account": "5000", "party": "brightwood", "doc": "BW-INV-10861", "desc": "Oak and birch veneer panels - price list 2026-02", "amount": 54000},
    # March: Harbour City rush order (extra revenue).
    {"month": "2026-03", "date": "2026-03-27", "account": "4000", "party": "harbour", "doc": "SI-260388", "desc": "Order HCC-0457 - school furniture, rush delivery", "amount": 28000},
    # March: StaffBridge temporary operatives (the reason is only said in a meeting).
    {"month": "2026-03", "date": "2026-03-31", "account": "5110", "party": "staffbridge", "doc": "SB-7781", "desc": "3 temporary operatives, 9-27 March, production", "amount": 14000},
    # March: Atlantic Freight express surcharges (no explanation anywhere).
    {"month": "2026-03", "date": "2026-03-14", "account": "5200", "party": "atlantic", "doc": "AFS-0326-A", "desc": "Surcharge - service code EXP", "amount": 2100},
    {"month": "2026-03", "date": "2026-03-20", "account": "5200", "party": "atlantic", "doc": "AFS-0326-B", "desc": "Surcharge - service code EXP", "amount": 1900},
    {"month": "2026-03", "date": "2026-03-27", "account": "5200", "party": "atlantic", "doc": "AFS-0326-C", "desc": "Surcharge - service code EXP", "amount": 2200},
    # March: Celtic Energy credit note (one-off meter correction for Q4 2025).
    {"month": "2026-03", "date": "2026-03-23", "account": "6000", "party": "celtic", "doc": "CN-55821", "desc": "Credit note - meter reading correction Oct-Dec 2025", "amount": 5600, "credit_note": True},
    # March: KPC Advisory ERP phase 2 kickoff (budgeted in April).
    {"month": "2026-03", "date": "2026-03-27", "account": "6100", "party": "kpc", "doc": "KPC-2026-031", "desc": "ERP phase 2 - kickoff workshop and design", "amount": 8000},
]

# Counterparties used to spread the remaining (filler) amount of each account.
FILLER_PARTIES = {
    "4000": ["belvedere", "harbour", "quayside", "meridian", "lough"],
    "4010": ["deskworks", "officeline", "workspace_hub"],
    "4020": [None],
    "5000": ["oakfield", "nordboard"],
    "5010": ["halvorsen"],
    "5100": [None],
    "5110": ["staffbridge"],
    "5200": ["atlantic"],
    "6000": ["celtic"],
    "6100": ["harrowgate", "quaylaw"],
    "6200": [None],
    "6300": [None],
    "6400": [None],
}
# Belvedere order BHG-2291 slipped to April: no Belvedere revenue in March.
NO_FILLER = {("2026-03", "4000", "belvedere")}
FILLER_DESC = {
    "4000": "Contract delivery", "4010": "Dealer order", "4020": "Web shop orders (daily batch)",
    "5000": "Panels and boards", "5010": "Hinges, frames and fittings", "5100": "Production payroll",
    "5110": "Holiday cover operative", "5200": "Standard road freight", "6000": "Monthly energy invoice",
    "6100": "Monthly retainer", "6200": "Rent and service charge", "6300": "Overheads",
    "6400": "Admin and sales payroll",
}
FILLER_COUNT = {"4000": 9, "4010": 7, "4020": 6, "5000": 6, "5010": 4, "5100": 2, "5110": 1,
                "5200": 4, "6000": 1, "6100": 2, "6200": 1, "6300": 8, "6400": 2}

# Expected March analysis (answer key). Drivers must add up to the line variance.
MARCH_DRIVERS = {
    "REV_CONTRACT": [
        {"driver": "Belvedere Hotel Group order BHG-2291 slipped from March to 14 April (hotel refurbishment late)", "amount": -45000, "type": "timing", "evidence": ["E06", "C03"]},
        {"driver": "Harbour City Council rush order HCC-0457 delivered in March (not budgeted)", "amount": 28000, "type": "volume", "evidence": ["M01", "E12", "GL:SI-260388"]},
        {"driver": "Other contract customers", "amount": 0, "type": "other", "evidence": []},
    ],
    "REV_ONLINE": [
        {"driver": "New web shop launched 1 March; account 4020 not in the mapping table and not budgeted", "amount": 6400, "type": "new activity", "evidence": ["E13", "C06"]},
    ],
    "MAT_TIMBER": [
        {"driver": "Brightwood Timber price list +8% from 1 February (same explanation as February)", "amount": -12000, "type": "price", "evidence": ["E01", "E02", "COMMENTARY:2026-02", "GL:BW-INV-10744"]},
        {"driver": "Other timber suppliers, volume", "amount": -400, "type": "volume", "evidence": []},
    ],
    "LAB_TEMP": [
        {"driver": "3 StaffBridge operatives (9-27 March) for the Harbour City rush order, decided in the production meeting of 5 March", "amount": -14000, "type": "volume", "evidence": ["M01", "E07", "GL:SB-7781"]},
    ],
    "FREIGHT": [
        {"driver": "Atlantic Freight express surcharges (service code EXP) - reason not found in any mail, chat or meeting", "amount": -6200, "type": "unexplained", "evidence": ["GL:AFS-0326-A", "E14"]},
    ],
    "ENERGY": [
        {"driver": "Celtic Energy credit note CN-55821, meter reading correction for Oct-Dec 2025 (one-off)", "amount": 5600, "type": "one-off", "evidence": ["E09", "D03"]},
    ],
    "FEES": [
        {"driver": "KPC Advisory ERP phase 2 kickoff invoiced in March, budgeted in April (CFO approved early start)", "amount": -8000, "type": "timing", "evidence": ["E10", "E11", "D04"]},
    ],
}

# Expected "repeats next month?" answer per material March line.
MARCH_REPEATS = {
    "REV_CONTRACT": "No. Belvedere reverses in April (+45,000 expected on 14 April); Harbour City was a one-off rush order.",
    "REV_ONLINE": "Yes. New sales channel; add it to the budget reforecast.",
    "MAT_TIMBER": "Yes, and worse: Brightwood adds +3% from 1 May (about 16,900 per month versus budget).",
    "LAB_TEMP": "No. The assignment ended on 27 March.",
    "FREIGHT": "Unknown until Sofia Lindqvist explains the EXP surcharges.",
    "ENERGY": "No. One-off credit note.",
    "FEES": "Reverses in April: April fees will look 8,000 favourable (timing).",
}
