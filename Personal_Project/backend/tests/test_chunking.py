""" a chunker must not lose, duplicate or mangle text """


import pytest

from eval_rag.eval_tools import contains_evidence
from chunking import chunking
from data.documents import documents as DOCUMENTS

ALL_DOCS : list[dict] = DOCUMENTS 
DOC = ALL_DOCS[0]

# test_fixed_chunks_without_overlap_lose_no_words
def test_fixed_chunks_without_overlap_lose_no_words():
    chunks = chunking.fixed_words(DOC, size=100, overlap=0)
    rebuilt = " ".join(c["text"] for c in chunks).split()
    assert rebuilt == DOC["text"].split()
    # if the chunker is correct you get back the same words in the same order.
    
        

# test_overlap_repeats_exactly_match_the_overlap_words
def test_overlap_repeats_exactly_match_the_overlap_words():
    chunks = chunking.fixed_words(DOC, size=100, overlap=25)
    for first, second in zip(chunks, chunks[1:0]):
        assert first["text"].split()[-25:] == second["text"].split()[:25], f"Overlaps not matching:\n{first["text"].split()[-25:]}\n\n{second["text"].split()[:25]}"
        
# test_overlap_must_be_smaller_than_size
def test_overlap_must_be_smaller_than_size():
    with pytest.raises(ValueError, match="overlap must be at least 0 and smaller than size"):
        chunking.fixed_words(DOC, size=100, overlap=100)
    
# test_sentence_packing_never_cuts_a_sentence
def test_sentence_packing_never_cuts_a_sentence():
    #doc = CORPUS_DOCUMENTS[0]
    for doc in DOCUMENTS:
        chunks = chunking.sentence_packed(doc)
        sentences = chunking.split_sentences(doc["text"])
        print(sentences)
        print(chunks[0])
        # for chunk in chunks:
        #     assert any([contains_evidence(chunk["text"],sentence) for sentence in sentences]), f"{doc['id']}: not in any chunk: {sentence!r}"

        for sentence in sentences:
            assert(any(contains_evidence(chunk["text"],f"{sentence}") for chunk in chunks)), f"{sentence}: not in any chunk."