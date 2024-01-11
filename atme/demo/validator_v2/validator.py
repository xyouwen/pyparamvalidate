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
        # 将 "参数名" 和 "参数值" 绑定为键值对
        bound_args = inspect.signature(func).bind(self, *args, **kwargs).arguments

        # 如果 参数名 在 kwargs 中，则优先从 kwargs 中获取，对应: 以关键字参数进行传值的情形， 如 is_string('Jane', exception_msg='name must be string')
        # 否则，从 bound_args 中获取，对应: 以位置参数进行传值的情形，如 is_string('Jane', 'name must be string')
        exception_msg = kwargs.get('exception_msg', None) or bound_args.get('exception_msg', None)
        error_prompt = _error_prompt(self.value, exception_msg, self._rule_des, self._field)

        result = func(self, *args, **kwargs)
        if not result:
            raise ValueError(error_prompt)

        return self

    return wrapper


class Validator:
    def __init__(self, value, field=None, rule_des=None):
        self.value = value
        self._field = field
        self._rule_des = rule_des

    # todo : 在这里添加装饰器器的执行过程
    '''
    对的，您的描述是正确的。在Python中，使用 @decorator 语法糖实际上是一个缩写，等同于调用 decorator(target_function)，其中 target_function 是要装饰的函数。
    在这里，@ParameterValidator("param").is_string() 装饰函数 example_function，实际上相当于 ParameterValidator("param").is_string()(example_function)。
    '''
    @raise_exception
    def is_string(self, exception_msg=None):
        """
        exception_msg 会在 raise_exception 装饰器中隐式调用。
        在校验方法中显示指定关键字参数 exception_msg=None, 尽量不要使用 **kwargs 这种写法，方便用户知道传递什么参数。
        """
        return isinstance(self.value, str)

    @raise_exception
    def is_not_empty(self, exception_msg=None):
        return bool(self.value)
