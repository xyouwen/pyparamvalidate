import pytest

from atme.demo.validator_v6.validator import Validator


def test_validator_01():
    """
    在 Validator 实例化时，不给 field、rule_des 传值; 在校验方法中，不给 exception_msg 传值
    """
    validator = Validator('Jane')
    assert validator.is_string().is_not_empty()

    with pytest.raises(ValueError) as exc_info:
        validator = Validator(123)
        validator.is_string().is_not_empty()

    assert 'invalid' in str(exc_info.value)
    print(exc_info.value)  # 输出: "123" is invalid.


def test_validator_02():
    """
    在 Validator 实例化时，给 field、rule_des 传值
    """
    validator = Validator('Jane', field='name', rule_des='name must be string from rule des.')
    assert validator.is_string().is_not_empty()

    with pytest.raises(ValueError) as exc_info:
        validator = Validator(123, field='name', rule_des='name must be string from rule des.')
        validator.is_string().is_not_empty()

    assert 'name must be string from rule des.' in str(exc_info.value)
    print(exc_info.value)  # 输出: name error: "123" is invalid. due to: name must be string from rule des.


def test_validator_03():
    """
    在 Validator 实例化时，给 field、rule_des 传值; 在校验方法中，给 exception_msg 传值
    """
    validator = Validator('Jane', field='name', rule_des='name must be string from rule des.')
    assert validator.is_string().is_not_empty()

    with pytest.raises(ValueError) as exc_info:
        validator = Validator(123, field='name', rule_des='name must be string from rule des.')
        validator.is_string('name must be string from method exception msg.').is_not_empty()

    assert 'name must be string from method exception msg.' in str(exc_info.value)
    print(exc_info.value)  # 输出: "123" is invalid due to "name error: name must be string from method exception msg."


def test_validator_04():
    """
    field_name 为空
    """
    validator = Validator('Jane', rule_des='name must be string from rule des.')
    assert validator.is_string().is_not_empty()

    with pytest.raises(ValueError) as exc_info:
        validator = Validator(123, rule_des='name must be string from rule des.')
        validator.is_string('name must be string from method exception msg.').is_not_empty()

    assert 'name must be string from method exception msg.' in str(exc_info.value)
    print(exc_info.value)  # 输出: "123" is invalid due to "name must be string from method exception msg."
