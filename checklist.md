## Your synthetic data and documents

* [X] Format : Json, pdfs? If we have multiple formats how will this be handled when we embed the texts?

- [X] All data is synthetic. Do not use real customer data, real account numbers or confidential
  material of any employer.
- [X] Invent firm names, people and figures. Real public concepts (a central bank rate decision,
  a covenant, a typology) are fine.
- [X] Write documents the way professionals in the domain write. Terse research notes, formal policy
  language and case notes are all better than generic paragraphs.
- [X] At least 5 structured records per entity and at least 8 documents.
- [X] Records and fields(data.py):
  - [X] Borrowers - id, sector, rating, leverage, interest cover
  - [X] Facilties - id,
  - [X] Covenants - id,

## Design note (One page)

* [ ] Why did you set your relevance floor where you did
* [ ] What happened when you tried other values?
* [ ] Would you chunk your documents? Why or why not, given their length and shape?
* [ ] What is the worst wrong answer your system could give, and what stops it?

## Bar

* [ ] Every feature genuinely calls your real, running API and services, nothing faked.
* [ ] Failures are handled: provider errors, empty indexes, unknown records, agent limits.
* [ ] The domain feels real: the data, prompts and refusal rule make sense to someone who works in it.
* [ ] Your version genuinely differs from the law firm version, following the six departures above.
* [ ] You can explain, out loud, what every button press does end to end, including what is sent to
  Voyage, Chroma and Claude.
* [ ] You can defend your choices: the relevance floor, the iteration limit and the model choice.

## How version must differ

* [X] **Your own data model.** Different entities, fields and filters. No "revenue per lawyer"
  style calculation copied across.
* [ ] **Your own extra tool.** The agent has a tool that is not a document search.
* [X] **Your own analysis schema.** The structured output has fields specific to your domain.
* [ ] **Your own refusal rule.** Decide what the system should not answer, and prove it in a test.
* [X] **One time-sensitive or risk-sensitive element.** For example document dates, limits and
  thresholds, or a human-in-the-loop rule.
* [ ] **One UI feature that the law firm version did not have.**

## Deliverables

- [ ] The API project and the UI project, each runnable from its README.
- [X] Your synthetic data and documents.
- [ ] The one page design note.
- [ ] A live demo of at least one question the agent answers using both tools, and one question it
  correctly refuses.

## What you must build

All of the following must be present and working against real, running services. Nothing faked
or hardcoded.

### 1. API (FastAPI)

- [X] A health endpoint.
- [X] Structured records for at least two entity types in your domain, with create, read, update,
  delete and at least two query filters. Validate input with Pydantic.
- [X] Consistent error handling. Map provider failures to sensible status codes (timeout to 504,
  rate limit to 429, other upstream failure to 502).
- [X] Configuration from environment variables (API keys, model names, thresholds). No secrets in code.

### 2. LLM features (Claude)

- [X] A plain summary endpoint for one of your records.
- [X] A streaming version of that summary, so text reaches the client as it is generated.
- [X] A structured analysis endpoint whose output is validated against a Pydantic model of your own
  design. It must return typed fields, not free text.
- [X] Prompts that keep rules in the system prompt and data in the user message.
- [X] A token estimate endpoint or token counts returned with every generated answer.

### 3. Vector database (Chroma with Voyage embeddings)

- [X] A persistent Chroma collection.
- [X] A manual index endpoint that embeds your documents and upserts them by id.
- [X] A search-only endpoint that returns the top results with their scores.
- [ ] A grounded question answering endpoint. It must cite the documents it used, and it must refuse
  without calling the LLM when no result clears a relevance floor that you choose and justify.
- [X] At least 8 documents of realistic prose in your domain.

### 4. Agent (tool use)

- [ ] An agent loop with a hard iteration limit and a clear result when the limit is reached.
- [X] A knowledge search tool, plus **at least one more tool of your own** that works on your
  structured records or computes something (see the domain options for ideas).
- [ ] Safe tool execution: unknown tools, missing arguments and tool failures are reported back to
  the model as errors, not raised as crashes.
- [ ] Return the number of tool calls and total token usage with the answer.

### 5. UI (Streamlit, in its own project with its own environment)

- [ ] **Ask:** free text question to the agent, showing the answer, tool calls, tokens and a distinct
  message if the agent did not complete.
- [ ] **Search only:** retrieval without generation, listing every result with title and score.
  Handle "index not built" differently from an ordinary failure.
- [ ] **Streaming summary:** pick a record, watch the text arrive as it streams.
- [ ] **One feature of your own design** that fits your domain (a comparison view, a watchlist, an
  alert triage screen, a chart, anything that uses your API in a way the law firm version did not).

### 6. Engineering basics

- [ ] Tests with the LLM and embedding calls mocked. Cover at least the summary, the refusal rule
  and the agent loop, including the iteration limit.
- [ ] A `requirements.txt` for each project.
- [ ] A README with the exact commands to run the API and the UI, and the environment variables needed.

* [ ] add a tool that tests covenant headroom from the numbers. The structured output
  is a credit assessment with a strengths list, a risks list and a proposed rating with rationale.
* [X] The streaming summary is a draft credit memo section.

Day 1

* [X] Domain chosen and pitched
* [X] data model designed
* [X] documents written

Day 2

* [X] API with records
* [X] health
* [X] CRUD
* [X] LLM summary endpoints

Day 3

* [X] Chroma indexing
* [ ] search and grounded answers with a refusal rule

Day 4

* [ ] Agent with your extra tool
* [ ] tests for the agent loop

Day 5

* [ ] Streamlit UI with the three required features and your own

Day 6

* [ ] Hardening
* [ ] README
* [ ] design note
* [ ] demo rehearsal
