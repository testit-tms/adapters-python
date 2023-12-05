# Test IT TMS adapter for Robot Framework
![Test IT](https://raw.githubusercontent.com/testit-tms/adapters-python/master/images/banner.png)

[![Release
Status](https://img.shields.io/pypi/v/testit-adapter-robotframework?style=plastic)](https://pypi.python.org/pypi/testit-adapter-robotframework)
[![Downloads](https://img.shields.io/pypi/dm/testit-adapter-robotframework?style=plastic)](https://pypi.python.org/pypi/testit-adapter-robotframework)
[![GitHub contributors](https://img.shields.io/github/contributors/testit-tms/adapters-python?style=plastic)](https://github.com/testit-tms/adapters-python)

## Getting Started

### Installation
```
pip install testit-adapter-robotframework
```

## Usage

### Configuration

| Description                                                                                                                                                                                                                                                                                                                                                                            | Property                   | Environment variable              | CLI argument                  |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------|-----------------------------------|-------------------------------|
| Location of the TMS instance                                                                                                                                                                                                                                                                                                                                                           | url                        | TMS_URL                           | tmsUrl                        |
| API secret key [How to getting API secret key?](https://github.com/testit-tms/.github/tree/main/configuration#privatetoken)                                                                                                                                                                                                                                                            | privateToken               | TMS_PRIVATE_TOKEN                 | tmsPrivateToken               |
| ID of project in TMS instance [How to getting project ID?](https://github.com/testit-tms/.github/tree/main/configuration#projectid)                                                                                                                                                                                                                                                    | projectId                  | TMS_PROJECT_ID                    | tmsProjectId                  |
| ID of configuration in TMS instance [How to getting configuration ID?](https://github.com/testit-tms/.github/tree/main/configuration#configurationid)                                                                                                                                                                                                                                  | configurationId            | TMS_CONFIGURATION_ID              | tmsConfigurationId            |
| ID of the created test run in TMS instance.<br/>It's necessary for **adapterMode** 0 or 1                                                                                                                                                                                                                                                                                              | testRunId                  | TMS_TEST_RUN_ID                   | tmsTestRunId                  |
| Parameter for specifying the name of test run in TMS instance (**It's optional**). If it is not provided, it is created automatically                                                                                                                                                                                                                                                  | testRunName                | TMS_TEST_RUN_NAME                 | tmsTestRunName                |
| Adapter mode. Default value - 0. The adapter supports following modes:<br/>0 - in this mode, the adapter filters tests by test run ID and configuration ID, and sends the results to the test run<br/>1 - in this mode, the adapter sends all results to the test run without filtering<br/>2 - in this mode, the adapter creates a new test run and sends results to the new test run | adapterMode                | TMS_ADAPTER_MODE                  | tmsAdapterMode                |
| It enables/disables certificate validation (**It's optional**). Default value - true                                                                                                                                                                                                                                                                                                   | certValidation             | TMS_CERT_VALIDATION               | tmsCertValidation             |
| Mode of automatic creation test cases (**It's optional**). Default value - false. The adapter supports following modes:<br/>true - in this mode, the adapter will create a test case linked to the created autotest (not to the updated autotest)<br/>false - in this mode, the adapter will not create a test case                                                                    | automaticCreationTestCases | TMS_AUTOMATIC_CREATION_TEST_CASES | tmsAutomaticCreationTestCases |
| Url of proxy server (**It's optional**)                                                                                                                                                                                                                                                                                                                                                | tmsProxy                   | TMS_PROXY                         | tmsProxy                      |
| Name of the configuration file If it is not provided, it is used default file name (**It's optional**)                                                                                                                                                                                                                                                                                 | -                          | TMS_CONFIG_FILE                   | tmsConfigFile                 |

#### File

Create **connection_config.ini** file in the root directory of the project:
```
[testit]
URL = URL
privateToken = USER_PRIVATE_TOKEN
projectId = PROJECT_ID
configurationId = CONFIGURATION_ID
testRunId = TEST_RUN_ID
testRunName = TEST_RUN_NAME
adapterMode = ADAPTER_MODE
certValidation = CERT_VALIDATION
automaticCreationTestCases = AUTOMATIC_CREATION_TEST_CASES

# This section are optional. It enables debug mode.
[debug]
tmsProxy = TMS_PROXY
```

#### Examples

Launch with a connection_config.ini file in the root directory of the project:

```
$ robot -v testit TEST_DIRECTORY
```

Launch with command-line parameters (parameters are case-insensitive):

```
$ robot -v testit -v tmsUrl:URL -v tmsPrivateToken:USER_PRIVATE_TOKEN -v tmsProjectId:PROJECT_ID -v tmsConfigurationId:CONFIGURATION_ID -v tmsTestRunId:TEST_RUN_ID -v tmsTestRunName:TEST_RUN_NAME -v tmsAdapterMode:ADAPTER_MODE -v tmsProxy:'{"http":"http://localhost:8888","https":"http://localhost:8888"}' -v tmsConfigFile:<optional file> -v tmsCertValidation:CERT_VALIDATION -v tmsAutomaticCreationTestCases:AUTOMATIC_CREATION_TEST_CASES TEST_DIRECTORY
```

If you want to enable debug mode then see [How to enable debug logging?](https://github.com/testit-tms/adapters-python/tree/main/testit-python-commons)

### Tags

Tags can be used to specify information about autotest. Tags are space sensitive, use only one space between words.

Description of tags:
- `testit.workItemsId` - a method that links autotests with manual tests. Receives the array of manual tests' IDs
- `testit.displayName` - internal autotest name (used in Test IT)
- `testit.externalId` - unique internal autotest ID (used in Test IT)
- `testit.title` - autotest name specified in the autotest card. If not specified, the name from the displayName method is used
- `testit.description` - autotest description specified in the autotest card
- `testit.links` - links listed in the autotest card
- `testit.labels` - tags listed in the autotest card
- `testit.nameSpace` - directory in the TMS system (default - file's name of test)
- `testit.className` - subdirectory in the TMS system (default - class's name of test)

Description of methods:
- `Add Links` - links in the autotest result
- `Add Link` - add one link in the autotest result
- `Add Attachments` - uploading files in the autotest result
- `Add Attachment` - upload given content with given filename in the autotest result
- `Add Message` - information about autotest in the autotest result

### Parallel execution

You can also run your test in parallel with [Pabot](https://pabot.org/).

```
$ pabot --pabotlib -v testit <test directory>
```

All other settings are the same as for standard execution.

### Examples

```robotframework
*** Settings ***
Documentation      Main Suite with examples
Library            testit_adapter_robotframework.TMSLibrary

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

Simple Test with Title or Description or DisplayName with simple formatting
    [Documentation]  Tags are space sensitive, use only one space between words
    [Tags]   testit.displayName:This works     testit.title:'This also works'
    ...    testit.description:"This works too"
    [Setup]  Setup
    Do Something
    Do Another Thing
    Log  I'am a step
    [Teardown]  Teardown

Test With All Params
    [Documentation]  It's better to use this kind of formatting for different data types in tags
    [Tags]   testit.externalID:123    testit.title:${{'Different title'}}   testit.displayName:${{'Different name'}}
    ...     testit.description:${{'Different description'}}    testit.workitemsID:${{[123, '456']}}
    ...     testit.links:${{{'url': 'http://google.com', 'type':'Issue'}}}   testit.labels:${{['smoke', 'lol']}}
    [Setup]  Setup
    Log    Something
    Log    Another
    [Teardown]  Teardown

Test With Add Link
    [Setup]  Setup
    Do Something
    Do Another Thing
    Add Links    @{LINKS}
#    You can also add one link (default type is Defect)
    Add Link    http://ya.ru
    Add Link    http://ya.ru    type=Issue
    Add Link    ${SIMPLE_LINK}[url]
    [Teardown]  Teardown

Test With Add Attachment
    [Setup]  Setup
    Do Something
    Do Another Thing
    ${V}   Get Variables
    Add Attachment    '${V}'    file.txt
    Add Attachments    images/banner.png     images/icon.png
    [Teardown]  Teardown

Test With Add Message
    [Setup]  Setup
    Do Something
    Do Another Thing
    Add Message    Wow, it's my error message!
    Fail
    [Teardown]  Teardown
```

# Contributing

You can help to develop the project. Any contributions are **greatly appreciated**.

* If you have suggestions for adding or removing projects, feel free to [open an issue](https://github.com/testit-tms/adapters-python/issues/new) to discuss it, or directly create a pull request after you edit the *README.md* file with necessary changes.
* Please make sure you check your spelling and grammar.
* Create individual PR for each suggestion.
* Please also read through the [Code Of Conduct](https://github.com/testit-tms/adapters-python/blob/master/CODE_OF_CONDUCT.md) before posting your first idea as well.

# License

Distributed under the Apache-2.0 License. See [LICENSE](https://github.com/testit-tms/adapters-python/blob/master/LICENSE.md) for more information.

