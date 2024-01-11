class DictUtility:

    def trim_dict(self, adict, trim_key=True, trim_value=True):
        """
        去除字典键和值的前后空格。

        :param adict: 要处理的字典
        :param trim_key: 是否去除键前后的空格，默认为 True
        :param trim_value: 是否去除值前后的空格，默认为 True
        :return: 处理后的字典

        示例:
            - nested_dict = {' key1 ': {'nested_key1': ' value1 ', 'nested_key2': {'nested_nested_key': ' nested_value '}}}
            - trimmed_dict = trim_dict(nested_dict, trim_key=True, trim_value=True)
            - print("原始字典：", nested_dict)
            - print("处理后的字典：", trimmed_dict)
        """
        idict = {}
        for k, v in adict.items():
            # 如果 trim_key 为 True 且键是字符串，则去除键前后的空格
            if trim_key and isinstance(k, str):
                k = k.strip()

            # 如果 trim_value 为 True 且值是字符串，则去除值前后的空格
            if trim_value and isinstance(v, str):
                idict[k] = v.strip()
            elif isinstance(v, dict):
                # 如果值是嵌套字典，则递归调用 trim_dict 函数
                idict[k] = self.trim_dict(v, trim_key, trim_value)
            else:
                idict[k] = v
        return idict

    def is_similar_dict(self, dict1, dict2, ignore_keys_whitespace=True):
        """
        比对两个字典，如果 key 完全相同， 且 value 类型相同，则返回为True, 支持多层嵌套比对。

        :param dict1: 第一个要比对的字典
        :param dict2: 第二个要比对的字典
        :param ignore_keys_whitespace: 是否忽略 key 的前后空格，默认为 True
        :return: 若字典相同则返回 True，否则返回 False
        """
        if ignore_keys_whitespace:
            dict1 = self.trim_dict(dict1, trim_key=True, trim_value=False)
            dict2 = self.trim_dict(dict2, trim_key=True, trim_value=False)

        # 比对两个字典的 key 是否完全一致
        keys1 = set(dict1.keys())
        keys2 = set(dict2.keys())

        if keys1 != keys2:
            return False

        # 比对两个字典的 value 数据类型是否一致
        for key in keys1:
            value1 = dict1[key]
            value2 = dict2[key]

            if not isinstance(value1, type(value2)):
                return False

            # 如果 value 是字典类型，则递归调用 compare_dicts 进行比对
            if isinstance(value1, dict):
                if not self.is_similar_dict(value1, value2):
                    return False

        return True
