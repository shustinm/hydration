from abc import abstractmethod
from .base import Struct
from contextlib import suppress
import struct


class MessageStruct(Struct):
    """
    Structs that want to integrate with messages must implement these properties
    """

    @property
    @abstractmethod
    def id(self):
        """
        :return: A numerical ID that represents this struct (opcode).
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self):
        """
        :return: A name of this struct, a message can't have two structs with the same name.
        """
        raise NotImplementedError


class Header:

    @property
    @abstractmethod
    def len_of_child(self):
        raise NotImplementedError

    @len_of_child.setter
    @abstractmethod
    def len_of_child(self, value):
        raise NotImplementedError

    def append(self, body, checks=True):
        return Message([self, body], checks)

    def __truediv__(self, other):
        return self.append(other)

    def __floordiv__(self, other):
        return self.append(other, checks=False)

    @property
    @abstractmethod
    def child_id(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError


class Message:
    def __init__(self, layers, checks=True):
        for layer in layers[:-1]:
            self._assert_is_header(layer)

        self.layers = layers

        if checks:
            self._update_struct_lengths()
            self._update_opcode()

        for layer in layers:
            with suppress(AttributeError):
                if hasattr(self, layer.name):
                    raise NameError('Message {} already has a layer named {}'.format(self, layer.name))
                setattr(self, layer.name, layer)

    def serialize(self):
        try:
            return b''.join(bytes(layer) for layer in self.layers)
        except struct.error as e:
            raise ValueError(str(e))

    def append(self, layer, checks=True):
        if isinstance(layer, MessageStruct):
            self._assert_is_header(self.layers[-1])

        self.layers.append(layer)

        if checks:
            self._update_struct_lengths()
            self._update_opcode()

    def _update_struct_lengths(self):
        """
        Iterate from the penultimate (1 before the last) layer to the first layer,
        setting its
        :return:
        """
        for i in range(len(self.layers) - 2, -1, -1):
            child = self.layers[i + 1]

            depth_len = getattr(child, 'len_of_child', 0)

            try:
                self.layers[i].body_len = len(child) + depth_len
            except AttributeError:
                pass

    def _update_opcode(self):
        """
        Update the penultimate (1 before the last) layer's opcode to match the last layer
        :return:
        """
        with suppress(NotImplementedError, AttributeError):
            self.layers[-2].child_id = self.layers[-1].id

    @staticmethod
    def _assert_is_header(layer):
        if not isinstance(layer, Header):
            raise ValueError('The last layer is not of type {}. You cannot append more layers'.format(Header))

    def __eq__(self, other):
        if isinstance(other, Message):
            return all(l1 == l2 for l1, l2 in zip(self.layers, other.layers))
        return False

    def __bytes__(self):
        return self.serialize()

    def __str__(self):
        # __str__ every layer and insert a line between each layer
        return '\n{}\n'.format('-' * 10).join(repr(layer) for layer in self.layers)

    def __truediv__(self, other):
        self.append(other)
        return self

    def __floordiv__(self, other):
        self.append(other, checks=False)
        return self

    def __getitem__(self, item):
        return self.layers[item]

    def __len__(self):
        return sum(map(len, self.layers))
