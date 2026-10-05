**The problem.** A credit analyst must assess a borrower quickly, drawing on financials, covenant
terms, prior credit memos and sector outlooks, then produce a defensible recommendation.

- **Records:** borrowers (sector, rating, leverage, interest cover), facilities, covenants.
- **Documents:** credit memos, sector outlooks, covenant summaries, lending policy, restructuring
  case studies.
- **Questions:** "Which borrowers are close to breaching an interest cover covenant?",
  "What does our lending policy say about leveraged loans in cyclical sectors?"
- **Differ it:** add a tool that tests covenant headroom from the numbers. The structured output
  is a credit assessment with a strengths list, a risks list and a proposed rating with rationale.
  The streaming summary is a draft credit memo section.

# Domain:

C : Corportate and Investment Banking: Credit Analysis

Explanation of Implementation (Some details may change overtime, but this is a high level overview of my current ideas):

* Use vector database to store embeddings of documents
* Stream Summary : Draft Credit Memo section (Whether we approve, decline, or modify a loan, citing document sources)
* Data Model:

  * ```
    Example of Covenant Headroom Test output 
    {
    "headroom": [
    {
    "covenant": "Interest cover >= 2.5x",
    "actual": 3.0,
    "threshold": 2.5,
    "ebitda_cushion_pct": 16.7,
    "status": "moderate"
    }
    ],
    "strengths": ["Leverage headroom of 20% with deleveraging trend"],
    "risks": ["Interest cover headroom of 16.7% is thin for a cyclical sector"],
    "proposed_rating": "BB+",
    "rationale": "Adequate coverage but limited cushion against a downturn..."
    }


    Records:
    Borrower{borrower_id, legal_name, trading_name, registration_number, lei, registered_address, entity_type, business_description, ownership_type,employee_count, size_band, }
    Facility{facility_id, borrower_id, agreement_id, facility_Type, tranche, status, currency, limit, drawn, undrawn, role, our_hold, committed, start_date, maturity_date, availability_period_end, repayment_profile, repayment_schedule, reference_rate, margin_bps, rate_floor, margin_ratchet, commitment_fee_bps, arragement_fee, hedging, ranking, security_description, collateral_value, valuation_date, ltv, guarantors, facility_rating, loss_given_default, expected_loss, purpose, approval_memo_id, approval_date, approved_by, policy_exception, covenant_ids, cross_default_linked_facilities}
    Covenant{}



    Example of Document json fields:
    doc_id : (str)
    date : (str)
    type : one of credit-memo, outlook, report, covenant summaries, lending policy, restructuring case study
    title : title of the document
    text : str contents
    ```
* Routes:

  * borrower/ask - Ask questions related to the borrower
  * borrower/summary - streamed summary to evaluate a borrower
  * borrower/stats - Calculated statistics about a borrower from the records. If some information can't
  * policy/search - Search for documents related to a policy
  * policy/ask - Ask questions related to policies
* Functions:

  * Ask : Questions related to lending policies and borrowers
  * Search : Records related to policies or borrowers.
  * Stream Summary : Draft Credit Memo section (Whether we approve, decline, or modify a loan, citing document sources)
  * 
* Tools:

  * Document Search - To find relevant documents related to questions.
  * Risk analysis methods - Functions to reliably calculate statistics from relevant numbers extracted from documents by the model. e.g. To test covenant headroom, find numbers from documents such as financials, covenant terms, covenant summaries, credit memos and then use the risk analysis methods to calculate stats based on them to reach a conclusion.
* Prompts:

  * Role based prompt of a credit analyst to assess suitability of borrowers and answer questions about policies
  * Prompt to provide context around some of the calculated figures, and provide explanations behind reasonings stating the stats and documents used.
* Questions to not answer:

  * For the policy routes, do not answer questions related to specific borrowers. If we implement authentication for routes, some users may be restricted from accessing sensitive information related to borrowers and only be allowed to query related to borrowers.

## Outline:

Documents

credit memos, sector outlooks, covenant summaries, lending policy, restructuring
case studies, financials, covenant terms, prior credit memos and sector outlooks

Differ:

* **Your own data model.** Different entities, fields and filters. No "revenue per lawyer"
  style calculation copied across.
* **Your own extra tool.** The agent has a tool that is not a document search.
* **Your own analysis schema.** The structured output has fields specific to your domain.
* **Your own refusal rule.** Decide what the system should not answer, and prove it in a test.
* **One time-sensitive or risk-sensitive element.** For example document dates, limits and
  thresholds, or a human-in-the-loop rule.
* **One UI feature that the law firm version did not have.**

**Differ it:** add a tool that tests covenant headroom from the numbers. The structured output
is a credit assessment with a strengths list, a risks list and a proposed rating with rationale.
The streaming summary is a draft credit memo section.

Questions:

* Document format
* Shape of data in document
* What do records refer to? The fields in each document

Use a list, plus one designated primary period.

**Why not just one period**

An assessment normally looks at more than a single period. Analysts check the trend (is leverage improving or worsening?) and often combine periods, such as rolling the last four quarters into a last-twelve-months figure. A single `period_id` couldn't record that. It would also make an assessment based on three years of accounts look as though it used only the latest one.

**Why not just a list**

The policy tests, such as `max_leverage` and `min_interest_cover`, need one specific period's figures, normally the latest. With only a list, the record wouldn't say which of those periods those figures came from, so you'd have to guess by taking the most recent one, which fails if the agent used something else.

Why choose the scale of 1 to 22?

Because the S&P scale has 22 distinct grades, so each grade gets its own number. S&P and Fitch grades run from AAA down to D, and numbering them in order gives 1 to 22:

* **1 to 10:** investment grade, from AAA to BBB-.
* **11 to 21:** speculative grade, from BB+ down to C (BB+, BB, BB-, B+, B, B-, CCC+, CCC, CCC-, CC, C).
* **22:** default (D).

It also lines up with the other agencies. Moody's has the same 21 grades from Aaa to C, so they map onto ranks 1 to 21, and Moody's has nothing at 22. I anchored the numbering to S&P rather than Fitch because Fitch has no CCC+ or CCC-, so it would have left gaps in the sequence.

**It's a convention, not an industry standard.** No regulator or agency defines a 1 to 22 scale. I chose it because it is the most direct way to number the grades. Other reasonable choices would work equally well:

* **Starting at 0 or making higher better:** some systems use AAA as the highest number, so "minimum rating" reads naturally as a minimum number. Mine has lower as better, so "min_credit_rating_rank" actually means a maximum number, which can confuse people.
* **Fewer buckets:** many banks' internal scales have 8 to 12 grades and group several agency grades into one. If your own institution uses an internal scale, that would normally be the master scale, with the agency grades mapped onto it.
* **Ignoring modifiers:** some policies only care about the main category (AA, A, BBB), which would give a scale of about 9 to 10 steps.

The main thing is that the numbering is used consistently, since policy values only have meaning against it. If your credit team already has an internal scale or a preferred convention, it would be sensible to use that instead, and I can rebuild the conversion table around it.

Rules when generating examples:

`borrower_id` duplicates what the facility already implies, which allows the two to disagree. `currency` has the same problem against `facility.currency`

## Calculations

```
available liquidity = cash - restricted cash + available undrawn facilities
liquidity headroom = available liquidity - debt due within 12 months - minimum liquidity requirement

Net debt        = total_debt - cash
Leverage (net)  = (total_debt - cash) / ebitda        [debt_basis = net]
Leverage (gross)= total_debt / ebitda                  [debt_basis = gross]
Interest cover  = ebitda / net_interest_expense
Adjusted EBITDA = reported EBITDA + ebitda_adjustments
EBITDA margin   = ebitda / revenue
DSCR            = operating_cash_flow / (net_interest_expense + scheduled principal)

Maximum covenant (<=):  headroom = threshold - actual
                        headroom % = (threshold - actual) / threshold
Minimum covenant (>=):  headroom = actual - threshold
                        headroom % = (actual - threshold) / threshold
Net worth covenant:     headroom = net_worth - threshold   (an amount, not a multiple)

Leverage covenant:        cushion = 1 - (actual leverage / threshold)
Interest cover covenant:  cushion = 1 - (threshold / actual cover)

Exposure and liquidity (facility, debt_repayment)

Utilisation       = drawn_amount / committed_amount
Undrawn           = committed_amount - drawn_amount
Liquidity         = cash + sum(available_amount)
Liquidity cover   = liquidity / principal falling due in the next 12 months
Arrears           = principal_amount - amount_paid
Days past due     = (paid_date or today) - due_date

Revenue growth   = (revenue_t - revenue_t-1) / revenue_t-1
Change in leverage = leverage_t - leverage_t-1
Free cash flow   = operating_cash_flow - capex
Cash conversion  = operating_cash_flow / ebitda
```
