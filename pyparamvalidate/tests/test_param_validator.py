import os

import pytest

from pyparamvalidate.core.param_validator import ParameterValidator


def test_is_string_validator_passing_01():
    """
    不描述参数规则
    """

    @ParameterValidator("param").is_string()
    def example_function(param):
        print(param)
        return param

    assert example_function(param="test") == "test"

    with pytest.raises(ValueError) as exc_info:
        example_function(param=123)

    print(exc_info.value)
    assert "invalid" in str(exc_info.value)


def test_is_string_validator_passing_02():
    """
    在校验器中描述参数规则
    """

    @ParameterValidator("param").is_string("Value must be a string")
    def example_function(param):
        print(param)
        return param

    assert example_function(param="test") == "test"

    with pytest.raises(ValueError) as exc_info:
        example_function(param=123)

    print(exc_info.value)
    assert "Value must be a string" in str(exc_info.value)


def test_is_string_validator_passing_03():
    """
    在 ParameterValidator 实例化时描述参数规则
    """

    @ParameterValidator("param", param_rule_des="Value must be a string").is_string()
    def example_function(param):
        print(param)
        return param

    assert example_function(param="test") == "test"

    with pytest.raises(ValueError) as exc_info:
        example_function(param=123)

    print(exc_info.value)
    assert "Value must be a string" in str(exc_info.value)


def test_is_int_validator():
    @ParameterValidator("param").is_int("Value must be an integer")
    def example_function(param):
        return param

    assert example_function(param=123) == 123

    with pytest.raises(ValueError) as exc_info:
        example_function(param="test")
    assert "Value must be an integer" in str(exc_info.value)


def test_is_positive_validator():
    @ParameterValidator("param").is_positive("Value must be positive")
    def example_function(param):
        return param

    assert example_function(param=5) == 5

    with pytest.raises(ValueError) as exc_info:
        example_function(param=-3)
    assert "Value must be positive" in str(exc_info.value)


def test_is_float_validator():
    @ParameterValidator("param").is_float("Value must be a float")
    def example_function(param):
        return param

    assert example_function(param=3.14) == 3.14

    with pytest.raises(ValueError) as exc_info:
        example_function(param="test")
    assert "Value must be a float" in str(exc_info.value)


def test_is_list_validator():
    @ParameterValidator("param").is_list("Value must be a list")
    def example_function(param):
        return param

    assert example_function(param=[1, 2, 3]) == [1, 2, 3]

    with pytest.raises(ValueError) as exc_info:
        example_function(param="test")
    assert "Value must be a list" in str(exc_info.value)


def test_is_dict_validator():
    @ParameterValidator("param").is_dict("Value must be a dictionary")
    def example_function(param):
        return param

    assert example_function(param={"key": "value"}) == {"key": "value"}

    with pytest.raises(ValueError) as exc_info:
        example_function(param=[1, 2, 3])
    assert "Value must be a dictionary" in str(exc_info.value)


def test_is_set_validator():
    @ParameterValidator("param").is_set("Value must be a set")
    def example_function(param):
        return param

    assert example_function(param={1, 2, 3}) == {1, 2, 3}

    with pytest.raises(ValueError) as exc_info:
        example_function(param="test")
    assert "Value must be a set" in str(exc_info.value)


def test_is_tuple_validator():
    @ParameterValidator("param").is_tuple("Value must be a tuple")
    def example_function(param):
        return param

    assert example_function(param=(1, 2, 3)) == (1, 2, 3)

    with pytest.raises(ValueError) as exc_info:
        example_function(param="test")
    assert "Value must be a tuple" in str(exc_info.value)


def test_is_not_none_validator():
    @ParameterValidator("param").is_not_none("Value must not be None")
    def example_function(param):
        return param

    assert example_function(param="test") == "test"

    with pytest.raises(ValueError) as exc_info:
        example_function(param=None)
    assert "Value must not be None" in str(exc_info.value)


def test_is_not_empty_validator():
    @ParameterValidator("param").is_not_empty("Value must not be empty")
    def example_function(param):
        return param

    assert example_function(param="test") == "test"

    with pytest.raises(ValueError) as exc_info:
        example_function(param="")
    assert "Value must not be empty" in str(exc_info.value)


def test_max_length_validator():
    @ParameterValidator("param").max_length(5, "Value must have max length of 5")
    def example_function(param):
        return param

    assert example_function(param="test") == "test"

    with pytest.raises(ValueError) as exc_info:
        example_function(param="toolongtext")
    assert "Value must have max length of 5" in str(exc_info.value)


def test_min_length_validator():
    @ParameterValidator("param").min_length(5, "Value must have min length of 5")
    def example_function(param):
        return param

    assert example_function(param="toolongtext") == "toolongtext"

    with pytest.raises(ValueError) as exc_info:
        example_function(param="test")
    assert "Value must have min length of 5" in str(exc_info.value)


def test_is_substring_validator():
    @ParameterValidator("param").is_substring("superstring", "Value must be a substring")
    def example_function(param):
        return param

    assert example_function(param="string") == "string"

    with pytest.raises(ValueError) as exc_info:
        example_function(param="test")
    assert "Value must be a substring" in str(exc_info.value)


def test_is_subset_validator():
    @ParameterValidator("param").is_subset({1, 2, 3}, "Value must be a subset")
    def example_function(param):
        return param

    assert example_function(param={1, 2}) == {1, 2}

    with pytest.raises(ValueError) as exc_info:
        example_function(param={4, 5})
    assert "Value must be a subset" in str(exc_info.value)


def test_is_sublist_validator():
    @ParameterValidator("param").is_sublist([1, 2, 3], "Value must be a sub-list")
    def example_function(param):
        return param

    assert example_function(param=[1, 2]) == [1, 2]

    with pytest.raises(ValueError) as exc_info:
        example_function(param=[1, 2, 3, 4, 5])
    assert "Value must be a sub-list" in str(exc_info.value)


def test_contains_substring_validator():
    @ParameterValidator("param").contains_substring("substring", "Value must contain substring")
    def example_function(param):
        return param

    assert example_function(param="This is a substring") == "This is a substring"

    with pytest.raises(ValueError) as exc_info:
        example_function(param="test")
    assert "Value must contain substring" in str(exc_info.value)


def test_contains_subset_validator():
    @ParameterValidator("param").contains_subset({1, 2, 3}, "Value must contain a subset")
    def example_function(param):
        return param

    assert example_function(param={1, 2, 3, 4, 5}) == {1, 2, 3, 4, 5}

    with pytest.raises(ValueError) as exc_info:
        example_function(param={4, 5})
    assert "Value must contain a subset" in str(exc_info.value)


def test_contains_sublist_validator():
    @ParameterValidator("param").contains_sublist([1, 2, 3], "Value must contain a sub-list")
    def example_function(param):
        return param

    assert example_function(param=[1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]

    with pytest.raises(ValueError) as exc_info:
        example_function(param=[4, 5])
    assert "Value must contain a sub-list" in str(exc_info.value)


def test_is_file_suffix_validator():
    @ParameterValidator("param").is_file_suffix(".txt", "Value must have .txt suffix")
    def example_function(param):
        return param

    assert example_function(param="example.txt") == "example.txt"

    with pytest.raises(ValueError) as exc_info:
        example_function(param="example.jpg")
    assert "Value must have .txt suffix" in str(exc_info.value)


def test_is_file_validator():
    @ParameterValidator("param").is_file("Value must be a valid file path")
    def example_function(param):
        return param

    assert example_function(param=__file__) == __file__

    with pytest.raises(ValueError) as exc_info:
        example_function(param="/nonexistent/file.txt")
    assert "Value must be a valid file path" in str(exc_info.value)


def test_is_dir_validator():
    @ParameterValidator("param").is_dir("Value must be a valid directory path")
    def example_function(param):
        return param

    assert example_function(param=os.path.dirname(__file__)) == os.path.dirname(__file__)

    with pytest.raises(ValueError) as exc_info:
        example_function(param="/nonexistent/directory")
    assert "Value must be a valid directory path" in str(exc_info.value)


def test_is_method_validator():
    def method():
        ...

    @ParameterValidator("param").is_method("Value must be a callable method")
    def example_function(param):
        return param

    assert example_function(param=method)

    with pytest.raises(ValueError) as exc_info:
        example_function(param="not a method")
    assert "Value must be a callable method" in str(exc_info.value)


def test_complex_validator():
    @ParameterValidator("description").is_string().is_not_empty()
    @ParameterValidator("gender", "Invalid").is_allowed_value(["male", "female"],
                                                              "Gender must be either 'male' or 'female'")
    @ParameterValidator("age", param_rule_des="Age must be a positive number").is_int().is_positive()
    @ParameterValidator("name").is_string("Name must be a string").is_not_empty()
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
    @ParameterValidator("param").customize(even_number_validator, 10, exception_msg="Value must be an even number and greater than 10")
    def example_function(param):
        return param

    assert example_function(param=12) == 12

    with pytest.raises(ValueError) as exc_info:
        example_function(param=5)
    assert "Value must be an even number" in str(exc_info.value)
