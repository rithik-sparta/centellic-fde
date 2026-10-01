##  Your synthetic data and documents

* [ ] Format : Json, pdfs? If we have multiple formats how will this be handled when we embed the texts?

- [ ] All data is synthetic. Do not use real customer data, real account numbers or confidential
  material of any employer.
- [ ] Invent firm names, people and figures. Real public concepts (a central bank rate decision,
  a covenant, a typology) are fine.
- [ ] Write documents the way professionals in the domain write. Terse research notes, formal policy
  language and case notes are all better than generic paragraphs.
- [ ] At least 5 structured records per entity and at least 8 documents.
- [ ] Records and fields(data.py):
  - [ ] Borrowers - id, sector, rating, leverage, interest cover
  - [ ] Facilties - id,
  - [ ] Covenants - id,

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

* [ ] **Your own data model.** Different entities, fields and filters. No "revenue per lawyer"
  style calculation copied across.
* [ ] **Your own extra tool.** The agent has a tool that is not a document search.
* [ ] **Your own analysis schema.** The structured output has fields specific to your domain.
* [ ] **Your own refusal rule.** Decide what the system should not answer, and prove it in a test.
* [ ] **One time-sensitive or risk-sensitive element.** For example document dates, limits and
  thresholds, or a human-in-the-loop rule.
* [ ] **One UI feature that the law firm version did not have.**


## Deliverables

- [ ] The API project and the UI project, each runnable from its README.
- [ ] Your synthetic data and documents.
- [ ] The one page design note.
- [ ]  A live demo of at least one question the agent answers using both tools, and one question it
  correctly refuses.
