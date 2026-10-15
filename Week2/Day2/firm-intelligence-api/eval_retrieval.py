"""
The step build the scoreboard.
Score every chunking strategy against the eval set.

build all 6 index -> embed the 32 questions once -> search every index -> score -> print + save


"""

import json
import statistics
from pathlib import Path
import time

import chunk_index
import chunking
from eval_set import EVAL_SET
from eval_tools import contains_evidence

# look at the top 1, top 3 and the top 5 results
K_VALUES = (1,3,5)


# where is the right chunk?
def first_hit_rank(hits : list[dict], evidence: str) -> int | None:
    for rank, hit in enumerate(hits, start=1):
        if contains_evidence(hit["text"], evidence):
            return rank
    return None


# turn our results into numbers
# find the rank of the correct chunk for every answerable question... then turn those ranks into scores.
def score_strategy(questions: list[dict], ranked: list[list[dict]]) -> dict:
    """Recall@k, MRR, context size and the questions thats missed, for ONE strategy."""
    answerable = [(q, hits) for q, hits in zip(questions,ranked) if q["doc_id"]]
    unanswerable = [(q, hits) for q, hits in zip(questions,ranked) if not q["doc_id"]]
    ranks = [first_hit_rank(hits, q["evidence"]) for q, hits in answerable ]
    
    # group by question kind
    kinds: dict[str, list[bool]] = {}
    for (q, _), rank in zip(answerable, ranks):
        kinds.setdefault(q["kind"], []).append(rank is not None and rank <= 3)
    
        
    return {
        **{f"recall@{k}": round(statistics.mean(r is not None and r <= k for r in ranks), 3) for k in K_VALUES},
        "mrr": round(statistics.mean(1/ r if r else 0 for r in ranks), 3), 
        "context_words@3": round(statistics.mean(
            sum( len( h["text"].split() ) for h in hits[:3]) for _, hits in answerable)),
        # our confidence scores
            # we use the gap between them to choose our relevance floor
        "top_score_answerable" : round(statistics.mean(hits[0]["score"] for _, hits in answerable),3),
        "top_score_unanswerable" : round(statistics.mean(hits[0]["score"] for _, hits in unanswerable),3),
        "recall@3_by_kind": {kind: round(statistics.mean(v),2) for kind, v in sorted(kinds.items())},
        "missed@3": [q["id"] for (q, _), r in zip(answerable, ranks) if not r or r > 3],
    }
    
def main() -> None:
    print("Building indexes (free if nothing has changed)...")
    for strategy in chunking.STRATEGIES:
        b = chunk_index.build(strategy)
        print(f"  {strategy:<22} {b['chunks']:>3} chunks  "
              f"{'rebuilt' if b['rebuilt'] else 'up to date':<10}  {b['embedding_tokens']:>6} tokens")

    vectors, tokens = chunk_index.embed_batched([q["question"] for q in EVAL_SET], input_type="query")
    print(f"\nEmbedded {len(EVAL_SET)} questions once ({tokens} tokens), reused for every strategy.\n")

    results = {}
    for strategy in chunking.STRATEGIES:
        ranked = chunk_index.search_with_vectors(strategy, vectors, k=max(K_VALUES))
        results[strategy] = score_strategy(EVAL_SET, ranked)

    header = f"{'strategy':<22}{'R@1':>6}{'R@3':>6}{'R@5':>6}{'MRR':>7}{'ctx words':>11}{'top ans':>9}{'top unans':>11}"
    print(header)
    print("-" * len(header))
    for strategy, r in results.items():
        print(f"{strategy:<22}{r['recall@1']:>6.2f}{r['recall@3']:>6.2f}{r['recall@5']:>6.2f}"
              f"{r['mrr']:>7.2f}{r['context_words@3']:>11}{r['top_score_answerable']:>9.2f}"
              f"{r['top_score_unanswerable']:>11.2f}")
    print("\nMissed at k=3:")
    for strategy, r in results.items():
        print(f"  {strategy:<22} {', '.join(r['missed@3']) or 'none'}")

    Path("eval_results").mkdir(exist_ok=True)
    Path("eval_results/retrieval.json").write_text(json.dumps(results, indent=2))
    print("\nSaved eval_results/retrieval.json")


if __name__ == "__main__":
    main()
    
""" 

  whole_document          16 chunks  up to date       0 tokens
  fixed_100               46 chunks  up to date       0 tokens
  fixed_overlap_25        55 chunks  up to date       0 tokens
  sentenced_100           49 chunks  up to date       0 tokens
  sections_plain          71 chunks  up to date       0 tokens
  sections_contextual     71 chunks  up to date       0 tokens
Embedded 32 questions once (382 tokens), reused for every strategy.

strategy                 R@1   R@3   R@5    MRR  ctx words  top ans  top unans
------------------------------------------------------------------------------
whole_document          0.69  1.00  1.00   0.84        862     0.56       0.43
fixed_100               0.48  0.79  0.90   0.61        273     0.60       0.49
fixed_overlap_25        0.52  0.93  0.97   0.67        277     0.61       0.50
sentenced_100           0.41  0.76  0.90   0.57        262     0.60       0.50
sections_plain          0.31  0.86  0.93   0.54        186     0.61       0.52
sections_contextual     0.86  1.00  1.00   0.93        197     0.66       0.50

Missed at k=3:
  whole_document         none
  fixed_100              q02, q05, q08, q09, q22, q26
  fixed_overlap_25       q02, q09
  sentenced_100          q02, q03, q04, q08, q09, q20, q22
  sections_plain         q02, q04, q09, q22
  sections_contextual    none
  
Reading your table
Recall - Of all the TRUE values how many were actually flagged as true by the model (TP / (TP + FN))
Mean Reciprocal Rank (MRR)

MRR asks how high up the first relevant result appears.

MRR - For each query, take the reciprocal of the rank of the first relevant item: rank 1 gives 1, rank 2 gives 0.5, rank 5 gives 0.2, and so on (0 if none is found). MRR is the average of that value across all queries.

Recall@k measures coverage: did you retrieve everything needed? 
It is insensitive to ranking within the top k. 
MRR measures ranking quality for the first hit: is the best result near the top? 
It is insensitive to how many other relevant items were found.

"""

"""
1. Is chunking worth it? Compare whole_document with your best chunked strategy on MRR and on ctx words. 
Yes. sections_contextual was the best performing one, which performed better than whole_document. We pay more and get less from whole_documents. 
MRR is higher and ctxt words in lower, Ranks relevant infor higher with fewer required tokens for the context,improving performance and saving on tokens.

2. What did blind splitting cost? 
Blind splitting led to poorer recall performance and lower MRR scores. Hits ceiling at 5 as it cuts 3 answers in half

3. What did the contextual prefix buy? sections_plain and sections_contextual split identically. Any difference between them is the prefix alone. Open retrieval.json and compare recall@3_by_kind for heading-dependent and title-dependent.
The contextual prefix provides improved context association to the chunk, leading to better recall on heading dependent and title dependent questions.

4. Which questions fail everywhere? A question missed by every strategy is not a chunking problem. Check its kind: negation and exact-id misses point at the embedding model, and that is next lesson's material, hybrid retrieval.
q02 fails everywhere but in sections_contextual. It is title-dependent question. Hybrid retrieval

5. The two score columns. Are unanswerable questions' best scores clearly below answerable ones? If they overlap, no single floor separates them cleanly.
Unanswerables scores lower than answerable scores. There is a clear split at 0.52 and 0.56.
This shows that the answerable questions have a clearly better score over unanswerable.
Our releance floor would need to increase to 0.52 to stop unaswerable questions being answered.

Choose a shortlist of your two best chunked strategies for Step 7, and keep whole_document as the baseline.

sections_contextual
fixed_overlap_25

"""