# -*- coding=utf-8 -*-
from deepdiff import DeepDiff
from string import Template
from deepdiff.operator import PrefixOrSuffixOperator
import json
import re

# Resp_Diff的单元测试代码


def Resp_Diff(resp, expected, exclude, custom_operators, ignore_order=True):
    print(resp, expected, exclude, custom_operators, ignore_order)
    print(type(resp))
    print(type(expected))
    print(type(exclude))
    if custom_operators == "IgnorePrefixOrSuffix":
        res = DeepDiff(
            resp,
            expected,
            exclude_paths=exclude,
            custom_operators=[CustomPrefixOrSuffixOperator()],
            ignore_order=ignore_order,
        )
    else:
        res = DeepDiff(resp, expected, exclude_paths=exclude, ignore_order=ignore_order)
    return res


def Resp_Diff2(
    resp, expected, exclude, excluderegex, custom_operators, ignore_order=True
):
    print(resp, expected, exclude, excluderegex)
    print(type(resp))
    print(type(expected))
    print(type(exclude))
    if custom_operators == "IgnorePrefixOrSuffix":
        res = DeepDiff(
            resp,
            expected,
            exclude_paths=exclude,
            exclude_regex_paths=excluderegex,
            custom_operators=[CustomPrefixOrSuffixOperator()],
            ignore_order=ignore_order,
        )
    else:
        res = DeepDiff(
            resp,
            expected,
            exclude_paths=exclude,
            exclude_regex_paths=excluderegex,
            ignore_order=ignore_order,
        )
    return res


# 自定义的 PrefixOrSuffixOperator，添加了 normalize_value_for_hashing 方法
class CustomPrefixOrSuffixOperator(PrefixOrSuffixOperator):
    def normalize_value_for_hashing(self, item, *args, **kwargs):
        """
        对字符串或 map（字典）进行归一化处理：
        - 如果 item 是字符串，则去除前后空格并转为小写
        - 如果 item 是 dict，则将内部 key 排序后转为 JSON 字符串
        - 否则，直接返回
        """
        if isinstance(item, str):
            return item.strip().lower()
        elif isinstance(item, dict):
            # 将字典转换为排序后的 JSON 字符串
            return json.dumps(item, sort_keys=True)
        return item


def Format_Json_template(template_str, values):
    """
    通用的JSON模板替换函数，将模板中的变量替换为对应的值

    Args:
        template_str: 包含$var形式变量的JSON模板字符串
        values: 变量值的字典，键名应与模板中的变量名匹配

    Returns:
        替换变量后的有效JSON字符串
    """
    import re
    from datetime import datetime, date, time
    from decimal import Decimal
    import base64

    # JSON序列化器 - 处理特殊类型
    def json_serializer(obj):
        """将Python对象转换为JSON可序列化对象"""
        # 处理日期时间类型
        if isinstance(obj, (datetime, date, time)):
            return obj.isoformat()
        # 处理Decimal
        elif isinstance(obj, Decimal):
            return float(obj)
        # 处理集合类型
        elif isinstance(obj, (set, frozenset)):
            return list(obj)
        # 处理字节类型
        elif isinstance(obj, (bytes, bytearray)):
            return base64.b64encode(obj).decode("ascii")
        # 其他类型尝试转为字符串
        try:
            return str(obj)
        except:
            return None

    # 处理每个变量的替换问题
    processed_template = template_str

    # 第一步：处理模板中带引号的变量，可能需要去除引号
    for key, value in values.items():
        # 查找形如 "$key" 或 "'$key'" 的模式，即被引号包围的变量
        quoted_patterns = [f'"{re.escape("$"+key)}"', f"'{re.escape('$'+key)}'"]

        for pattern in quoted_patterns:
            # 如果变量在引号内，需要处理
            if re.search(pattern, processed_template) and (
                isinstance(value, str)
                or isinstance(value, (dict, list, tuple, set, frozenset))
                or isinstance(value, (datetime, date, time))  # 日期时间类型特殊处理
                or isinstance(value, (bytes, bytearray))  # 二进制数据特殊处理
            ):
                # 移除引号，使用不带引号的变量占位符
                unquoted_placeholder = f"__UNQUOTED_{key}__"
                processed_template = re.sub(
                    pattern, unquoted_placeholder, processed_template
                )

    # 第二步：创建替换字典
    replacements = {}
    for key, value in values.items():
        unquoted_key = f"__UNQUOTED_{key}__"

        # 对于出现在模板中的无引号占位符
        if unquoted_key in processed_template:
            if isinstance(value, (dict, list, tuple, set, frozenset)):
                # 复杂集合类型转为JSON字符串，但不带外层引号
                replacements[unquoted_key] = json.dumps(
                    value, ensure_ascii=False, default=json_serializer
                )
            elif isinstance(value, bool):
                # 布尔值转为小写字符串
                replacements[unquoted_key] = "true" if value else "false"
            elif value is None:
                # None转为null
                replacements[unquoted_key] = "null"
            elif isinstance(value, (datetime, date, time)):
                # 日期时间类型 - 需要加引号，否则JSON无效
                replacements[unquoted_key] = f'"{value.isoformat()}"'
            elif isinstance(value, Decimal):
                # Decimal类型
                replacements[unquoted_key] = str(float(value))
            elif isinstance(value, (bytes, bytearray)):
                # 二进制数据转Base64 - 不添加额外引号
                encoded = base64.b64encode(value).decode("ascii")
                # 直接使用编码后的字符串，不添加引号（因为在引号内的占位符）
                replacements[unquoted_key] = f'"{encoded}"'
            elif isinstance(value, str):
                # 字符串类型，确保空字符串也正确处理
                replacements[unquoted_key] = json.dumps(value, ensure_ascii=False)
            else:
                # 其他类型转为字符串
                replacements[unquoted_key] = f"{str(value)}"

        # 普通变量的处理
        if isinstance(value, (dict, list, tuple, set, frozenset)):
            # 复杂集合类型转为JSON字符串
            replacements["$" + key] = json.dumps(
                value, ensure_ascii=False, default=json_serializer
            )
        elif isinstance(value, bool):
            # 布尔值转为小写字符串
            replacements["$" + key] = "true" if value else "false"
        elif value is None:
            # None转为null
            replacements["$" + key] = "null"
        elif isinstance(value, str):
            # 字符串类型，确保空字符串也正确处理
            replacements["$" + key] = json.dumps(value, ensure_ascii=False)
        elif isinstance(value, (datetime, date, time)):
            # 特殊类型通过serializer处理
            replacements["$" + key] = json.dumps(
                value, ensure_ascii=False, default=json_serializer
            )
        elif isinstance(value, Decimal):
            # Decimal类型 - 与无引号占位符一致使用float转换
            replacements["$" + key] = str(float(value))
        elif isinstance(value, (bytes, bytearray)):
            # 二进制数据转Base64 - 确保只有一层引号
            encoded = base64.b64encode(value).decode("ascii")
            # 添加引号，但不使用json.dumps，防止额外转义
            replacements["$" + key] = f'"{encoded}"'
        else:
            # 其他类型正常转换
            replacements["$" + key] = f"{str(value)}"

    # 第三步：执行替换
    result = processed_template
    print(f"processed_template=${processed_template}")
    print(f"result={result}")

    # 按照占位符长度降序排列，确保先替换较长的占位符
    sorted_placeholders = sorted(replacements.keys(), key=len, reverse=True)
    for placeholder in sorted_placeholders:
        replacement = replacements[placeholder]
        print(f"placeholder={placeholder}, replacement={replacement}")
        result = result.replace(placeholder, replacement)

    # 第四步：尝试验证结果是否为有效JSON
    try:
        print(f"result: {result}")
        json_obj = json.loads(result)
        return json.dumps(json_obj, ensure_ascii=False)
    except json.JSONDecodeError as e:
        print(f"JSON格式化失败: {e}, 结果: {result}")
        return result


if __name__ == "__main__":
    # 测试1：基本模板替换
    template1 = '{"name":"$name", "age":$age, "float":$float, "active":$active, "isNull":$isNull}'
    values1 = {"name": "张三", "age": 30, "float": 1.23, "active": True, "isNull": None}
    result1 = Format_Json_template(template1, values1)
    print("测试1结果:", result1)

    # 测试2：包含嵌套对象
    template2 = '{"user":$user, "created_at":"$date"}'
    values2 = {
        "user": {"id": 1001, "name": "李四", "roles": ["admin", "user"]},
        "date": "2023-01-01",
    }
    result2 = Format_Json_template(template2, values2)
    print("测试2结果:", result2)

    # 测试3：原始测试用例
    template3 = '{"type":5,"objId":10000,"cmd":"fetchUserInfoById","device":"$device","sequence":$index,"info":{"error":0,"return":{"code":0,"message":$message, "result":$users}}, "manager":"UserInfoManager"}'
    values3 = {
        "device": "Mobile",
        "index": 1,
        "message": "",
        "users": {
            "zuoyu_wy1": {
                "userId": "zuoyu_wy1",
                "nickName": "Linda Zimmerman",
                "avatarUrl": "https://www.baidu.com/xxx/1.png",
                "mail": "bhill@gmail.com",
                "phone": "413.342.9317x85236",
                "gender": 0,
                "sign": "11EAOOpwdr",
                "birth": "1993-12-16",
                "ext": "zztKZWCPHZ",
            }
        },
    }
    result3 = Format_Json_template(template3, values3)
    print("测试3结果:", result3)

    # 测试4：使用不同方式定义字典的版本
    template4 = '{"type":5,"objId":10000,"cmd":"fetchUserInfoById","device":"$device","sequence":$index,"info":{"error":0,"return":{"code":0,"message":$message, "result":"$users"}}, "manager":"UserInfoManager"}'
    value4 = {}
    value4["device"] = "Mobile"
    value4["index"] = 1
    value4["message"] = ""
    value4["users"] = {
        "zuoyu_wy1": {
            "userId": "zuoyu_wy1",
            "nickName": "Linda Zimmerman",
            "avatarUrl": "https://www.baidu.com/xxx/1.png",
            "mail": "bhill@gmail.com",
            "phone": "413.342.9317x85236",
            "gender": 0,
            "sign": "11EAOOpwdr",
            "birth": "1993-12-16",
            "ext": "zztKZWCPHZ",
        }
    }
    result4 = Format_Json_template(template4, value4)
    print("测试4结果:", result4)

    # 测试5：测试各种Python数据类型
    from datetime import datetime, date, time
    from decimal import Decimal
    import base64

    template5 = """
    {
        "基本类型": {
            "整数": $int_val,
            "浮点数": $float_val,
            "字符串": "$str_val",
            "空字符串": "$empty_str",
            "特殊字符串": "$special_str",
            "布尔真": $bool_true,
            "布尔假": $bool_false,
            "空值": $null_val
        },
        "引号内复杂类型": {
            "字典": "$dict_val",
            "列表": "$list_val",
            "元组": "$tuple_val",
            "集合": "$set_val"
        },
        "引号外复杂类型": {
            "字典": $dict_val_unquoted,
            "列表": $list_val_unquoted,
            "嵌套": $nested_val
        },
        "特殊类型": {
            "日期时间": "$datetime_val",
            "日期": "$date_val",
            "时间": $time_val,
            "Decimal": $decimal_val,
            "二进制": "$bytes_val"
        },
        "边界情况": {
            "引号中的引号": "$quoted_str",
            "多层嵌套": $multi_nested,
            "零值": $zero_val,
            "空集合": $empty_collection
        }
    }
    """

    values5 = {
        # 基本类型
        "int_val": 42,
        "float_val": 3.14159,
        "str_val": "Hello, World",
        "empty_str": "",
        "special_str": 'Special "quoted" string with \\ backslashes',
        "bool_true": True,
        "bool_false": False,
        "null_val": None,
        # 复杂类型 - 用于引号内外测试
        "dict_val": {"key1": "value1", "key2": 2},
        "dict_val_unquoted": {"key1": "value1", "key2": 2},
        "list_val": [1, 2, 3, "four"],
        "list_val_unquoted": [1, 2, 3, "four"],
        "tuple_val": (1, 2, 3, "four"),
        "set_val": {1, 2, 3, 4},
        "nested_val": {"a": [1, 2, {"b": True}]},
        # 特殊类型
        "datetime_val": datetime(2023, 4, 28, 12, 30, 45),
        "date_val": date(2023, 4, 28),
        "time_val": time(12, 30, 45),
        "decimal_val": Decimal("3.141592653589793238462643383279"),
        "bytes_val": b"Binary data \x00\xff",
        # 边界情况
        "quoted_str": 'String with "quotes" inside',
        "multi_nested": {"a": {"b": {"c": [1, 2, {"d": False}]}}},
        "zero_val": 0,
        "empty_collection": [],
    }

    result5 = Format_Json_template(template5, values5)
    print("\n测试5结果 - 各种Python数据类型:")
    print(result5)

    # 验证所有结果是否为有效的JSON
    for i, result in enumerate([result1, result2, result3, result4, result5], 1):
        try:
            json_obj = json.loads(result)
            print(f"测试{i}生成的结果是有效的JSON")
        except json.JSONDecodeError as e:
            print(f"测试{i}生成的结果不是有效的JSON: {e}")
