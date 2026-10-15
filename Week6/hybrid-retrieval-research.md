Hybrid retrieval runs more than one retriever on the same query, typically keyword search (BM25) and vector search (embeddings), then merges their result lists into one. **Fusion** is the merging step. The two families differ in what they take from each list.

---

Fusion types:

**Rank or score? There are two families of fusion. Rank-based fusion (such as Reciprocal**

**Rank Fusion) uses only each list's order . Score-based fusion rescales each list's scores**

**and adds them. What does each gain, and what does each throw away?**

| Rank-based fusion                                                                                                                                                                                                                                                                                                    | Score-based-fusion                                                                                                                                                                                                                                         |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| RRF_score(d) = Σ over retrievers of  1 / (k + rank_i(d))                                                                                                                                                                                                                                                            | final = α · vector_score + (1 − α) · bm25_score                                                                                                                                                                                                       |
| Uses the position of each item in each score list.                                                                                                                                                                                                                                                                  | Combines the raw scores each retriever assigned using a weighted sum.                                                                                                                                                                                      |
| Reciprocal Rank Fusion (RFF). Sums the reciprocal ranks of documents in each scoring metric.<br />e.g. if doc-01 is scored 1st with metricA but 3rd with metric B. Its score is 1/1 + 1/3.                                                                                                                           | Scores are normalised before addition, to account for scales of scoring systems.                                                                                                                                                                           |
| Sometimes a smoothing constant k is added to the denominator.                                                                                                                                                                                                                                                        | Sum can be weighted to account more for one scoring system over others.                                                                                                                                                                                    |
| Strengths: <br />No normalisation or scale matching needed. <br />Robust to outlier scores, works with any retriever, and it needs almost no tuning. Strong default                                                                                                                                                  | Strengths:<br />Keeps magnitude information.<br />Weights allow you to decide which strategy is given how much importance                                                                                                                                  |
| Weaknesses: <br />Discards magnitude. <br />Rank 1 might be a near-perfect match in one list and a mediocre one in the other, but RRF treats them the same. It also can’t express “this retriever is more trustworthy” without adding explicit weights, and you can’t threshold on a meaningful absolute score. | Weaknesses:<br />Sensitive to method of normalisation. Min-Max depends on best and worst items in the list. Prone to outliers.<br />The weights can be query dependent, one weight maybe better suited for some types of queries over others. Needs tuning |

---

# BM25:

BM25 (Best Matching 25) is the standard keyword-ranking function. It scores each document by how well it matches the query terms, using three ideas: rare words matter more, repeated words help with diminishing returns, and long documents shouldn’t win just for being long.

### The formula

For a query Q and document D, the score is a sum over the query terms:

```
score(D, Q) = Σ over terms t in Q of   IDF(t) · [ f(t,D) · (k1 + 1) ] / [ f(t,D) + k1 · (1 − b + b · |D| / avgdl) ]
```

* `f(t,D)` is how many times term t appears in document D. Term frequency
* `|D|` is the document’s length and `avgdl` is the average document length in the collection.
* `IDF(t)` measures how rare the term is. A common form (used by Lucene) is `ln(1 + (N − n + 0.5) / (n + 0.5))`, where N is the number of documents and n is how many contain t.
* Hyperparameters:
  * k1 = k1 sets how quickly term frequency saturates. The higher k1 becomes the less importance we give to term frequency.
  * b = How much we penalise document length. Ranges from 0 to 1.

The three ideas

1. Rarity (IDF). A match on “the” tells you almost nothing, while a match on “ERR_4021” tells you a lot. Terms that appear in few documents get a high weight, and terms that appear everywhere get close to zero.
2. Term-frequency saturation. Seeing a word once is strong evidence, and seeing it ten times is only a bit stronger. The fraction f·(k1+1) / (f + k1·…) rises quickly and then flattens toward a ceiling of k1 + 1. With k1 = 1.2 and an average-length document, the per-term factor for a term appearing 1, 2, 5 and 10 times is about 1.0, 1.38, 1.77 and 1.96. It can never exceed 2.2. This stops keyword stuffing from dominating the score, which was a weakness of plain TF-IDF.
3. Length normalization. A long document has more chances to contain a term by accident. The |D| / avgdl term shrinks the contribution of matches in longer-than-average documents and boosts those in shorter ones. With k1 = 1.2, b = 0.75 and a term appearing 3 times, the factor is about 1.29 in a document twice the average length, 1.57 at average length, and 1.76 in a document half the average length.

---

## NDCG (Normalized Discounted Cumulative Gain)

**Measures how good a ranked list is. It rewards putting highly relevant results near the top and penalizes burying them lower down**. It’s the main metric in the paper we’ve been looking at, which reports NDCG@1000.

### How it’s built

1. **Gain.** Each result has a relevance grade, either binary (relevant or not) or graded (say 0 to 3).
2. **Cumulative.** DCG adds up the gains down the list.
3. **Discounted.** Each result’s gain is divided by `log2(rank + 1)`, so a result at rank 1 counts fully, rank 2 counts about 63%, and rank 10 about 29%.
4. **Normalized.** DCG is divided by the best score any ordering of those documents could achieve (the “ideal DCG”). That puts the result between 0 and 1.

```
DCG@k  = Σ (i = 1 to k)  rel_i / log2(i + 1)
NDCG@k = DCG@k / IDCG@k
```

Some implementations use `2^rel − 1` as the gain instead of `rel`, which emphasizes highly relevant results more. The formula above uses the linear version.

`rel_i` is the relevance grade of the document at rank position `i` in the results list. It’s a number a person (or a labeling process) assigned to that document for that query, and it is the “gain” that NDCG adds up.

IDCG@k is the “ideal” DCG@k: the highest DCG a ranking of the top k could possibly get for that query. It’s the denominator that turns DCG into NDCG:

### How it’s computed

1. Take every document that has a relevance label for the query.
2. Sort them from highest grade to lowest. This is the best ordering anyone could produce.
3. Apply the same DCG formula to the first k of that sorted list:

```
IDCG@k = Σ (i = 1 to k)  rel_i* / log2(i + 1)
```


`i` is the rank (1 for the top result, 2 for the next, and so on). `rel_i` is how relevant the document sitting at that rank is.

### Worked example

A query returns four documents with relevance grades 0, 3, 2, 1 in that order:

| Rank | Grade | Discount (log2(rank+1)) | Contribution |
| ---- | ----- | ----------------------- | ------------ |
| 1    | 0     | 1.000                   | 0.000        |
| 2    | 3     | 1.585                   | 1.893        |
| 3    | 2     | 2.000                   | 1.000        |
| 4    | 1     | 2.322                   | 0.431        |

DCG = 3.324. The ideal order is 3, 2, 1, 0, which gives 3 + 1.262 + 0.500 + 0 = 4.762. So NDCG@4 = 3.324 / 4.762 ≈  **0.70** . If the first two results were swapped to put the grade-3 document first, the score would rise to about 0.99.

### What it tells you, and how it differs from the other metrics

* **It handles graded relevance and the whole ranking.** Recall@k ignores order within the top k, and MRR looks only at the first relevant result. NDCG accounts for every position and for how relevant each result is.
* **The @k sets how deep it looks.** NDCG@10 judges the first page of results, which suits search and RAG. NDCG@1000, as in the paper, judges the whole candidate list, which suits a first-stage retriever feeding a reranker.
* **Scores aren’t comparable across datasets.** In the paper, vector-only NDCG was 0.441 on MS MARCO and 0.889 on Quora. That reflects the difficulty of the datasets and how their relevance labels were made, not a difference in the retriever. Compare methods on the same dataset.


---

**Does hybrid actually help? Find one published comparison with numbers: hybrid**

**against keyword-only or vector-only . Note the dataset, the metric, the size of the gain,**

**and who ran it.**

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

**Where does the keyword half come from? In production, is it classic BM25 from an inverted index, or a learned sparse model? Find one example of each.**

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

Weaviate

**Its default fusion is score-based, with an alpha setting. Why might it prefer that to rank-based fusion?**

Weaviate’s stated reason. Its docs say relativeScoreFusion “retains more information from the original searches than rankedFusion, which only retains the rankings.” They give a worked example where an object that is far ahead in one search gets rewarded for the size of its lead. Rank-based fusion treats rank 1 and rank 2 the same however far apart their scores are.

[Unlocking the Power of Hybrid Search - A Deep Dive into Weaviate&#39;s Fusion Algorithms](https://weaviate.io/blog/hybrid-search-fusion-algorithms#what-can-we-learn-from-this)
