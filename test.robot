
*** Keywords ***
Create Nested Dict With Variables
    [Arguments]    ${outer_key}    ${inner_key}    ${value}
    &{inner_dict}    Create Dictionary    ${inner_key}=${value}
    &{outer_dict}    Create Dictionary    ${outer_key}=${inner_dict}
    RETURN    ${outer_dict}



*** Keywords ***
Create Nested Dict With Dict Syntax
    [Arguments]    ${outer_key}    ${inner_key}    ${value}
    &{inner_dict}    Create Dictionary    ${inner_key}=${value}
    &{outer_dict}    Create Dictionary    ${outer_key}=&{inner_dict}
    RETURN    ${outer_dict}



*** Test Cases ***
Test Dynamic Nested Dictionary
    ${key1}=    Set Variable    outer_key
    ${key2}=    Set Variable    inner_key
    ${value2}=    Set Variable    some_value
    ${result}=    Create Nested Dict With Variables    ${key1}    ${key2}    ${value2}
    # 结果: {'outer_key': {'inner_key': 'some_value'}}
