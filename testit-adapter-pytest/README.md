# Test IT TMS adapter for Pytest
![Test IT](https://raw.githubusercontent.com/testit-tms/adapters-python/master/images/banner.png)

## Getting Started

### Installation
```
pip install testit-adapter-pytest
```

## Usage

### Configuration

Create `connection_config.ini` file in the root directory of the project:
```
[testit]
url = <url>
privatetoken = <token>
projectID = <id>
configurationID = <id>
testrunID = <optional id>
testrun_name = <optional name>

# This section are optional. It enables debug mode.
[debug]
testit_proxy = {"http": "http://localhost:8888", "https": "http://localhost:8888"}
```

And fill parameters with your configuration, where:  
`url` - location of the TMS instance  
`privatetoken` - API secret key  

1. go to the https://{DOMAIN}/user-profile profile  
2. copy the API secret key

`projectID` - id of project in TMS instance

1. create a project
2. open DevTools -> network
3. go to the project https://{DOMAIN}/projects/20/tests
4. GET-request project, Preview tab, copy id field  

`configurationID` - id of configuration in TMS instance  

1. create a project  
2. open DevTools -> network  
3. go to the project https://{DOMAIN}/projects/20/tests  
4. GET-request configurations, Preview tab, copy id field  

`testrunID` - id of the created test-run in TMS instance  
`testrun_name` - parameter for specifying the name of test-run in TMS instance  
`testit_proxy` - parameter for configuring proxy for sending requests  

> testrunID and testrun_name are optional. If it's not provided than it create automatically.  
> testit_proxy are optional. It enables debug mode.

### Tags

Decorators can be used to specify information about autotest.

Description of decorators (\* - required):
- `testit.workItemID` - linking an autotest to a test case
- \*`testit.displayName` - name of the autotest in the Test IT system (can be replaced with documentation strings)
- \*`testit.externalID` - ID of the autotest within the project in the Test IT System
- `testit.title` - title in the autotest card
- `testit.description` - description in the autotest card
- `testit.labels` - tags in the work item
- `testit.link` - links in the autotest card
- `testit.step` - the designation of the step called in the body of the test or other step

All decorators support the use of parameterization attributes

Description of methods:
- `testit.addLink` - links in the autotest result
- `testit.addAttachments` - uploading files in the autotest result
- `testit.addMessage` - information about autotest in the autotest result
- `testit.step` - usage in the "with" construct to designation a step in the body of the test

### Launch

Launch with a connection_config.ini file in the root directory of the project:

```
$ pytest --testit
```

Launch with command-line parameters:

```
$ pytest --testit --testit_url=<url> --privatetoken=<token> --projectid=<id> --configurationid=<id> --testrunid=<optional id> --testrun_name=<optional name> --testit_proxy='{"http":"http://localhost:8888","https":"http://localhost:8888"}'
```

> testrunID and testrun_name are optional. If it's not provided than it create automatically.  
> testit_proxy are optional. It enables debug mode.

### Examples

#### Decorators
```py
import pytest
import testit

# Test with a minimal set of decorators
@testit.externalID('Simple_autotest2')
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

@testit.externalID('Simple_test_skip')
@testit.displayName('Simple test skip')
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

@testit.workItemID(627)
@testit.displayName('Simple autotest 1 - {name}')
@testit.externalID('Simple_autotest1_{name}')
@testit.title('Authorization')
@testit.description('E2E_autotest')
@testit.labels('{labels}')
@testit.link(url='https://dumps.example.com/module/JCP-777')
@testit.link(url='{url}', type='{link_type}', title='{link_title}')
@pytest.mark.parametrize('name, labels, url, link_type, link_title', [
    ('param 1', ['E2E', 'test'], 'https://dumps.example.com/module/JCP-777', testit.LinkType.DEFECT, 'JCP-777'),
    ('param 2', (), 'https://dumps.example.com/module/docs', testit.LinkType.RELATED, 'Documentation'),
    ('param 3', ('E2E', 'test'), 'https://dumps.example.com/module/projects', testit.LinkType.REQUIREMENT, 'Projects'),
    ('param 4', {'E2E', 'test'}, 'https://dumps.example.com/module/', testit.LinkType.BLOCKED_BY, ''),
    ('param 5', 'test', 'https://dumps.example.com/module/repository', testit.LinkType.REPOSITORY, 'Repository')
])
def test_1(name, labels, url, link_type, link_title):
    testit.addLink(
        title='component_dump.dmp',
        type=testit.LinkType.RELATED,
        url='https://dumps.example.com/module/some_module_dump'
    )
    testit.addLink(
        title='component_dump.dmp',
        type=testit.LinkType.BLOCKED_BY,
        url='https://dumps.example.com/module/some_module_dump'
    )
    testit.addLink(
        title='component_dump.dmp',
        type=testit.LinkType.DEFECT,
        url='https://dumps.example.com/module/some_module_dump'
    )
    testit.addLink(
        title='component_dump.dmp',
        type=testit.LinkType.ISSUE,
        url='https://dumps.example.com/module/some_module_dump'
    )
    testit.addLink(
        title='component_dump.dmp',
        type=testit.LinkType.REQUIREMENT,
        url='https://dumps.example.com/module/some_module_dump'
    )
    testit.addLink(
        title='component_dump.dmp',
        type=testit.LinkType.REPOSITORY,
        url='https://dumps.example.com/module/some_module_dump'
    )
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

