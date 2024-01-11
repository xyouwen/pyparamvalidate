import functools
import inspect


def _error_prompt(value, exception_msg=None, rule_des=None, field=None):
    """
    优先使用校验方法中的错误提示, 如果方法中没有错误提示，则使用"字段规则描述"代替错误提示
    拼接出：name error: "123" is invalid. due to: name must be string.
    """

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
            # 如果是静态方法，则将它替换为一个新的静态方法，新的静态方法调用 raise_exception 函数，将原静态方法作为参数传递给raise_exception
            if isinstance(value, staticmethod):
                dct[key] = staticmethod(raise_exception(value.__func__))

            # 如果是类方法，则将它替换为一个新的类方法，新的类方法调用 raise_exception 函数，将原类方法作为参数传递给raise_exception
            if isinstance(value, classmethod):
                dct[key] = classmethod(raise_exception(value.__func__))

            # 如果是普通的成员方法，则将它替换为一个新的函数，新函数调用 raise_exception 函数，将原函数作为参数传递给 raise_exception
            # 排除掉以双下划线 __ 开头的方法, 如 __init__，__new__等
            if inspect.isfunction(value) and not key.startswith("__"):
                dct[key] = raise_exception(value)

        return super().__new__(cls, name, bases, dct)


class Validator(metaclass=RaiseExceptionMeta):
    def __init__(self, value, field=None, rule_des=None):
        """
        :param value: 待校验的值
        :param field: 校验字段
            - 用于提示具体哪个字段错误
            - 如 'name error: name must be string'
            - error 前面的 `name` 即为 field
        :param rule_des: 校验规则描述
        """
        self.value = value
        self._field = field
        self._rule_des = rule_des

    def is_string(self, exception_msg=None):
        return isinstance(self.value, str)

    def is_not_empty(self, exception_msg=None):
        return bool(self.value)
