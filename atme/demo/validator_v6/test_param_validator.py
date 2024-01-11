import pytest

from atme.demo.validator_v6.param_validator import ParameterValidator


def test_is_string_validator_passing_01():
    """
    校验一个参数
    """

    @ParameterValidator("param").is_string(exception_msg='param must be string')
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
    校验多个参数
    """

    @ParameterValidator("param2").is_string().is_not_empty()
    @ParameterValidator("param1").is_string().is_not_empty()
    def example_function(param1, param2):
        print(param1, param2)
        return param1, param2

    assert example_function("test1", "test2") == ("test1", "test2")

    with pytest.raises(ValueError) as exc_info:
        example_function(123, 123)

    print(exc_info.value)
    assert "invalid" in str(exc_info.value)
