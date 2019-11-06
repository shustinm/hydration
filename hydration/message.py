from typing import Iterable, Callable
from itertools import tee
import struct


class Message:
    def __init__(self, layers: Iterable):
        self.layers = list(layers)

        self._update_metas()

        for layer in layers:
            self._add_name_of_layer(layer)

    def serialize(self):
        try:
            return b''.join(bytes(layer) for layer in self.layers)
        except struct.error as e:
            raise ValueError(str(e))

    def append(self, layer):
        self.layers.append(layer)
        self._update_metas()
        if hasattr(layer, 'name'):
            self._add_name_of_layer(layer)

    # noinspection PyProtectedMember
    def _update_metas(self):
        """
        Iterate from the penultimate (1 before the last) layer to the first layer, connect metas
        :return:
        """
        for index, layer in enumerate(self.layers[-2::-1]):
            child_layer = self.layers[index + 1]
            for k, v in child_layer._meta_up.items():
                down_value = v(child_layer) if callable(v) else v
                layer._meta_down[k] = down_value
                setattr(layer, )

    def _add_name_of_layer(self, layer):
        if getattr(layer, 'name'):
            if hasattr(self, layer.name):
                raise NameError('Message {} already has a layer named {}'.format(self, layer.name))
            setattr(self, layer.name, layer)

    def __eq__(self, other):
        if isinstance(other, Message):
            return all(l1 == l2 for l1, l2 in zip(self.layers, other.layers))
        return False

    def __bytes__(self):
        return self.serialize()

    def __str__(self):
        # __str__ every layer and insert a line between each layer
        return '\n{}\n'.format('-' * 10).join(str(layer) for layer in self.layers)

    def __truediv__(self, other):
        self.append(other)
        return self

    def __getitem__(self, item):
        return self.layers[item]

    def __len__(self):
        return sum(map(len, self.layers))
