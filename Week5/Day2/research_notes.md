How I'd like you to work

Work on your own with your laptop open, we want as many "ideas" as possible so work in silos. Write in your own words, one page, four headings.
Use any source, but name it. If you use an AI assistant, check what it tells you against a real source. That is the skill today is about.
We'll pool your notes on the board before the experiment.


1. What is a hallucination? (5 min)

Write a definition in one or two sentences.

Incidents when the AI makes claims tha sound plausible but are factually wrong, irrelevant or entirely fabricated.
When an LLM model makes claims that sound fluent and confident that are factually incorrect.

Look up the terms "intrinsic" and "extrinsic" hallucination. What is the difference, and which should worry you more for a system that answers from documents?
Find one real example. What made it convincing?

Intrinsic Hallucination - contradicts the source material or input the model was given. For example, if you provide an article saying a company was founded in 1998 and the model's summary says 2005, it has directly conflicted with the source, and you can detect the error by checking against that source.

Extrinsic Hallucination - adds information that can't be verified from the source, or that isn't grounded in reality at all. For example, the model summarises the same article and adds a quote from the CEO that appears nowhere in it. The claim isn't necessarily contradicted by the input, but it isn't supported by it either, so checking it requires outside knowledge.

- extrinsic hallucination is most harmful in our case - No way to easily cross check source material. Nothing in the source contradicts it.


2. Why do they happen? (8 min)

Find out how a language model decides what to write next. Why is "plausible" not the same as "true"?
Find at least three distinct causes, one sentence each.
Think about our pipeline. The relevance floor stops the model being called on irrelevant context. What could still go wrong when the context is only nearly relevant?

How a model decides what to write next: A language model assigns a probability to every possible next token given the text so far, then picks one (often the most likely, or a sample from the top candidates) and repeats. It is optimised to produce text that fits patterns seen in training, not to check whether the result is true.

Why "plausible" isn't "true": Plausibility means the text is statistically likely and fluent given the context, while truth requires the claim to match the real world. A false statement can look just as natural as a true one, and nothing in the generation process flags the difference.

Distinct causes of hallucination:

Biased training data - Model cannot generalise very well. Rare, really specific info is not included.

Large ambiguous prompt

Large context window (... lost in the middle)

Training objective: Models are trained to predict likely next words, so they are rewarded for sounding right rather than being right, and they learn no built-in notion of verification.

Gaps and errors in training data: If a fact is rare, missing, outdated, or contradicted in the data, the model fills the gap with a pattern-matched guess rather than admitting it doesn't know.

Lossy compression of knowledge: Facts are stored as blurred statistical associations in the weights rather than as exact records, so details like dates, names, and citations get mixed up or invented.

Pressure to answer: Training and evaluation often reward giving an answer over saying "I don't know," so models tend to guess confidently instead of abstaining.

Decoding randomness and error compounding: Sampling can pick a plausible but wrong token, and since each token conditions the next, one early mistake can snowball into a confidently wrong passage.

Weak or missing grounding: Without access to sources or tools like search, the model has nothing to check its output against, and ambiguous or misleading prompts make this worse.

The relevance floor stops the model being called on irrelevant context. What could still go wrong when the context is only nearly relevant?
An output that uses relevant context, but makes unfounded claims that loosely relate to the context without any sources.


3. Why are they dangerous in production? (10 min)

Read about Mata v. Avianca (2023): https://www.lawnext.com/2023/06/court-imposes-sanctions-on-lawyers-who-filed-bogus-cases-after-relying-on-chatgpt-for-legal-research.html. 
What did the fake output look like? 
The fabricated material was convincing. In the brief opposing Avianca's motion to dismiss, attorney Steven Schwartz cited cases such as Varghese v. China Southern Airlines, Shaboon v. Egyptair, and Martinez v. Delta Air Lines. Each had a case name, a court, a docket number, a reporter citation, a judge, quoted passages, and a procedural history. The "opinions" even cited other decisions internally. They read like real case law on airline liability and limitation periods, but none of them existed. When the judge demanded copies, the "opinion" Schwartz produced was stylistically off and incoherent in places, though it still looked official at a glance.

How did the lawyer try to check it, and why was that check worthless?
Schwartz went back to ChatGPT and asked it whether Varghese was a real case, and later whether the other cases it had supplied were fake. It said they were real and could be found in reputable legal databases like Westlaw and LexisNexis.

Asking the same system that produced the error to verify itself using the same failure mode. Outcome: Fined 5k for incorrect use.

This check was worthless for three reasons:

It used the same source to verify itself. If a model has invented something, asking it to confirm will usually produce another confident invention.
ChatGPT isn't a database. It has no mechanism for looking up cases and generates text that fits the conversation. Answering "yes, it's real" was the most plausible reply, not the result of any lookup.
It skipped the real verification. Actually searching Westlaw, LexisNexis, or the court's own records would have exposed the fakes immediately.


Find one more real incident, from any industry. 

Who was harmed, and who was held responsible?

Moffatt v. Air Canada (2024)

What happened: In November 2022, after his grandmother died, Jake Moffatt asked Air Canada's website chatbot about bereavement fares. The chatbot told him he could book a full-price ticket and apply for the bereavement discount retroactively within 90 days. That was false, because Air Canada's actual policy didn't allow refunds after travel. He relied on the answer, bought the tickets, and was later refused the partial refund. The chatbot had even linked to the real policy page, which contradicted what it had just said.

Who was harmed: Moffatt, a grieving customer who paid more than he needed to because he trusted the airline's own tool. The sum was small, but it was a real financial loss at a bad moment.

Who was held responsible: Air Canada. It argued that the chatbot was effectively a separate legal entity responsible for its own statements, and that customers should have checked the policy page. The British Columbia Civil Resolution Tribunal rejected both arguments in February 2024. It held that the chatbot is part of the airline's website and that the company is responsible for all information it presents, and it found negligent misrepresentation. Air Canada was ordered to pay Moffatt roughly CA$812 in damages, interest, and fees.

Why it matters: Unlike Mata v. Avianca, where the person who used the AI was sanctioned, here the organisation that deployed the AI was held liable for what it said to a member of the public. The ruling is a tribunal decision rather than binding precedent, but it is widely cited as a sign that companies can't disown their chatbots' mistakes.


Our API serves law firm market intelligence. Write three specific ways a hallucinated sentence could hurt a client.
A timeout gives you a 504. What do you get when the model invents a fact, and why is that harder to catch?

Nothing can check if a response is hallucinated. It behaves as intended technically, but the output can not be verified easily. 

Hallucination vs a Timeut - Timeout is loud, hallucination is quiet but a more dangerous failure. It may look legit but is factually incorrect.

Inventing a law firms revenues or profits. 

May invent a competitors strategy. Leading to losses in busines strategy. 

Invent fake regulation. 

Real citation to the wrong doc.

Outcome -> Loss of trust






4. How do we stop them? (10 min)

Read Anthropic's guide: https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations. For each technique, note how it works, what it costs, and whether our project already does it. (More than one, but not all.)
The page ends by saying these techniques reduce hallucinations but do not eliminate them. What do you do about the remainder?
Which techniques could you check in code, and which need a human?

Reduce hallucinations

Minimize hallucinations in Claude's outputs by allowing uncertainty, grounding responses in direct quotes, and verifying claims with citations.

Even the most advanced language models, like Claude, can sometimes generate text that is factually incorrect or inconsistent with the given context. This phenomenon, known as "hallucination," can undermine the reliability of your AI-driven solutions. This guide will explore techniques to minimize hallucinations and ensure Claude's outputs are accurate and trustworthy.
Basic hallucination minimization strategies

    Allow Claude to say "I don't know": Explicitly give Claude permission to admit uncertainty. This simple technique can drastically reduce false information.
    
    How it works? Add a prompt telling Claude to say it does not know when it is uncertian.
    What it costs? May not recieve an answer for all prompts. Risk of over refusing.
    Does our project do this? Yes, in grounded system prompt.

Example: Analyzing a merger & acquisition report

    Use direct quotes for factual grounding: For tasks involving long documents (>20k tokens), ask Claude to extract word-for-word quotes first before performing its task. This grounds its responses in the actual text, reducing hallucinations.

    How it works? Ask Claude to quote sources directly rather than paraphrase.
    What it costs? Responses may be longer if we are quoting large peices of text. 
    Does our project do this? No

Example: Auditing a data privacy policy

    Verify with citations: Make Claude's response auditable by having it cite quotes and sources for each of its claims. You can also have Claude verify each claim by finding a supporting quote after it generates a response. If it can't find a quote, it must retract the claim.

    How it works? Add a prompt telling Claude to cite its sources and quotes for each claim. 
    What it costs? Tokens will be spent on citing for each claim.
    Does our project do this? Yes, we tell the model to cite sources for each claim

Example: Drafting a press release on a product launch

Direct quotes

Advanced techniques

    Chain-of-thought verification: Use thinking with display: "summarized", and review the summarized reasoning in the thinking blocks when an answer looks wrong. This can reveal faulty logic or assumptions.

    Best-of-N verification: Run Claude through the same prompt multiple times and compare the outputs. Inconsistencies across outputs could indicate hallucinations.

    Iterative refinement: Use Claude's outputs as inputs for follow-up prompts, asking it to verify or expand on previous statements. This can catch and correct inconsistencies.

    External knowledge restriction: Explicitly instruct Claude to only use information from provided documents and not its general knowledge.

The page ends by saying these techniques reduce hallucinations but do not eliminate them. What do you do about the remainder?
The remaining hallucinations would need to be caught through a human in the loop system.

Which techniques could you check in code, and which need a human?
Code:
Allow Claude to say "I don't know"
Use direct quotes for factual grounding

Human:
Verify with citations. Do so for high stakes tasks such as reports

5. Predict (~5 min)

In Step 4 we send the same document and the same two questions through two prompts: a loose "be as helpful as you can" one, and our grounded one. Write down what you expect each to do, and what you would count as a hallucination. Do this before you run anything.



Predictions:

Helpful

More likely to hallcinate. May refer to general info rather than grounded info. Could contain info like name, tenure, comparison with other firms etc... variation across runs depending on the maturity of the model.

The model will attempt to answer the questions,but will not cite sources. It may reference code in the repo without saying from where exactly it found it.

Grounded

The model will be more detailed in its response. Citing sources in the repo with file names and line numbers.

More likely to refus (use the refusal sentence or answer only the supported part.

What counts any specific claim that I can't go and find in the document (a citation on it does not make it grounded)

What I would count as a hallucination:



BE AS HELPFUL AS YOU CAN

Read Anthropic's guide: https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations. For each technique, note how it works, what it costs, and whether our project already does it. (More than one, but not all.)
The page ends by saying these techniques reduce hallucinations but do not eliminate them. What do you do about the remainder?
Which techniques could you check in code, and which need a human?
Be as helpful as you can

---

| Technique | How it works | Cost (estimate) | In firm-intelligence-api? |
|-----------|--------------|-----------------|---------------------------|
| **Allow "I don't know"** | The prompt gives Claude a fixed phrase to use when it lacks the information. | Near zero. Risk of over-refusing. | **Yes.** `GROUNDED_SYSTEM_PROMPT` in `llm.py` sets the exact sentence "The provided documents do not answer that question." |
| **Direct quotes first** | Claude extracts verbatim quotes before analysing, mainly for long documents. | Extra tokens and a second pass. | **No.** The documents are short paragraphs, so this matters less today. |
| **Citations, then verify and retract** | Claude cites a source for each claim, or drafts and then removes unsupported claims. | Extra tokens, plus parsing. | **Half.** The prompt asks for `[doc-001]`-style citations, but the check in `grounding.py` is broken and nothing calls it. There is no retraction step. |
| **Chain-of-thought verification** | Turn on thinking with summarised output and read it when an answer looks wrong. | Thinking tokens and human time. | **No.** No thinking parameter anywhere. |
| **Best-of-N** | Run the same prompt several times and compare the answers. | N times the cost and latency. | **No.** |
| **Iterative refinement** | Feed the answer back and ask Claude to check it. | Extra round-trips. | **No.** |
| **External knowledge restriction** | Tell Claude to use only the supplied documents. | Near zero. | **Partly.** `answer_from_context` says to use only the context provided. The agent prompt in `agent.py` has no such restriction. |

2. The remainder

The page ends by saying these techniques don't eliminate hallucinations and to validate critical information. I'd handle that in four ways:

Assume errors will happen. Design the pipeline so a wrong claim is caught or contained, not so that none occur.
Automate every check that can be automated (see section 3), and run them on every output.
Review by risk. Humans fully review high-stakes outputs, such as legal, financial or medical ones. Lower-stakes outputs get a random sample audit.
Keep an eval set. Include questions with no answer in the source, and track the hallucination rate and the over-refusal rate over time. Re-run it whenever prompts or models change.

I'd also show citations to end users, so they can check a claim themselves.

3. Code versus human

Checkable in code:

Quotes and citations: every quoted string must be an exact substring of the source. This is deterministic and catches fabricated quotes.
Retraction format: confirm that unsupported claims were actually removed, for example by checking for the [] markers.
"I don't know" behaviour: match the fixed phrase, and measure how often it appears on your unanswerable test questions.
Best-of-N: compare runs automatically. Exact match works for structured fields, and an embedding or LLM judge works for prose.
External knowledge restriction (partial): check that numbers, dates and named entities in the output appear in the source. This catches many leaks but not paraphrased ones.
Process checks: confirm the thinking block exists, or that the second pass ran.

Needs a human:

Does the quote support the claim? Code can check that a quote exists, not that it entails the claim. An LLM judge helps but is itself fallible, so spot-check it.
Was an "I don't know" correct, or an over-refusal? This needs domain knowledge.
Chain-of-thought review: deciding whether the reasoning is faulty is a judgment call.
Final sign-off on high-stakes outputs.

---

GROUNDED SYSTEM PROMPT

I will give you the following tasks. Do not make up information you cannot put a source to. Use British English, no em-dashes. For every claim you make, cite the sources you used. Make sure that they exist on the public internet and are reliable.

Read Anthropic's guide: https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations. For each technique, note how it works, what it costs, and whether our project already does it. (More than one, but not all.)
The page ends by saying these techniques reduce hallucinations but do not eliminate them. What do you do about the remainder?
Which techniques could you check in code, and which need a human?

---

| Technique | How it works (per the guide) | Cost | In the project? | Evidence in the repo |
|---|---|---|---|---|
| Allow "I don't know" | Explicitly permit Claude to admit uncertainty, for example with a fixed phrase. | Not stated. Inference: negligible tokens, but may cause over-cautious answers. | **Yes** (grounded path), partial elsewhere | `GROUNDED_SYSTEM_PROMPT` demands an exact refusal sentence (`llm.py:138-143`). `/agent/context` refuses before calling the model if no hit scores at least 0.35 (`routers/agent.py:34-43`, `routers/knowledge.py:10`). The agent prompt says to report honestly if the tool finds nothing (`agent.py:11-16`). The summary prompt only says never to invent facts (`llm.py:27-31`). |
| Direct quotes first | For long documents (over 20k tokens), extract word-for-word quotes first, then answer using only those quotes. | Not stated. Prompt-based quoting uses output tokens. | **No** | No quote-extraction step. The corpus documents read are short, well under the 20k-token threshold, so it may not be needed yet. |
| Verify with citations | Claude cites a quote for each claim, or finds a supporting quote afterwards and retracts any claim without one. | The API Citations feature slightly raises input tokens, and `cited_text` does not count as output tokens. It cannot be combined with structured outputs, and scanned PDFs are not citable. | **Partial, and broken** | Prompt asks for `[doc-001]` citations (`llm.py:140`). Response lists retrieved sources (`routers/agent.py:69-71`). API Citations feature not used. No retract step. `grounding.check_citations` exists but nothing in the app calls it. |
| Chain-of-thought verification | Use thinking with `display: "summarized"` and read the thinking blocks when an answer looks wrong. | Thinking tokens are billed as output tokens even if not returned. Full thinking is billed, not the summary. Omitting display saves latency, not cost. | **No** | No `thinking` parameter in any call. Model is `claude-haiku-4-5-20251001` (`llm.py:11`). |
| Best-of-N | Run the same prompt several times and compare outputs. Inconsistencies may signal hallucinations. | Not stated. Inference: roughly N times the calls. | **No** | No repeated-call or comparison code. |
| Iterative refinement | Feed outputs into follow-up prompts asking Claude to verify or expand earlier statements. | Not stated. Inference: at least one extra call per pass. | **No** | The loop in `agent.py` repeats retrieval (capped at 4 iterations) but never asks the model to verify its own answer. |
| External knowledge restriction | Instruct Claude to use only the provided documents, not its general knowledge. | Not stated. Inference: answers will be narrower. | **Yes** (grounded path), partial on the agent path | "Using ONLY the context provided" and "never use knowledge from outside the context" (`llm.py:139,142`). The agent prompt says "do not guess" but does not restrict it to tool results. |
