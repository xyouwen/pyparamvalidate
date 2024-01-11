import functools
import inspect
from typing import TypeVar


def _error_prompt(value, exception_msg=None, rule_des=None, field=None):
    default = f'"{value}" is invalid.'
    prompt = exception_msg or rule_des
    prompt = f'{default} due to: {prompt}' if prompt else default
    prompt = f'{field} error: {prompt}' if field else prompt
    return prompt


def raise_exception(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        bound_args = inspect.signature(func).bind(self, *args, **kwargs).arguments

        exception_msg = kwargs.get('exception_msg', None) or bound_args.get('exception_msg', None)
        error_prompt = _error_prompt(self.value, exception_msg, self._rule_des, self._field)

        result = func(self, *args, **kwargs)
        if not result:
            raise ValueError(error_prompt)

        return self

    return wrapper


class RaiseExceptionMeta(type):
    def __new__(cls, name, bases, dct):
        for key, value in dct.items():
            if isinstance(value, staticmethod):
                dct[key] = staticmethod(raise_exception(value.__func__))

            if isinstance(value, classmethod):
                dct[key] = classmethod(raise_exception(value.__func__))

            if inspect.isfunction(value) and not key.startswith("__"):
                dct[key] = raise_exception(value)

        return super().__new__(cls, name, bases, dct)


Self = TypeVar('Self', bound='Validator')


class Validator(metaclass=RaiseExceptionMeta):
    def __init__(self, value, field=None, rule_des=None):
        self.value = value
        self._field = field
        self._rule_des = rule_des

    def is_string(self, exception_msg=None) -> Self:
        return isinstance(self.value, str)

    def is_not_empty(self, exception_msg=None) -> Self:
        return bool(self.value)
