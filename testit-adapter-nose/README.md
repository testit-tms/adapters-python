# Test IT TMS adapter for Nose

![Test IT](https://raw.githubusercontent.com/testit-tms/adapters-python/master/images/banner.png)

## Getting Started

### Installation

```
pip install testit-adapter-nose
```

## Usage

### Configuration

#### File

1. Create **connection_config.ini** file in the root directory of the project:
    ```
    [testit]
    URL = <url>
    privateToken = <token>
    projectId = <id>
    configurationId = <id>
    testRunId = <optional id>
    testRunName = <optional name>
    adapterMode = <optional>
    certValidation = <optional boolean>
    automaticCreationTestCases = <optional boolean>
    
    # This section are optional. It enables debug mode.
    [debug]
    tmsProxy = {"http": "http://localhost:8888", "https": "http://localhost:8888"}
    ```

2. Fill parameters with your configuration, where:
    * `URL` - location of the TMS instance

    * `privateToken` - API secret key
        1. go to the https://{DOMAIN}/user-profile profile
        2. copy the API secret key

    * `projectId` - ID of project in TMS instance.

        1. create a project
        2. open DevTools -> network
        3. go to the project https://{DOMAIN}/projects/{PROJECT_GLOBAL_ID}/tests
        4. GET-request project, Preview tab, copy id field

    * `configurationId` - ID of configuration in TMS instance.

        1. create a project
        2. open DevTools -> network
        3. go to the project https://{DOMAIN}/projects/{PROJECT_GLOBAL_ID}/tests
        4. GET-request configurations, Preview tab, copy id field

    * `testRunId` - id of the created test run in TMS instance. `testRunId` is optional. If it is not provided, it is
      created automatically.

    * `testRunName` - parameter for specifying the name of test run in TMS instance. `testRunName` is optional. If it is
      not provided, it is created automatically.

    * `adapterMode` - adapter mode. Default value - 0. The adapter supports following modes:

        * 0 - in this mode, the adapter filters tests by test run ID and configuration ID, and sends the results to the
          test run.
        * 1 - in this mode, the adapter sends all results to the test run without filtering.
        * 2 - in this mode, the adapter creates a new test run and sends results to the new test run.
    
    * `certValidation` - it enables/disables certificate validation. Default value - true.

    * `automaticCreationTestCases` - mode of automatic creation test cases. Default value - false. The adapter supports following modes:
        * true - in this mode, the adapter will create a test case linked to the created autotest (not to the updated autotest).
        * false - in this mode, the adapter will not create a test case.

    * `tmsProxy` - it enables debug mode. `tmsProxy` is optional.

#### ENV

You can use environment variables (environment variables take precedence over file variables):

* `TMS_URL` - location of the TMS instance.

* `TMS_PRIVATE_TOKEN` - API secret key.

* `TMS_PROJECT_ID` - ID of a project in TMS instance.

* `TMS_CONFIGURATION_ID` - ID of a configuration in TMS instance.

* `TMS_ADAPTER_MODE` - adapter mode. Default value - 0.

* `TMS_TEST_RUN_ID` - ID of the created test-run in TMS instance. `TMS_TEST_RUN_ID` is optional. If it is not provided,
  it is created automatically.

* `TMS_TEST_RUN_NAME` - name of the new test-run.`TMS_TEST_RUN_NAME` is optional. If it is not provided, it is created
  automatically.

* `TMS_CONFIG_FILE` - name of the configuration file. `TMS_CONFIG_FILE` is optional. If it is not provided, it is used
  default file name.

* `TMS_PROXY` - it enables debug mode. `TMS_PROXY` is optional.

* `TMS_CERT_VALIDATION` - it enables/disables certificate validation. Default value - true.

* `TMS_AUTOMATIC_CREATION_TEST_CASES` - mode of automatic creation test cases. Default value - false.

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

- `testit.workItemIds` - linking an autotest to a test case
- `testit.displayName` - name of the autotest in the TMS system (can be replaced with documentation strings)
- `testit.externalId` - ID of the autotest within the project in the TMS system
- `testit.title` - title in the autotest card
- `testit.description` - description in the autotest card
- `testit.labels` - tags in the work item
- `testit.link` - links in the autotest card
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

