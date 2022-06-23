# OptimusBach

### OptimusBach is an Artificial Intelligence model capable of harmonising a given melody into a four-part vocal music piece in the style of J. S. Bach's chorales.

In this project, a sequence-to-sequence Transformer model was trained on a dataset build from Bach's chorales. The dataset was constructed using the music21 Python library and the Transformer model was build using tensorflow's Keras API. The resulting trained model is capable of producing harmonisations for any melody that does not exceed 8 quarter notes in length.

## Project Structure

The image below gives a visual represenation of how all the different files in this project work together.

![alt text](https://raw.githubusercontent.com/konassimako/OptimusBach/main/program_visual_structure.png "Visual representation of the project")

## Using the trained model

You can use the trained model to produce a harmonisation for your melody. Everything you need to do that is contained in the [trained model](https://github.com/konassimako/OptimusBach/tree/main/trained%20model) folder.

### Prerequisites 

* You need to install a music notation software to be able to display the generated music ([Musescore](https://musescore.org) is free and works great).
* You need to install tensorflow with Keras.
* You need to install the music21 and numpy Python libraries.

### Step-by-step:

1. Save the [model weights](https://github.com/konassimako/OptimusBach/blob/main/trained%20model/trained%20model%20weights/SmallSingleLayerModel.h5), input melody (you can find some example melodies [here](https://github.com/konassimako/OptimusBach/tree/main/trained%20model/sample%20melodies)) and the encoding and decoding [dictionaries](https://github.com/konassimako/OptimusBach/tree/main/trained%20model/dictionaries) in the same folder that you are going to run the [MusicGeneration.py](https://github.com/konassimako/OptimusBach/blob/main/trained%20model/MusicGeneration.py) file.
2. In the MusicGeneration.py file change the filepaths to where you have saved the above files and where you want your generated sequence to be saved.
3. In the [GeneratedSequenceDecoding.py](https://github.com/konassimako/OptimusBach/blob/main/trained%20model/GeneratedSequenceDecoding.py) file change the filepath to where you saved the generated sequence and the decoding dictionary.
4. Make sure that the [CreateSheetMusic.py](https://github.com/konassimako/OptimusBach/blob/main/trained%20model/CreateSheetMusic.py) file is saved in the same folder that you are going to run the [GeneratedSequenceDecoding.py](https://github.com/konassimako/OptimusBach/blob/main/trained%20model/GeneratedSequenceDecoding.py) file.
5. Run the [GeneratedSequenceDecoding.py](https://github.com/konassimako/OptimusBach/blob/main/trained%20model/GeneratedSequenceDecoding.py) file to view the generated music in your music notation software.
