# Test IT TMS adapter for Nose

![Test IT](https://raw.githubusercontent.com/testit-tms/adapters-python/master/images/banner.png)

[![Release
Status](https://img.shields.io/pypi/v/testit-adapter-nose?style=plastic)](https://pypi.python.org/pypi/testit-adapter-nose)
[![Downloads](https://img.shields.io/pypi/dm/testit-adapter-nose?style=plastic)](https://pypi.python.org/pypi/testit-adapter-nose)
[![GitHub contributors](https://img.shields.io/github/contributors/testit-tms/adapters-python?style=plastic)](https://github.com/testit-tms/adapters-python)

## Getting Started

### Installation

```
pip install testit-adapter-nose
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
$ nose2 --testit
```

If you want to enable debug mode then
see [How to enable debug logging?](https://github.com/testit-tms/adapters-python/tree/main/testit-python-commons)

### Decorators

Decorators can be used to specify information about autotest.

Description of decorators:

- `testit.workItemIds` - a method that links autotests with manual tests. Receives the array of manual tests' IDs
- `testit.displayName` - internal autotest name (used in Test IT)
- `testit.externalId` - unique internal autotest ID (used in Test IT)
- `testit.title` - autotest name specified in the autotest card. If not specified, the name from the displayName method is used
- `testit.description` - autotest description specified in the autotest card
- `testit.labels` - tags listed in the autotest card
- `testit.link` - links listed in the autotest card
- `testit.step` - the designation of the step called in the body of the test or other step
- `testit.nameSpace` - directory in the TMS system (default - file's name of test)
- `testit.className` - subdirectory in the TMS system (default - class's name of test)

All decorators support the use of parameterization attributes

Description of methods:

- `testit.addLinks` - links in the autotest result
- `testit.addAttachments` - uploading files in the autotest result
- `testit.addMessage` - information about autotest in the autotest result
- `testit.step` - usage in the "with" construct to designation a step in the body of the test

### Examples

#### Simple test

```py
import pytest
import testit


# Test with a minimal set of decorators
@testit.externalId('Simple_autotest2')
def test_2():
    """Simple autotest 2"""
    assert oneStep()
    assert twoStep()


@testit.step
def oneStep():
    assert oneOneStep()
    assert oneTwoStep()
    return True


@testit.step
def twoStep():
    return True


@testit.step('step 1.1', 'description')
def oneOneStep():
    return True


@testit.step('step 2')
def oneTwoStep():
    return True
```

#### Parameterized test

```py
# Parameterized test with a full set of decorators
from os.path import join, dirname

import testit
from nose2.tools import params

@params(1, 2, 3)
@testit.workItemIds(627)
@testit.externalId('param {num}')
@testit.displayName('param {num}')
@testit.title('Test with params')
@testit.description('E2E_autotest')
@testit.labels('parameters', 'test')
@testit.links(url='https://dumps.example.com/module/JCP-777')
@testit.links(url='https://dumps.example.com/module/JCP-777',
              title='JCP-777',
              type=testit.LinkType.RELATED,
              description='Description of JCP-777')
def test_nums(num):
    assert num < 4
```

# Contributing

You can help to develop the project. Any contributions are **greatly appreciated**.

* If you have suggestions for adding or removing projects, feel free
  to [open an issue](https://github.com/testit-tms/adapters-python/issues/new) to discuss it, or directly create a pull
  request after you edit the *README.md* file with necessary changes.
* Please make sure you check your spelling and grammar.
* Create individual PR for each suggestion.
* Please also read through
  the [Code Of Conduct](https://github.com/testit-tms/adapters-python/blob/master/CODE_OF_CONDUCT.md) before posting
  your first idea as well.

# License

Distributed under the Apache-2.0 License.
See [LICENSE](https://github.com/testit-tms/adapters-python/blob/master/LICENSE.md) for more information.

