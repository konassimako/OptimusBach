# OptimusBach

## OptimusBach is an Artificial Intelligence model capable of harmonising a given melody into a four-part vocal music piece in the style of J. S. Bachs's chorales.

In this project, a sequence-to-sequence Transformer model was trained on a dataset build from Bach's chorales. The dataset was constructed using the music21 Python library and the Transformer model was build using tensorflow's Keras API. The resulting trained model is capable of producing harmonisations for any melody that does not exceed 8 quarter notes in length.

