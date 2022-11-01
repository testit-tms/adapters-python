*** Settings ***
Documentation      This suite only for parallel execution display
Library            TMSLibrary

*** Variables ***
&{SIMPLE_LINK}             url=http://google.com
&{FULL_LINK}               url=http://google.co.uk   title=Google     type=Related   description=just a link

@{LINKS}               ${SIMPLE_LINK}   ${FULL_LINK}


*** Test Cases ***
Simple Test
    [Setup]  Setup
    Do Something
    Do Another Thing
    Log  I'am a step
    [Teardown]  Teardown

Simple Test with link as variable
    [Tags]   testit.links:${SIMPLE_LINK}
    [Setup]  Setup
    Do Something
    Do Another Thing
    Log  I'am a step
    [Teardown]  Teardown

Simple Test with link as dict
    [Tags]   testit.links:${{{'url': 'http://google.com', 'type':'Issue'}}}
    [Setup]  Setup
    Do Something
    Do Another Thing
    Log  I'am a step
    [Teardown]  Teardown

Simple Test with WorkitemId as string
    [Tags]   testit.workitemsID:123
    [Setup]  Setup
    Do Something
    Do Another Thing
    Log  I'am a step
    [Teardown]  Teardown

Simple Test with WorkitemId as list
    [Tags]   testit.workitemsID:${{[123, '456']}}
    [Setup]  Setup
    Do Something
    Do Another Thing
    Log  I'am a step
    [Teardown]  Teardown

Test With All Params
    [Tags]   testit.title:${{'Different title'}}   testit.displayName:${{'Test workitems'}}
    ...     testit.description:${{'Different description'}}    testit.workitemsID:'164725'
    ...     testit.links:${{{'url': 'http://google.com', 'type':'Issue'}}}   testit.labels:${{['smoke', 'lol']}}
    [Setup]  Setup
    Log    Something
    Log    Another
    [Teardown]  Teardown

*** Keywords ***
Do Something
    Log Variables
    Log  something

Template
    [Arguments]   ${LOGIN}   ${PASSWORD}=123
    Log  ${LOGIN}
    Log  ${PASSWORD}

Do Another Thing
    Do Something
    Log  Another

Setup
    Log  I'm a setup
    Log  Still a setup

Teardown
    Setup
    Log  I'm a teardown
    Log  End
