from attr import attrs, attrib
from attr import Factory


@attrs
class FixtureResult:
    title = attrib(default=None)
    outcome = attrib(default=None)
    description = attrib(default=None)
    message = attrib(default=None)
    stacktrace = attrib(default=None)
    steps = attrib(default=None)
    attachments = attrib(default=Factory(list))
    parameters = attrib(default=Factory(list))
    start = attrib(default=None)
    stop = attrib(default=None)


@attrs
class FixturesContainer:
    uuid = attrib(default=None)
    external_ids = attrib(default=Factory(list))
    befores = attrib(default=Factory(list))
    afters = attrib(default=Factory(list))
