import abc
from typing import Union


class Field(abc.ABC):
    @property
    @abc.abstractmethod
    def value(self):
        raise NotImplementedError

    @value.setter
    @abc.abstractmethod
    def value(self, value):
        raise NotImplementedError

    @abc.abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def __bytes__(self) -> bytes:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def from_bytes(cls, data: bytes):
        raise NotImplementedError

    @abc.abstractmethod
    def validate(self, value):
        raise NotImplementedError

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return not self.value == other.value


class VLA:
    """
    Used for fields that have variable length, their length parameter is stored in another field.
    """
    def __init__(self, scalar: Union[Field, str]):
        """
        The goal, in the end, is to have the name of the scalar that contains the length.
        If not given in the __init__, StructMeta will fill the name itself.
        :param scalar: The scalar (from the stuct or its' name)
        """
        self.length = 0
        if isinstance(scalar, str):
            self.length_field_name = scalar
        else:
            self.length_field_name = None
            self.length_field_obj = scalar

    def __len__(self):
        return self.length
