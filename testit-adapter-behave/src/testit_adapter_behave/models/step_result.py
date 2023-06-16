from attr import Factory, attrib, s


@s
class ScenarioStepResult:
    title = attrib(default='')
    description = attrib(default='')
    started_on = attrib(default=None)
    completed_on = attrib(default=None)
    duration = attrib(default=None)
    outcome = attrib(default=None)
    step_results = attrib(default=Factory(list))
    attachments = attrib(default=Factory(list))
    parameters = attrib(default=Factory(dict))
