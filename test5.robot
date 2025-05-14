*** Keywords ***
Some Keyword
    [Arguments]    @{users}    # 接收可变数量的参数作为列表
    FOR    ${user}    IN    @{users}
        Log To Console    ${user}
    END
Some Father Keyword
    [Arguments]    @{users}    # 接收可变数量的参数作为列表
    @{usersAlias}    Set Variable    @{users}    xxx
    Some Keyword    @{usersAlias}

Some Dict Keyword
    [Arguments]    &{dict}
    @{users}    Create List    ${dict}    ${dict}
    Some Keyword    @{users}

*** Test Cases ***
Test Some Keyword
    Some Keyword    user1    user2    user3

Test Some Keyword3
    [Documentation]    Test Some Keyword3
    ...    这个结果 不是 期望的
    @{list}    Create List    user1    user2    user3
    Some Keyword    ${list}
Test Some Keyword4
    [Documentation]    Test Some Keyword4
    ...    这个结果 是 期望的
    @{list}    Create List    user1    user2    user3
    Some Keyword    @{list}
Test Some Keyword5
    [Documentation]    Test Some Keyword5
    ...    这个结果 不是 期望的
    @{list}    Create List    user1    user2    user3
    Some Keyword    users=${list}
Test Some Keyword6
    [Documentation]    Test Some Keyword6
    ...    这个结果 不是 期望的
    @{list}    Create List    user1    user2    user3
    Some Keyword    users=@{list}


Test Some Sub Keyword
    Some Father Keyword    user1    user2    user3

Test Some Dict Keyword
    Some Dict Keyword    name=xxx    age=18    users=user1
