"""
Small, pure helpers for scoring. No network and no model.
"""


import re

from agent.grounding import is_refusal, normalise  # one definition of refusal


def contains_evidence(chunk_text : str, evidence : str) -> bool:
    """True if the chunk holds the whole evidence span. Line breaks never break a match."""
    return normalise(evidence) in normalise(chunk_text)


#alternative matches
def _alternative_matches(answer: str, alternative: str) -> bool:
    alternative = alternative.strip().lower()
    prefix = alternative.endswith("*")
    core = alternative.rstrip("*").strip()
    if not core:
        return False

    # Leading boundary
    if core[0].isdigit():
        # Numbers may follow letters or symbols (GBP7.5, $7.5, £7.5),
        # but must not be the tail of a longer number (17.5, 1,200).
        start = r"(?<![0-9])(?<![0-9][.,])"
    else:
        start = r"(?<![a-z0-9])"

    # Trailing boundary (unchanged)
    if prefix:
        end = ""
    elif core[-1].isdigit():
        end = r"(?![0-9])(?![.,][0-9])"
    else:
        end = r"(?![a-z0-9])"

    return re.search(start + re.escape(core) + end, answer.lower()) is not None


#keywords_present
# what the keywords list looks like
# Question                          keywords                            meaning
# q11 (offshore wind capacity)      ["4.2"]                             Must mention 4.2
# q14 (Okonkwo Bell offices)        ["Lagos", "Nairobi"]                Must mention both

def keywords_present(answer : str | None, keywords : list[str]) -> bool:
    """True only for a non-refusal answer that contains every keyword group"""
    if is_refusal(answer):
        return False
    
    return all(
        any(_alternative_matches(answer, alt) for alt in group.split("|")) for group in keywords
    )
    
    
# Answer                                    # result
# Offices in Lagos and Nairobi              True
# An office in Lagos                        False
# An office in Nairobi                      False
# 