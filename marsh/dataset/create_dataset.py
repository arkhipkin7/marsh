import os
import cv2
import sys
import random
import pickle
import numpy as np
import pandas as pd
import tensorflow as tf


# Declare PATH for Train and Test
DATA_DIR = 'data'
CATEGORIES = ['building', 'car', 'cat',
              'clothes', 'dog', 'drugs',
              'human', 'plants', 'porno',
              'sea', 'text_msg', 'weapons'
              ]
IMAGE_SIZE = 77


def create_training_data():
    training_date = []
    for categories in CATEGORIES:
        path = os.path.join(DATA_DIR, categories)
        class_num = CATEGORIES.index(categories)
        for img in os.listdir(path):
            try:
                img_array = cv2.imread(os.path.join(path, img), cv2.IMREAD_COLOR)
                new_array = cv2.resize(img_array, (IMAGE_SIZE, IMAGE_SIZE))
                training_date.append([new_array, class_num])
            except Exception as e:
                pass
    return training_date

# convert list to np.ndarray
data = np.asarray(create_training_data())

x_data = []
y_data = []

for x in data:
    x_data.append(x[0])
    y_data.append(x[1])

# Normalize image
x_data_np = np.asarray(x_data) / 255.0
y_data_np = np.asarray(y_data)

# # Store the data in pickle file
pickle_out = open('x_data_np', 'wb')
pickle.dump(x_data_np, pickle_out)
pickle_out.close()

pickle_out = open('y_data_np', 'wb')
pickle.dump(y_data_np, pickle_out)
pickle_out.close()
