from attr import attrs, attrib
from attr import Factory


@attrs
class ExecutableTest:
    external_id = attrib()
    name = attrib()
    steps = attrib(default=Factory(list))
    step_results = attrib(default=Factory(list))
    setup_steps = attrib(default=Factory(list))
    setup_step_results = attrib(default=Factory(list))
    teardown_steps = attrib(default=Factory(list))
    teardown_step_results = attrib(default=Factory(list))
    result_links = attrib(default=Factory(list))
    duration = attrib(default=None)
    outcome = attrib(default=None)
    failure_reason_names = attrib(default=Factory(list))
    traces = attrib(default=None)
    attachments = attrib(default=Factory(list))
    parameters = attrib(default=Factory(dict))
    properties = attrib(default=Factory(dict))
    namespace = attrib(default=None)
    classname = attrib(default=None)
    title = attrib(default=None)
    description = attrib(default=None)
    links = attrib(default=Factory(list))
    labels = attrib(default=Factory(list))
    work_item_ids = attrib(default=Factory(list))
    message = attrib(default=None)
    node_id = attrib(default=None)
