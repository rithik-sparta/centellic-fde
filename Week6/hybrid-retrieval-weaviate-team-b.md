# Hybrid retrieval briefing: Weaviate, Team B

## How it does hybrid search

Weaviate hybrid search runs **vector search and BM25F keyword search in parallel**, then fuses the two result sets into one ranking. A Python query uses `collection.query.hybrid(query="...", alpha=..., limit=...)`.

Source: Weaviate, *Hybrid search*
https://docs.weaviate.io/weaviate/concepts/search/hybrid-search

## Fusion and its defaults

**Method:** Weaviate supports `rankedFusion` and `relativeScoreFusion`. `relativeScoreFusion` has been the default since **v1.24**.

**How they differ:** `rankedFusion` keeps only each result's position in the two lists, so it is easy to combine very different scoring systems but throws away how large the score gaps were. `relativeScoreFusion` min-max normalises the BM25 and vector scores to 0–1 and then combines the weighted scores, so it keeps information about whether one result won by a lot or by a very small margin.

**Why Weaviate prefers score-based fusion:** its documentation says `relativeScoreFusion` retains more information from the original searches than rank-only fusion. For example, if the top BM25 result is far ahead of the rest while several vector results are nearly tied, score-based fusion can preserve that difference.

**Weighting:** `alpha` controls the vector side. `alpha=0` is keyword-only, `0.5` gives equal weight, and `1` is vector-only. The **server default is 0.75**, but Weaviate warns that client/server versions can affect the effective value, so `alpha` should be set explicitly when it matters.

Sources:
https://docs.weaviate.io/weaviate/concepts/search/hybrid-search
https://weaviate.io/blog/hybrid-search-fusion-algorithms

## The keyword side

Weaviate's keyword retriever is **BM25F**, a classic sparse/lexical method backed by an inverted index. BM25 scores literal query terms using term frequency, inverse document frequency and document-length normalisation. Weaviate's default BM25 parameters are `k1=1.2` and `b=0.75`.

For our app, this matters because an exact identifier such as `LP-3307` may have little semantic meaning to an embedding model but can be matched directly by BM25.

A learned sparse alternative is **Elastic ELSER**. Instead of relying only on literal terms, ELSER expands text into learned weighted terms representing associations learned by the model.

Sources:
https://docs.weaviate.io/weaviate/concepts/search/keyword-search
https://www.elastic.co/docs/explore-analyze/machine-learning/nlp/ml-nlp-elser/

## One catch

Hybrid search adds more tuning. We must choose the fusion method and `alpha`, and Weaviate's fused score is not the same thing as our current Voyage/Chroma cosine score. Therefore our existing relevance floor of `0.53` should **not** simply be reused as a hybrid threshold; it would need to be calibrated again on our evaluation set.

There is also a version/client detail: Weaviate documents `0.75` as the server default for `alpha`, but says clients do not always leave `alpha` unset, so the effective weighting can differ. We should set it explicitly.

* **Only one search operator is allowed per query** at the collection level.
* **Collections with named vectors must specify a target vector.**

Source:
https://docs.weaviate.io/weaviate/concepts/search/hybrid-search

## Evidence that hybrid helps

Microsoft compared keyword, vector and hybrid retrieval using Azure AI Search on customer datasets and academic benchmarks. On its customer datasets, **NDCG@3 improved from 43.8 for vector-only to 48.4 for hybrid**, a gain of 4.6 points (about 10.5%). On **BEIR**, NDCG@10 improved from **45.0 to 48.4**, a gain of 3.4 points (about 7.6%). On MIRACL the gain was much smaller, from 58.3 to 58.8, showing that hybrid does not improve every dataset by the same amount.

This was a **vendor-run Microsoft benchmark**, so it is useful evidence rather than neutral proof.

Source:
https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/azure-ai-search-outperforming-vector-search-with-hybrid-retrieval-and-reranking/3929167

## Core questions

**1. Rank or score: what does each gain and lose?**
Rank-based fusion such as RRF is robust because it only needs the ordering of each retriever's results, so incompatible BM25 and vector score scales are not a problem. Its weakness is that it throws away score magnitude. Score-based fusion preserves more information about how strongly each retriever preferred one result over another, but depends on how the scores are normalised and can be more sensitive to score distributions.

RRF itself was introduced by Cormack, Clarke and Buettcher in 2009. Their experiments reported that RRF beat the best individual ranking by roughly 4–5% on average across their tested settings.


| Rank-based fusion                                                                                                                                                                                                                                                                                                    | Score-based-fusion                                                                                                                                                                                                                                         |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| RRF_score(d) = Σ over retrievers of  1 / (k + rank_i(d))                                                                                                                                                                                                                                                            | final = α · vector_score + (1 − α) · bm25_score                                                                                                                                                                                                       |
| Uses the position of each item in each score list.                                                                                                                                                                                                                                                                  | Combines the raw scores each retriever assigned using a weighted sum.                                                                                                                                                                                      |
| Reciprocal Rank Fusion (RFF). Sums the reciprocal ranks of documents in each scoring metric.<br />e.g. if doc-01 is scored 1st with metricA but 3rd with metric B. Its score is 1/1 + 1/3.                                                                                                                           | Scores are normalised before addition, to account for scales of scoring systems.                                                                                                                                                                           |
| Sometimes a smoothing constant k is added to the denominator.                                                                                                                                                                                                                                                        | Sum can be weighted to account more for one scoring system over others.                                                                                                                                                                                    |
| Strengths: <br />No normalisation or scale matching needed. <br />Robust to outlier scores, works with any retriever, and it needs almost no tuning. Strong default                                                                                                                                                  | Strengths:<br />Keeps magnitude information.<br />Weights allow you to decide which strategy is given how much importance                                                                                                                                  |
| Weaknesses: <br />Discards magnitude. <br />Rank 1 might be a near-perfect match in one list and a mediocre one in the other, but RRF treats them the same. It also can’t express “this retriever is more trustworthy” without adding explicit weights, and you can’t threshold on a meaningful absolute score. | Weaknesses:<br />Sensitive to method of normalisation. Min-Max depends on best and worst items in the list. Prone to outliers.<br />The weights can be query dependent, one weight maybe better suited for some types of queries over others. Needs tuning |

Source:
https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf

---



**2. Does hybrid actually help?**
Yes, it can. In Microsoft's benchmark, hybrid beat vector-only on both the customer datasets and BEIR: 43.8 → 48.4 NDCG@3 on the customer data and 45.0 → 48.4 NDCG@10 on BEIR. The smaller MIRACL gain shows that the benefit depends on the data and query types.

Source:
https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/azure-ai-search-outperforming-vector-search-with-hybrid-retrieval-and-reranking/3929167

Source: [An Analysis of Fusion Functions for Hybrid Retrieval](https://arxiv.org/pdf/2210.11934)

One source is **Bruch, Gai and Ingber, “An Analysis of Fusion Functions for Hybrid Retrieval”** (arXiv 2210.11934, ACM DOI 10.1145/3596512). It compares keyword-only, vector-only and hybrid retrieval head to head across nine datasets, and the authors report significance tests. Hybrid beat both single retrievers on every dataset when fused by a weighted score combination.

* **Who ran it:** Sebastian Bruch, Siyu Gai (UC Berkeley, interning at Pinecone) and Amir Ingber. Bruch and Ingber are at Pinecone, which sells a vector database.
* **Datasets:** MS MARCO Passage v1 (8.8M passages, 6,980 dev queries) plus eight BEIR sets: NQ (2.68M docs, 3,452 queries), Quora (523K, 10,000), NFCorpus (3.6K, 323), HotpotQA (5.23M, 7,405), FEVER (5.42M, 6,666), SciFact (5K, 300), DBPedia (4.63M, 400) and FiQA (57K, 648).
* **Systems:** BM25 (PISA, k1=0.9, b=0.4) as keyword search, and all-MiniLM-L6-v2 (384-dimensional vectors, exact FAISS search) as vector search. Hybrid was either a weighted score combination (“TM2C2”, α=0.8) or RRF (η=60).
* **Metrics:** NDCG@1000 and Recall@1000, with the cutoff at 100 for SciFact and NFCorpus. NQ, MS MARCO and Quora are “in-domain” because the embedding model was fine-tuned on them. The other six are zero-shot.

Hybrid search beat both keyword-only (BM25) and vector-only retrieval in this paper, with a bigger gain over the weaker retriever on each dataset. All numbers below come from the paper’s Table 2.

### Setup and metrics

* **Systems:** BM25 for keyword, all-MiniLM-L6-v2 for vector, and two hybrids. One is a weighted score combination (the paper’s “TM2C2”, α = 0.8). The other is RRF (η = 60).
* **Datasets:** MS MARCO, NQ and Quora are “in-domain”, since the embedding model was fine-tuned on them. NFCorpus, HotpotQA, FEVER, SciFact, DBPedia and FiQA are zero-shot.
* **Metrics:** NDCG@1000 as the main metric, with Recall@1000 alongside. The cutoff is 100 for SciFact and NFCorpus because they are small. Significance was tested with paired two-tailed t-tests at p < 0.01.

### Size of the gain (NDCG)

| Dataset        | BM25  | Vector | Hybrid (weighted) | Gain vs vector            | Gain vs BM25              |
| -------------- | ----- | ------ | ----------------- | ------------------------- | ------------------------- |
| MS MARCO       | 0.309 | 0.441  | 0.454             | +0.013                    | +0.145                    |
| NQ             | 0.382 | 0.505  | 0.542             | +0.037                    | +0.160                    |
| Quora          | 0.800 | 0.889  | 0.901             | +0.012                    | +0.101                    |
| NFCorpus       | 0.268 | 0.296  | 0.327             | +0.031                    | +0.059                    |
| HotpotQA       | 0.682 | 0.520  | 0.699             | +0.179                    | +0.017                    |
| FEVER          | 0.689 | 0.558  | 0.744             | +0.186                    | +0.055                    |
| SciFact        | 0.698 | 0.681  | 0.753             | +0.072                    | +0.055                    |
| DBPedia        | 0.415 | 0.425  | 0.512             | +0.087                    | +0.097                    |
| FiQA           | 0.315 | 0.467  | 0.496             | +0.029                    | +0.181                    |
| **Mean** | 0.506 | 0.531  | **0.603**   | **+0.072 (+13.5%)** | **+0.097 (+19.1%)** |

## Recall@1000

| Dataset              | BM25  | Vector | Hybrid (weighted) | Hybrid (RRF) | Weighted gain vs vector  | Weighted gain vs BM25    |
| -------------------- | ----- | ------ | ----------------- | ------------ | ------------------------ | ------------------------ |
| MS MARCO (in-domain) | 0.836 | 0.964  | 0.974             | 0.969        | +0.010                   | +0.138                   |
| NQ (in-domain)       | 0.886 | 0.978  | 0.985             | 0.984        | +0.007                   | +0.099                   |
| Quora (in-domain)    | 0.992 | 0.999  | 0.999             | 0.999        | 0.000                    | +0.007                   |
| NFCorpus             | 0.255 | 0.320  | 0.338             | 0.327        | +0.018                   | +0.083                   |
| HotpotQA             | 0.878 | 0.756  | 0.884             | 0.888        | +0.128                   | +0.006                   |
| FEVER                | 0.969 | 0.931  | 0.972             | 0.972        | +0.041                   | +0.003                   |
| SciFact              | 0.900 | 0.932  | 0.958             | 0.955        | +0.026                   | +0.058                   |
| DBPedia              | 0.540 | 0.408  | 0.564             | 0.567        | +0.156                   | +0.024                   |
| FiQA                 | 0.720 | 0.908  | 0.907             | 0.904        | −0.001                  | +0.187                   |
| **Mean**       | 0.775 | 0.800  | **0.842**   | 0.841        | **+0.043 (+5.4%)** | **+0.067 (+8.7%)** |

* **Weighted hybrid:** it was ahead of both single retrievers on every dataset, and every NDCG difference was significant at p < 0.01. The smallest gain over the better single retriever was +0.012 (Quora) and the largest was +0.087 (DBPedia).
* **RRF hybrid:** mean NDCG of 0.579, which is +0.047 (+8.9%) over vector-only and +0.072 (+14.2%) over BM25. It was less consistent. It scored below vector-only on MS MARCO, Quora and FiQA, and below BM25 on HotpotQA.
* **Recall@1000:** the gains were smaller, since recall at that depth is already high. For example, HotpotQA vector recall went from 0.756 to 0.884 with hybrid, and DBPedia from 0.408 to 0.564. On Quora and FiQA, vector-only recall was already about 0.91 to 1.0, so hybrid added nothing.

### Key findings

* **Hybrid helps most where one retriever is weak.** The largest gains over vector-only came on HotpotQA and FEVER (about +0.18, roughly +33% relative), where the vector model is far behind BM25. The largest gains over BM25 came on FiQA and the in-domain sets.
* **Gains are small where the vector model was fine-tuned.** On MS MARCO and Quora, hybrid beat vector-only by only about 0.01 NDCG.
* **Weighted combination beat RRF** on NDCG for every dataset. The authors say this contradicts an earlier study that favoured RRF.
* **RRF is sensitive to its parameters.** A version tuned on in-domain data generalized poorly to zero-shot datasets.
* **The normalization method barely matters** for the weighted combination, since different linear normalizations give equivalent rankings.
* **The weight is sample-efficient to tune.** Under 5% of the training queries was enough, and α between 0.6 and 0.8 consistently improved results.
* **An oracle choosing α per query would do much better** (for example 0.547 NDCG on MS MARCO), so there is headroom beyond one fixed weight.

### Caveats

* **Vector side:** it is one small embedding model. In their appendix, fusing BM25 with the stronger Splade model gave no gain on MS MARCO (0.507 against 0.508).
* **Tuning:** α = 0.8 was tuned on in-domain data and then applied to the zero-shot sets unchanged.
* **Authors:** Pinecone authors wrote it, and Pinecone sells vector search.

---



**3. Where does the keyword half come from?**
A classic example is **Weaviate BM25F**, which uses an inverted index and lexical term statistics. A learned sparse example is **Elastic ELSER**, which generates weighted learned terms and stores them as a sparse representation.

Sources:
https://docs.weaviate.io/weaviate/concepts/search/keyword-search
https://www.elastic.co/docs/explore-analyze/machine-learning/nlp/ml-nlp-elser/


In hybrid search, the keyword half comes from a second retrieval method that finds documents using terms rather than relying only on semantic similarity from embeddings.
There are two main approaches:

1. Classic lexical search (BM25): **searches an inverted index of terms found in documents. It works well when the query contains exact keywords, names, identifiers, or technical phrases.**

   1. BM25 is the algorithm that powers Elasticsearch and Solr, both of which use Lucene. It's been the standard in **information retrieval** since the 1990s and remains widely used today, even as neural approaches have emerged. [BM25: the Search Algorithm Behind Elasticsearch](https://mbrenndoerfer.com/writing/bm25-search-algorithm-elasticsearch-implementation)
2. Learned sparse retrieval: **uses a trained model to produce sparse, weighted term representations for queries and documents. It can match related terms that weren't explicitly present in the original query, while still using an inverted-index-style retrieval system**.

   1. SPLADE (Sparse Lexical and Expansion Model) -

   When SPLADE encodes a document, it produces a vector of length equal to the vocabulary size (typically ~30,000 for BERT-base). Most entries are zero. Non-zero entries represent *vocabulary tokens* that are relevant to this document — including tokens that weren't explicitly in the document but the model has learned are semantically related.

   The process works like this:

   1. Feed the document text through a BERT-style transformer
   2. **For each output token position, apply a linear projection to vocabulary size**, then RELU and log(1 + x) to encourage sparsity
   3. Max-pool across token positions: for each vocabulary word, take the maximum activation across all document positions
   4. The resulting sparse vector represents the document as a ***weighted bag of vocabulary terms***
   5. [Sparse Retrieval with BM25 and SPLADE: Implementing Learned Sparse Encoders Alongside Dense Vectors for Production Hybrid RAG](https://www.wickedsmartdata.com/articles/sparse-retrieval-with-bm25-and-splade-implementing-learned-sparse-encoders-alongside-dense-vectors-for-production-hybrid-rag#splade-learned-sparse-encoders)

   The hybrid system combines the results from this keyword-based retrieval with results from dense vector search, often using a method such as Reciprocal Rank Fusion (RRF).


## Advice for our app	

| Area            | Our app now                    | Recommendation                                                                                                            |
| --------------- | ------------------------------ | ------------------------------------------------------------------------------------------------------------------------- |
| Retrieval       | Voyage vector search only      | Test hybrid rather than replacing vector search                                                                           |
| Chunking        | `sections_contextual`        | Keep it as the baseline because it already performs strongly                                                              |
| Exact IDs       | `q24` can be falsely refused | Add a lexical/BM25 path to help exact identifiers such as `LP-3307`                                                     |
| Fusion          | None                           | Start by testing Weaviate-style `relativeScoreFusion` against a rank-based method                                       |
| Weighting       | None                           | Test `alpha` values such as `0.25`, `0.50` and `0.75`; do not assume the default is best                          |
| Relevance floor | `0.53` for vector retrieval  | Recalibrate after hybrid fusion because the score meaning changes                                                         |
| Evaluation      | 32-question labelled eval set  | Compare vector-only, keyword-only and hybrid on Recall@1, Recall@3, MRR, answer accuracy, refusal accuracy and token cost |

**Recommendation:** Yes, we should test hybrid search. Our vector retrieval is already strong on semantic questions, so keyword retrieval should be added as a complement, especially for exact IDs rather than as a replacement. I would only adopt it if the same evaluation set shows that it fixes cases such as `q24` without reducing performance on semantic questions.

## Open questions

- Which `alpha` performs best on our own corpus?
- Does `relativeScoreFusion` beat a rank-based method on our 32-question evaluation set?
- How should the relevance gate be recalibrated after fusion?
- Would an exact-ID field/tokenisation rule improve identifiers further than generic BM25 alone?

---



Weaviate

**Its default fusion is score-based, with an alpha setting. Why might it prefer that to rank-based fusion?**

Weaviate’s stated reason. Its docs say relativeScoreFusion “retains more information from the original searches than rankedFusion, which only retains the rankings.” They give a worked example where an object that is far ahead in one search gets rewarded for the size of its lead. Rank-based fusion treats rank 1 and rank 2 the same however far apart their scores are.

[Unlocking the Power of Hybrid Search - A Deep Dive into Weaviate&#39;s Fusion Algorithms](https://weaviate.io/blog/hybrid-search-fusion-algorithms#what-can-we-learn-from-this)
