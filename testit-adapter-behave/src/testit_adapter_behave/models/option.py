from attr import attrs, attrib


# TODO: Add model to python-commons
@attrs(kw_only=True)
class Option(object):
    set_url = attrib(default=None)
    set_private_token = attrib(default=None)
    set_project_id = attrib(default=None)
    set_configuration_id = attrib(default=None)
    set_test_run_id = attrib(default=None)
    set_test_run_name = attrib(default=None)
    set_tms_proxy = attrib(default=None)
    set_adapter_mode = attrib(default=None)
    set_config_file = attrib(default=None)
