import inspect
from functools import wraps
from typing import Callable

from atme.demo.validator_v5.validator import Validator


class ParameterValidator:
    def __init__(self, param_name: str, param_rule_des=None):
        """
        :param param_name: 参数名
        :param param_rule_des: 该参数的规则描述
        """
        self.param_name = param_name
        self.param_rule_des = param_rule_des

        self._validators = []

    def __getattr__(self, name: str):
        """
        当调用一个不存在的属性或方法时，Python 会自动调用 __getattr__ 方法，可以利用这个特性，动态收集用户调用的校验方法。

        以用户使用 ParamValidator("param").is_string(exception_msg='param must be string').is_not_empty() 为例，代码执行过程如下:

        1. 当用户调用 ParamValidator("param").is_string(exception_msg='param must be string') 时，
        2. 由于 is_string 方法不存在，__getattr__ 方法被调用，返回 validator_method 函数(此时未被调用)，is_string 方法实际上是 validator_method 函数的引用，
        3. 当执行 is_string(exception_msg='param must be string') 时，is_string 方法被调用, 使用关键字参数传递 exception_msg='param must be string'，
        4. 实际上是执行了 validator_method(exception_msg='param must be string') , validator_method 函数完成调用后，执行函数体中的逻辑：
             - 向 self._validators 中添加了一个元组 ('is_string', (),  {'exception_msg': 'param  must  be  string'})
             - 返回 self 对象
        5. self 对象继续调用 is_not_empty(), 形成链式调用效果，此时的 validator_method 函数的引用就是 is_not_empty, 调用过程与 1-4 相同。
        """

        def validator_method(*args, **kwargs):
            self._validators.append((name, args, kwargs))
            return self

        return validator_method

    def __call__(self, func: Callable) -> Callable:
        """
        使用 __call__ 方法, 让 ParameterValidator 的实例变成可调用对象，使其可以像函数一样被调用。

        '''
        @ParameterValidator("param").is_string()
        def example_function(param):
            return param

        example_function(param="test")
        '''

        以这段代码为例，代码执行过程如下：

        1. 使用 @ParameterValidator("param").is_string() 装饰函数 example_function，相当于: @ParameterValidator("param").is_string()(example_function)
        2. 此时返回一个 wrapper 函数（此时未调用）, example_function 函数实际上是 wrapper 函数的引用；
        3. 当执行 example_function(param="test") 时，相当于执行 wrapper(param="test"), wrapper 函数被调用，开始执行 wrapper 内部逻辑, 见代码中注释。
        """

        @wraps(func)
        def wrapper(*args, **kwargs):

            # 获取函数的参数和参数值
            bound_args = inspect.signature(func).bind(*args, **kwargs).arguments

            if self.param_name in kwargs:
                # 如果用户以关键字参数传值，如 example_function(param="test") ，则从 kwargs 中取参数值；
                value = kwargs[self.param_name]
            else:
                # 如果用户以位置参数传值，如 example_function("test")，则从 bound_args 是取参数值；
                value = bound_args.get(self.param_name)

            # 实例化 Validator 对象
            validator = Validator(value, field=self.param_name, rule_des=self.param_rule_des)

            # 遍历所有校验器(注意：这里使用 vargs, vkwargs，避免覆盖原函数的 args, kwargs)
            for method_name, vargs, vkwargs in self._validators:
                # 通过 函数名 反射获取校验函数对象
                validate_method = getattr(validator, method_name)

                # 执行校验函数
                validate_method(*vargs, **vkwargs)

            # 执行原函数
            return func(*args, **kwargs)

        return wrapper
