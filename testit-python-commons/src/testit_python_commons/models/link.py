from testit_python_commons.models.link_type import LinkType
from testit_python_commons.services.logger import adapter_logger
from testit_python_commons.utils import HtmlEscapeUtils


class Link:
    __url: str = None
    __title: str = None
    __link_type: LinkType = None
    __description: str = None

    @adapter_logger
    def set_url(self, url: str):
        self.__url = url

        return self

    @adapter_logger
    def get_url(self) -> str:
        return self.__url

    @adapter_logger
    def set_title(self, title: str):
        self.__title = HtmlEscapeUtils.escape_html_tags(title)

        return self

    @adapter_logger
    def get_title(self) -> str:
        return self.__title

    @adapter_logger
    def set_link_type(self, link_type: LinkType):
        self.__link_type = link_type

        return self

    @adapter_logger
    def get_link_type(self) -> LinkType:
        return self.__link_type

    @adapter_logger
    def set_description(self, description: str):
        self.__description = HtmlEscapeUtils.escape_html_tags(description)

        return self

    @adapter_logger
    def get_description(self) -> str:
        return self.__description
