import inspect
from contextlib import suppress

from .base import Struct
from .fields import Field

try:
    from typing import Protocol, runtime_checkable
except ImportError:
    from typing_extensions import Protocol, runtime_checkable


@runtime_checkable
class HeaderWithLen(Protocol):
    body_len: Field


@runtime_checkable
class HeaderWithOpcode(Protocol):
    body_opcode: Field


@runtime_checkable
class Opcoded(Protocol):
    opcode: int


class Message:
    def __init__(self, *layers, update_metadata: bool = True):

        self.layers = []
        for layer in layers:
            # Messages are flat, they will not contain other messages, so just add its' layers
            if isinstance(layer, Message):
                self.layers.extend(layer.layers)
                continue
            # Check if we're appending bytes
            elif isinstance(layer, bytes):
                # If the last layer is already bytes, change it instead
                if isinstance(self.layers[-1], bytes):
                    self.layers[-1] += layer
                    continue
            elif not isinstance(layer, Struct):
                raise TypeError('Invalid type given: {}, expected: Message, Struct, or bytes'.format(type(layer), ))

            self.layers.append(layer)

        if update_metadata:
            self._update_metas()

    def serialize(self):
        return b''.join(bytes(layer) for layer in self.layers)

    def _update_metas(self):
        """
        Iterate from the penultimate (1 before the last) layer to the first layer,
        and update struct data according to protocols
        """
        for layer, child in zip(self.layers[-2::-1], self.layers[::-1]):
            if isinstance(layer, HeaderWithLen):
                layer.body_len = len(child)
            if isinstance(layer, HeaderWithOpcode) and isinstance(child, Opcoded):
                layer.body_opcode = child.opcode

    def __eq__(self, other):
        if isinstance(other, Message):
            return all(l1 == l2 for l1, l2 in zip(self, other))
        return False

    def __bytes__(self):
        return self.serialize()

    def __str__(self):
        # __str__ every layer and insert a line between each layer
        return '\n{}\n'.format('-' * 10).join(str(layer) for layer in self.layers)

    def __add__(self, other):
        return Message(self, other)

    def __truediv__(self, other):
        return Message(self, other)

    def __iter__(self):
        return iter(self.layers)

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.layers[item]

        if inspect.isclass(item):
            occurrence_to_find = 0
        elif isinstance(item, tuple):
            item, occurrence_to_find = item
        else:
            raise TypeError

        occurrences = 0
        for layer in self.layers:
            if isinstance(layer, item):
                if occurrence_to_find == occurrences:
                    return layer
                else:
                    occurrences += 1

        if occurrences == 0:
            raise KeyError(f"Couldn't find any layer that's an instance of {item}")
        else:
            raise KeyError(f"Found only {occurrences + 1} occurrences of {item}, "
                           f"but expected to find at least {occurrence_to_find + 1}")

    def __contains__(self, item):
        with suppress(KeyError):
            return bool(self[item])

        return item in self.layers

    def __len__(self):
        return sum(map(len, self.layers))
