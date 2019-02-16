import pytest
import numpy as np
from keras.layers import Input

from main import *


class TestSimpleReNet(object):

    @pytest.fixture
    def sut(self):
        self.w_p = 2
        self.h_p = 2
        model = SimpleReNet([[self.w_p, self.h_p]], 1, 1, 2)
        model.compile(loss='categorical_crossentropy', optimizer='adam',
                metrics=['categorical_accuracy'])
        return model


    @pytest.fixture
    def simple_data_x(self):
        self.num_samples = 60
        self.img_width = 10
        self.img_height = 10
        self.number_of_channels = 1
        x = np.zeros((self.num_samples, self.img_width, self.img_height,
                self.number_of_channels), dtype=np.uint8)
        x[30:] = np.ones((10, 10, 1))
        return x


    @pytest.fixture
    def simple_data_y(self):
        self.num_samples = 60
        y = np.zeros((self.num_samples), dtype=np.uint8)
        y[30:] = 1
        return y


    def test_model_output_for_2_classes_shape_is_num_samples_x_2(self, sut, simple_data_x,
            simple_data_y):
        sut.fit(simple_data_x, simple_data_y, epochs=1, shuffle=False)
        result = sut.predict(simple_data_x)
        assert result.shape == (self.num_samples, 2)


    def test_get_columns_outputs_returns_columns_with_valid_shape(self, sut):
        arg = Input((10, 10, 1))

        for result in sut.get_columns(arg):
            result_shape = list(map(lambda x: int(x), result.shape[1:]))
            assert result_shape == [10, 2, 1]


    def test_get_columns_generates_5_columns(self, sut):
        arg = Input((10, 10, 1))

        number_of_col = 0
        for result in sut.get_columns(arg):
            number_of_col += 1

        assert number_of_col == 5 # Y / h_p


    def test_get_columns_not_even_number_of_columns_for_patches_exception_raised(self, sut):
        arg = Input((10, 11, 1))

        with pytest.raises(ValueError) as err:
            for result in sut.get_columns(arg):
                assert result is None

        assert "invalid patches size" in str(err.value)


    def test_get_vert_patches_returns_patches_with_valid_shape(self, sut, simple_data_x):
        arg = Input((10, 2, 1))
        sut.J = self.img_height // self.h_p

        result = sut.get_vert_patches(arg)
        result_shape = list(map(lambda x: int(x), result.shape[1:]))
        assert result_shape == [self.h_p*self.w_p*self.number_of_channels, sut.J]
