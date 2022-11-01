# Test IT TMS adapter for Behave

![Test IT](https://raw.githubusercontent.com/testit-tms/adapters-python/master/images/banner.png)

## Getting Started

### Installation

```
pip install testit-adapter-behave
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
        3. go to the project https://{DOMAIN}/projects/20/tests
        4. GET-request project, Preview tab, copy id field

    * `configurationId` - ID of configuration in TMS instance.

        1. create a project
        2. open DevTools -> network
        3. go to the project https://{DOMAIN}/projects/20/tests
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

#### Command line

You also can CLI variables (CLI variables take precedence over environment variables):

* `tmsUrl` - location of the TMS instance.

* `tmsPrivateToken` - API secret key.

* `tmsProjectId` - ID of a project in TMS instance.

* `tmsConfigurationId` - ID of a configuration in TMS instance.

* `tmsAdapterMode` - adapter mode. Default value - 0.

* `tmsTestRunId` - ID of the created test-run in TMS instance. `tmsTestRunId` is optional. If it is not provided, it is
  created automatically.

* `tmsTestRunName` - name of the new test-run.`tmsTestRunName` is optional. If it is not provided, it is created
  automatically.

* `tmsConfigFile` - name of the configuration file. `tmsConfigFile` is optional. If it is not provided, it is used
  default file name.

* `tmsProxy` - it enables debug mode. `tmsProxy` is optional.

#### Examples

Launch with a connection_config.ini file in the root directory of the project:

```
$ behave -f testit_adapter_behave.formatter:AdapterFormatter
```

Launch with command-line parameters:

```
$ behave -f testit_adapter_behave.formatter:AdapterFormatter -D tmsUrl=<url> -D tmsPrivateToken=<token> -D
tmsProjectId=<id> -D tmsConfigurationId=<id> -D tmsTestRunId=<optional id> -D tmsAdapterMode=<optional> -D
tmsTestRunName=<optional name> -D tmsProxy='{"http":"http://localhost:8888","https":"http://localhost:8888"}'
```

### Tags

Use tags to specify information about autotest.

Description of tags:

- `WorkItemIds` - linking an autotest to a test case.
- `DisplayName` - name of the autotest in Test IT.
- `ExternalId` - ID of the autotest within the project in Test IT.
- `Title` - title in the autotest card.
- `Description` - description in the autotest card.
- `Labels` - tags in the autotest card.
- `Links` - links in the autotest card.

Description of methods:

- `testit.addLinks` - links in the autotest result
- `testit.addAttachments` - uploading files in the autotest result
- `testit.addMessage` - information about autotest in the autotest result
- `testit.step` - usage in the "with" construct to designation a step in the body of the test

### Examples

#### Simple Test

```py
import testit
from behave import given
from behave import then
from behave import when


@given("I authorize on the portal")
def authorization(context):
    with testit.step("I set login"):
        pass
    with testit.step("I set password"):
        pass


@when("I create a project")
def create_project(context):
    pass


@when("I open the project")
def enter_project(context):
    pass


@when("I create a section")
def create_section(context):
    testit.addLinks(
        title='component_dump.dmp',
        type=testit.LinkType.RELATED,
        url='https://dumps.example.com/module/some_module_dump',
        description='Description'
    )


@then("I create a test case")
def create_test_case(context):
    testit.addAttachments('pictures/picture.jpg')
```

```buildoutcfg
Feature: Sample

  Background:
    Given I authorize on the portal

  @ExternalId=failed_with_all_annotations
  @DisplayName=Failed_test_with_all_annotations
  @WorkItemIds=123
  @Title=Title_in_the_autotest_card
  @Description=Test_with_all_annotations
  @Labels=Tag1,Tag2
  @Links={"url":"https://dumps.example.com/module/repository","title":"Repository","description":"Example_of_repository","type":"Repository"}
  Scenario: Create new project, section and test case
    When I create a project
    And I open the project
    And I create a section
    Then I create a test case
```

#### Parameterized test

```py
from behave import when
from behave import then


@when("Summing {left:d}+{right:d}")
def step_impl(context, left, right):
    context.sum = left + right


@then("Result is {result:d}")
def step_impl(context, result):
    assert context.sum == result

```

```buildoutcfg
Feature: Rule
  Tests that use Rule

  Scenario Outline: Summing
    When Summing <left>+<right>
    Then Result is <result>

    Examples:
      | left | right | result |
      | 1    | 1     | 3      |
      | 9    | 9     | 18     |
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

