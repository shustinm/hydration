from abc import ABC, abstractmethod
from typing import Any, Callable


class Validator(ABC):
    @abstractmethod
    def validate(self, value: Any) -> None:
        """
        Raises ValueError if the value is invalid.
        :param value:                       The value to check
        :return:                            None
        :raises: :class:`ValueError`:       Value is invalid
        """
        pass


class RangeValidator(Validator):
    def __init__(self, range_obj: range):
        """
        :param range_obj:   A range object (returned by calling range())
        """
        self.range = range_obj

    def validate(self, value: Any) -> None:
        if value not in self.range:
            raise ValueError('Given value {} is not in {}'.format(value, self.range))


class ExactValueValidator(Validator):
    def __init__(self, value: Any):
        self.value = value
        
    def validate(self, value: Any) -> None:
        if not self.value == value:
            raise ValueError('Given value {} is not equal to {}'.format(value, self.value))


class FunctionValidator(Validator):
    def __init__(self, func: Callable):
        """
        :param func:    A callable that returns True if the value is valid
        """
        self.func = func

    def validate(self, value: Any) -> None:
        if not self.func(value):
            raise ValueError('Calling {}({}) returned a False value'.format(self.func.__name__, value))


class SetValidator(Validator):
    def __init__(self, items: set):
        """
        :param items:   A set of items that are valid
        """
        self.items = set(items)

    def validate(self, value: Any) -> None:
        if value not in self.items:
            raise ValueError('Given value {} is not in {}'.format(value, self.items))
