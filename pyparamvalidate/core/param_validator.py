import inspect
import os
from functools import wraps
from typing import TypeVar, Callable

from schema import Schema

from pyparamvalidate.core.validator import Validator

Self = TypeVar('Self', bound='ParameterValidator')


class ParameterValidator:
    def __init__(self, param_name: str, param_rule_des=None):
        """
        :param param_name: 参数名
        :param param_rule_des: 该参数的规则描述
        """
        self.param_name = param_name
        self.param_rule_des = param_rule_des

        self._validators = []

    def __getattribute__(self, name: str):
        """
        __getattribute__ 在每次访问对象的属性时都会触发，不管属性是否存在。
        通过重写 __getattribute__，可以自定义属性的获取逻辑，实现了对特定属性的直接访问（param_name 、param_rule_des 、 _validators），
        而对于其他属性，则创建名为 validator_method 的函数，将其作为属性返回
        """

        '''
        如果获取到的属性名为 param_name 、param_rule_des 、 _validators , 则使用 object.__getattribute__(self, name) 直接获取对象的属性值。
        不对 self.param_name 、 self.param_rule_des 、 self._validators 做改变
        '''
        if name in ['param_name', 'param_rule_des', '_validators']:
            return object.__getattribute__(self, name)

        '''
        如果属性名不在上述列表中，说明用户正在访问一个不存在的属性，这时创建了一个函数 collect_validator_method
        
        以用户使用 ParamValidator("param").is_string(exception_msg='param must be string').is_not_empty() 为例，代码执行过程如下:

        1. 当用户调用 ParamValidator("param").is_string(exception_msg='param must be string') 时，
        2. 由于 is_string 方法不存在，__getattr__ 方法被调用，返回 validator_method 函数(此时未被调用)，is_string 方法实际上是 validator_method 函数的引用，
        3. 当执行 is_string(exception_msg='param must be string') 时，is_string 方法被调用, 使用关键字参数传递 exception_msg='param must be string'，
        4. 实际上是执行了 validator_method(exception_msg='param must be string') , validator_method 函数完成调用后，执行函数体中的逻辑：
             - 向 self._validators 中添加了一个元组 ('is_string', (),  {'exception_msg': 'param  must  be  string'})
             - 返回 self 对象
        5. self 对象继续调用 is_not_empty(), 形成链式调用效果，此时的 validator_method 函数的引用就是 is_not_empty, 调用过程与 1-4 相同。
        '''

        def validator_method(*args, **kwargs):
            self._validators.append((name, args, kwargs))
            return self

        return validator_method

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取函数的参数和参数值
            bound_args = inspect.signature(func).bind(*args, **kwargs).arguments

            if self.param_name in kwargs:
                # 如果函数被装饰，且以关键字参数传值，则从 kwargs 中取参数值
                value = kwargs[self.param_name]
            else:
                # 如果函数被装饰，且以位置参数传值，则从 bound_args 中取参数值
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

    '''
    ==============================分隔符===============================
    
    以下所有方法，是从 Validator 类中复制过来，目的是：
    - 为了让编辑器如 Pycharm 智能提示 ParameterValidator 本类中可以使用的校验方法；
    - 这些方法仅供 Pycharm 智能提示使用，没有任何实际作用；
        可以是：
            def is_string(self, exception_msg=None) -> Self:
                ...
        也可以是：
            def is_string(self, exception_msg=None) -> Self:
                return isinstance(self.value, str)            
    - ParameterValidator 类的实例通过 __getattribute__ 方法动态收集用户的调用方法；
    - 然后使用 __call__ 方法反射调用 Validator 类中的调用方法
    
    在模块中定义了: Self = TypeVar('Self', bound='ParameterValidator')，目的是：
    - 方便从 Validator 类中复制校验方法，粘贴之后不做任何代码层面的修改：
    - 方便链式调用，如： @ParameterValidator("param").is_string().is_not_empty()
    '''

    def schema_validate(self, schema: Schema) -> Self:
        """
        schema 官方参考文档： https://pypi.org/project/schema/

        下面是涵盖了 Schema 大部分特性的示例说明 :

        1. 定义 schema

            # 自定义处理函数，首字母大写
            def capitalize(value):
                return value.capitalize()


            # 邮箱格式验证函数
            def validate_email(value):
                email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
                return bool(re.match(email_regex, value))


            user_schema = schema.Schema({
            'username': schema.And(str, lambda s: len(s.strip()) > 0, error='Username cannot be empty or contain only spaces'),
            'phone_number': schema.Regex(r'^\d{11}$', error='Invalid phone number format. It should be a 10-digit number.'),
            'email': schema.And(schema.Or(str, None), lambda s: validate_email(s) if s is not None else True, error='Invalid email format'),
            'age': schema.And(int, lambda n: 0 <= n <= 120, error='Age must be an integer between 0 and 120'),
            'gender': schema.And(str, lambda s: s.lower() in ['male', 'female', 'other'], error='Invalid gender'),
            'family_members': schema.And(schema.Use(list), [schema.Use(capitalize)]),
            'others': {
                'address': schema.And(str, lambda s: s.strip(), error='Address must be a non-empty string'),
                'blog': schema.Or(None, schema.Regex(r'^https?://\S+$', error='Invalid blog format. It should be a valid URL starting with http:// or https://')),
                'other': schema.Or(str, None)
                }
            })

        2. 使用 schema 进行校验

            @ParameterValidator("user_data").schema_validate(user_schema)
            def example_function(user_data):
                return user_data

        """
        ...

    def customize(self, validate_method, *args, exception_msg=None, **kwargs) -> Self:
        """
        注意事项：请参考示例 3

        示例 1：使用 lambda 函数
            '''
            @ParameterValidator("param").customize(lambda x: x % 2 == 0, exception_msg="Value must be an even number")
            def example_function(param):
                return param
            '''

        示例 2：函数只有一个参数
            '''
            def even_number_validator(value):
                return value % 2 == 0

            @ParameterValidator("param").customize(even_number_validator, exception_msg="Value must be an even number")
            def example_function(param):
                return param
            '''

        示例 3：如果函数有多个参数，必须将 "待校验参数" 放在第一位
            '''
            # 方法定义注意事项：如果有多个参数，必须将 "待校验参数" 放在第一位
            def even_number_validator(value, threshold):

                return value % 2 == 0 and value > threshold

            # 方法调用注意事项：第一个参数不要传值，exception_msg 必须以关键字参数传值。
            @ParameterValidator("param").customize(even_number_validator, 10, exception_msg="Value must be an even number")
            def example_function(param):
                return param
            '''
        """
        ...

    def is_string(self, exception_msg=None) -> Self:
        return isinstance(self.value, str)

    def is_int(self, exception_msg=None):
        return isinstance(self.value, int)

    def is_positive(self, exception_msg=None):
        return self.value > 0

    def is_float(self, exception_msg=None):
        return isinstance(self.value, float)

    def is_list(self, exception_msg=None):
        return isinstance(self.value, list)

    def is_dict(self, exception_msg=None):
        return isinstance(self.value, dict)

    def is_set(self, exception_msg=None):
        return isinstance(self.value, set)

    def is_tuple(self, exception_msg=None):
        return isinstance(self.value, tuple)

    def is_not_none(self, exception_msg=None):
        return self.value is not None

    def is_not_empty(self, exception_msg=None):
        return bool(self.value)

    def is_allowed_value(self, allowed_values, exception_msg=None):
        return self.value in allowed_values

    def is_specific_value(self, specific_value, exception_msg=None):
        return self.value == specific_value

    def max_length(self, max_length, exception_msg=None):
        return len(self.value) <= max_length

    def min_length(self, min_length, exception_msg=None):
        return len(self.value) >= min_length

    def is_substring(self, super_string, exception_msg=None):
        return self.value in super_string

    def is_subset(self, superset, exception_msg=None):
        return self.value.issubset(superset)

    def is_sublist(self, superlist, exception_msg=None):
        return set(self.value).issubset(set(superlist))

    def contains_substring(self, substring, exception_msg=None):
        return substring in self.value

    def contains_subset(self, subset, exception_msg=None):
        return subset.issubset(self.value)

    def contains_sublist(self, sublist, exception_msg=None):
        return set(sublist).issubset(set(self.value))

    def is_file(self, exception_msg=None):
        return os.path.isfile(self.value)

    def is_dir(self, exception_msg=None):
        return os.path.isdir(self.value)

    def is_file_suffix(self, file_suffix, exception_msg=None):
        return self.value.endswith(file_suffix)

    def is_method(self, exception_msg=None):
        return callable(self.value)
