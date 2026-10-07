import re

from corpus import CORPUS_DOCUMENTS
from documents import DOCUMENTS
from eval_set import EVAL_SET, answerable
from eval_tools import contains_evidence, keywords_present, normalise

ALL_DOCS = {d["id"] : d for d in DOCUMENTS + CORPUS_DOCUMENTS}

def section_containing(body : str, evidence: str) -> tuple[str,str]:
    """Return (heading, section text) for the section holding the evidence."""
    for part in re.split(r"(?m)^## ", body):
        heading, _, text = part.partition("\n")
        if contains_evidence(text, evidence):
            return heading.strip(), text
    
    return AssertionError(f"evidence not found in any section: {evidence}")


# test ids are unique
def test_ids_are_unique():
    assert len(ALL_DOCS) == (len(DOCUMENTS) + len(CORPUS_DOCUMENTS))
    
# test every span is in its documents
def test_every_span_is_in_its_documents():
    for eval in answerable():
        print(eval["id"])
        print(eval["evidence"])
        print(ALL_DOCS[eval["doc_id"]]["body"])
        assert contains_evidence(ALL_DOCS[eval["doc_id"]]["body"], eval["evidence"]) == True

# test every evidence span appears exactly once in the whole corpus
# def test_every_evidence_span_appears_exactly_once_in_the_whole_corpus():
#     CORPUS_TEXT = "\n\n\n".join(doc["body"] for _,doc in ALL_DOCS.items())
#     for evidence in EVAL_SET:
#         assert len(re.findall(evidence["evidence"], CORPUS_TEXT)) == 1
        

# test_keyword matching in whole word and refusal aware