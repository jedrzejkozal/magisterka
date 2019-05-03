import os
import numpy as np

from keras.utils import to_categorical
from keras.datasets import cifar10
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import EarlyStopping, TensorBoard, LambdaCallback
from keras.optimizers import Adam

from Models.SVHNReproduction.SVHNModel import *
from Utils.InputNormalization import *
from Utils.LoadSVHN import *
from Utils.Masking import *


script_path = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(script_path ,'SVHNdataset/')
x_train, y_train, x_test, y_test = load_SVHN(dataset_path)

img_rows, img_cols = 32, 32
num_channels = 3

print("x_train: ", x_train.shape)
print("y_train: ", y_train.shape)
print("x_test: ", x_test.shape)
print("y_test: ", y_test.shape)

print("y_train bincount: ", np.bincount(np.squeeze(y_train)))
print("y_test bincount: ", np.bincount(np.squeeze(y_test)))

x_train = x_train.astype('float32')
x_test = x_test.astype('float32')
x_train /= 255
x_test /= 255

x_train = normalize(x_train)
x_test = normalize(x_test)

y_train = to_categorical(y_train)
y_test = to_categorical(y_test)

print("x_train: ", x_train.shape)
print("y_train: ", y_train.shape)
print("x_test: ", x_test.shape)
print("y_test: ", y_test.shape)


datagen = ImageDataGenerator(width_shift_range=[-2.0, 0.0, 2.0])
datagen.fit(x_train)


model = get_svhn_model()
model.compile(loss='categorical_crossentropy',
        optimizer=Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=10.0**-8.0),
        metrics=['categorical_accuracy'])

#just for model to figure out what is the shape of input tensors
#workaround for how keras fit_generator works
x_train_single_ex = x_train[0:1]
y_train_single_ex = y_train[0:1]
model.fit(x_train_single_ex, y_train_single_ex, epochs=1)
model.summary()

batch_size = 32
num_epochs = 50
masking = Masking(img_rows, img_cols, num_channels)
for i in range(num_epochs):
    print("epoch {}/{}".format(i+1, num_epochs))
    masked_x_train = masking.mask_input(x_train)
    model.fit_generator(datagen.flow(masked_x_train, y_train,
            batch_size=batch_size),
            epochs=1,
            steps_per_epoch=np.ceil(x_train.shape[0] / batch_size),
            validation_data=(x_test, y_test),
            callbacks=[EarlyStopping(monitor='val_loss', patience=20, verbose=1)
                ]
        )
