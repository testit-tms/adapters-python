
# input values from configuration file
class PropertiesNames:
    URL = 'url'
    PRIVATE_TOKEN = 'privatetoken'
    PROJECT_ID = "projectid"
    CONFIGURATION_ID = 'configurationid'
    TEST_RUN_ID = 'testrunid'
    TEST_RUN_NAME = 'testrunname'
    TMS_PROXY = 'tmsproxy'
    ADAPTER_MODE = 'adaptermode'
    CERT_VALIDATION = 'certvalidation'
    AUTOMATIC_CREATION_TEST_CASES = 'automaticcreationtestcases'
    AUTOMATIC_UPDATION_LINKS_TO_TEST_CASES = 'automaticupdationlinkstotestcases'
    IMPORT_REALTIME = 'importrealtime'
    SYNC_STORAGE_PORT = 'syncstorageport'
    LEGACY_WORKFLOW = 'legacyworkflow'

ENV_TO_PROPERTY = {
    'TMS_URL': PropertiesNames.URL,
    'TMS_PRIVATE_TOKEN': PropertiesNames.PRIVATE_TOKEN,
    'TMS_PROJECT_ID': PropertiesNames.PROJECT_ID,
    'TMS_CONFIGURATION_ID': PropertiesNames.CONFIGURATION_ID,
    'TMS_TEST_RUN_ID': PropertiesNames.TEST_RUN_ID,
    'TMS_TEST_RUN_NAME': PropertiesNames.TEST_RUN_NAME,
    'TMS_PROXY': PropertiesNames.TMS_PROXY,
    'TMS_ADAPTER_MODE': PropertiesNames.ADAPTER_MODE,
    'TMS_CERT_VALIDATION': PropertiesNames.CERT_VALIDATION,
    'TMS_AUTOMATIC_CREATION_TEST_CASES': PropertiesNames.AUTOMATIC_CREATION_TEST_CASES,
    'TMS_AUTOMATIC_UPDATION_LINKS_TO_TEST_CASES': PropertiesNames.AUTOMATIC_UPDATION_LINKS_TO_TEST_CASES,
    'TMS_IMPORT_REALTIME': PropertiesNames.IMPORT_REALTIME,
    'TMS_SYNC_STORAGE_PORT': PropertiesNames.SYNC_STORAGE_PORT,
    'TMS_LEGACY_WORKFLOW': PropertiesNames.LEGACY_WORKFLOW,
}

OPTION_TO_PROPERTY = {
    'set_url': PropertiesNames.URL,
    'set_private_token': PropertiesNames.PRIVATE_TOKEN,
    'set_project_id': PropertiesNames.PROJECT_ID,
    'set_configuration_id': PropertiesNames.CONFIGURATION_ID,
    'set_test_run_id': PropertiesNames.TEST_RUN_ID,
    'set_test_run_name': PropertiesNames.TEST_RUN_NAME,
    'set_tms_proxy': PropertiesNames.TMS_PROXY,
    'set_adapter_mode': PropertiesNames.ADAPTER_MODE,
    'set_cert_validation': PropertiesNames.CERT_VALIDATION,
    'set_automatic_creation_test_cases': PropertiesNames.AUTOMATIC_CREATION_TEST_CASES,
    'set_automatic_updation_links_to_test_cases': PropertiesNames.AUTOMATIC_UPDATION_LINKS_TO_TEST_CASES,
    'set_import_realtime': PropertiesNames.IMPORT_REALTIME,
    'set_sync_storage_port': PropertiesNames.SYNC_STORAGE_PORT,
    'set_legacy_workflow': PropertiesNames.LEGACY_WORKFLOW,
}