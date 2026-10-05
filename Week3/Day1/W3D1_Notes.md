* Retry with exponential backoff not implemented in Anthropic API, because retries are configured client side, not server side.

## Embeddings and First Retrieval

* Match by meaning.
* Embeddings treats text as positions in space
* Vectors point in similar direction even with no words in common.
* Vector point elsewhere, even if they share plenty of words.
* cosine similarity = measures similarity of two vectors
  * 1 = close to identical
  * 0.6-0.9 = similar
  * 0.0 = unrelates
  * below 0.6 = unrelated. must decide what to do
  * formula = a.b/abs(a)abs(b)
* fuzzy match

## Key takeaways

* Embeddings are a treated as positions in space
* Use cosine similarity to compare two vectors together
* Vector embeddings encode meaning of a token, or text.
* Monkeypatch used to mock functionality
* Voyageai is an embedding model used to create vectors from texts.
* Where to use a larger model?
* How a model attaches meaning in terms of vector.
  * Attention mechanism
* Evaluate embeddings against benchmarks to test how well they capture meaning
