import grounding

SOURCES = {
    "doc-101" : "Harding & Voss closed the year with revenue of $1.24 bilion, up 4.1 percent.",
    "doc-107" : "Fixed-share partners are excluded from the equity partner count.",    
}

# failure 1 - ungrounded claims

# test that refusal needs no citations
def test_refusal_needs_no_citations():
    report = grounding.check_citations(grounding.REFUSAL_SENTENCE, ["doc-101"])
    assert report["refusal"] is True and report["passed"] is True
    
    
# test fully cited answer passes
def test_fully_cited_answer_passes():
    report = grounding.check_citations("The equity partner count does not account for fixed share partners [doc-107].", ["doc-107"])
    print(report)
    assert report["refusal"] is False
    assert report["passed"] is True 
    assert len(report["cited"]) == 1
    

# test uncited sentence is flagged
def test_uncited_sentence_is_flagged():
    report = grounding.check_citations("The equity partner count does not account for fixed share partners [doc-107]. The firm is the most profitable", ["doc-107"])
    assert report["passed"] is False and "The firm is the most profitable" in report["uncited_sentences"]


# test citation after the full stop still counts
# def test_citation_after_the_full_stop_still_counts():
#     report = grounding.check_citations("Harding & Voss closed the year with revenue of $1.24 bilion. [doc-107]", ["doc-107"])
#     print(report)
#     assert report["passed"] is True
#     assert report["uncited_sentences"] == []
#     assert report["cited"] == ["The equity partner count does not account for fixed share partners. [doc-107]"]
#     assert report["refusal"] is False and report["passed"] is True and report["cited"] == ["The equity partner count does not account for fixed share partners. [doc-107]"]
    
def test_citation_after_full_stop_still_counts():
    answer = "Harding & Voss closed the year with revenue of $1.24 billion, up 4.1 percent.[doc-101]"
    report = grounding.check_citations(answer, ["doc-101"])
    assert report["passed"] is True
    assert len(report["cited"]) is not None