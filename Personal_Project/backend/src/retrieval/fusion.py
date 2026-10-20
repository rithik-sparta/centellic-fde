"""
Rank fusion - merge ranked lists into one
"""

def reciprocal_rank_fusion(rankings : list[list[str]], k: int = 60) -> list[tuple[str,float]]:
    scores: dict[str,float] = {}
    for ranking in rankings:
        # Why we start from 1? Formula counts from 1. If we start from 0, top card will get 1/60 and our calculations will be off. 
        # If top card is used, we will have an off by one error
        for position, item in enumerate(ranking, start=1):
            scores[item] = scores.get(item, 0.0) + (1.0 / (k + position))
    # ties keep the order the ids were added
    return sorted(scores.items(), key = lambda pair : pair[1], reverse = True)
    # Each judge gives a card 1 / (k + position) points... position 1 is the top of that judges list
        # with the standard k = 60
            # position, points
            # 1st 1/61 = ...
            # 2rd 1/62 = ...
            # 3rd 1/63 = ...
    # k here controls how much being 1st matters -> the higher k is the less being first matters
    # Catch - RRF throws information away, only the position survives.
    