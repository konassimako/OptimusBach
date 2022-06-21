# This file is used by the ReadAllData.py file. It contains necessary functions to read the data.
from music21 import *


# This functions takes a score object as input an transposes it to C major (if it is in major key)
# or A minor (if it is in minor key)

def transposeScore(score):
    scoreKey = score.analyze('key')
    if scoreKey.mode == 'minor':
        i = interval.Interval(scoreKey.tonic, pitch.Pitch('A'))
        transScore = score.transpose(i)
        return transScore
    elif scoreKey.mode == 'major':
        i = interval.Interval(scoreKey.tonic, pitch.Pitch('C'))
        transScore = score.transpose(i)
        return transScore
    else:
        return False


# This function takes a score as an input and checks if it is a four part (voice) chorale.
# Returns true if it is, False if it is not


def isChorale(score):
    soprano = score.parts.getElementById('Soprano')
    alto = score.parts.getElementById('Alto')
    tenor = score.parts.getElementById('Tenor')
    bass = score.parts.getElementById('Bass')
    if (soprano is None) or (alto is None) or (tenor is None) or (bass is None):
        return False
    else:
        return True
