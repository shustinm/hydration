import abc
from typing import Union

from .validators import Validator


class Field(abc.ABC):

    @property
    @abc.abstractmethod
    def validator(self) -> Validator:
        raise NotImplementedError

    @validator.setter
    @abc.abstractmethod
    def validator(self, value):
        raise NotImplementedError

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

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return not self.value == other.value


class VLA(Field):
    """
    Used for fields that have variable length, their length parameter is stored in another field.
    """

    @property
    def validator(self):
        return None

    def __init__(self, field: Union[Field, str]):
        """
        The goal, in the end, is to have the name of the scalar that contains the length.
        If not given in the __init__, StructMeta will fill the name itself.
        :param field: The field (from the stuct or its' name)
        """
        self.length = 0
        if isinstance(field, str):
            self.length_field_name = field
        else:
            self.length_field_name = None
            self.length_field_obj = field

    def __len__(self):
        return self.length

    @property
    def value(self):
        raise NotImplementedError

    @value.setter
    def value(self, value):
        raise NotImplementedError

    def __repr__(self) -> str:
        raise NotImplementedError

    def __str__(self) -> str:
        raise NotImplementedError

    def __bytes__(self) -> bytes:
        raise NotImplementedError

    def from_bytes(self, data: bytes):
        raise NotImplementedError
