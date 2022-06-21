# This program uses the trained OptimusBach model to harmonise a melody.
# Please change the filepaths to match where you have saved the encodingDictionary.pkl, the meoldy.pkl and SmallSingleLayerModel.h5
# and where you want the generated sequence to be saved.
# For more information see the ReadMe on this folder

from transformer_model import *
import pickle
import numpy as np

embed_dim = 64
latent_dim = 256
num_heads = 8
vocab_size = 121
sequence_length = 162
batch_size = 64

encoder_inputs = keras.Input(shape=(None,), dtype="int64", name="encoder_inputs")
x = PositionalEmbedding(sequence_length, vocab_size, embed_dim)(encoder_inputs)
encoder_outputs = TransformerEncoder(embed_dim, latent_dim, num_heads)(x)
encoder = keras.Model(encoder_inputs, encoder_outputs)
# Let's build the decoder
decoder_inputs = keras.Input(shape=(None,), dtype="int64", name="decoder_inputs")
encoded_seq_inputs = keras.Input(shape=(None, embed_dim), name="decoder_state_inputs")
x = PositionalEmbedding(sequence_length, vocab_size, embed_dim)(decoder_inputs)
x = TransformerDecoder(embed_dim, latent_dim, num_heads)(x, encoded_seq_inputs)
x = layers.Dropout(0.2)(x)
decoder_outputs = layers.Dense(vocab_size, activation='softmax')(x)
decoder = keras.Model([decoder_inputs, encoded_seq_inputs], decoder_outputs)

decoder_outputs = decoder([decoder_inputs, encoder_outputs])
# Now bringing it all together
transformer = keras.Model(
    [encoder_inputs, decoder_inputs], decoder_outputs, name="transformer")
# Let's load the weights of the trained model
transformer.load_weights("filepath/SmallSingleLayerModel.h5")
transformer.summary()
# Let's compile the model
transformer.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
# Let's load a melody from the big dataset (that was not used in training to test it)
with open("/filepath/melody.pkl", "rb") as f:
    dataset = pickle.load(f)
with open("/filepath/encodingDictionary.pkl", "rb") as f:
    encodingDictionary = pickle.load(f)
for i in range(len(dataset)):
    dataset[i] = encodingDictionary[dataset[i]]
paddingMelody = [120] * (sequence_length - len(dataset))
dataset.extend(paddingMelody)
melody = [dataset]
encoder_input = tf.convert_to_tensor(melody)
decoded_sequence = [sequence_length * [120]]
decoded_sequence[0][0] = 0

# let's use the start token to generate the next tokens
max_seq_length = sequence_length
for i in range(max_seq_length):
    decoder_input = tf.convert_to_tensor(decoded_sequence)
    predictions = transformer([encoder_input, decoder_input])
    sampled_token = np.argmax(predictions[0, i, :])
    if i+1 < max_seq_length:
        decoded_sequence[0][i+1] = sampled_token

    if sampled_token == 1:
        break
print("Done and done!")
with open("/filepath/generated_music.pkl", "wb") as f:
    pickle.dump([(melody[0], decoded_sequence[0])], f)
print("yo ho")








