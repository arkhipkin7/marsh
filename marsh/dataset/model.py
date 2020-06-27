import time
import pickle
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

from tensorflow import keras
from tensorflow.keras import Sequential
from sklearn.model_selection import train_test_split
from tensorflow.keras.layers import (
    Dense,
    Dropout,
    Activation,
    Conv2D,
    MaxPooling2D,
    Input,
    BatchNormalization,
    Add,
    GlobalAveragePooling2D,
)

CATEGORIES = ['building', 'car', 'cat',
              'clothes', 'dog', 'drugs',
              'human', 'plants', 'porno',
              'sea', 'text_msg', 'weapons'
              ]
EPOCHS = 60
STEPS_PER_EPOCH = 95

# Load the DataSet which is ndarray
X_temp = open('x_data_np', 'rb')
x_data_np = pickle.load(X_temp)

# Load the Notes which is ndarray
Y_temp = open('y_data_np', 'rb')
y_data_np = pickle.load(Y_temp)

# Separation of data into Training(70%) and Test(30%)
X_train, X_test, y_train, y_test = train_test_split(x_data_np, y_data_np,
                                                    test_size=0.3, random_state=101)


# Random 25 of images
plt.figure(figsize=(10, 10))
for i in range(25):
    plt.subplot(5, 5, i + 1)
    plt.xticks([])
    plt.yticks([])
    plt.grid(False)
    plt.imshow(X_train[i], cmap=plt.cm.binary)
    plt.xlabel(CATEGORIES[y_train[i]])

plt.show()


# Create model
def res_net_block(input_data, filepath, conv_size):
    x = Conv2D(filepath, conv_size, activation='relu', padding='same')(input_data)
    x = BatchNormalization()(x)
    x = Conv2D(filepath, conv_size, activation=None, padding='same')(x)
    x = BatchNormalization()(x)
    x = Add()([x, input_data])
    x = Activation('relu')(x)
    return x


def non_res_block(input_data, filepath, conv_size):
    x = Conv2D(filepath, conv_size, activation='relu', padding='same')(input_data)
    x = BatchNormalization()(x)
    x = Conv2D(filepath, conv_size, activation='relu', padding='same')(x)
    x = BatchNormalization()(x)
    return x


inputs = Input(shape=(77, 77, 3))
x = Conv2D(32, 3, activation='relu')(inputs)
x = Conv2D(64, 3, activation='relu')(x)
x = MaxPooling2D(3)(x)

num_res_net_blocks = 12
for i in range(num_res_net_blocks):
    x = res_net_block(x, 64, 3)

x = Conv2D(64, 3, activation='relu')(x)
x = GlobalAveragePooling2D()(x)
x = Dense(256, activation='relu')(x)
x = Dropout(0.5)(x)
outputs = Dense(12, activation='softmax')(x)

res_net_model = keras.Model(inputs, outputs)

res_net_model.compile(optimizer=keras.optimizers.Adam(),
                      loss='sparse_categorical_crossentropy',
                      metrics=['acc'])

start = time.time()

res_net_model.fit(X_train, y_train, epochs=EPOCHS, steps_per_epoch=STEPS_PER_EPOCH)

print(f'Time of learning: {time.time() - start}')

test_loss, test_acc = res_net_model.evaluate(X_test, y_test, batch_size=128)
print('Test accuracy: ', test_acc)

res_net_model.save('77x77cnn.model')

model = tf.keras.models.load_model('77x77cnn.model')

predictions = model.predict(X_test)

print(predictions.shape)

def plot_image(i, predictions_array, true_label, img):
    predictions_array, true_label, img = predictions_array[i], true_label[i], img[i]
    plt.grid(False)
    plt.xticks([])
    plt.yticks([])

    plt.imshow(img, cmap=plt.cm.binary)
    
    predicted_label = np.argmax(predictions_array)

    if predicted_label == true_label:
        color = 'blue'
    else:
        color = 'red'

    plt.xlabel(f' {CATEGORIES[predicted_label]} {100 * np.max(predictions_array)} - {CATEGORIES[true_label]}' , color=color)

def plot_value_array(i, predictions_array, true_label):
    predictions_array, true_label = predictions_array[i], true_label[i]
    plt.grid(False)
    plt.xticks([])
    plt.yticks([])
    thisplot = plt.bar(range(12), predictions_array, color='#777777')
    plt.ylim([0, 1])
    predictions_label = np.argmax(predictions_array)

    thisplot[predictions_label].set_color('red')
    thisplot[true_label].set_color('blue')

i = 0
num_rows = 5
num_cols = 3
num_images = num_rows * num_cols

plt.figure(figsize=(2*2*num_cols, 2*num_rows))
for i in range(num_images):
    plt.subplot(num_rows, 2*num_cols, 2*i+1)
    plot_image(i, predictions, y_test, X_test)
    plt.subplot(num_rows, 2*num_cols, 2*i+2)
    plot_value_array(i, predictions, y_test)
plt.show()
