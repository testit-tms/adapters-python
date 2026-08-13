
# flake8: noqa

# Import all APIs into this package.
# If you have many APIs here with many many models used in each API this may
# raise a `RecursionError`.
# In order to avoid this, import only the API that you directly need like:
#
#   from adapters_api.api.attachments_api import AttachmentsApi
#
# or import this package, but before doing it, use:
#
#   import sys
#   sys.setrecursionlimit(n)

# Import APIs into API package:
from adapters_api.api.attachments_api import AttachmentsApi
from adapters_api.api.auto_tests_api import AutoTestsApi
from adapters_api.api.configurations_api import ConfigurationsApi
from adapters_api.api.parameters_api import ParametersApi
from adapters_api.api.project_attributes_api import ProjectAttributesApi
from adapters_api.api.project_sections_api import ProjectSectionsApi
from adapters_api.api.project_work_items_api import ProjectWorkItemsApi
from adapters_api.api.projects_api import ProjectsApi
from adapters_api.api.sections_api import SectionsApi
from adapters_api.api.test_results_api import TestResultsApi
from adapters_api.api.test_runs_api import TestRunsApi
from adapters_api.api.work_items_api import WorkItemsApi
from adapters_api.api.workflows_api import WorkflowsApi
