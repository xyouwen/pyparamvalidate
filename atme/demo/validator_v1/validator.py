class Validator:
    def __init__(self, value, field=None, rule_des=None):
        """
        :param value: 待校验的值
        :param field: 校验字段
            - 用于提示具体哪个字段错误
            - 如 'name error: name must be string'
            - error 前面的 `name` 即为 field
        :param rule_des: 校验规则描述
        """
        self.value = value
        self._field = field
        self._rule_des = rule_des

    @staticmethod
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

    def is_string(self, exception_msg=None):
        """
        校验方法：是否为字符串

        :param exception_msg: 校验错误的提示
        :return: self
            - return self 的目的是为了允许链式调用
            - 如： Validator(input).is_string().is_empty()
        """

        if not isinstance(self.value, str):
            raise ValueError(self._error_prompt(self.value, exception_msg, self._rule_des, self._field))

        return self

    def is_not_empty(self, exception_msg=None):
        if not bool(self.value):
            raise ValueError(self._error_prompt(self.value, exception_msg, self._rule_des, self._field))
        return self
