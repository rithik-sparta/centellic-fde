"""
Chunking Strategies
Every strategy takes a docuent and returns a list of chunks.

A chunk is a dict:
    - id        "<doc id>#<two-digit-number>, kept stable for the same input
    - doc_id    the parent document, used for citations
    - title     the parent documents title
    - text      The text within the chunk. Exactly what gets embedded and what the model will read.
"""



import re


def _chunk(doc : dict, number : int, text : str) -> dict:
    # 2 - 02
    #  Add padding with numer:02d so sorting chunks is ordered correctly (lexicographical order)
    return {"id" : f"{doc['id']}#{number:02d}", "doc_id" : doc["id"], "title" : doc["title"], "text" : text}

def split_sentences(text: str) -> list[str]:
    """Sentences, with each '## Heading' line kept as a unit of its own"""
    units = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        
        if line.startswith("## "):
            units.append(line)
        else :
            units.extend(s for s in re.split(r"?<=[.!?]\s+", line) if s)
            
    return units
    
def pack(units: list[str], max_words: int) -> list[str]:
    """Join whole units until adding the next one would pass max_words"""
    # groups holds dinished chunks, current is the chunk being built, count is its word total
    groups, current, count = [], [], 0
    for unit in units:
        n = len(unit.split())
        if current and count + n > max_words:
            groups.append(" ".join(current))
            current, count = [], 0
        current.append(unit)
        count += n
    if current:
        groups.append(" ".join(current))
    return groups

# CHUNKING STRATEGIES

# whole document
def whole_documents(doc : dict) -> list[dict]:
    """baseline... what our project has done until now"""
    return [_chunk(doc, 0, doc["body"].strip())]

# fixed words
def fixed_words(doc : dict, size : int = 100, overlap: int = 0) -> list[dict]:
    """Every 'size' words, regardless of sentences or section. Cheap and blind"""
    if not 0 <= overlap < size:
        raise ValueError("overlap must be at least 0 and smaller than size")
    words = doc["body"].split()
    step = size - overlap
    chunks = []
    for number,start in enumerate(range(0,len(words), step)):
        chunks.append(_chunk(doc, number, "".join(words[start:start+size])))
        if start + size >= len(words):
            break
        
    
    return chunks
    

