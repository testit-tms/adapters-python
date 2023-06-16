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
