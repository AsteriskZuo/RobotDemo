*** Settings ***
Library    wayangutils.py
Resource    test2.robot
Library    json

*** Keywords ***
Test Replace Json String Template
    [Arguments]    ${expectedstr}    ${expectedarg}
    ${result}    Format Json Template    ${expectedstr}    ${expectedarg}
    RETURN    ${result}

Is String Type
    [Arguments]    ${value}
    [Documentation]    Check if the value is a string type
    ${is_string}    Evaluate    isinstance($value, str)
    RETURN    ${is_string}

Is Dict Type
    [Arguments]    ${value}
    [Documentation]    Check if the value is a dict type
    ${is_dict}    Evaluate    isinstance($value, dict)
    RETURN    ${is_dict}

*** Test Cases ***
Test Replace Json String Template
    ${expectedstr}    Set Variable   {"type":5,"objId":10000,"cmd":"fetchUserInfoById","device":"$device","sequence":"$index","info":{"error":0,"return":{"code":0,"message":"$message", "result":"$users"}}, "manager":"UserInfoManager"}
    &{user_info}    Create Dictionary    userId=zuoyu_wy1    nickName=Linda Zimmerman    avatarUrl=xxx    mail=bhill@gmail.com    phone=413.342.9317x85236    gender=${0}    sign=11EAOOpwdr    birth=1993-12-16    ext=zztKZWCPHZ
    &{users_dict}    Create Dictionary    zuoyu_wy1=${user_info}
    &{expectedarg}    Create Dictionary    device=Mobile    index=${1}    message=""    users=${users_dict}
    ${result}    Test Replace Json String Template    ${expectedstr}    ${expectedarg}

    ${test1}    Create Dictionary    key=value
    ${test1_json}    Evaluate    json.dumps(${test1})    json
    Log    ${test1_json}
    ${test1_json_str}    Convert To String    ${test1_json}
    Log    ${test1_json_str}
    ${result_json}    Evaluate    json.loads('${test1_json_str}')    json
    # ${result_json}    Evaluate    json.loads('["foo", {"bar":["baz", null, 1.0, 2]}]')    json
    Log    ${expectedarg}
    Log    ${expectedstr}
    Log    ${result}
    Log    ${result_json}
    ${result_type}=    Is String Type    ${result}
    Log    ${result_type}
    ${result_dict_type}=    Is Dict Type    ${users_dict}
    Log    ${result_dict_type}

