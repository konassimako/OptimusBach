from transformer_model import *
from tensorflow.keras.callbacks import EarlyStopping
import pickle
import matplotlib.pyplot as plt

# Let's define our hyperparameters
embed_dim = 64
latent_dim = 256
num_heads = 8
vocab_size = 121
sequence_length = 162
batch_size = 64
epochs = 30


# This function takes the input and target pairs as input and returns them in the form:
# ({"encoder inputs": encoder_input_data, "decoder inputs": decoder_input_data}, decoder_target_data)
# Decoder_input_data  has no <eos> and decoder_target_data has no <sos>
def formatDataset(sop, har):
    return (
        {
            "encoder_inputs": sop,
            "decoder_inputs": har[:, :-1],
        },
        tf.one_hot(har[:, 1:], depth=vocab_size, dtype="int64"),
    )


# This functions takes the list of data pairs and returns a tensorflow dataset
def makeDataset(pairs):
    sop, har = zip(*pairs)
    sop = list(sop)
    har = list(har)
    dataset = tf.data.Dataset.from_tensor_slices((sop, har))
    dataset = dataset.batch(batch_size)
    dataset = dataset.map(formatDataset)
    return dataset


# Let's load our data
with open('/filePath/SmallTrainDataset.pkl', 'rb') as f:
    trainPairs = pickle.load(f)
with open('/filepath/SmallValDataset.pkl', 'rb') as f:
    valPairs = pickle.load(f)
# Now let's make them tensorflow dataframes
trainDataset = makeDataset(trainPairs)
valDataset = makeDataset(valPairs)
# Let's check if  the dataset dimensions are ok
for inputs, targets in trainDataset.take(1):
    print(f'inputs["encoder_inputs"].shape: {inputs["encoder_inputs"].shape}')
    print(f'inputs["decoder_inputs"].shape: {inputs["decoder_inputs"].shape}')
    print(f"targets.shape: {targets.shape}")
# Now let's build the encoder model
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
    [encoder_inputs, decoder_inputs], decoder_outputs, name="transformer"
)

# Now let's train the model
transformer.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
monitor = EarlyStopping(monitor='val_loss', min_delta=1e-3, patience=5,
                        verbose=1, mode='auto', restore_best_weights=True)
history = transformer.fit(trainDataset, epochs=epochs, validation_data=valDataset,
                          callbacks=[monitor])
transformer.save_weights("/filepath/SmallSingleLayerModel.h5")
# Let's plot the training and validation loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
