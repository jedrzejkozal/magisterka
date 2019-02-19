from ReNetTest import *
from SimpleReNet import *


class TestSimpleReNet(ReNetTest):

    @classmethod
    def setup(cls):
        cls.num_samples = 60
        cls.img_width = 10
        cls.img_height = 10
        cls.number_of_channels = 1

    @pytest.fixture
    def sut(self):
        self.__class__.setup()
        self.w_p = 2
        self.h_p = 2
        self.I = self.img_width // self.w_p
        self.J = self.img_height // self.h_p
        self.reNet_hidden_size = 1
        fully_conn_hidden_size = 1
        num_classes = 2
        model = SimpleReNet([[self.w_p, self.h_p]],
                self.reNet_hidden_size, fully_conn_hidden_size, num_classes)
        model.compile(loss='categorical_crossentropy', optimizer='adam',
                metrics=['categorical_accuracy'])
        return model
