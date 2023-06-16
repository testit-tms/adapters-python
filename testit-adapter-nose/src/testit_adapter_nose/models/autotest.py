import typing

from attr import Factory, attrib, s

from .step_result import AutotestStepResult


@s(kw_only=True)
class Autotest:
    external_id = attrib()  # noqa: N815
    name = attrib()  # noqa: N815
    step_results = attrib(default=Factory(typing.List[AutotestStepResult]))  # noqa: N815
    setup_results = attrib(default=Factory(typing.List[AutotestStepResult]))  # noqa: N815
    teardown_results = attrib(default=Factory(list))  # noqa: N815
    result_links = attrib(default=Factory(list))  # noqa: N815
    duration = attrib(default=None)
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
    work_item_ids = attrib(default=Factory(list))  # noqa: N815
    message = attrib(default="")
    started_on = attrib(default=None)
    completed_on = attrib(default=None)

    step_depth = attrib(default=Factory(list))
    result_depth = attrib(default=Factory(list))
