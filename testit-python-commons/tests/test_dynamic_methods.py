import random
import string
import pytest

from testit_python_commons import dynamic_methods
from testit_python_commons.services import TmsPluginManager, Utils
from testit_python_commons.models.link_type import LinkType
from testit_python_commons.models.link import Link


class TestDynamicMethods:
    @pytest.fixture
    def link_model(self) -> Link:
        return Utils.convert_link_dict_to_link_model({
            "url": "https://www.example.com",
            "title": ''.join(random.choices(string.ascii_letters + string.digits, k=10)),
            "type": LinkType.ISSUE,
            "description": ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        })

    @pytest.fixture
    def mock_plugin_manager_hook(self, mocker):
        mock_plugin_manager = mocker.patch.object(TmsPluginManager, 'get_plugin_manager')
        mock_hook = mock_plugin_manager.return_value.hook

        return mock_hook

    def test_add_link_deprecated(self, link_model, mock_plugin_manager_hook, mocker):
        mock_convert = mocker.patch.object(Utils, 'convert_link_dict_to_link_model')
        mock_convert.return_value = link_model

        dynamic_methods.addLink(
            url=link_model.get_url(),
            title=link_model.get_title(),
            type=link_model.get_link_type(),
            description=link_model.get_description()
        )

        mock_plugin_manager_hook.add_link.assert_called_once_with(link=link_model)
        mock_convert.assert_called_once_with({
            "url": link_model.get_url(),
            "title": link_model.get_title(),
            "type": link_model.get_link_type(),
            "description": link_model.get_description()
        })

    def test_add_links_with_url(self, link_model, mock_plugin_manager_hook, mocker):
        mock_convert = mocker.patch.object(Utils, 'convert_link_dict_to_link_model')
        mock_convert.return_value = link_model

        dynamic_methods.addLinks(
            url=link_model.get_url(),
            title=link_model.get_title(),
            type=link_model.get_link_type(),
            description=link_model.get_description()
        )

        mock_plugin_manager_hook.add_link.assert_called_once_with(link=link_model)
        mock_convert.assert_called_once_with({
            "url": link_model.get_url(),
            "title": link_model.get_title(),
            "type": link_model.get_link_type(),
            "description": link_model.get_description()
        })

    def test_add_links_with_list(self, link_model, mock_plugin_manager_hook, mocker):
        mock_convert = mocker.patch.object(Utils, 'convert_link_dict_to_link_model')
        mock_convert.return_value = link_model

        link_data = {
            "url": link_model.get_url(),
            "title": link_model.get_title(),
            "type": link_model.get_link_type(),
            "description": link_model.get_description()
        }
        dynamic_methods.addLinks(links=[link_data])

        mock_plugin_manager_hook.add_link.assert_called_once_with(link=link_model)
        mock_convert.assert_called_once_with(link_data)

    def test_add_message(self, mock_plugin_manager_hook):
        test_message = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        dynamic_methods.addMessage(test_message)
        mock_plugin_manager_hook.add_message.assert_called_once_with(test_message=test_message)