# -*- coding=utf-8 -*-
from deepdiff import DeepDiff
from string import Template
from deepdiff.operator import PrefixOrSuffixOperator
import json
import re

#Resp_Diff的单元测试代码


def Resp_Diff(resp, expected, exclude, custom_operators, ignore_order=True):
    print(resp, expected, exclude, custom_operators, ignore_order)
    print(type(resp))
    print(type(expected))
    print(type(exclude))
    if custom_operators == "IgnorePrefixOrSuffix":
        res = DeepDiff(resp, expected,
                       exclude_paths=exclude,
                       custom_operators=[CustomPrefixOrSuffixOperator()],
                       ignore_order=ignore_order)
    else:
        res = DeepDiff(resp, expected,
                       exclude_paths=exclude,
                       ignore_order=ignore_order)
    return res

def Resp_Diff2(resp, expected, exclude, excluderegex, custom_operators, ignore_order=True):
    print(resp, expected, exclude, excluderegex)
    print(type(resp))
    print(type(expected))
    print(type(exclude))
    if custom_operators == "IgnorePrefixOrSuffix":
        res = DeepDiff(resp, expected,
                       exclude_paths=exclude,
                       exclude_regex_paths=excluderegex,
                       custom_operators=[CustomPrefixOrSuffixOperator()],
                       ignore_order=ignore_order)
    else:
        res = DeepDiff(resp, expected,
                       exclude_paths=exclude,
                       exclude_regex_paths=excluderegex,
                       ignore_order=ignore_order)
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
    # 查找模板中的所有变量及其上下文
    variables = {}
    # 查找带引号的变量，如 "$var"
    quoted_vars = re.findall(r'"(\$[a-zA-Z0-9_]+)"', template_str)
    # 查找不带引号的变量，如 $var
    unquoted_vars = re.findall(r'[^"]\$([a-zA-Z0-9_]+)[^"]', template_str)
    
    for var in quoted_vars:
        name = var[1:]  # 去掉$符号
        variables[name] = "quoted"
        
    for var in unquoted_vars:
        variables[var] = "unquoted"

    print(variables)
    
    # 预处理values字典
    processed_values = {}
    for key, value in values.items():
        # 根据变量在模板中的上下文进行处理
        if key in variables:
            context = variables[key]
            if isinstance(value, str):
                if context == "quoted":
                    # 变量在引号内，值应该是不带引号的纯字符串
                    processed_values[key] = value
                else:
                    # 变量不在引号内，值需要被JSON编码
                    processed_values[key] = json.dumps(value, ensure_ascii=False)
            elif isinstance(value, bool):
                processed_values[key] = "true" if value else "false"
            elif value is None:
                processed_values[key] = "null"
            elif isinstance(value, (dict, list)):
                # 复杂类型需要JSON编码
                processed_values[key] = json.dumps(value, ensure_ascii=False)
            else:
                # 数值类型直接转为字符串
                processed_values[key] = str(value)
        else:
            # 变量不在模板中，采用通用处理方式
            if isinstance(value, str):
                processed_values[key] = json.dumps(value, ensure_ascii=False)
            elif isinstance(value, bool):
                processed_values[key] = "true" if value else "false"
            elif value is None:
                processed_values[key] = "null"
            elif isinstance(value, (dict, list)):
                processed_values[key] = json.dumps(value, ensure_ascii=False)
            else:
                processed_values[key] = str(value)
    
    # 使用Template进行替换
    s = Template(template_str)
    result = s.safe_substitute(processed_values)
    
    # 验证结果是否为有效JSON，如果不是，尝试修复常见问题
    try:
        json_obj = json.loads(result)
        return json.dumps(json_obj, ensure_ascii=False)
    except json.JSONDecodeError:
        # 尝试修复常见问题后再验证
        try:
            # 修复常见的格式问题
            fixed_result = result.replace('""', '\"\"').replace("''", "\'\'")
            json_obj = json.loads(fixed_result)
            return json.dumps(json_obj, ensure_ascii=False)
        except Exception as e:
            print(f"格式化失败: {e}")
            # 如果仍然失败，返回原始结果
            return result


if __name__ == "__main__":
    # 测试1：基本模板替换
    template1 = '{"name":"$name", "age":$age, "float":$float, "active":$active, "isNull":$isNull}'
    values1 = {
        "name": "张三",
        "age": 30,
        "float": 1.23,
        "active": True,
        "isNull": None
    }
    result1 = Format_Json_template(template1, values1)
    print("测试1结果:", result1)
    
    # 测试2：包含嵌套对象
    template2 = '{"user":$user, "created_at":"$date"}'
    values2 = {
        "user": {"id": 1001, "name": "李四", "roles": ["admin", "user"]},
        "date": "2023-01-01"
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
                "ext": "zztKZWCPHZ"
            }
        }
    }
    result3 = Format_Json_template(template3, values3)
    print("测试3结果:", result3)
    
    # 验证所有结果是否为有效的JSON
    for i, result in enumerate([result1, result2, result3], 1):
        try:
            json_obj = json.loads(result)
            print(f"测试{i}生成的结果是有效的JSON")
        except json.JSONDecodeError as e:
            print(f"测试{i}生成的结果不是有效的JSON: {e}")