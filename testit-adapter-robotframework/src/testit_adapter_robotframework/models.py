import ast
import re

from attr import Factory, asdict, attrib, s

from robot.api import logger
from testit_python_commons.models.link import Link

from .utils import get_hash


LinkTypes = ['Related', 'BlockedBy', 'Defect', 'Issue', 'Requirement', 'Repository']


def link_type_check(self, attribute, value):
    if value.title() not in LinkTypes:
        raise ValueError(f"Incorrect Link type: {value}")


def url_check(self, attribute, value):
    if not bool(re.match(
            r"(https?|ftp)://"
            r"(\w+(-\w+)*\.)?"
            r"((\w+(-\w+)*)\.(\w+))"
            r"(\.\w+)*"
            r"([\w\-._~/]*)*(?<!\.)",
            value)):
        raise ValueError(f"Incorrect URL: {value}")


class Default:

    def order(self):
        return asdict(self)


@s
class StepResult(Default):
    title = attrib(default='')
    description = attrib(default='')
    started_on = attrib(default=None)
    completed_on = attrib(default=None)
    duration = attrib(default=None)
    outcome = attrib(default=None)
    step_results = attrib(default=Factory(list))
    attachments = attrib(default=Factory(list))
    parameters = attrib(default=Factory(dict))


@s
class Step(Default):
    title = attrib()
    description = attrib()
    steps = attrib(default=Factory(list))


@s
class Label:
    name = attrib()


@s(kw_only=True)
class Autotest(Default):
    externalID = attrib(default=None)  # noqa: N815
    autoTestName = attrib()  # noqa: N815
    steps = attrib(default=Factory(list))
    stepResults = attrib(default=Factory(list))  # noqa: N815
    setUp = attrib(default=Factory(list))  # noqa: N815
    setUpResults = attrib(default=Factory(list))  # noqa: N815
    tearDown = attrib(default=Factory(list))  # noqa: N815
    tearDownResults = attrib(default=Factory(list))  # noqa: N815
    resultLinks = attrib(default=Factory(list))  # noqa: N815
    duration = attrib(default=None)
    failureReasonNames = attrib(default=Factory(list))  # noqa: N815
    traces = attrib(default=None)
    outcome = attrib(default=None)
    namespace = attrib(default=None)
    attachments = attrib(default=Factory(list))
    parameters = attrib(default=Factory(dict))
    properties = attrib(default=Factory(dict))
    classname = attrib(default=None)
    title = attrib(default=None)
    description = attrib(default=None)
    links = attrib(default=Factory(list))
    labels = attrib(default=Factory(list))
    workItemsID = attrib(default=Factory(list))  # noqa: N815
    message = attrib(default="")
    started_on = attrib(default=None)
    completed_on = attrib(default=None)

    step_depth = attrib(default=Factory(list))
    result_depth = attrib(default=Factory(list))

    def add_attributes(self, attrs):
        self.title = attrs['originalname']
        self.autoTestName = attrs['originalname']
        self.description = attrs['doc']
        self.template = attrs['template']
        self.classname = attrs['longname'].split('.')[-2]
        for tag in attrs['tags']:
            if tag.lower().startswith('testit.'):
                attr = re.findall(r'(?<=\.).*?(?=:)', tag)[0].strip().lower()
                value = tag.split(':', 1)[-1].strip()
                if attr == 'externalid':
                    self.externalID = str(value).replace("'", "").replace('"', '')
                elif attr == 'displayname':
                    self.autoTestName = str(value).replace("'", "").replace('"', '')
                elif attr == 'title':
                    self.title = str(value).replace("'", "").replace('"', '')
                elif attr == 'description':
                    self.description = str(value).replace("'", "").replace('"', '')
                elif attr == 'workitemsid' or attr == 'workitemsids':
                    value = ast.literal_eval(value)
                    if isinstance(value, (str, int)):
                        self.workItemsID.append(str(value))
                    elif isinstance(value, list):
                        self.workItemsID.extend([str(i) for i in value])
                    else:
                        logger.error(f"[TestIt] Wrong workitem format: {value}")
                elif attr == 'links':
                    value = ast.literal_eval(value)
                    try:
                        if isinstance(value, dict):
                            self.links.append(Link()\
                                .set_url(value['url'])\
                                .set_title(value.get('title', None))\
                                .set_link_type(value.get('type', None))\
                                .set_description(value.get('description', None)))
                        elif isinstance(value, list):
                            self.links.extend([Link()\
                                .set_url(link['url'])\
                                .set_title(link.get('title', None))\
                                .set_link_type(link.get('type', None))\
                                .set_description(link.get('description', None)) for link in value if isinstance(link, dict)])
                    except ValueError as e:
                        logger.error(f"[TestIt] Link Error: {e}")
                elif attr == 'labels':
                    value = ast.literal_eval(value)
                    if isinstance(value, (str, int)):
                        self.labels.append(Label(value))
                    elif isinstance(value, list):
                        self.labels.extend([Label(item) for item in value if isinstance(item, (str, int))])
                elif attr == 'namespace':
                    self.namespace = str(value).replace("'", "").replace('"', '')
                elif attr == 'classname':
                    self.classname = str(value).replace("'", "").replace('"', '')
                else:
                    logger.error(f"[TestIt] Unknown attribute: {attr}")
        if not self.externalID:
            self.externalID = get_hash(attrs['longname'])

    def add_step(self, step_type, title, description, parameters):
        if len(self.step_depth) == 0:
            if step_type.lower() == 'setup':
                self.setUp.append(Step(title, description))
                self.step_depth.append(self.setUp[-1])
                self.setUpResults.append(StepResult(title, description, parameters=parameters))
                self.result_depth.append(self.setUpResults[-1])
            elif step_type.lower() == 'teardown':
                self.tearDown.append(Step(title, description))
                self.step_depth.append(self.tearDown[-1])
                self.tearDownResults.append(StepResult(title, description, parameters=parameters))
                self.result_depth.append(self.tearDownResults[-1])
            else:
                self.steps.append(Step(title, description))
                self.step_depth.append(self.steps[-1])
                self.stepResults.append(StepResult(title, description, parameters=parameters))
                self.result_depth.append(self.stepResults[-1])
        elif 1 <= len(self.step_depth) < 14:
            self.step_depth[-1].steps.append(Step(title, description))
            self.step_depth.append(self.step_depth[-1].steps[-1])
            self.result_depth[-1].step_results.append(StepResult(title, description, parameters=parameters))
            self.result_depth.append(self.result_depth[-1].step_results[-1])

    def add_step_result(self, title, start, complete, duration, outcome, attachments):
        if self.result_depth:
            if self.result_depth[-1].title == title:
                step = self.result_depth.pop()
                step.started_on = start
                step.completed_on = complete
                step.duration = duration
                step.outcome = outcome
                step.attachments = attachments
        if self.step_depth:
            if self.step_depth[-1].title == title:
                self.step_depth.pop()


class Option:

    def __init__(self, **kwargs):
        if kwargs.get('tmsUrl', None):
            self.set_url = kwargs.get('tmsUrl', None)
        if kwargs.get('tmsPrivateToken', None):
            self.set_private_token = kwargs.get('tmsPrivateToken', None)
        if kwargs.get('tmsProjectId', None):
            self.set_project_id = kwargs.get('tmsProjectId', None)
        if kwargs.get('tmsConfigurationId', None):
            self.set_configuration_id = kwargs.get('tmsConfigurationId', None)
        if kwargs.get('tmsTestRunId', None):
            self.set_test_run_id = kwargs.get('tmsTestRunId', None)
        if kwargs.get('tmsTestRunId', None):
            self.set_tms_proxy = kwargs.get('tmsTestRunId', None)
        if kwargs.get('tmsTestRunName', None):
            self.set_test_run_name = kwargs.get('tmsTestRunName', None)
        if kwargs.get('tmsAdapterMode', None):
            self.set_adapter_mode = kwargs.get('tmsAdapterMode', None)
        if kwargs.get('tmsConfigFile', None):
            self.set_config_file = kwargs.get('tmsConfigFile', None)
        if kwargs.get('tmsCertValidation', None):
            self.set_cert_validation = kwargs.get('tmsCertValidation', None)
        if kwargs.get('tmsAutomaticCreationTestCases', None):
            self.set_automatic_creation_test_cases = kwargs.get('tmsAutomaticCreationTestCases', None)
