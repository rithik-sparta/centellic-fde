"""A labelled eval set for retrieval and answer quality, built for documents.py (credit documents).

Each answerable question records:
  doc_id    the document that holds the answer
  evidence  a short verbatim span from that document. A retrieved chunk counts as a hit
            only if it contains this exact span, so a chunk that cuts the span in half
            is a miss. That is deliberate: it is how chunking damage shows up in the numbers.
  keywords  what a correct answer must mention. Every item must appear in the answer.
            "a|b" means either a or b is acceptable. Matching is case-insensitive and
            whole-word, so "no" does not match inside "not". A trailing * allows any
            ending, so "exclud*" matches "excluded" and "excludes". A refusal never
            counts as correct, whatever words it happens to contain.
  kind      what the question tests

Unanswerable questions have doc_id None and no evidence. The correct behaviour is refusal.

Kinds used here:
  numeric            a figure that must be reported exactly
  lookup             a plain fact stated in one place
  negation           the answer is a "no" / "not" / "none" or a non-event
  title-dependent    the borrower or document is named only in the title or header, so a chunk
                     from further down the text may not say whose figure it is
  heading-dependent  the subject is named earlier in the document and the span sits under it
  disambiguation     the same borrower or term appears in several documents; the question must
                     be tied to the right one
  rare-term          depends on a specific uncommon word (debenture, unsecured, reimbursement)
"""

EVAL_SET = [
    # Northbridge Components annual credit review (doc-01)
    {"id": "q01", "question": "What is Northbridge Components' net leverage in its annual credit review?",
     "doc_id": "doc-01", "evidence": "Net leverage 2.59x; interest cover 5.37x", "keywords": ["2.59"], "kind": "title-dependent"},
    {"id": "q02", "question": "What internal rating change does the Northbridge Components credit review support?",
     "doc_id": "doc-01", "evidence": "improvement in internal rating from rank 8 to rank 7", "keywords": ["8", "7"], "kind": "lookup"},
    {"id": "q03", "question": "How much of the Northbridge Components term loan is undrawn?",
     "doc_id": "doc-01", "evidence": "GBP0.4m undrawn on the term loan", "keywords": ["0.4m|0.4|400,000"], "kind": "numeric"},
    {"id": "q04", "question": "What is the leverage covenant level that Northbridge Components' leverage remains within?",
     "doc_id": "doc-01", "evidence": "Leverage remains comfortably within the 4.00x covenant", "keywords": ["4.00x|4.00|4.0x|4x"], "kind": "numeric"},
    {"id": "q05", "question": "What was Northbridge Components' operating cash flow for the period?",
     "doc_id": "doc-01", "evidence": "Operating cash flow GBP1.7m", "keywords": ["1.7"], "kind": "numeric"},

    # Calder Food Retail trading outlook (doc-02)
    {"id": "q06", "question": "What interest cover does Calder Food Retail report in its trading outlook?",
     "doc_id": "doc-02", "evidence": "Net leverage 10.48x; interest cover 1.44x", "keywords": ["1.44"], "kind": "disambiguation"},
    {"id": "q07", "question": "Was Calder Food Retail's June mandatory prepayment paid on time?",
     "doc_id": "doc-02", "evidence": "The June mandatory prepayment was paid late", "keywords": ["late|not on time|no"], "kind": "negation"},
    {"id": "q08", "question": "What does the Calder Food Retail trading outlook recommend?",
     "doc_id": "doc-02", "evidence": "recommend enhanced monitoring and a credible deleveraging plan", "keywords": ["enhanced monitoring", "deleveraging"], "kind": "lookup"},

    # Westmoor Renewables financial performance report (doc-03)
    {"id": "q09", "question": "What interest cover does Westmoor Renewables report?",
     "doc_id": "doc-03", "evidence": "interest cover 6.26x", "keywords": ["6.26"], "kind": "title-dependent"},
    {"id": "q10", "question": "How are lease liabilities treated in Westmoor Renewables' covenant-defined EBITDA and debt?",
     "doc_id": "doc-03", "evidence": "with lease liabilities excluded from debt", "keywords": ["exclud*"], "kind": "rare-term"},
    {"id": "q11", "question": "What internal rating change does the Westmoor Renewables report support?",
     "doc_id": "doc-03", "evidence": "upgrade from rank 6 to rank 5", "keywords": ["6", "5"], "kind": "lookup"},
    {"id": "q12", "question": "What is the size of the Westmoor Renewables facility?",
     "doc_id": "doc-03", "evidence": "GBP7.5m senior secured term loan", "keywords": ["7.5"], "kind": "title-dependent"},

    # Oakridge Logistics covenant summary (doc-04)
    {"id": "q13", "question": "What is the maximum net debt to EBITDA ratio Oakridge Logistics must maintain?",
     "doc_id": "doc-04", "evidence": "at or below 4.75x", "keywords": ["4.75"], "kind": "numeric"},
    {"id": "q14", "question": "Within how many days of quarter end must Oakridge Logistics deliver its covenant compliance certificate?",
     "doc_id": "doc-04", "evidence": "must be delivered to the lender within 20 days of each quarter end", "keywords": ["20"], "kind": "disambiguation"},
    {"id": "q15", "question": "Under what security document can the Oakridge Logistics lender enforce its security?",
     "doc_id": "doc-04", "evidence": "enforce its security under the all-assets debenture", "keywords": ["debenture"], "kind": "rare-term"},
    {"id": "q16", "question": "Are lease liabilities included in debt for the Oakridge Logistics leverage covenant?",
     "doc_id": "doc-04", "evidence": "lease liabilities are included in debt", "keywords": ["includ*|yes"], "kind": "disambiguation"},
    {"id": "q17", "question": "Is late delivery of the compliance certificate an event of default for Oakridge Logistics?",
     "doc_id": "doc-04", "evidence": "or to deliver the compliance certificate on time, constitutes an event of default", "keywords": ["event of default"], "kind": "lookup"},

    # 2026 corporate lending policy update (doc-05)
    {"id": "q18", "question": "What is the maximum net leverage under the 2026 general corporate lending policy?",
     "doc_id": "doc-05", "evidence": "Maximum net leverage: 5.5x", "keywords": ["5.5"], "kind": "numeric"},
    {"id": "q19", "question": "What is the minimum interest cover under the 2026 general corporate lending policy?",
     "doc_id": "doc-05", "evidence": "Minimum interest cover: 2.25x", "keywords": ["2.25"], "kind": "numeric"},
    {"id": "q20", "question": "What are the Leisure sector limits for leverage and interest cover in the lending policy?",
     "doc_id": "doc-05", "evidence": "maximum leverage 4.0x, minimum interest cover 3.0x", "keywords": ["4.0", "3.0"], "kind": "numeric"},
    {"id": "q21", "question": "Which policy is Transport lending assessed against in the 2026 corporate lending policy update?",
     "doc_id": "doc-05", "evidence": "Transport is assessed against this general policy pending a dedicated sector overlay", "keywords": ["general"], "kind": "heading-dependent"},
    {"id": "q22", "question": "What is the maximum internal rating rank under the 2026 general lending policy?",
     "doc_id": "doc-05", "evidence": "Maximum internal rating rank: 15", "keywords": ["15"], "kind": "numeric"},
    {"id": "q23", "question": "When did the 2026 general corporate lending policy take effect?",
     "doc_id": "doc-05", "evidence": "Effective: 01-Jan-26", "keywords": ["01-Jan-26|1 January 2026|1 Jan 2026|January 2026"], "kind": "lookup"},
    {"id": "q24", "question": "Do facilities under the general corporate lending policy require security?",
     "doc_id": "doc-05", "evidence": "Facilities require security", "keywords": ["yes|require*"], "kind": "lookup"},

    # Merefield Leisure restructuring case (doc-06)
    {"id": "q25", "question": "What is Merefield Leisure's interest cover?",
     "doc_id": "doc-06", "evidence": "net leverage 14.00x; interest cover 0.82x", "keywords": ["0.82"], "kind": "title-dependent"},
    {"id": "q26", "question": "How large is the scheduled principal instalment that Merefield Leisure missed?",
     "doc_id": "doc-06", "evidence": "A GBP0.6m scheduled principal instalment has been missed", "keywords": ["0.6"], "kind": "numeric"},
    {"id": "q27", "question": "What security remains available to the Merefield Leisure lender?",
     "doc_id": "doc-06", "evidence": "Property security remains available to the lender", "keywords": ["property"], "kind": "lookup"},
    {"id": "q28", "question": "Is the Merefield Leisure case treated as ordinary relationship management?",
     "doc_id": "doc-06", "evidence": "This is a restructuring and recovery case rather than ordinary relationship management", "keywords": ["no|not|rather than"], "kind": "negation"},
    {"id": "q29", "question": "Is the Merefield Leisure term loan fully drawn?",
     "doc_id": "doc-06", "evidence": "GBP7.0m senior secured term loan, fully drawn", "keywords": ["fully drawn|yes"], "kind": "title-dependent"},

    # Calder Food Retail covenant amendment summary (doc-07)
    {"id": "q30", "question": "What was the original net debt to EBITDA covenant level in the Calder Food Retail facility agreement?",
     "doc_id": "doc-07", "evidence": "net debt to EBITDA at or below 4.50x", "keywords": ["4.50"], "kind": "numeric"},
    {"id": "q31", "question": "What was Calder Food Retail's leverage at the 31 March 2026 covenant test?",
     "doc_id": "doc-07", "evidence": "leverage measured at 4.72x", "keywords": ["4.72"], "kind": "numeric"},
    {"id": "q32", "question": "To what level did the temporary amendment raise the Calder Food Retail leverage threshold?",
     "doc_id": "doc-07", "evidence": "raised the threshold to 5.00x", "keywords": ["5.00|5.0x|5x"], "kind": "numeric"},
    {"id": "q33", "question": "When did the temporary covenant amendment for Calder Food Retail take effect?",
     "doc_id": "doc-07", "evidence": "effective 1 April 2026", "keywords": ["1 April 2026|April 2026"], "kind": "lookup"},
    {"id": "q34", "question": "Did Calder Food Retail pass the leverage test after the temporary amendment?",
     "doc_id": "doc-07", "evidence": "leverage was measured at 10.48x against the amended 5.00x threshold", "keywords": ["no|not|fail*|breach*"], "kind": "negation"},
    {"id": "q35", "question": "Can the Calder Food Retail lender charge a fee to agree a further waiver or amendment?",
     "doc_id": "doc-07", "evidence": "charge a fee to agree any further waiver or amendment", "keywords": ["fee"], "kind": "disambiguation"},

    # Harbourview Care Services operating outlook (doc-08)
    {"id": "q36", "question": "What is Harbourview Care Services' net leverage?",
     "doc_id": "doc-08", "evidence": "Net leverage 3.16x; interest cover 3.80x", "keywords": ["3.16"], "kind": "title-dependent"},
    {"id": "q37", "question": "Is the Harbourview Care Services term loan secured or unsecured?",
     "doc_id": "doc-08", "evidence": "GBP6.5m senior unsecured term loan", "keywords": ["unsecured"], "kind": "rare-term"},
    {"id": "q38", "question": "How much facility availability remains for Harbourview Care Services?",
     "doc_id": "doc-08", "evidence": "GBP0.7m of facility availability remains", "keywords": ["0.7"], "kind": "numeric"},
    {"id": "q39", "question": "Was Harbourview Care Services' scheduled July principal repayment made on time?",
     "doc_id": "doc-08", "evidence": "The scheduled July principal repayment was met on the due date", "keywords": ["met|on time|due date|paid"], "kind": "lookup"},
    {"id": "q40", "question": "Does the Harbourview Care Services outlook propose any change to its internal rating?",
     "doc_id": "doc-08", "evidence": "No change to internal rating rank 7 is proposed", "keywords": ["no change|unchanged|no|not"], "kind": "negation"},

    # Aldergate Business Solutions credit memo (doc-09)
    {"id": "q41", "question": "What is Aldergate Business Solutions' net leverage in its credit memo?",
     "doc_id": "doc-09", "evidence": "Net leverage 3.37x; interest cover 2.90x", "keywords": ["3.37"], "kind": "title-dependent"},
    {"id": "q42", "question": "Has Aldergate Business Solutions been assigned an internal rating yet?",
     "doc_id": "doc-09", "evidence": "no internal rating has yet been assigned to this relationship", "keywords": ["no|not|none|yet"], "kind": "negation"},
    {"id": "q43", "question": "Does Aldergate Business Solutions hold an external agency rating?",
     "doc_id": "doc-09", "evidence": "No external agency rating is held", "keywords": ["no|not|none"], "kind": "negation"},
    {"id": "q44", "question": "Why was the Aldergate Business Solutions credit memo prepared?",
     "doc_id": "doc-09", "evidence": "to bring the relationship into the formal internal rating process for the first time", "keywords": ["first time|first-time|initial*"], "kind": "lookup"},
    {"id": "q45", "question": "How much of the Aldergate Business Solutions term loan is undrawn?",
     "doc_id": "doc-09", "evidence": "GBP0.9m undrawn on the term loan", "keywords": ["0.9"], "kind": "numeric"},

    # Aldergate Business Solutions covenant summary (doc-10)
    {"id": "q46", "question": "What minimum interest cover must Aldergate Business Solutions maintain under its covenant?",
     "doc_id": "doc-10", "evidence": "interest cover (EBITDA divided by net interest) at or above 2.75x", "keywords": ["2.75"], "kind": "numeric"},
    {"id": "q47", "question": "On what basis is the Aldergate Business Solutions interest cover covenant tested?",
     "doc_id": "doc-10", "evidence": "tested quarterly on a reported basis", "keywords": ["reported"], "kind": "lookup"},
    {"id": "q48", "question": "How soon must Aldergate Business Solutions deliver its quarterly management accounts to the lender?",
     "doc_id": "doc-10", "evidence": "quarterly management accounts must be delivered to the lender within 30 days of each quarter end", "keywords": ["30"], "kind": "disambiguation"},
    {"id": "q49", "question": "What assets can the Aldergate Business Solutions lender enforce its security over?",
     "doc_id": "doc-10", "evidence": "enforce its security over business assets and receivables", "keywords": ["business assets","receivables"], "kind": "lookup"},

    # Rating direction summaries (doc-11)
    {"id": "q50", "question": "What rating direction is expected for Northbridge Components at the next assessment?",
     "doc_id": "doc-11", "evidence": "Northbridge Components Ltd (Manufacturing): likely upgrade", "keywords": ["upgrade"], "kind": "disambiguation"},
    {"id": "q51", "question": "What rating direction is expected for Oakridge Logistics at the next assessment?",
     "doc_id": "doc-11", "evidence": "likely to stay the same for now, with a downward bias", "keywords": ["same", "downward"], "kind": "heading-dependent"},
    {"id": "q52", "question": "Of the borrowers whose rank is expected to stay stable, which is the most exposed to a downgrade?",
     "doc_id": "doc-11", "evidence": "Of the borrowers whose rank is currently stable, it is the most exposed", "keywords": ["Oakridge"], "kind": "heading-dependent"},
    {"id": "q53", "question": "What is the main weakness identified for Aldergate Business Solutions in the rating direction summaries?",
     "doc_id": "doc-11", "evidence": "The main weakness is thin interest cover headroom", "keywords": ["interest cover"], "kind": "heading-dependent"},
    {"id": "q54", "question": "Are Aldergate Business Solutions' earnings reported with adjustments?",
     "doc_id": "doc-11", "evidence": "Earnings are reported without adjustments", "keywords": ["without adjustments|unadjusted|no adjustments|not adjusted"], "kind": "negation"},
    {"id": "q55", "question": "Which covenants has Calder Food Retail breached according to the rating direction summaries?",
     "doc_id": "doc-11", "evidence": "It has breached both its original and its temporary leverage covenant", "keywords": ["original", "temporary"], "kind": "heading-dependent"},
    {"id": "q56", "question": "What are the main watch items for Westmoor Renewables in the rating direction summaries?",
     "doc_id": "doc-11", "evidence": "Heavy capital expenditure and merchant power price exposure are the main watch items", "keywords": ["capital expenditure|capex", "merchant"], "kind": "heading-dependent"},
    {"id": "q57", "question": "What rating direction is expected for Merefield Leisure Holdings?",
     "doc_id": "doc-11", "evidence": "Merefield Leisure Holdings Ltd (Leisure): likely downgrade", "keywords": ["downgrade"], "kind": "lookup"},

    # Sector outlook summary (doc-12)
    {"id": "q58", "question": "What is the outlook for the Retail sector in the sector outlook summary?",
     "doc_id": "doc-12", "evidence": "Retail: negative. Earnings are sensitive to consumer demand", "keywords": ["negative"], "kind": "heading-dependent"},
    {"id": "q59", "question": "What is the outlook for the Energy sector?",
     "doc_id": "doc-12", "evidence": "Energy: stable to positive", "keywords": ["positive"], "kind": "lookup"},
    {"id": "q60", "question": "Which sector is described as the most cyclical?",
     "doc_id": "doc-12", "evidence": "it is the most cyclical sector and carries the tightest policy limits", "keywords": ["Leisure"], "kind": "heading-dependent"},
    {"id": "q61", "question": "What is the main margin pressure in the Business Services sector?",
     "doc_id": "doc-12", "evidence": "wage costs are the main margin pressure", "keywords": ["wage"], "kind": "heading-dependent"},
    {"id": "q62", "question": "What are the main watch items for the Healthcare sector?",
     "doc_id": "doc-12", "evidence": "staffing cost inflation and any change to reimbursement terms", "keywords": ["staffing", "reimbursement"], "kind": "rare-term"},
    {"id": "q63", "question": "What cost pressure do Transport operators face according to the sector outlook?",
     "doc_id": "doc-12", "evidence": "operators face fleet replacement costs", "keywords": ["fleet"], "kind": "heading-dependent"},
    {"id": "q64", "question": "What time horizon does the sector outlook summary cover?",
     "doc_id": "doc-12", "evidence": "Horizon: next 12 months", "keywords": ["12 months|twelve months"], "kind": "lookup"},

    # Unanswerable: the corpus does not contain these answers
    {"id": "q65", "question": "What is the capital of France?",
     "doc_id": None, "evidence": None, "keywords": [], "kind": "unanswerable"},
    {"id": "q66", "question": "Who is the chief executive of Northbridge Components?",
     "doc_id": None, "evidence": None, "keywords": [], "kind": "unanswerable"},
    {"id": "q67", "question": "What interest margin is charged on the Oakridge Logistics revolving facility?",
     "doc_id": None, "evidence": None, "keywords": [], "kind": "unanswerable"},
    {"id": "q68", "question": "What is the leverage covenant threshold on the Harbourview Care Services loan?",
     "doc_id": None, "evidence": None, "keywords": [], "kind": "unanswerable"},
    {"id": "q69", "question": "What is the valuation of the property security held over Merefield Leisure?",
     "doc_id": None, "evidence": None, "keywords": [], "kind": "unanswerable"},
    {"id": "q70", "question": "What maximum leverage does the Retail sector-specific policy allow?",
     "doc_id": None, "evidence": None, "keywords": [], "kind": "unanswerable"},
    {"id": "q71", "question": "What was Westmoor Renewables' net leverage at the end of 2025?",
     "doc_id": None, "evidence": None, "keywords": [], "kind": "unanswerable"},
]


def answerable() -> list[dict]:
    return [q for q in EVAL_SET if q["doc_id"] is not None]


def unanswerable() -> list[dict]:
    return [q for q in EVAL_SET if q["doc_id"] is None]
