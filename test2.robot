*** Keywords ***
Is String Type
    [Arguments]    ${value}
    [Documentation]    Check if the value is a string type
    ${is_string}    Evaluate    isinstance($value, str)
    RETURN    ${is_string}

*** Test Cases ***

Test Is String Type
    ${result}=    Is String Type    Hello, World!
    Should Be True    ${result}

Test Is Not String Type
    ${result}=    Is String Type    ${42}

Test Is Not String Type 2
    &{dict}    Create Dictionary    key=value
    ${result}=    Is String Type    ${dict}
