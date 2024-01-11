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


'''
- TypeVar 是 Python 中用于声明类型变量的工具
- 声明一个类型变量，命名为 'Self', 意思为表示类的实例类型
- bound 参数指定泛型类型变量的上界，即限制 'Self' 必须是 'Validator' 类型或其子类型
'''
Self = TypeVar('Self', bound='Validator')


class Validator(metaclass=RaiseExceptionMeta):
    def __init__(self, value, field=None, rule_des=None):
        self.value = value
        self._field = field
        self._rule_des = rule_des

    def is_string(self, exception_msg=None) -> Self:
        """
        将返回类型注解定义为 Self, 支持编辑器如 pycharm 智能提示链式调用方法，如：Validator(input).is_string().is_not_empty()

        - 从 Python 3.5 版本开始支持类型注解
            - 在 Python 3.5 中引入了 PEP 484（Python Enhancement Proposal 484），其中包括了类型注解的概念，并引入了 typing 模块，用于支持类型提示和静态类型检查；
            - 类型注解允许开发者在函数参数、返回值和变量上添加类型信息，但是在运行时，Python 解释器不会检查这些注解是否正确；
            - 它们主要用于提供给静态类型检查器或代码编辑器进行，以提供更好的代码提示和错误检测；
            - Python 运行时并不强制执行这些注解，Python 依然是一门动态类型的语言。

        - 本方法中：
            - 返回值类型为 bool 类型，用于与装饰器函数 raise_exception 配合使用，校验 self.value 是否通过；
            - 为了支持编辑器如 pycharm 智能识别链式调用方法，将返回类型注解定义为 Self, 如：Validator(input).is_string().is_not_empty()；
            - Self, 即 'Validator', 由 Self = TypeVar('Self', bound='Validator') 定义；
            - 如果返回类型不为 Self, 编辑器如 pycharm 在 Validator(input).is_string() 之后，不会智能提示 is_not_empty()
        """
        return isinstance(self.value, str)

    def is_not_empty(self, exception_msg=None) -> Self:
        return bool(self.value)
