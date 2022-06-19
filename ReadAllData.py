# This program uses the music21 library to read all of Bach's chorales. It then encodes them and saves them using picle.
from functions import *
import pickle

# Let's search for all the bach chorales
bachCorpus = corpus.search('bach', fileExtensions='xml')
# let's parse this shit
bachParsed = []
for score in bachCorpus:
    chorale = score.parse()
    if isChorale(chorale):  # checking if this score is indeed a chorale with four voice parts
        bachParsed.append(transposeScore(chorale))  # if it is, transpose it and keep it in our database
# Let's make a dictionary to keep all the different tokens
tokens = {"START": 0, "END": 1, "|||": 2, "(.)": 3, "-": 4}  # This dictionary contains all different tokens. START
# marks the beginning of a piece, END mark the end of a piece, ||| is a time step delimiter, (.) signifies a fermata and
# - is a 16th note rest.
t_index = 5
sop_tokens = []  # This list will contain all the soprano tokens in sequence
alto_tokens = []  # This list will contain all the alto tokens in sequence
ten_tokens = []  # This list will contain all the tenor tokens in sequence
bass_tokens = []  # This list will contain all the bass tokens in sequence
fermatas = []  # This list will contain boolean variables. True if there is a fermata in this time step, false if there
# is not
# Let's iterate over every chorale
for chorale in bachParsed:
    # Let's get the four parts that we need
    soprano = chorale.parts.getElementById('Soprano')
    alto = chorale.parts.getElementById('Alto')
    tenor = chorale.parts.getElementById('Tenor')
    bass = chorale.parts.getElementById('Bass')
    for part in [soprano, alto, tenor, bass]:  # For every part
        hasSemiDemi = False  # this variable shows if the note has a duration shorter than our sampling rate
        for n in part.recurse().notesAndRests:  # for every note in this part
            thisVoice = []  # this list temporarily contains all the tokens of the given voice in sequence
            hasFermata = False  # this variable shows if this particular note has a fermata
            if note.Rest in n.classSet:  # if we have a rest
                restDuration = int(n.quarterLength / 0.25)
                thisVoice.extend(["-"] * restDuration)
                if part.id == 'Soprano':
                    fermatas.extend([False] * restDuration)
            else:  # if we have a note
                midiNumber = n.pitch.midi  # this is the note's midi number {0,127}
                tieCount = int((n.quarterLength / 0.25)) - 1  # we sample in 16th notes. How many times to append
                # this note?
                if part.id == 'Soprano':  # we don't need to check all voices for expressions
                    hasExpression = (len(n.expressions) != 0)  # Does this note have any expression objects (e.g.
                    # fermatas)?
                else:
                    hasExpression = False
                if hasExpression:  # If this note has expressions, let's see if it is a fermata
                    for exp in n.expressions:
                        if expressions.Fermata in exp.classSet:
                            hasFermata = True  # Hey we found a fermata!
                if tieCount > 0:  # if the duration is greater than 16th
                    tokenStart = (midiNumber, False)  # Token starts with hasTie = False since it's a new note
                    tokenEnd = (
                        midiNumber, True)  # Token ends with hasTie = True since its duration is more than a 16th note
                    tokens[tokenStart] = t_index  # insert the start token into the dictionary, t_index is the value and
                    # token is the key
                    t_index += 1
                    tokens[tokenEnd] = t_index  # insert the ending token
                    t_index += 1
                    thisVoice.append(tokenStart)  # this voice sings this token this many times in sequence
                    if part.id == 'Soprano':  # if this is the soprano part maybe we need to append fermatas
                        if hasFermata:  # if there is a fermata
                            fermatas.extend(
                                [True] * (tieCount + 1))  # we append true times equal to the duration of the note
                        else:  # if there is no fermata
                            fermatas.extend(
                                [False] * (tieCount + 1))  # we append False times equal to the duration of the note
                    thisVoice.extend([tokenEnd] * tieCount)
                elif n.quarterLength != 0:  # if it is a 16th note or shorter (make sure it is not a grace note)
                    if not hasSemiDemi:  # if the previous note was NOT a semidemiquaver
                        tokenStart = (midiNumber, False)
                        tokens[tokenStart] = t_index  # insert into the dictionary
                        t_index += 1
                        thisVoice.append(tokenStart)  # append in the voice sequence
                        if part.id == 'Soprano':  # A fermata probably won't be on a 16th note, but just to be safe
                            if hasFermata:
                                fermatas.append(True)
                            else:
                                fermatas.append(False)
                    if n.quarterLength < 0.25 and not hasSemiDemi:  # if this is the first semidemiquaver of the pair
                        hasSemiDemi = True
                    elif n.quarterLength < 0.25 and hasSemiDemi:  # if this is the second semidemiquaver of the pair
                        hasSemiDemi = False
            if part.id == 'Soprano':  # if this part is soprano, save her singing sequence here
                sop_tokens.extend(thisVoice)
            elif part.id == 'Alto':  # if this part is alto, save her singing sequence here
                alto_tokens.extend(thisVoice)
            elif part.id == 'Tenor':  # if this part is tenor, save his singing sequence here
                ten_tokens.extend(thisVoice)
            else:  # if this part is bass, save his singing sequence here
                bass_tokens.extend(thisVoice)
    endOfPiece = ["END", "START"]  # We insert these to signify the ending of one chorale
    sop_tokens.extend(endOfPiece)  # and the beginning of the next
    alto_tokens.extend(endOfPiece)
    ten_tokens.extend(endOfPiece)
    bass_tokens.extend(endOfPiece)
    fermatas.extend([False, False])  # Fermatas sequence must be of same length
# Now let's make our token sequence. The piece will begin with the START token then for every time step there will be
# four notes (Soprano, Alto, Tenor, Bass) and then a time step delimiter (|||). If at any given time step there is a
# fermata, a (.) token will appear prior to the note tokens
tokenSequence = ["START"]  # this signifies the beginning of the piece
sopranoOnlySequence = ["START"]  # this is just the soprano notes for testing the model later
for i in range(len(sop_tokens)):
    if sop_tokens[i] == "END" or sop_tokens[i] == "START":  # check if its a metadata token
        tokenSequence.append(sop_tokens[i])
        sopranoOnlySequence.append(sop_tokens[i])
    else:
        if fermatas[i]:  # if there is a fermata at this time step
            tokenSequence.append("(.)")  # append it
            sopranoOnlySequence.append("(.)")
        tokenSequence.append(sop_tokens[i])  # append the notes for this time step from soprano to bass
        sopranoOnlySequence.append(sop_tokens[i])
        tokenSequence.append(alto_tokens[i])
        tokenSequence.append(ten_tokens[i])
        tokenSequence.append(bass_tokens[i])
        tokenSequence.append("|||")  # this signifies that this time step has ended
        sopranoOnlySequence.append("|||")
# Because we inserted both "END" and "START" tokens at the same time, we have an extra "START" at the end
# of the sequence. Let's remove it!
del tokenSequence[-1]
del sopranoOnlySequence[-1]
# Let's tidy up the dictionary we just made, so the values are integers in ascending order [0, len(dict))
n = 0
for key in tokens:
    tokens[key] = n
    n += 1
# Now let's encode our data using the dictionary we made earlier
encodedSequence = []
for token in tokenSequence:
    encodedSequence.append(tokens[token])
# Now that our sequence is encoded an ready to go for network preprocessing, let's create a dictionary for decoding
dec_tokens = {v: k for k, v in tokens.items()}
# Let's check that we did everything correctly
decodedSequence = []
for token in encodedSequence:
    decodedSequence.append(dec_tokens[token])
if tokenSequence == decodedSequence:
    print("You beautiful bastard you did it!")
# Now we are going to use pickle to save the encoding and decoding dictionaries as well as the encoded sequence to
# memory, so that we can use them in other files too
with open('/Users/Konstandinos/Desktop/encodingDictionary.pkl', 'wb') as f:
    pickle.dump(tokens, f)  # pickling the encoding dictionary
with open('/Users/Konstandinos/Desktop/decodingDictionary.pkl', 'wb') as f:
    pickle.dump(dec_tokens, f)  # pickling the decoding dictionary
with open('/Users/Konstandinos/Desktop/encodedSequence.pkl', 'wb') as f:
    pickle.dump(encodedSequence, f)  # pickling the encoded sequence
with open('/Users/Konstandinos/Desktop/Generation/sopranoOnlySequence.pkl', 'wb') as f:
    pickle.dump(sopranoOnlySequence, f)