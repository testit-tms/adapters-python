# Test IT TMS adapter for Pytest
![Test IT](https://raw.githubusercontent.com/testit-tms/adapters-python/master/images/banner.png)

## Getting Started

### Installation
```
pip install testit-adapter-pytest
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
    
    * `testRunId` - id of the created test run in TMS instance. `testRunId` is optional. If it is not provided, it is created automatically.  
      
    * `testRunName` - parameter for specifying the name of test run in TMS instance. `testRunName` is optional. If it is not provided, it is created automatically.   
    
    * `adapterMode` - adapter mode. Default value - 0. The adapter supports following modes:  
        
        * 0 - in this mode, the adapter filters tests by test run ID and configuration ID, and sends the results to the test run.
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
  
* `TMS_TEST_RUN_ID` - ID of the created test-run in TMS instance. `TMS_TEST_RUN_ID` is optional. If it is not provided, it is created automatically.
  
* `TMS_TEST_RUN_NAME` - name of the new test-run.`TMS_TEST_RUN_NAME` is optional. If it is not provided, it is created automatically.
  
* `TMS_CONFIG_FILE` - name of the configuration file. `TMS_CONFIG_FILE` is optional. If it is not provided, it is used default file name.

* `TMS_PROXY` - it enables debug mode. `TMS_PROXY` is optional.

#### Command line

You also can CLI variables (CLI variables take precedence over environment variables):

* `tmsUrl` - location of the TMS instance.
  
* `tmsPrivateToken` - API secret key.
  
* `tmsProjectId` - ID of a project in TMS instance.
  
* `tmsConfigurationId` - ID of a configuration in TMS instance.

* `tmsAdapterMode` - adapter mode. Default value - 0.

* `tmsTestRunId` - ID of the created test-run in TMS instance. `tmsTestRunId` is optional. If it is not provided, it is created automatically.
  
* `tmsTestRunName` - name of the new test-run.`tmsTestRunName` is optional. If it is not provided, it is created automatically.
  
* `tmsConfigFile` - name of the configuration file. `tmsConfigFile` is optional. If it is not provided, it is used default file name.

* `tmsProxy` - it enables debug mode. `tmsProxy` is optional.

#### Examples

Launch with a connection_config.ini file in the root directory of the project:

```
$ pytest --testit
```

Launch with command-line parameters:

```
$ pytest --testit --tmsUrl=<url> --tmsPrivateToken=<token> --tmsProjectId=<id> --tmsConfigurationId=<id> --tmsTestRunId=<optional id> --tmsTestRunName=<optional name> --tmsProxy='{"http":"http://localhost:8888","https":"http://localhost:8888"}'
```

### Decorators

Decorators can be used to specify information about autotest.

Description of decorators:
- `testit.workItemIds` - linking an autotest to a test case
- `testit.displayName` - name of the autotest in the Test IT system (can be replaced with documentation strings)
- `testit.externalId` - ID of the autotest within the project in the Test IT System
- `testit.title` - title in the autotest card
- `testit.description` - description in the autotest card
- `testit.labels` - tags in the work item
- `testit.link` - links in the autotest card
- `testit.step` - the designation of the step called in the body of the test or other step

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

@testit.externalId('Simple_test_skip')
@testit.displayName('Simple test skip')
@testit.links(url='https://dumps.example.com/module/JCP-777')
@testit.links(
    url='https://dumps.example.com/module/JCP-777',
    type=testit.LinkType.RELATED,
    title='JCP-777',
    description='Description of JCP-777')
@pytest.mark.skipif(True, reason='Because i can')
def test_skip():
    assert True
```

#### Parameterized test
```py
# Parameterized test with a full set of decorators
from os.path import join, dirname

import pytest
import testit

@testit.workItemIds(627)
@testit.displayName('Simple autotest 1 - {name}')
@testit.externalId('Simple_autotest1_{name}')
@testit.title('Authorization')
@testit.description('E2E_autotest')
@testit.labels('{labels}')
@testit.links(links=[
    {'url': '{url}', 'type': '{link_type}', 'title': '{link_title}', 'description': '{link_desc}'},
    {'url': '{url}', 'type': '{link_type}', 'title': '{link_title}', 'description': '{link_desc}'}
])
@pytest.mark.parametrize('name, labels, url, link_type, link_title, link_desc', [
    ('param 1', ['E2E', 'test'], 'https://dumps.example.com/module/JCP-777', testit.LinkType.DEFECT, 'JCP-777', 'Desc of JCP-777'),
    ('param 2', (), 'https://dumps.example.com/module/docs', testit.LinkType.RELATED, 'Documentation', 'Desc of JCP-777'),
    ('param 3', ('E2E', 'test'), 'https://dumps.example.com/module/projects', testit.LinkType.REQUIREMENT, 'Projects', 'Desc of Projects'),
    ('param 4', {'E2E', 'test'}, 'https://dumps.example.com/module/', testit.LinkType.BLOCKED_BY, '', ''),
    ('param 5', 'test', 'https://dumps.example.com/module/repository', testit.LinkType.REPOSITORY, 'Repository', 'Desc of Repository')
])
def test_1(name, labels, url, link_type, link_title, link_desc):
    testit.addLinks(
        title='component_dump.dmp',
        type=testit.LinkType.RELATED,
        url='https://dumps.example.com/module/some_module_dump',
        description='Description'
    )
    testit.addLinks(url='https://dumps.example.com/module/some_module_dump')
    testit.addLinks(links=[
        {'url': 'https://dumps.example.com/module/some_module_dump', 'type': testit.LinkType.BLOCKED_BY, 'title': 'component_dump.dmp', 'description': 'Description'},
        {'url': 'https://dumps.example.com/module/some_module_dump', 'type': testit.LinkType.DEFECT},
        {'url': 'https://dumps.example.com/module/some_module_dump', 'type': testit.LinkType.ISSUE, 'title': 'component_dump.dmp'},
        {'url': 'https://dumps.example.com/module/some_module_dump', 'type': testit.LinkType.REQUIREMENT, 'title': 'component_dump.dmp', 'description': 'Description'},
        {'url': 'https://dumps.example.com/module/some_module_dump', 'type': testit.LinkType.REPOSITORY, 'description': 'Description'},
        {'url': 'https://dumps.example.com/module/some_module_dump'}
    ])
    with testit.step('Log in the system', 'system authentication'):
        with testit.step('Enter the login', 'login was entered'):
            with testit.step('Enter the password', 'password was entered'):
                assert True
        with testit.step('Create a project', 'the project was created'):
            with testit.step('Enter the project', 'the contents of the project are displayed'):
                assert True
            with testit.step('Create a test case', 'test case was created'):
                assert True
    with testit.step('Attachments'):
        testit.addAttachments(
            join(dirname(__file__), 'docs/text_file.txt'),
            join(dirname(__file__), 'pictures/picture.jpg'),
            join(dirname(__file__), 'docs/document.docx')
        )
        testit.addAttachments(
            join(dirname(__file__), 'docs/document.doc'),
            join(dirname(__file__), 'docs/logs.log')
        )
        assert True
```

# Contributing

You can help to develop the project. Any contributions are **greatly appreciated**.

* If you have suggestions for adding or removing projects, feel free to [open an issue](https://github.com/testit-tms/adapters-python/issues/new) to discuss it, or directly create a pull request after you edit the *README.md* file with necessary changes.
* Please make sure you check your spelling and grammar.
* Create individual PR for each suggestion.
* Please also read through the [Code Of Conduct](https://github.com/testit-tms/adapters-python/blob/master/CODE_OF_CONDUCT.md) before posting your first idea as well.

# License

Distributed under the Apache-2.0 License. See [LICENSE](https://github.com/testit-tms/adapters-python/blob/master/LICENSE.md) for more information.

