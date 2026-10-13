
# Chunking decision

**Date:** <today></today> 13-10-2026 **Decided by:** Rithik Patel **Corpus:** documents.py + corpus.py (16 documents)
**Eval set:** eval_set.py (29 answerable, 3 unanswerable)  **Embedding model:** voyage-3-lite

## Decision

We serve **sections_contextual** with a relevance floor of 0.55.

| Strategy                             | R@1  | R@3  | MRR  | Context words@3 | Answer acc. | Refusal acc. |
| ------------------------------------ | ---- | ---- | ---- | --------------- | ----------- | ------------ |
| whole_document                       | 0.69 | 1.00 | 0.84 | 862             | 0.56        | 0.43         |
| sections_contextual<second></second> | 0.86 | 1.00 | 0.93 | 197             | 0.66        | 0.50         |
| fixed_overlap_25<best></best>        | 0.52 | 0.93 | 0.67 | 277             | 0.61        | 0.50         |

## Evidence



```
# > python -m eval_answers sections_contextual fixed_overlap_25 whole_document
"""
floor = 0.35
strategy                answers  refusals  calls  avg in tokens
sections_contextual        0.97      1.00     30        422.933
    false refusals: q24
    wrong or not refused: none
fixed_overlap_25           0.83      1.00     30          464.4
    false refusals: q02, q17, q18, q24
    wrong or not refused: q09
whole_document             0.97      1.00     30        926.133
    false refusals: q24
    wrong or not refused: none
"""

# > python -m eval_answers sections_contextual --floor 0.45

""" 
floor = 0.45

strategy                answers  refusals  calls  avg in tokens
sections_contextual        0.97      1.00     30            413
    false refusals: q24
    wrong or not refused: none
"""

# > python -m eval_answers sections_contextual --floor 0.55
"""
floor = 0.55

strategy                answers  refusals  calls  avg in tokens
sections_contextual        0.90      1.00     29        314.966
    false refusals: q06, q09, q24
    wrong or not refused: none
"""
```



```
best-hit score per question, lowest first
  0.251  q30  unanswerable       UNANSWERABLE
  0.280  q24  exact-id           answerable
  0.533  q06  lookup             answerable
  0.587  q10  lookup             answerable
  0.596  q14  lookup             answerable
  0.597  q12  negation           answerable
  0.604  q31  unanswerable       UNANSWERABLE
  0.608  q09  lookup             answerable
  0.618  q16  numeric            answerable
  0.632  q28  lookup             answerable
  0.634  q32  unanswerable       UNANSWERABLE
  0.634  q04  lookup             answerable
  0.641  q11  numeric            answerable
  0.648  q25  numeric            answerable
  0.653  q01  numeric            answerable
  0.662  q29  lookup             answerable
  0.672  q02  title-dependent    answerable
  0.675  q05  negation           answerable
  0.677  q18  numeric            answerable
  0.684  q20  negation           answerable
  0.686  q07  numeric            answerable
  0.687  q22  heading-dependent  answerable
  0.688  q15  title-dependent    answerable
  0.697  q17  numeric            answerable
  0.698  q13  lookup             answerable
  0.733  q03  title-dependent    answerable
  0.736  q08  numeric            answerable
  0.747  q23  numeric            answerable
  0.758  q19  title-dependent    answerable
  0.758  q21  heading-dependent  answerable
  0.759  q27  rare-term          answerable
  0.787  q26  lookup             answerable

what each floor refuses at the gate, before the model is ever called
  floor 0.40: refuses  1 of 29 answerable (bad)   1 of 3 unanswerable (good)
  floor 0.45: refuses  1 of 29 answerable (bad)   1 of 3 unanswerable (good)
  floor 0.50: refuses  1 of 29 answerable (bad)   1 of 3 unanswerable (good)
  floor 0.55: refuses  2 of 29 answerable (bad)   1 of 3 unanswerable (good)
  floor 0.60: refuses  5 of 29 answerable (bad)   1 of 3 unanswerable (good)
  floor 0.65: refuses 11 of 29 answerable (bad)   3 of 3 unanswerable (good)
```

## Why this one

Chosen sections_contextual strategy as it has the highest MMR and recall (R@1) scores. It also has the lowest average context words at 197, allowing for the same relevant information as whole_document to be represented with fewer tokens. 

A score of 0.55 was chosen as we want the model to be more guarded in its responses only answering if it is very confident in the context retrieved. 

The avg in tokens with a floor of 0.55 is 100 tokens less compared to a floor of 0.45. The answer accuracy for a floor of 0.55 is 0.90 which is marginally lower than at floor 0.45 at 0.97, allowing for a similar performance. This can allow for responses that are of a lower average cost while also being more accurate compared to using whole_documents.

## Known weaknesses

Question missed: q24, kind: exact-id. 

This embedding model was unable to retrieve the relevant context from the source, leading to a model refusal. Eventhough LP-3307 was mentioned in the document, it was retrieving the incorrect chunk. 

In order to resolve this hybrid retrieval would be needed for this question as embedding based retrieval alone cannot retrieve the correct chunk.

Question missed: q06, kind: lookup

Question missed: q09, kind: lookup

Lookup performance was impacted by the higher floor value, leading to false_refusals eventhough the questions were answerable. This cost was deemed as acceptable for a more reliable retrieval that is more likely to refuse unanswerable questions at the cost of missing some unanswerable questions.


## Revisit when

The retrieval would need to be revisited if documents of a different format are added to the corpus (i.e. ones that do not follow the standard heading format of two hashes heading and newline). This is due to each chunk being prefixed with the document title and section heading, which is parsed via regular expressions. If the documents text format changes this can affect how the document is chunked or if it is chunked at all, leading to a degradation of performance metrics such as recall and MMR.


Documents that include new data formats such as tables or long code snippets may also need to be accounted for.
