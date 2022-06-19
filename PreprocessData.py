# This program uses pickle to read an encoded sequence of all of Bach's chorales as well as the encoding-decoding
# dictionaries needed to process the data. Then we preprocess the data (input-output pairs) for our neural network.

import pickle
from itertools import repeat
from random import shuffle


# let's read our encoded sequence from memory
with open('/filepath/encodedSequence.pkl', 'rb') as f:
    encodedSequence = pickle.load(f)
# let's preprocess the data
encodedSoprano = []  # This is a list containing all the soprano sequences
encodedHarmonization = []  # This is a list containing all the harmonization sequences
for i in range(len(encodedSequence)):
    if encodedSequence[i] == 0 or encodedSequence[i] == 2:
        tempSoprano = [0]
        tempHarmonization = [0]
        n = 0
        j = i
        while n < 32:  # Each sequence must contain 32 time steps (delimiters)
            if encodedSequence[j+1] == 1:  # if the next token is "END" then we have reached the end of the chorale
                tempSoprano.append(encodedSequence[j])  # we append the time delimiter and stop
                tempHarmonization.append(encodedSequence[j])
                n = 32
                i = j+1  # move on to the end of the chorale
            elif encodedSequence[j+1] == 3:  # if the next token is a "Fermata" we append everything in between
                tempSoprano.extend([2, encodedSequence[j + 1], encodedSequence[j + 2]])
                tempHarmonization.extend([2, encodedSequence[j + 1], encodedSequence[j + 3],
                                    encodedSequence[j + 4], encodedSequence[j + 5]])
                j += 6  # move on to the next time step
                n += 1  # increment our time delimiter counter
            else:  # if we have a single time step with no fermatas we append everything in between
                tempSoprano.extend([2, encodedSequence[j + 1]])
                tempHarmonization.extend([2, encodedSequence[j + 2], encodedSequence[j + 3],
                                      encodedSequence[j + 4]])
                j += 5  # move on  to the next time step
                n += 1  # increment our time delimiter counter
        tempSoprano.append(1)  # we append the END token
        tempHarmonization.append(1)
        encodedSoprano.append(tempSoprano)
        encodedHarmonization.append(tempHarmonization)
# let's check that every pair of sequences has the same number of time steps(i.e. equal number of time delimiter tokens)
# the following piece of code performs the check mentioned above. It has been tested and everything is ok.
"""
allesOK = True
for i in range(len(encodedSoprano)):
    nSop = 0
    nHar = 0
    for j in range(len(encodedSoprano[i])):
        if encodedSoprano[i][j] == 2:
            nSop += 1
    for j in range(len(encodedHarmonization[i])):
        if encodedHarmonization[i][j] == 2:
            nHar += 1
    if nSop != nHar:
        allesOK = False
    if not allesOK:
        break
print(allesOK)
"""
with open("/filepath/encodedSoprano.pkl", "wb") as f:
    pickle.dump(encodedSoprano,f)
# The existence of fermatas in some time steps means that not all sequences will have the same length.
# We need to perform data padding. Let's load our dictionaries to create a padding token first
with open('/filepath/encodingDictionary.pkl', 'rb') as f:
    encodingDictionary = pickle.load(f)
with open('/filepath/decodingDictionary.pkl', 'rb') as f:
    decodingDictionary = pickle.load(f)
encodingDictionary["PAD"] = 120  # Add the new padding token to our dictionaries
decodingDictionary[120] = "PAD"
# Now let's find what is the max sequence length for the harmonization and what it is for the soprano
maxSop = -1
maxHar = -1
for i in range(len(encodedSoprano)):
    if len(encodedSoprano[i]) > maxSop:
        maxSop = len(encodedSoprano[i])
    if len(encodedHarmonization[i]) > maxHar:
        maxHar = len(encodedHarmonization[i])
print(f"Soprano: {maxSop}, Harmonization: {maxHar}")
# Now let's add padding tokens so every sequence has length of maxHar = 162 (maxSop = 98)
# Note that the output sequences will be of length 163 because before we give the data to the decoder the <sos> and
# <eos> tokens will be removed.
# Additionally let's create tuples of input-target padded pairs and keep them in a list
maxSeqLength = max(maxSop, maxHar)
pairs = []
for i in range(len(encodedSoprano)):
    if len(encodedSoprano[i]) < maxSeqLength:
        nTimes = maxSeqLength - len(encodedSoprano[i])
        encodedSoprano[i].extend(repeat(120, nTimes))
    if len(encodedHarmonization[i]) < maxSeqLength:
        nTimes = maxSeqLength - len(encodedHarmonization[i])
        encodedHarmonization[i].extend(repeat(120, nTimes + 1))
    pairs.append((encodedSoprano[i], encodedHarmonization[i]))
# To test our network architecture we are going to create a small dataset (20% of the dataset) and run training
# But first of all let's save our entire dataset and our updated dictionaries
with open('/filepath/BigDataset.pkl', 'wb') as f:
    pickle.dump(pairs, f)
with open('/filepath/encodingDictionary.pkl', 'wb') as f:
    pickle.dump(encodingDictionary, f)
with open('/filepath/decodingDictionary.pkl', 'wb') as f:
    pickle.dump(decodingDictionary, f)
# Now let's shuffle the list and create our small dataset
shuffle(pairs)
# Now let's keep 20% for our small dataset
nSmall = int(len(pairs) * 0.2)  # Size of our small dataset
nRest = len(pairs) - nSmall  # Size of the remaining dataset
# Now from our small dataset we want to create a training dataset (90%) and a validation dataset (10%)
nTrain = int(nSmall * 0.9)
nVal = nSmall - nTrain
# Now let's split our dataset accordingly
n = 0
smallTrainDataset = []
smallValDataset = []
remainingDataset = []
for i in range(len(pairs)):
    if i < nTrain:
        smallTrainDataset.append(pairs[i])
    elif i < nSmall:
        smallValDataset.append(pairs[i])
    else:
        remainingDataset.append(pairs[i])
# Let's save our datasets
with open('/filepath/SmallTrainDataset.pkl', 'wb') as f:
    pickle.dump(smallTrainDataset, f)
with open('/filepath/SmallValDataset.pkl', 'wb') as f:
    pickle.dump(smallValDataset, f)
with open('/filepath/RemainingDataset.pkl', 'wb') as f:
    pickle.dump(remainingDataset, f)
# Just checking the sizes
print(f"Small training dataset size is: {len(smallTrainDataset)}")
print(f"Small validation dataset size is: {len(smallValDataset)}")
print(f"Remaining dataset size is : {len(remainingDataset)}")
