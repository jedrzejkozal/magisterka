import os
import numpy as np

from keras.utils import to_categorical
from keras.datasets import cifar10
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import EarlyStopping, TensorBoard, LambdaCallback
from keras.optimizers import Adam
from shutil import rmtree
from os import makedirs

from Utils.SaveResults import *
from Utils.TensorBoardSaveSplits import *
from Utils.InputNormalisation import *
from Models.Cifar10Reproduction.Cifar10Model import *
#from Utils.ImageGeneratorWithMasking import *


#image parameters:
num_classes = 10
img_rows, img_cols = 32, 32
(x_train, y_train), (x_test, y_test) = cifar10.load_data()

x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 3)
x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 3)

x_train = x_train.astype('float32')
x_test = x_test.astype('float32')
x_train /= 255
x_test /= 255

x_train = x_train[:40000]
y_train = y_train[:40000]


# ZCA
x_train = x_train.reshape(x_train.shape[0], img_rows*img_cols*3)
x_test = x_test.reshape(x_test.shape[0], img_rows * img_cols*3)

"""
sigma = np.cov(np.transpose(x_train))
evalues, evectors = np.linalg.eigh(sigma)
n_samples = x_train.shape[0]
W = evectors @ np.diag(evalues**(-1/2)) @ evectors.T * (n_samples-1)

# please note:
# in https://www.cs.toronto.edu/~kriz/learning-features-2009-TR.pdf matrix X is defined as (d, n)
# so with this notation result ZCA matrix with shape (n, d) is calculated as Y^T = X^T W^T
# so using notation with X as (n, d) Y = X W^T with W calculated for X defined as (d, n)
def ZCA(X):
    return X @ np.transpose(W)

x_train = ZCA(x_train)
x_test = ZCA(x_test)
"""

x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 3)
x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 3)

x_train = zero_mean(x_train)
x_test = zero_mean(x_test)
x_train = unit_var(x_train)
x_test = unit_var(x_test)

print("x_train: ", x_train.shape)
print("y_train: ", y_train.shape)
print("x_test: ", x_test.shape)
print("y_test: ", y_test.shape)


# convert class vectors to binary class matrices
y_train = to_categorical(y_train, num_classes)
y_test = to_categorical(y_test, num_classes)

x_train_single_ex = x_train[0:1]
y_train_single_ex = y_train[0:1]

#just for testing
#x_train = x_train[:100]
#y_train = y_train[:100]
#x_test = x_test[:100]
#y_test = y_test[:100]

log_dir = 'TensorBoard_cifar10_logs'
rmtree(log_dir, ignore_errors=True)
makedirs(log_dir)

shift = 3
datagen = ImageDataGenerator(width_shift_range=shift, height_shift_range=shift,
                horizontal_flip=True, vertical_flip=True)#, zca_whitening=True)
#datagen = ImageDataGeneratorWithMasking(width_shift_range=shift, height_shift_range=shift, horizontal_flip=True, vertical_flip=True)
datagen.fit(x_train)


model = get_cifar10_model()
model.compile(loss='categorical_crossentropy',
        optimizer=Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=10.0**-8.0),
        metrics=['categorical_accuracy'])

#just for model to figure out what is the shape of input tensors
#workaround for how keras fit_generator works
model.fit(x_train_single_ex, y_train_single_ex, epochs=1)
model.summary()

batch_size = 30
history = model.fit_generator(datagen.flow(x_train, y_train, batch_size=batch_size),
                epochs=10,
                steps_per_epoch=np.ceil(x_train.shape[0] / batch_size),
                validation_data=(x_test, y_test),
                callbacks=[EarlyStopping(monitor='val_loss', patience=20, verbose=1),
                        #LambdaCallback(on_epoch_end=lambda x, y: model.layers[0].generate_mask()),
                        TensorBoardSaveSplits(log_dir=log_dir,
                                #splits_size=[28,28],
                                #splits_path='sprite.png',
                                batch_size=batch_size,
                                histogram_freq=1,
                                write_images=True,
                                write_grads=False,
                                #embeddings_freq=1,
                                #embeddings_layer_names=['features'],
                                #embeddings_metadata='metadata.tsv',
                                #embeddings_data=x_test
                                )
                ]
            )
