from abc import ABC, abstractmethod
from typing import Any, Callable, Iterable, Union


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


class SequenceValidator(Validator):
    def __init__(self, scalar_validator: Validator):
        """
        :param scalar_validator:    A validator to validate the scalars
        """
        self.validator = scalar_validator

    def validate(self, value: Iterable):
        for val in value:
            self.validator.validate(val)


ValidatorType = Union[Validator, range, int, tuple, str, set, tuple, list, Callable]


def as_validator(validator_input: ValidatorType) -> Union[Validator, None]:
    if validator_input is None:
        return None
    if isinstance(validator_input, Validator):
        return validator_input
    elif isinstance(validator_input, range):
        return RangeValidator(validator_input)
    elif isinstance(validator_input, (int, float, str)):
        return ExactValueValidator(validator_input)
    elif isinstance(validator_input, (set, tuple, list)):
        return SetValidator(validator_input)
    elif callable(validator_input):
        return FunctionValidator(validator_input)
    else:
        raise TypeError(f'Unable to assign a validator for {validator_input}, please import one and use it explicitly')
