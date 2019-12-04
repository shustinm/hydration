from .base import Struct, StructMeta
from .fields import Field
from typing import Optional, Union, Iterable

try:
    from typing import Protocol, runtime_checkable
except ImportError:
    from typing_extensions import Protocol, runtime_checkable


@runtime_checkable
class NamedStruct(Protocol):
    call_name: str


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
    def __init__(self, layers: Optional[Iterable[Union[Struct, bytes]]] = ()):
        self.unparsed_data = b''

        if not isinstance(layers, Iterable):
            layers_to_append = (layers,)
        else:
            layers_to_append = layers

        self.layers = []
        for layer in layers_to_append:
            if not isinstance(layer, (Struct, Message, bytes)):
                raise TypeError('Invalid type given: {}, expected: Struct or bytes'.format(type(layer), ))
            self.layers.append(layer)
            self._add_name_of_layer(layer)

        self._update_metas()

    def serialize(self):
        return b''.join(bytes(layer) for layer in self.layers)

    # noinspection PyProtectedMember
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

    def _add_name_of_layer(self, layer):
        if isinstance(layer, NamedStruct):
            if hasattr(self, layer.call_name):
                raise NameError('Message {} already has a layer named {}'.format(self, layer.call_name))
            setattr(self, layer.call_name, layer)

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
        return Message((self, other))

    def __iter__(self):
        return iter(self.layers)

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.layers[item]
        elif isinstance(item, type) and issubclass(item, Struct):
            for layer in self.layers:
                if isinstance(layer, item):
                    return layer
        elif isinstance(item, str):
            for layer in filter(lambda l: isinstance(l, NamedStruct), self.layers):
                if layer.call_name == item:
                    return layer
        raise KeyError

    def __contains__(self, item):
        return bool(self[item])

    def __len__(self):
        return sum(map(len, self.layers))
