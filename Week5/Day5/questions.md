
1. Why do we split documents into chunks at all? Name two of the three forces pulling on chunk size.

   * Precise vectors - One vector per topic, not one vector for several topics averaged
   * Complete Evidence - Cut a sentence in half, or lose its heading, and the model sees half a fact.
   * Context cost - Three whole document: about 750 words per answer. Three section chunks: about 190. We pay for every input token on every call. Want to be efficient with our token use.
2. What is the weakness of fixed 100-word chunks? Give a concrete example from our corpus.

   1. Context can be split across chunks, which can lead to the model getting incomplete context from searches.
3. What does overlap fix, and what can it never fix?

   1. Overlap fixes context splitting. Overlap does not fix sentences being cut off, no guarantee chunks contain whole sentences.
4. pack meets a sentence longer than the word limit. What does it do with it, and why?

   1. The sentence is put into its own seperate chunk
5. In sentences_100, a heading can end up at the bottom of one chunk, away from its own text. Why does that happen, and how does by_section avoid it?

   1. In sentence_100 a heading can end up at the bottom of a chunk as it splits the doc by sentences without taking into account sections.By section ensures chunks are created according to the sections of the document.
6. What does the contextual prefix add to a chunk, and what does it cost?

   1. Contextual Prefix - Adds the document title and heading to the beginning of the chunk in order to relate the chunk to the document and section it belongs to. It costs a small amount of tokens per chunk to add.
7. What is an evidence span, and why only count a retrieved chunk as a hit if it holds the whole span?

   1. Evidence Span - Holds a text snippet that must be in the chunk. We want to treat the retrieved chunk as a hit if it holds the entire evidence.
8. Recall@3 and MRR can disagree. Give an example of when.

   1. Recall - Do the top 3 chunks hold the correct answer.
   2. MRR - Does the top ranking chunk hold the correct answer
   3. These may disagree if only the first chunk is relevant giving a high MRR score, but a low recall score. Similarly if the top retrieved result is irrelevant, but the following 2 are it can give high recall, but low MRR score.
9. Why does build store a fingerprint, and what three things can make it trigger a rebuild?

   1. Chunking strategy
   2. Model
   3. text content
10. You change the chunking strategy. What else in the system might quietly stop being right, and how would you find out?

    1. If the chunking strategy is changed, retrieval can break as we would retrieve the wrong chunks from the previous chunking strategy. The relevance floor may be invalid due to the change in strategy and would have to be modified.
