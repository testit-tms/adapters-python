import os
import re
import logging
from typing import Any, List, Optional, Union
from datetime import datetime, date, time, timedelta
from decimal import Decimal
from uuid import UUID


class HtmlEscapeUtils:
    """
    HTML escape utilities for preventing XSS attacks.
    Escapes HTML tags in strings and objects using reflection.
    """
    
    NO_ESCAPE_HTML_ENV_VAR = "NO_ESCAPE_HTML"
    
    # Align with Java adapters: tag must start with letter, '!' or '/'
    _HTML_TAG_PATTERN = re.compile(
        r'''<[a-zA-Z!/][^<>"']*(?:"[^"]*"[^<>"']*|'[^']*'[^<>"']*)*>'''
    )

    @staticmethod
    def escape_html_tags(text: Optional[str]) -> Optional[str]:
        """
        Escapes HTML tags to prevent XSS attacks.
        First checks if the string contains HTML tags using regex pattern.
        Only performs escaping if HTML tags are detected.
        Escapes < as &lt; and > as &gt; (idempotent for already-escaped text).
        
        Args:
            text: The text to escape
            
        Returns:
            Escaped text or original text if escaping is disabled
        """
        if text is None:
            return None
            
        # Check if escaping is disabled via environment variable
        no_escape_html = os.environ.get(HtmlEscapeUtils.NO_ESCAPE_HTML_ENV_VAR, "").lower()
        if no_escape_html == "true":
            return text
            
        # First check if the string contains HTML tags
        if not HtmlEscapeUtils._HTML_TAG_PATTERN.search(text):
            return text  # No HTML tags found, return original string
            
        return text.replace('<', '&lt;').replace('>', '&gt;')
    
    @staticmethod
    def escape_html_in_object(obj: Any) -> Any:
        """
        Escapes HTML tags in all string attributes of an object using reflection.
        Also processes list attributes: if list of objects - calls escape_html_in_object_list,
        if list of strings - escapes each string.
        Can be disabled by setting NO_ESCAPE_HTML environment variable to "true".
        
        Args:
            obj: The object to process
            
        Returns:
            The processed object with escaped strings
        """
        if obj is None:
            return None
            
        # Check if escaping is disabled via environment variable
        no_escape_html = os.environ.get(HtmlEscapeUtils.NO_ESCAPE_HTML_ENV_VAR, "").lower()
        if no_escape_html == "true":
            return obj
            
        try:
            if isinstance(obj, list):
                HtmlEscapeUtils._process_list(obj)
            elif isinstance(obj, dict):
                HtmlEscapeUtils._process_dict(obj)
            else:
                HtmlEscapeUtils._process_object_attributes(obj)
        except Exception as e:
            # Silently ignore reflection errors
            logging.debug(f"Error processing object attributes: {e}")
            
        return obj
    
    @staticmethod
    def escape_html_in_object_list(obj_list: Optional[List[Any]]) -> Optional[List[Any]]:
        """
        Escapes HTML tags in list items: strings in-place, objects via reflection.
        Can be disabled by setting NO_ESCAPE_HTML environment variable to "true".
        
        Args:
            obj_list: The list of objects to process
            
        Returns:
            The processed list with escaped strings in all objects
        """
        if obj_list is None:
            return None
            
        # Check if escaping is disabled via environment variable
        no_escape_html = os.environ.get(HtmlEscapeUtils.NO_ESCAPE_HTML_ENV_VAR, "").lower()
        if no_escape_html == "true":
            return obj_list

        HtmlEscapeUtils._process_list(obj_list)
        return obj_list
    
    @staticmethod
    def _process_dict(obj: dict) -> None:
        for key, value in obj.items():
            if isinstance(value, str):
                obj[key] = HtmlEscapeUtils.escape_html_tags(value)
            elif isinstance(value, list):
                HtmlEscapeUtils._process_list(value)
            elif isinstance(value, dict):
                HtmlEscapeUtils._process_dict(value)
            elif value is not None and not HtmlEscapeUtils._is_simple_type(type(value)):
                HtmlEscapeUtils.escape_html_in_object(value)

    @staticmethod
    def _iter_object_attr_names(obj: Any):
        """
        OpenAPI models store fields in attribute_map/_data_store; they are not listed by dir().
        Prefer those maps, fall back to public dir() attributes for plain objects.
        """
        attribute_map = getattr(obj, 'attribute_map', None)
        if isinstance(attribute_map, dict) and attribute_map:
            return attribute_map.keys()

        data_store = getattr(obj, '_data_store', None)
        if isinstance(data_store, dict) and data_store:
            return data_store.keys()

        return (
            attr_name for attr_name in dir(obj)
            if not attr_name.startswith('_') and not callable(getattr(obj, attr_name, None))
        )

    @staticmethod
    def _should_skip_attr(attr_name: str) -> bool:
        return (
            attr_name.startswith('_')
            or attr_name.startswith("external_id")
            or attr_name.startswith("externalId")
            or attr_name.startswith("auto_test_external_id")
            or attr_name.startswith("autoTestExternalId")
        )

    @staticmethod
    def _process_object_attributes(obj: Any) -> None:
        """
        Process all attributes of an object for HTML escaping.
        """
        for attr_name in HtmlEscapeUtils._iter_object_attr_names(obj):
            if HtmlEscapeUtils._should_skip_attr(attr_name):
                continue

            try:
                value = getattr(obj, attr_name, None)
                if callable(value):
                    continue
                HtmlEscapeUtils._process_attribute_value(obj, attr_name, value)
            except Exception as e:
                # Silently ignore attribute errors
                logging.debug(f"Error processing attribute {attr_name}: {e}")
    
    @staticmethod
    def _process_attribute_value(obj: Any, attr_name: str, value: Any) -> None:
        """
        Process a single attribute value for HTML escaping.
        """
        if isinstance(value, str):
            # Escape string attributes
            try:
                setattr(obj, attr_name, HtmlEscapeUtils.escape_html_tags(value))
            except AttributeError:
                # Attribute might be read-only
                pass
        elif isinstance(value, list):
            HtmlEscapeUtils._process_list(value)
        elif isinstance(value, dict):
            HtmlEscapeUtils._process_dict(value)
            try:
                # Write back so OpenAPI models that return dict copies keep escaped values
                setattr(obj, attr_name, value)
            except AttributeError:
                pass
        elif value is not None and not HtmlEscapeUtils._is_simple_type(type(value)):
            # Process nested objects (but not simple types)
            HtmlEscapeUtils.escape_html_in_object(value)
    
    @staticmethod
    def _process_list(lst: List[Any]) -> None:
        """
        Process a list for HTML escaping.
        """
        if not lst:
            return
            
        first_element = lst[0]
        
        if isinstance(first_element, str):
            # List of strings - escape each string
            for i, item in enumerate(lst):
                if isinstance(item, str):
                    lst[i] = HtmlEscapeUtils.escape_html_tags(item)
        elif first_element is not None:
            # List of objects - process each object
            for item in lst:
                HtmlEscapeUtils.escape_html_in_object(item)
    
    @staticmethod
    def _is_simple_type(obj_type: type) -> bool:
        """
        Checks if a type is a simple type that doesn't need HTML escaping.
        
        Args:
            obj_type: Type to check
            
        Returns:
            True if it's a simple type
        """
        simple_types = {
            # Basic types
            bool, int, float, complex, bytes, bytearray,
            # String type (handled separately)
            str,
            # Date/time types
            datetime, date, time, timedelta,
            # Other common types
            Decimal, UUID,
            # None type
            type(None)
        }
        
        return (
            obj_type in simple_types or
            # Check for enums
            (hasattr(obj_type, '__bases__') and any(
                base.__name__ == 'Enum' for base in obj_type.__bases__
            ))
        ) 