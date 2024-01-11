pyparamvalidate 是一个简单易用的函数参数验证器。它提供了各种内置验证器，支持自定义验证规则，有助于
python 开发人员轻松进行函数参数验证，提高代码的健壮性和可维护性。

项目地址：[github](https://github.com/xyouwen/pyparamvalidate)

# 一、安装

```bash
pip install pyparamvalidate
```

如果安装过程中提示 `Failed to build numpy` 错误：

```
Failed to build numpy
ERROR: Could not build wheels for numpy, which is required to install pyproject.toml-based projects
```

请先手动安装 `numpy` 库:

```
pip install numpy
```

# 二、使用示例

该示例可使用 `pytest` 执行:

```python
import pytest
from pyparamvalidate import ParameterValidator


def test_complex_validator():
    @ParameterValidator("description").is_string().is_not_empty()
    @ParameterValidator("gender", "Invalid").is_allowed_value(["male", "female"],
                                                              "Gender must be either 'male' or 'female'")
    @ParameterValidator("age", param_rule_des="Age must be a positive number").is_int().is_positive()
    @ParameterValidator("name").is_string(exception_msg="Name must be a string").is_not_empty()
    def example_function(name, age, gender='male', **kwargs):
        description = kwargs.get("description")
        return name, age, gender, description

    # 正向测试用例
    result = example_function(name="John", age=25, gender="male", description="A person")
    assert result == ("John", 25, "male", "A person")

    # 反向测试用例：测试 name 不是字符串的情况
    with pytest.raises(ValueError) as exc_info:
        example_function(name=123, age=25, gender="male", description="A person")
    assert "Name must be a string" in str(exc_info.value)
    print('\n')
    print(exc_info.value)
    print('==================================')

    # 反向测试用例：测试 age 不是正整数的情况
    with pytest.raises(ValueError) as exc_info:
        example_function(name="John", age="25", gender="male", description="A person")
    assert "Age must be a positive number" in str(exc_info.value)
    print(exc_info.value)
    print('==================================')

    # 反向测试用例：测试 gender 不是预定义值的情况
    with pytest.raises(ValueError) as exc_info:
        example_function(name="John", age=25, gender="other", description="A person")
    assert "Gender must be either 'male' or 'female'" in str(exc_info.value)
    print(exc_info.value)
    print('==================================')

    # 反向测试用例：测试 description 不是字符串的情况
    with pytest.raises(ValueError) as exc_info:
        example_function(name="John", age=25, gender="male", description=123)
    assert "invalid" in str(exc_info.value)
    print(exc_info.value)
    print('==================================')

    # 反向测试用例：测试 description 是空字符串的情况
    with pytest.raises(ValueError) as exc_info:
        example_function(name="John", age=25, gender="male", description="  ")
    assert "invalid" in str(exc_info.value)
    print(exc_info.value)
    print('==================================')

```

输出结果：

```
============================= test session starts =============================
collecting ... collected 1 item

test_param_validator.py::test_complex_validator PASSED                   [100%]

name error: "123" is invalid. due to: Name must be a string
==================================
age error: "25" is invalid. due to: Age must be a positive number
==================================
gender error: "other" is invalid. due to: Gender must be either 'male' or 'female'
==================================
description error: "123" is invalid.
==================================
description error: "  " is invalid.
==================================


============================== 1 passed in 0.03s ==============================
```

# 三、特性说明

## 3.1 关于校验方法

- 支持链式调用

```python
from pyparamvalidate import ParameterValidator


@ParameterValidator("name").is_string().is_not_empty()
def example_function(name, age, gender='male', **kwargs):
    ...
```

- 支持自定义校验方法

```python
import pytest
from pyparamvalidate import ParameterValidator


def test_custom_validator():
    # ====================================== 使用 lambda 函数 ======================================
    @ParameterValidator("param").customize(lambda x: x % 2 == 0, exception_msg="Value must be an even number")
    def example_function(param):
        return param

    assert example_function(param=12) == 12

    with pytest.raises(ValueError) as exc_info:
        example_function(param=5)
    assert "Value must be an even number" in str(exc_info.value)

    # ====================================== 使用 自定义 函数 ======================================
    def even_number_validator(value, threshold):
        # 注意：如果自定义校验方法有多个参数，必须要将 `待校验参数` 放在第一位
        # 示例：本例中，将 `value` 参数放在第一位

        return value % 2 == 0 and value > threshold

    # 注意：
    # 1. 使用自定义校验方法时，不要给第一个参数传值，该值从被装饰函数的参数中获取。
    # 2. `customize` 方法中的 `exception_msg` 参数，必须使用 `关键字参数` 形式进行传值。
    @ParameterValidator("param").customize(even_number_validator, 10,
                                           exception_msg="Value must be an even number and greater than 10")
    def example_function(param):
        return param

    assert example_function(param=12) == 12

    with pytest.raises(ValueError) as exc_info:
        example_function(param=5)
    assert "Value must be an even number" in str(exc_info.value)
```

- 支持使用`schema`库进行较复杂校验，如：

```python
import schema
import re
from pyparamvalidate import ParameterValidator


# 1. 定义 schema

def capitalize(value):
    return value.capitalize()


def validate_email(value):
    email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return bool(re.match(email_regex, value))


user_schema = schema.Schema({
    'username': schema.And(str, lambda s: len(s.strip()) > 0, error='Username cannot be empty or contain only spaces'),
    'phone_number': schema.Regex(r'^\d{11}$', error='Invalid phone number format. It should be a 10-digit number.'),
    'email': schema.And(schema.Or(str, None), lambda s: validate_email(s) if s is not None else True,
                        error='Invalid email format'),
    'age': schema.And(int, lambda n: 0 <= n <= 120, error='Age must be an integer between 0 and 120'),
    'gender': schema.And(str, lambda s: s.lower() in ['male', 'female', 'other'], error='Invalid gender'),
    'family_members': schema.And(schema.Use(list), [schema.Use(capitalize)]),
    'others': {
        'address': schema.And(str, lambda s: s.strip(), error='Address must be a non-empty string'),
        'blog': schema.Or(None, schema.Regex(r'^https?://\S+$', error='Invalid blog format. It should be a valid URL starting with http:// or https://')),
        'other': schema.Or(str, None)
    }
})


# 2. 使用 schema 进行校验

@ParameterValidator("user_data").schema_validate(user_schema)
def example_function(user_data):
    return user_data
```

## 3.2 关于校验错误的提示

- 可以在 `ParameterValidator`实例化时描述参数规则  `param_rule_des`：

```
@ParameterValidator("age", param_rule_des="Age must be a positive number")
```

- 也可以在 `validate_method` 中描述错误提示 `exception_msg`：

```
@ParameterValidator("name").is_string(exception_msg="Name must be a string")
```

- 如果 `param_rule_des` 和 `exception_msg` 同时为空，则默认提示 `<param> error: "<value> is invalid."`
- 如果 `param_rule_des` 和 `exception_msg` 同时为真，则优先使用 `exception_msg`
  的值，提示 `<param> error: "<value>" is invalid .due to: <exception_msg>`

# 3.3 关于 ParameterValidator 类 和 Validator 类

- `ParameterValidator` 类使用 `Validator` 类中的校验方法；
- `ParameterValidator` 类中定义的校验方法，仅用于编辑器如 `Pycharm` 智能识别可调用的方法，无实际用途；
- 如果要扩展校验方法，需先继承 `Validator` 类添加校验方法，然后再将添加的方法复制粘贴至 `ParameterValidator`
  类，用于编辑器智能识别可调用的方法。

# 四、内置验证器

- `is_string`：检查参数是否为字符串。
- `is_int`：检查参数是否为整数。
- `is_positive`：检查参数是否为正数。
- `is_float`：检查参数是否为浮点数。
- `is_list`：检查参数是否为列表。
- `is_dict`：检查参数是否为字典。
- `is_set`：检查参数是否为集合。
- `is_tuple`：检查参数是否为元组。
- `is_not_none`：检查参数是否不为None。
- `is_not_empty`：检查参数是否不为空（对于字符串、列表、字典、集合等）。
- `is_allowed_value`：检查参数是否在指定的允许值范围内。
- `max_length`：检查参数的长度是否不超过指定的最大值。
- `min_length`：检查参数的长度是否不小于指定的最小值。
- `is_substring`：检查参数是否为指定字符串的子串。
- `is_subset`：检查参数是否为指定集合的子集。
- `is_sublist`：检查参数是否为指定列表的子列表。
- `contains_substring`：检查参数是否包含指定字符串。
- `contains_subset`：检查参数是否包含指定集合。
- `contains_sublist`：检查参数是否包含指定列表。
- `is_file`：检查参数是否为有效的文件。
- `is_dir`：检查参数是否为有效的目录。
- `is_file_suffix`：检查参数是否以指定文件后缀结尾。
- `is_method`：检查参数是否为可调用的方法（函数）。
- `schema_validate`：使用`schema`库校验数据。
- `customize`：自定义校验器。
