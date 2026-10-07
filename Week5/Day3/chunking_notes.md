1. What is citation drift?

Write a definition in one or two sentences.

Citation drift refers to the instability of sources used in AI-generated answers. It describes how the same question can yield different cited domains over time and across various platforms. This phenomenon is a structural characteristic of probabilistic retrieval and generation in AI systems. The citation no longer matches the source.

---

A citation can be wrong in two different ways:**it points at a source that was never supplied**, or it **points at a real source that doesn't support the claim**. Look up the term "misgrounded". Which of the two is easier to catch in code, and which is harder?

In the context of citation drift, "misgrounded" refers to **citations that are inaccurately attributed**. This can occur when the source of a citation changes or when there are errors in AI-generated responses. As a result, the reference no longer aligns with the original claim it was meant to support.

**Identifying a source that was never supplied** invalid citation is easier to catch with code, as we only check if the citation matches an existing source.

**Identifying a source that does not support the claim**  misgrounded citation is more difficult, as we need to identify if the claim actually exists within the source material cited.

---

Which of the two does the checker you built in Step 3 already catch?

The checker can identify sources that were never supplied

2. How common is it? (6 min)

The checker identfies uncited sources in the responses  This happens on every run of the loose prompt. 70% of cases when claims were uncited, 30% where citations were misgrounded.

---

3
Read the abstract of "Evaluating Verifiability in Generative Search Engines" (Liu, Zhang and Liang, 2023): https://arxiv.org/abs/2304.09848. Write down its two headline numbers. In your own words, what do "citation recall" and "citation precision" each ask?
Now read the Stanford summary of the legal research tools study: https://hai.stanford.edu/news/ai-trial-legal-models-hallucinate-1-out-6-queries. The paper is at https://arxiv.org/abs/2405.20362.
Find how the study defines a hallucination. It has two parts.
Note the headline range. The summary and the paper's abstract word it slightly differently, so say which you'd quote and why.
Why does it matter that these are commercial legal tools whose vendors claimed "hallucination-free" citations?
\

2.3 Citation Recall -
verifiability, i.e.,
systems should cite comprehensively (high ci-
tation recall. Proportion of claims fully supported by their citations. All statements are fully supported by the citation

2.4 Citation Precision - all statements are fully supported
by citations) and accurately (high citation pre-
cision; every cite supports its associated state-
ment)
.
Proportion of citations that support their associated statements.

 Every citation supports their statement.

Hallucination definition -
These systems can hallucinate in one of two ways. First, a response from an AI tool might just be incorrect—it describes the law incorrectly or makes a factual error. Second, a response might be misgrounded—the AI tool describes the law correctly, but cites a source which does not in fact support its claims.

In production environment, hallucinations could lead to decisions based on un supported claims.
In a legal domain, this could lead to fines based on following uncited claims.


---

3. Why does it happen?

Find at least three causes, one sentence each. Think about: several similar documents, a claim that blends two sources, and a model writing from memory and attaching a citation afterwards.
Look back at your hallucination probe outputs. Find a place where one citation was attached to a whole paragraph rather than a single sentence. What does that do to the question "which source supports this sentence"?

**Several similar documents:** When a retrieval step returns near-duplicate or closely related sources (e.g. multiple versions of a report or articles covering the same event), the model can't reliably tell which one a given detail came from and attaches the wrong one.

**A claim that blends two sources:** If a sentence merges facts from two different documents into one statement, any single citation will only partly support it, so the claim looks sourced while neither source says exactly that.

**Writing from memory, then adding a citation afterwards:** When the model drafts an answer from what it already "knows" and only later looks for a source to attach, the citation is chosen to fit the text rather than being where the text came from, so it can be plausible-looking but wrong or entirely invented.

---

4. Why is it dangerous in production?

Why is a wrong citation arguably worse than no citation? Look up "automation bias" and say how citations make it worse.
Write one scenario where the sentence is true but the citation is wrong. Who is affected, and would anyone notice? Is that still a failure? Argue both sides.

Automation bias is the tendency to over-rely on output from an automated system, accepting its suggestions with less scrutiny than you'd give a human source, and sometimes even overriding your own correct judgment to go along with it. It shows up in two forms: errors of commission (acting on a wrong recommendation) and errors of omission (failing to notice a problem because the system didn't flag it). It's been documented for decades in aviation, medical decision support, and similar settings, and it tends to get stronger as a system is right more often, because people learn that checking rarely pays off.

Citations make it worse for a few reasons:

They look like verification has already happened. A reference signals that the claim has been checked against something real. Readers treat the presence of a citation as evidence of accuracy, even when they haven't opened it.

They raise the cost of checking while seeming to lower the need. To catch a misgrounded citation you have to open the source, read it, and compare it with the claim, which is more work than judging a bare statement. That friction pushes people to skip the step, and the tool's polished appearance gives them a reason to.

They make errors harder to spot. A fabricated claim with no source is at least visibly unsupported. A claim attached to a real, relevant-looking source that doesn't actually say it passes the quick sanity checks (is the case real? is the link live?) and fails only under close reading. The legal study you just read makes this point: it argues these subtler errors can be more dangerous than invented cases.

They borrow credibility from the source. If the cited document is authoritative, such as a Supreme Court decision, some of that authority transfers to the claim, even when the claim misdescribes or contradicts it.

Mostly-correct output trains trust. If most citations check out, people reasonably relax. The occasional bad one then lands in exactly the place where attention has dropped.


### A scenario: the sentence is true, the citation is wrong

A compliance assistant at a UK firm is asked whether a data breach must be reported. It answers: "A personal data breach that's likely to risk individuals' rights must be reported to the ICO within 72 hours of the firm becoming aware of it." That is correct. The attached citation is the firm's internal Data Retention Policy, which says nothing about breach reporting.

* **Who is affected?** The employee who acts on it is fine today. The people exposed are the ones downstream. An auditor or regulator asking what the decision rested on gets a document that doesn't say it. A colleague who copies the sentence and citation into a template spreads the bad pointer. When the rule changes or the answer is wrong in a similar-looking case, the same process produces a false claim with a citation that looks just as good.
* **Would anyone notice?** Probably not at first. The claim matches what the employee already believes, so they have no reason to check. It surfaces only at an audit, a dispute or a rule change.

### Is it still a failure? Both sides

**Yes, it's a failure.**

* The citation's job is to let a reader verify the claim, and it can't, so the output is defective even if the sentence is true.
* The right answer came from the model's memory, not the cited source. That is the "cite afterwards" failure from your first question, and it will produce wrong claims on other days.
* The audit trail is corrupted. A decision made on a true claim with a false justification is hard to defend.
* It trains users to trust citations that don't deserve it, and the damage shows up later.

**No, or at least not much of one.**

* The user got a correct answer and acted correctly, so no harm occurred.
* Harm-based standards treat outcomes as what matters. If every such case ended well, the practical cost would be near zero.
* Some claims are common knowledge or widely corroborated, so the wrong citation misleads little when the user could find a real source in seconds.
* Counting every mismatch as a failure inflates error rates and may push teams toward over-checking low-stakes content.

I'd call it a real failure but a lower-severity one. It's a near miss that shows the process is broken. The false-claim, false-citation case is the one that hurts, and the same defect produces both, so tracking support rate rather than link validity is what catches it. Per the TechTarget summary, management should track errors and overrides and use that data to retrain both systems and staff. One more finding bears on this: experimental work found that internalised personal accountability reduced both omission and commission errors. Making a named person responsible for verifying a citation may therefore help more than telling people to be careful.

---



5. How do we stop it?

Read Anthropic's citations page: https://platform.claude.com/docs/en/build-with-claude/citations.
How do API citations differ from asking the model to type [doc-101] in its answer?
What does the page say is guaranteed? What does that not guarantee?
Note any limitation the page mentions.

API Citations cite the exact lines in the document that the claim is made from rather than just the document itself.

Citations are guaranteed to have valid pointers to provided documents. It does not guarantee that the claim can be verified by the citation.

Limitation -
Cannot be used with structured outputs.

Name two other ways to catch drift. Which could you do in code, and which would need a model?
For a client-facing product, which would you choose, and what would you still leave to a human?

**Automated existence checks.** Resolve sources of citations to confirm they exist and match the stated title, authors and year. This catches fabricated references but not misgrounded ones.

**Quote and number matching.** Script a check that any quoted text or figure appears verbatim in the source. It's crude but catches a lot of misquotation.

---

Chunking Strategy

* 6 ways to split documents. One way to choose between them. Numbers from your own eval harness.
* Retune relevance floor based on data.
* Why split documents?

  * Precise vectors - One vector per topic, not one vector for several topics averaged
  * Complete Evidence - Cut a sentence in half, or lose its heading, and the model sees half a fact.
  * Context cost - Three whole document: about 750 words per answer. Three section chunks: about 190. We pay for every input token on every call. Want to be efficient with our token use.
* **There is no universally right chunk size. So we measure.**
* **Split docs (chunking) -> embed -> search** rather than **embed -> search**
* | Strategy             | How it splits                      | The question it tests                 |
  | -------------------- | ---------------------------------- | ------------------------------------- |
  | whole_document       | Whats chunking?                    | Is chunking worth it?                 |
  | fixed_100            | Every 100 words, blind             | What does the cheapest chunker cost?  |
  | fixed_100_overlap_25 | 100-word windows, 25 shared        | Does overlap repair blind cuts?       |
  | sentences_100        | Whole sentences, up to 100 words   | Do sentence boundaries matter?        |
  | sections_plain       | One chunk per section              | Does document structure help?         |
  | sections_contextual  | Sections, prefixed Title > Heading | Does knowing its source help a chunk? |
* | Metric                     | The question it answers                       |
  | -------------------------- | --------------------------------------------- |
  | Recall@k                   | Is a chunk holding the answer in the top k?   |
  | MRR (Mean reciprocal rank) | How high does the first correct chunk rank?   |
  | Context words@3            | How much text does the model read per answer? |
  | Answer accuracy            | Does the final answer contain the right fact? |
  | Refusal Accuracy           | Does it refuse what the corpus cannot answer? |
* No quality claim without numbers from your own harness
* Choose the metric based on what we need the model to do.
* A hit means the whole fact: The eval set is code. Its tests caught two duplicated spans on their first run.
* If a span is cut in half between chunks, that is seen as half a fact and the fact scores as no fact.
* eval set and golden set are the same.
* Overlap repairs context splitting, at the cost of more tokens.
* One index per strategy:

  * Batch embeddings - A full run of 6 strategies is 7 Voyage requests.
  * Fingerprint every build - Chunks plus model name. Unchanged means rebuilding costs nothing.
  * Embed questions once - 32 questions, one call, reused against six indexes
  * Test in memory - Fake vectors must never reach the real store.
* `
*
