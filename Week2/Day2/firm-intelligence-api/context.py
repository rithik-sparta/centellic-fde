""" 
How retrieved hits become the text the model reads
Failure: lost in the middle


"""

# hits
from typing import Any
"""
Outcomes
By the end you can:

Validate an eval set with tests before trusting any score it produces.
Build and test six chunking strategies behind one interface.
Measure chunking damage before spending a single token.
Build one vector index per strategy with batched embedding and automatic rebuild detection.
Compute recall@k, mean reciprocal rank and context cost for every strategy.
Measure answer accuracy and refusal accuracy, and re-tune the relevance floor from data.
Ship the winning strategy behind the existing API and record the decision with evidence.
"""


# document_id -> relevance score
def order_for_context(scores : list[dict[str, Any]]) -> list[dict]:
    
    
    ranked = sorted(scores, key = lambda x : x["score"], reverse=True)
    
    front = ranked[0::2]
    
    back = ranked[1::2]
    back = back[::-1]
    
    return front + back


