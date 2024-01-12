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


# python 装饰器基础, 请参考：https://kindtester.blog.csdn.net/article/details/135550880
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

    @raise_exception
    def is_string(self, exception_msg=None):
        """
        exception_msg 会在 raise_exception 装饰器中隐式调用。
        """
        return isinstance(self.value, str)

    '''
   
    @raise_exception
    def is_string(self, **kwargs):
        """
        虽然这种方式能实现同样的效果，但是不推荐使用，理由是：
        1. pycharm 无法智能提示；
        2. 必须要有明确的文档说明，告知用户要传递的参数是什么；
        3.使用 exception_msg=None 作为关键字参数可以解决这两个问题；
        """
        return isinstance(self.value, str)
        
     '''

    @raise_exception
    def is_not_empty(self, exception_msg=None):
        return bool(self.value)
