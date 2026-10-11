# Synthetic supporting credit documents.
# All names and contents are fictional and created for modelling purposes.

documents : list[dict] = [
    {
        "id": "doc-01",
        "date": "05-08-2026",
        "type": "credit-memo",
        "title": "Northbridge Components annual credit review",
        "text": "NORTHBRIDGE COMPONENTS LTD — ANNUAL CREDIT REVIEW\nSector: Manufacturing | Facility: GBP6.0m senior secured term loan | Period: H1 2026 to 30-Jun-26\n\nNet leverage 2.59x; interest cover 5.37x. Operating cash flow GBP1.7m. GBP0.4m undrawn on the term loan. Leverage remains comfortably within the 4.00x covenant.\n\nThe review supports an improvement in internal rating from rank 8 to rank 7. Key considerations: a deleveraging trend, positive cash generation and adequate covenant headroom. Industrial demand and input-cost volatility remain monitoring points."
    },
    {
        "id": "doc-02",
        "date": "06-08-2026",
        "type": "outlook",
        "title": "Calder Food Retail trading outlook",
        "text": "CALDER FOOD RETAIL LTD — TRADING OUTLOOK\nSector: Retail | Facility: GBP9.0m revolving facility | As at: 30-Jun-26\n\nNet leverage 10.48x; interest cover 1.44x. Margin pressure and higher financing costs persist. The June mandatory prepayment was paid late, though the amount due has since been settled.\n\nOutlook depends on cost reduction, asset disposals and stabilisation of like-for-like sales. Position is materially weaker than the prior review; recommend enhanced monitoring and a credible deleveraging plan."
    },
    {
        "id": "doc-03",
        "date": "07-08-2026",
        "type": "report",
        "title": "Westmoor Renewables financial performance report",
        "text": "WESTMOOR RENEWABLES LTD — FINANCIAL PERFORMANCE REPORT\nSector: Energy | Facility: GBP7.5m senior secured term loan | Period: six months to 30-Jun-26\n\nNet leverage 1.70x; interest cover 6.26x; operating cash flow GBP2.3m, supported by contracted renewable generation revenue. EBITDA is stated on a covenant-defined basis, with lease liabilities excluded from debt.\n\nCapital expenditure remains elevated against the generation build-out, but liquidity and covenant headroom are substantial. Evidence supports an internal rating upgrade from rank 6 to rank 5."
    },
    {
        "id": "doc-04",
        "date": "08-08-2026",
        "type": "covenant-summary",
        "title": "Covenant summary — Oakridge Logistics Group revolving facility",
        "text": "OAKRIDGE LOGISTICS GROUP LTD — COVENANT SUMMARY\nFacility: GBP8.0m revolving facility, senior secured\n\nFinancial covenant: the borrower shall maintain net debt to EBITDA at or below 4.75x, tested quarterly on a trailing twelve-month basis. EBITDA is adjusted and lease liabilities are included in debt.\n\nReporting: quarterly management accounts and a covenant compliance certificate must be delivered to the lender within 30 days of each quarter end.\n\nConsequence of breach: failure to meet the leverage test, or to deliver the compliance certificate on time, constitutes an event of default under the facility agreement.\n\nLender's rights: on an event of default the lender may suspend further drawdowns, require a cash sweep of surplus receipts, charge a fee to agree a waiver or amendment, or accelerate repayment and enforce its security under the all-assets debenture, including the assignment of customer receivables."
    },
    {
        "id": "doc-05",
        "date": "09-08-2026",
        "type": "lending-policy",
        "title": "2026 corporate lending policy update",
        "text": "CORPORATE LENDING POLICY — 2026 GENERAL UPDATE\nGeneral corporate lending policy | Effective: 01-Jan-26\n\n1. Scope. Applies to all corporate borrowers in sectors without an active sector-specific policy.\n2. Limits. Maximum internal rating rank: 15. Maximum net leverage: 5.5x. Minimum interest cover: 2.25x. Facilities require security.\n3. Exposure. Assessments shall consider total committed exposure and available security before recommending new or amended facilities.\n4. Cyclical sectors. Retail, Transport and Leisure show recurring earnings volatility. Lending decisions in these sectors shall not rely on peak trading performance; assessments shall use sustainable or through-cycle earnings with downside sensitivity testing. Retail and Leisure are subject to additional sector-specific limits; Transport is assessed against this general policy pending a dedicated sector overlay.\n5. Leisure overlay. Leisure carries the tightest sector-specific limits (maximum leverage 4.0x, minimum interest cover 3.0x) because occupancy and discretionary spending can weaken rapidly in a downturn."
    },
    {
        "id": "doc-06",
        "date": "10-08-2026",
        "type": "restructuring-case-study",
        "title": "Merefield Leisure restructuring case",
        "text": "MEREFIELD LEISURE HOLDINGS LTD — RESTRUCTURING CASE NOTE\nFacility: GBP7.0m senior secured term loan, fully drawn | Status: Defaulted\n\nPosition: net leverage 14.00x; interest cover 0.82x; operating cash flow negative. A GBP0.6m scheduled principal instalment has been missed. Property security remains available to the lender.\n\nThis is a restructuring and recovery case rather than ordinary relationship management. Workstreams: (1) revised cash-flow forecast; (2) property valuation; (3) stakeholder discussions; (4) assess whether the existing capital structure is supportable on sustainable through-cycle earnings."
    },
    {
        "id": "doc-07",
        "date": "15-07-2026",
        "type": "covenant-summary",
        "title": "Calder Food Retail covenant amendment summary",
        "text": "CALDER FOOD RETAIL LTD — COVENANT AMENDMENT SUMMARY\nFacility: GBP9.0m revolving facility\n\nThe original facility agreement required net debt to EBITDA at or below 4.50x, tested quarterly. The borrower breached this covenant at the 31 March 2026 test, with leverage measured at 4.72x.\n\nA temporary amendment, effective 1 April 2026, raised the threshold to 5.00x. At the following quarterly test, leverage was measured at 10.48x against the amended 5.00x threshold — a further breach.\n\nA breach of the leverage covenant is an event of default under the facility agreement. The lender may decline further drawdowns under the revolver, require additional security or cash cover, charge a fee to agree any further waiver or amendment, or accelerate repayment and enforce its security."
    },
    {
        "id": "doc-08",
        "date": "12-08-2026",
        "type": "outlook",
        "title": "Harbourview Care Services operating outlook",
        "text": "HARBOURVIEW CARE SERVICES LTD — OPERATING OUTLOOK\nSector: Healthcare | Facility: GBP6.5m senior unsecured term loan | As at: 30-Jun-26\n\nNet leverage 3.16x; interest cover 3.80x; operating cash flow GBP1.6m. GBP0.7m of facility availability remains. The scheduled July principal repayment was met on the due date.\n\nDemand remains stable. Staffing cost inflation and customer concentration are the main watch items, offset by stable occupancy and long-term care contracts. No change to internal rating rank 7 is proposed."
    },
    {
        "id": "doc-09",
        "date": "11-08-2026",
        "type": "credit-memo",
        "title": "Aldergate Business Solutions initial internal rating review",
        "text": "ALDERGATE BUSINESS SOLUTIONS LTD — CREDIT MEMO\nSector: Business Services | Facility: GBP6.5m senior secured term loan | Period: H1 2026 to 30-Jun-26\n\nNet leverage 3.37x; interest cover 2.90x. Operating cash flow GBP1.15m. GBP0.9m undrawn on the term loan. No external agency rating is held, and no internal rating has yet been assigned to this relationship.\n\nThis review has been prepared to bring the relationship into the formal internal rating process for the first time, using the facility terms, covenant and financial information on file. The facility and financial position are submitted for internal rating and credit committee review."
    },
    {
        "id": "doc-10",
        "date": "11-08-2026",
        "type": "covenant-summary",
        "title": "Aldergate Business Solutions covenant summary",
        "text": "ALDERGATE BUSINESS SOLUTIONS LTD — COVENANT SUMMARY\nFacility: GBP6.5m senior secured term loan\n\nFinancial covenant: the borrower shall maintain interest cover (EBITDA divided by net interest) at or above 2.75x, tested quarterly on a reported basis.\n\nReporting: quarterly management accounts must be delivered to the lender within 30 days of each quarter end.\n\nConsequence of breach: failure to meet the interest cover test, or to deliver management accounts on time, constitutes an event of default under the facility agreement.\n\nLender's rights: on an event of default the lender may suspend further drawdowns, require additional security, charge a fee to agree a waiver, or accelerate repayment and enforce its security over business assets and receivables."
    },
        {
        "id": "doc-11",
        "date": "14-08-2026",
        "type": "report",
        "title": "Rating direction summaries for each borrower",
        "text": "BORROWER RATING DIRECTION SUMMARIES\nScope: all borrowers | Expected direction of internal rank at the next assessment\n\nNorthbridge Components Ltd (Manufacturing): likely upgrade. Leverage has come down, debt service is strong, operating cash flow is positive and repayments have been made on time. Covenant headroom is healthy. Industrial demand and input cost volatility are the main watch items.\nCalder Food Retail Ltd (Retail): likely downgrade. Earnings have fallen while debt has risen, leaving the borrower well outside its sector policy limits. It has breached both its original and its temporary leverage covenant, and a mandatory repayment was paid late. Further weakening is possible if the proposed disposals and cost reductions do not deliver.\nWestmoor Renewables Ltd (Energy): likely upgrade. Leverage is low, interest cover is strong and the borrower holds substantial cash, backed by long-dated contracted revenues and asset security. Covenant headroom is wide. Heavy capital expenditure and merchant power price exposure are the main watch items.\nHarbourview Care Services Ltd (Healthcare): likely to stay the same. Demand is defensive, occupancy and long-term care contracts are stable, and scheduled repayments are being met on time. Staffing cost inflation and customer concentration are the main watch items but do not justify a change in either direction.\nOakridge Logistics Group Ltd (Transport): likely to stay the same for now, with a downward bias. Cash generation is positive and the leverage covenant passes, but headroom has narrowed and a scheduled repayment was only partly paid. Freight volumes are cyclical, so a dip in earnings could trigger a downgrade. Of the borrowers whose rank is currently stable, it is the most exposed.\nMerefield Leisure Holdings Ltd (Leisure): likely downgrade. The borrower is in default after missing a scheduled principal payment, earnings do not cover interest and operating cash flow is negative. No improvement is expected while the case remains in restructuring and recovery review. Property security is the main mitigant.\nAldergate Business Solutions Ltd (Business Services): not yet ranked, so no direction is given. The borrower is profitable and cash generative, leverage is within the general lending policy limits, repayments have been made on time and part of the secured facility is undrawn. The main weakness is thin interest cover headroom, so a modest rise in financing costs or a fall in earnings would breach the covenant. Earnings are reported without adjustments."
    },
    {
        "id": "doc-12",
        "date": "14-08-2026",
        "type": "outlook",
        "title": "Sector outlook summary across all lending sectors",
        "text": "SECTOR OUTLOOK SUMMARY: ALL LENDING SECTORS\nCoverage: Manufacturing, Retail, Energy, Healthcare, Transport, Leisure, Business Services | Horizon: next 12 months\n\nOverall outlook is mixed: stable for Manufacturing, Energy, Healthcare and Business Services, and cautious to negative for the three cyclical sectors named in lending policy (Retail, Transport and Leisure), where earnings volatility and higher financing costs are reducing covenant headroom. Lending in cyclical sectors should rely on sustainable or through-cycle earnings with downside testing, not peak trading.\n\nManufacturing: stable. Demand follows industrial activity and input costs remain volatile, so margins are sensitive to both.\nRetail: negative. Earnings are sensitive to consumer demand, and promotional pressure, rent inflation and higher financing costs are squeezing margins.\nEnergy: stable to positive. Contracted renewable revenues give good earnings visibility; merchant power price exposure and capital expenditure are the main risks.\nHealthcare: stable. Demand is defensive; staffing cost inflation and any change to reimbursement terms are the main watch items.\nTransport: cautious. Freight volumes follow the economic cycle and operators face fleet replacement costs; the sector is assessed against the general lending policy pending a dedicated sector overlay.\nLeisure: negative. Occupancy and discretionary spending can weaken quickly and interest costs add pressure; it is the most cyclical sector and carries the tightest policy limits.\nBusiness Services: stable. Demand follows corporate budgets and contract renewals; wage costs are the main margin pressure."
    }
]
