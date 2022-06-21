# This file contains functions used by the GeneratedSequenceDecoding file.
# They need to be saved in the same folder.

from music21 import *


# This functions takes as arguments two lists (padded); one for the melody and one for harmonization.
# it creates an xml file of the piece returning True on a success
def generateSheetMusic(melody, harmonization):
    sequence_length = len(melody)
    tSignature = meter.TimeSignature('6/8')
    soprano = stream.Part(id='Soprano')
    soprano.partName = 'Soprano'
    #soprano.append(tSignature)
    alto = stream.Part(id='Alto')
    alto.partName = 'Alto'
    #alto.append(tSignature)
    tenor = stream.Part(id='Tenor')
    tenor.partName = 'Tenor'
    #tenor.append(tSignature)
    bass = stream.Part(id='Bass')
    bass.partName = 'Bass'
    #bass.append(tSignature)
    # let's separate the harmonization sequence into three voices for easier processing
    alto_sequence = []
    tenor_sequence = []
    bass_sequence = []
    i = 0
    while harmonization[i] != "END":
        if harmonization[i] == "START":
            i += 1
        elif harmonization[i] == "|||":
            if harmonization[i + 1] == "(.)":
                alto_sequence.extend([harmonization[i + 1], harmonization[i + 2]])
                tenor_sequence.extend([harmonization[i + 1], harmonization[i + 3]])
                bass_sequence.extend([harmonization[i + 1], harmonization[i + 4]])
                i += 5
            else:
                alto_sequence.extend([harmonization[i + 1]])
                tenor_sequence.extend([harmonization[i + 2]])
                bass_sequence.extend([harmonization[i + 3]])
                i += 4
    soprano_sequence = []
    for i in range(len(melody)):
        if melody[i] != "|||" and melody[i] != "END" and melody[i] != "PAD" and melody[i] != "START":
            soprano_sequence.append(melody[i])
    # now let's decode the parts
    soprano = createPart(soprano_sequence, soprano)
    alto = createPart(alto_sequence, alto)
    tenor = createPart(tenor_sequence, tenor)
    bass = createPart(bass_sequence, bass)
    s = stream.Score()
    s.append(soprano)
    s.append(alto)
    s.append(tenor)
    s.append(bass)
    s.show()


def createPart(sequence, voicePart):
    midiNumber = sequence[0][0]
    noteDuration = 0.25
    hasFermata = False
    previousToken = "Note"
    currentToken = "Note"
    for i in range(1, len(sequence)):
        if sequence[i] == "(.)":
            hasFermata = True
        elif sequence[i] == "-":
            previousToken = currentToken
            currentToken = "Pause"
            if previousToken == "Note":
                n = note.Note(midiNumber)
                n.duration.quarterLength = noteDuration
                if hasFermata and sequence[i-1] != "(.)":
                    n.expressions.append(expressions.Fermata())
                    hasFermata = False
                voicePart.append(n)
            n = note.Rest()
            n.duration.quarterLength = 0.25
            voicePart.append(n)
        else:
            previousToken = currentToken
            currentToken = "Note"
            if sequence[i][1]:
                noteDuration += 0.25
            else:
                if previousToken != "-":
                    n = note.Note(midiNumber)
                    n.duration.quarterLength = noteDuration
                    if hasFermata and sequence[i-1] != "(.)":
                        n.expressions.append(expressions.Fermata())
                        hasFermata = False
                    voicePart.append(n)
                midiNumber = sequence[i][0]
                noteDuration = 0.25
    if currentToken == "Pause":
        if previousToken == "Note":
            n = note.Note(midiNumber)
            n.duration.quarterLength = noteDuration
            voicePart.append(n)
        n = note.Rest()
        n.duration.quarterLength = 0.25
        voicePart.append(n)
    else:
        n = note.Note(midiNumber)
        n.duration.quarterLength = noteDuration
        voicePart.append(n)

    return voicePart
