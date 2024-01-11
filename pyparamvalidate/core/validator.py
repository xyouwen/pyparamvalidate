import functools
import inspect
import os
import logging
from typing import TypeVar

from schema import Schema

logger = logging.getLogger(__name__)


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


class CallValidateMethodError(Exception):
    ...


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

            valid_data = {
            'username': 'JohnDoe',
            'phone_number': '13888886666',
            'email': 'john@example.com',
            'age': 25,
            'gender': 'male',
            'family_members': ['Alice', 'Bob', 'Charlie'],
            'others': {
                'address': '123 Main St',
                'blog': 'http://example.com',
                'other': 'Some additional info'
                }
            }

            Validator(valid_data).schema_validate(user_schema)

        """
        if not isinstance(schema, Schema):
            raise CallValidateMethodError(f'{schema} must be a instance of Schema, not {type(schema)}, '
                                          f'Please use "schema.Schema()" to initialize the schema.'
                                          f'Documentation: https://pypi.org/project/schema/')

        # 将 validate 之后的值赋值给 self.value，因为 schema 在校验的过程中可以对 value 进行预处理
        self.value = schema.validate(self.value)
        return self

    def customize(self, validate_method, *args, exception_msg=None, **kwargs) -> Self:
        """
        注意：请参考示例 3

        示例 1：使用 lambda 函数
            '''
            Validator(4).customize(validate_method=lambda x: x % 2 == 0)
            '''

        示例 2：函数只有一个参数
            '''
            def even_number_validator(value):
                return value % 2 == 0

            Validator(4).customize(validate_method=even_number_validator)
            '''

        示例 3：如果函数有多个参数，必须将 "待校验参数" 放在第一位
            '''
            def even_number_validator(value, threshold):
                # 注意：自定义校验方法，如果有多个参数，必须将 "待校验参数" 放在第一位
                return value % 2 == 0 and value > threshold

            # 正确的调用方式：第一个参数不要传值，exception_msg 必须以关键字参数传值。
            Validator(12).customize(even_number_validator, 10, exception_msg='value must be an even number and greater than 10.')
            '''
        """

        try:
            return validate_method(self.value, *args, **kwargs)
        except TypeError as e:

            raise CallValidateMethodError(
                f'''
                Note:
                
                1. Please do not send value to first argument in calling {validate_method.__name__}.
                2. You must pass the value for "exception_msg" as a "keyword argument".
                3. please refer to: 
                
                    def even_number_validator(value, threshold):
                        return value % 2 == 0 and value > threshold
                        
                    Validator(12).customize(even_number_validator, 10, exception_msg='value must be an even number and greater than 10.')
                    
                4. origin error: {e}'
                ''')

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

    def is_not_empty(self, exception_msg=None, stripped=True):
        if stripped:
            if isinstance(self.value, str):
                self.value = self.value.strip()
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
