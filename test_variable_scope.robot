*** Settings ***
Documentation     Example test cases using the data-driven testing approach.
...
...               The _data-driven_ style works well when you need to repeat
...               the same workflow multiple times.
...
...               Tests use ``Calculate`` keyword created in this file, that in
...               turn uses keywords in ``CalculatorLibrary.py``. An exception
...               is the last test that has a custom _template keyword_.
...
...               Notice that one of these tests fails on purpose to show how
...               failures look like.
Test Template     Calculate
Library           CalculatorLibrary.py

*** Test Cases ***    Expression    Expected
Failing               1 + 1         2

*** Keywords ***
Test variable scope
    [Arguments]    ${suite_var}    ${global_var}    ${test_var}
    ${s}    Set Variable    value
    ${g}    Convert To String    ${EMPTY}
    ${t}    Create Dictionary
    Set Suite Variable    ${s}    ${suite_var}    # 提升变量作用域
    Set Global Variable    ${g}    ${global_var}    # 提升变量作用域
    Set Test Variable    ${t}    ${test_var}    # 提升变量作用域
    Log    "${s}:${g}:${t}"

*** Keywords ***
Calculate
    [Arguments]    ${expression}    ${expected}
    # IF    ${FALSE}
    #     ${s}    Set Variable    ${EMPTY}
    #     ${g}    Set Variable    ${EMPTY}
    #     ${t}    Create Dictionary
    # END
    
    [Setup]    Test variable scope    "suite_var_value"    "suite_var_value"    {key: value}
    
    # robotcode: ignore-undefined-variable
    Log    "2:${s}:${g}:${t}"

