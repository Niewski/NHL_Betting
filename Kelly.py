def getKellyDiff(probs, payout, limit):
    bookOdds = getImpliedOdds(payout)
    bookKelly = getKelly(bookOdds, payout)
    myKelly = getKelly(probs, payout)
    kellyDiff = (myKelly - bookKelly) * 100
    if kellyDiff > limit:
        return limit
    else:
        return round(kellyDiff, 2)

## Half-Kelly
def getKelly(probs, payout):
    return ((probs * payout - (1-probs)) / payout) / 2

def getImpliedOdds(payout):
    return 1 / payout