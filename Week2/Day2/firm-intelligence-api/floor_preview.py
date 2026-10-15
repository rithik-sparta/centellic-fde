import chunk_index
from eval_set import EVAL_SET

STRATEGY = "sections_contextual"
vectors, _ = chunk_index.embed_batched([q["question"] for q in EVAL_SET], input_type="query")
ranked = chunk_index.search_with_vectors(STRATEGY, vectors, k=3)

rows = sorted((hits[0]["score"], q["id"], q["kind"], bool(q["doc_id"])) for q, hits in zip(EVAL_SET, ranked))

print("best-hit score per question, lowest first")
for score, qid, kind, answerable in rows:
    print(f"  {score:.3f}  {qid}  {kind:<18} {'answerable' if answerable else 'UNANSWERABLE'}")

print("\nwhat each floor refuses at the gate, before the model is ever called")
for floor in (0.40, 0.45, 0.50, 0.55, 0.60, 0.65):
    bad = sum(1 for s, _, _, a in rows if a and s < floor)
    good = sum(1 for s, _, _, a in rows if not a and s < floor)
    print(f"  floor {floor:.2f}: refuses {bad:>2} of 29 answerable (bad)   {good} of 3 unanswerable (good)")
    
""" 
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
"""