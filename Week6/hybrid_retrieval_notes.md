* Keyword search - Matches words exactly
* Where vector search slips:
    * Exact identifiers
    * Rare iterms
    * Numbers and negation
* Answer is tied to a rare token. Keyword-search = rarity is the strongest signal.
* BM25
  * Rarity: A word in few chunks is worth more | none
  * Saturation: Repeats help with diminishing returns | k1
  * Length Normalisation: Long chunks are marked down | b
* Score of a chunk : Sum of query words it contains. 

## Hybrid Pipeline
* Embed question
* Search twice
* Fuse the rankings
* Keep each cosine
* Gate the answer

*
