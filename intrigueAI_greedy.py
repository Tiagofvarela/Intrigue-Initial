from intrigueAI import IntrigueAI


class Greedy(IntrigueAI):
    """Greedy always offers the least amount of money and tries to make the most profit.
    No preferences in targeting squares or people."""

    #PRIORITIES:
    #Square - How much this individual deal is good or bad, regardless of the bigger picture.
    PRIORITY_SQUARE:float = 1
    #Opinion - How much profit they've made or lost me.
    PRIORITY_OPINION:float = 0
    #Ownership - Difference between all my assets and all their assets.
    PRIORITY_OWNERSHIP:float = 1

    #BRIBE
    BRIBE_SQUARE_MULTIPLIER:float = 0.1
    BRIBE_MIN_SQUARE_MULTIPLIER:float = 0
    BRIBE_RANDOMNESS_FACTOR:float = 0
    BRIBE_MIN_COMPETE:int = 0
    BRIBE_OPINION_MULTIPLIER: float = 0

    #CONFLICT

    #PLACEMENT
    PLACEMENT_FAIRNESS = 0

    #APPLICATIONS
    APPLICATION_AVOID_REPEAT:float = 1
    APPLICATION_COMPETE:float = 0