import os
import re

import pytest
import schema

from pyparamvalidate.core.validator import Validator, CallValidateMethodError


# 自定义处理函数，首字母大写
def capitalize(value):
    return value.capitalize()


# 邮箱格式验证函数
def validate_email(value):
    email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return bool(re.match(email_regex, value))


reference_correct_data = {
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

user_schema = schema.Schema({
    'username': schema.And(str, lambda s: len(s.strip()) > 0,
                           error='Username cannot be empty or contain only spaces'),
    'phone_number': schema.Regex(r'^\d{11}$', error='Invalid phone number format. It should be a 10-digit number.'),
    'email': schema.And(schema.Or(str, None), lambda s: validate_email(s) if s is not None else True,
                        error='Invalid email format'),
    'age': schema.And(int, lambda n: 0 <= n <= 120, error='Age must be an integer between 0 and 120'),
    'gender': schema.And(str, lambda s: s.lower() in ['male', 'female', 'other'], error='Invalid gender'),
    'family_members': schema.And(schema.Use(list), [schema.Use(capitalize)]),
    'others': {
        'address': schema.And(str, lambda s: s.strip(), error='Address must be a non-empty string'),
        'blog': schema.Or(None, schema.Regex(r'^https?://\S+$',
                                             error='Invalid blog format. It should be a valid URL starting with http:// or https://')),
        'other': schema.Or(str, None)
    }
})


def test_schema_validate_01():
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
    assert Validator(valid_data).schema_validate(user_schema).value == valid_data


# 反向测试用例
def test_schema_validate_02():
    invalid_data_list = [
        # 无效的用户名（空字符串）
        {'username': '   ', 'phone_number': '13888886666', 'email': 'john@example.com', 'age': 25, 'gender': 'male',
         'family_members': ['Alice', 'Bob', 'Charlie'],
         'others': {'address': '123 Main St', 'other': 'Some additional info'}},
        # 无效的邮箱格式
        {'username': 'JohnDoe', 'phone_number': '13888886666', 'email': 'invalidemail', 'age': 25, 'gender': 'male',
         'family_members': ['Alice', 'Bob', 'Charlie'],
         'others': {'address': '123 Main St', 'other': 'Some additional info'}},
        # 无效的年龄（负数）
        {'username': 'JohnDoe', 'phone_number': '13888886666', 'email': 'john@example.com', 'age': -5, 'gender': 'male',
         'family_members': ['Alice', 'Bob', 'Charlie'],
         'others': {'address': '123 Main St', 'other': 'Some additional info'}},
        # 无效的性别
        {'username': 'JohnDoe', 'phone_number': '13888886666', 'email': 'john@example.com', 'age': 25,
         'gender': 'unknown',
         'family_members': ['Alice', 'Bob', 'Charlie'],
         'others': {'address': '123 Main St', 'other': 'Some additional info'}},
        # 无效的博客格式（不是以 http:// 或 https:// 开头）
        {'username': 'JohnDoe', 'phone_number': '13888886666', 'email': 'john@example.com', 'age': 25, 'gender': 'male',
         'family_members': ['Alice', 'Bob', 'Charlie'], 'others': {'address': '123 Main St', 'blog': 'invalidblog',
                                                                   'other': 'Some additional info'}},
        # 无效的家庭成员列表（包含空字符串）
        {'username': 'JohnDoe', 'phone_number': '13888886666', 'email': 'john@example.com', 'age': 25, 'gender': 'male',
         'family_members': ['Alice', '', 'Charlie'],
         'others': {'address': '123 Main St', 'other': 'Some additional info'}},
        # 无效的地址（空字符串）
        {'username': 'JohnDoe', 'phone_number': '13888886666', 'email': 'john@example.com', 'age': 25, 'gender': 'male',
         'family_members': ['Alice', 'Bob', 'Charlie'], 'others': {'address': '', 'other': 'Some additional info'}},
        # 无效的电话号码格式（不是10位数字）
        {'username': 'JohnDoe', 'phone_number': '12345', 'email': 'john@example.com', 'age': 25, 'gender': 'male',
         'family_members': ['Alice', 'Bob', 'Charlie'],
         'others': {'address': '123 Main St', 'other': 'Some additional info'}},
        # 无效的博客格式（None 但不为空字符串）
        {'username': 'JohnDoe', 'phone_number': '13888886666', 'email': 'john@example.com', 'age': 25, 'gender': 'male',
         'family_members': ['Alice', 'Bob', 'Charlie'],
         'others': {'address': '123 Main St', 'blog': '', 'other': 'Some additional info'}},
        # 无效的博客格式（不是以 http:// 或 https:// 开头）
        {'username': 'JohnDoe', 'phone_number': '13888886666', 'email': 'john@example.com', 'age': 25, 'gender': 'male',
         'family_members': ['Alice', 'Bob', 'Charlie'], 'others': {'address': '123 Main St', 'blog': 'invalidblog',
                                                                   'other': 'Some additional info'}}
    ]

    for invalid_data in invalid_data_list:
        with pytest.raises(schema.SchemaError) as exc_info:
            Validator(invalid_data).schema_validate(user_schema)
        print(exc_info.value)
        print('===============================')


def test_customize_validator_01():
    Validator(4).customize(validate_method=lambda x: x % 2 == 0)

    with pytest.raises(ValueError) as exc_info:
        Validator(3).customize(validate_method=lambda x: x % 2 == 0, exception_msg='value must be an even number.')
    assert "value must be an even number." in str(exc_info.value)


def test_customize_validator_02():
    def even_number_validator(value):
        return value % 2 == 0

    Validator(4).customize(validate_method=even_number_validator)

    with pytest.raises(ValueError) as exc_info:
        Validator(3).customize(validate_method=lambda x: x % 2 == 0, exception_msg='value must be an even number.')
    assert "value must be an even number." in str(exc_info.value)


def test_customize_validator_03():
    def even_number_validator(value, threshold):
        return value % 2 == 0 and value > threshold

    Validator(12).customize(even_number_validator, 10)

    Validator(12).customize(even_number_validator, 10,
                            exception_msg='value must be an even number and greater than 10.')

    Validator(12).customize(even_number_validator, threshold=10,
                            exception_msg='value must be an even number and greater than 10.')

    with pytest.raises(ValueError) as exc_info:
        Validator(2).customize(validate_method=even_number_validator, threshold=10,
                               exception_msg='value must be an even number and greater than 10.')
    assert "value must be an even number and greater than 10." in str(exc_info.value)

    with pytest.raises(CallValidateMethodError) as exc_info:
        Validator(2).customize(even_number_validator, 2, 10,
                               exception_msg='value must be an even number and greater than 10.')


def test_is_string():
    assert Validator("test").is_string(exception_msg='value must be string')

    with pytest.raises(ValueError) as exc_info:
        Validator(123).is_string(exception_msg='value must be string')
    assert "value must be string" in str(exc_info.value)


def test_is_int():
    assert Validator(42).is_int(exception_msg='value must be integer')

    with pytest.raises(ValueError) as exc_info:
        Validator("test").is_int(exception_msg='value must be integer')
    assert "value must be integer" in str(exc_info.value)


def test_is_positive():
    assert Validator(42).is_positive(exception_msg='value must be positive')

    with pytest.raises(ValueError) as exc_info:
        Validator(-1).is_positive(exception_msg='value must be positive')
    assert "value must be positive" in str(exc_info.value)


def test_is_float():
    assert Validator(3.14).is_float(exception_msg='value must be float')

    with pytest.raises(ValueError) as exc_info:
        Validator("test").is_float(exception_msg='value must be float')
    assert "value must be float" in str(exc_info.value)


def test_is_list():
    assert Validator([1, 2, 3]).is_list(exception_msg='value must be list')

    with pytest.raises(ValueError) as exc_info:
        Validator("test").is_list(exception_msg='value must be list')
    assert "value must be list" in str(exc_info.value)


def test_is_dict():
    assert Validator({"key": "value"}).is_dict(exception_msg='value must be dict')

    with pytest.raises(ValueError) as exc_info:
        Validator([1, 2, 3]).is_dict(exception_msg='value must be dict')
    assert "value must be dict" in str(exc_info.value)


def test_is_set():
    assert Validator({1, 2, 3}).is_set(exception_msg='value must be set')

    with pytest.raises(ValueError) as exc_info:
        Validator([1, 2, 3]).is_set(exception_msg='value must be set')
    assert "value must be set" in str(exc_info.value)


def test_is_tuple():
    assert Validator((1, 2, 3)).is_tuple(exception_msg='value must be tuple')

    with pytest.raises(ValueError) as exc_info:
        Validator([1, 2, 3]).is_tuple(exception_msg='value must be tuple')
    assert "value must be tuple" in str(exc_info.value)


def test_is_not_none():
    assert Validator("test").is_not_none(exception_msg='value must not be None')

    with pytest.raises(ValueError) as exc_info:
        Validator(None).is_not_none(exception_msg='value must not be None')
    assert "value must not be None" in str(exc_info.value)


def test_is_not_empty():
    assert Validator("test").is_not_empty(exception_msg='value must not be empty')

    with pytest.raises(ValueError) as exc_info:
        Validator("").is_not_empty(exception_msg='value must not be empty')
        assert "value must not be empty" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        Validator("  ").is_not_empty(exception_msg='value must not be empty')
        assert "value must not be empty" in str(exc_info.value)


def test_is_allowed_value():
    assert Validator(3).is_allowed_value(allowed_values=[1, 2, 3, 4, 5],
                                         exception_msg='value must be in allowed_values')

    with pytest.raises(ValueError) as exc_info:
        Validator(6).is_allowed_value(allowed_values=[1, 2, 3, 4, 5],
                                      exception_msg='value must be in allowed_values')
    assert "value must be in allowed_values" in str(exc_info.value)


def test_is_specific_value():
    assert Validator(3).is_specific_value(specific_value=3,
                                          exception_msg='value must be in allowed_values')

    with pytest.raises(ValueError) as exc_info:
        Validator(6).is_specific_value(specific_value=3,
                                       exception_msg='value must be in allowed_values')
    assert "value must be in allowed_values" in str(exc_info.value)


def test_max_length():
    assert Validator("test").max_length(max_length=5,
                                        exception_msg='value length must be less than or equal to 5')

    with pytest.raises(ValueError) as exc_info:
        Validator("test").max_length(max_length=3,
                                     exception_msg='value length must be less than or equal to 3')
    assert "value length must be less than or equal to 3" in str(exc_info.value)


def test_min_length():
    assert Validator("test").min_length(min_length=3,
                                        exception_msg='value length must be greater than or equal to 3')

    with pytest.raises(ValueError) as exc_info:
        Validator("test").min_length(min_length=5,
                                     exception_msg='value length must be greater than or equal to 5')
    assert "value length must be greater than or equal to 5" in str(exc_info.value)


def test_is_substring():
    assert Validator("st").is_substring(super_string="test",
                                        exception_msg='sub_string must be a substring of super_string')

    with pytest.raises(ValueError) as exc_info:
        Validator("abc").is_substring(super_string="test",
                                      exception_msg='sub_string must be a substring of super_string')
    assert "sub_string must be a substring of super_string" in str(exc_info.value)


def test_is_subset():
    assert Validator({1, 2}).is_subset(superset={1, 2, 3, 4},
                                       exception_msg='subset must be a subset of superset')

    with pytest.raises(ValueError) as exc_info:
        Validator({5, 6}).is_subset(superset={1, 2, 3, 4},
                                    exception_msg='subset must be a subset of superset')
    assert "subset must be a subset of superset" in str(exc_info.value)


def test_is_sublist():
    assert Validator([1, 2]).is_sublist(superlist=[1, 2, 3, 4],
                                        exception_msg='sublist must be a sublist of superlist')

    with pytest.raises(ValueError) as exc_info:
        Validator([5, 6]).is_sublist(superlist=[1, 2, 3, 4],
                                     exception_msg='sublist must be a sublist of superlist')
    assert "sublist must be a sublist of superlist" in str(exc_info.value)


def test_contains_substring():
    assert Validator("test").contains_substring(substring="es",
                                                exception_msg='superstring must contain substring')

    with pytest.raises(ValueError) as exc_info:
        Validator("test").contains_substring(substring="abc",
                                             exception_msg='superstring must contain substring')
    assert "superstring must contain substring" in str(exc_info.value)


def test_contains_subset():
    assert Validator({1, 2, 3, 4}).contains_subset(subset={1, 2},
                                                   exception_msg='superset must contain subset')

    with pytest.raises(ValueError) as exc_info:
        Validator({1, 2, 3, 4}).contains_subset(subset={5, 6},
                                                exception_msg='superset must contain subset')
    assert "superset must contain subset" in str(exc_info.value)


def test_contains_sublist():
    assert Validator([1, 2, 3, 4]).contains_sublist(sublist=[1, 2],
                                                    exception_msg='superlist must contain sublist')

    with pytest.raises(ValueError) as exc_info:
        Validator([1, 2, 3, 4]).contains_sublist(sublist=[5, 6],
                                                 exception_msg='superlist must contain sublist')
    assert "superlist must contain sublist" in str(exc_info.value)


def test_is_file_suffix():
    assert Validator("example.txt").is_file_suffix(file_suffix=".txt",
                                                   exception_msg='path must have the specified file suffix')

    with pytest.raises(ValueError) as exc_info:
        Validator("example.txt").is_file_suffix(file_suffix=".csv",
                                                exception_msg='path must have the specified file suffix')
    assert "path must have the specified file suffix" in str(exc_info.value)


def test_is_file():
    assert Validator(__file__).is_file(exception_msg='path must be an existing file')

    with pytest.raises(ValueError) as exc_info:
        Validator("path").is_file(
            exception_msg='path must be an existing file')
    assert "path must be an existing file" in str(exc_info.value)


def test_is_dir():
    assert Validator(os.path.dirname(__file__)).is_dir(
        exception_msg='path must be an existing directory')

    with pytest.raises(ValueError) as exc_info:
        Validator(__file__).is_dir(
            exception_msg='path must be an existing directory')
    assert "path must be an existing directory" in str(exc_info.value)


def test_is_method():
    assert Validator(print).is_method(exception_msg='value must be a callable method')

    with pytest.raises(ValueError) as exc_info:
        Validator("test").is_method(exception_msg='value must be a callable method')
    assert "value must be a callable method" in str(exc_info.value)
