import logging
import random
import time
from http.client import RemoteDisconnected

import testit_api_client
import urllib3

CONNECTION_RETRIES = 3
CONNECTION_RETRY_DELAY_SEC = 1
API_EXCEPTION_RETRIES = 10
NON_RETRIABLE_API_STATUS_CODES = (400, 404)

_RETRIABLE_CONNECTION_TYPES = (
    urllib3.exceptions.ProtocolError,
    urllib3.exceptions.NewConnectionError,
    ConnectionError,
    ConnectionResetError,
    ConnectionAbortedError,
    RemoteDisconnected,
    TimeoutError,
)


def is_non_retriable_api_exception(exc: BaseException) -> bool:
    return (
        isinstance(exc, testit_api_client.exceptions.ApiException)
        and int(exc.status) in NON_RETRIABLE_API_STATUS_CODES
    )


def is_retriable_connection_error(exc: BaseException) -> bool:
    seen = set()
    current = exc
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        if isinstance(current, _RETRIABLE_CONNECTION_TYPES):
            return True
        current = current.__cause__ or current.__context__
    return False


def _execute_with_connection_retries(func, args, kwargs):
    connection_attempts = 0

    while True:
        try:
            return func(*args, **kwargs)
        except BaseException as e:
            if not is_retriable_connection_error(e):
                raise

            connection_attempts += 1
            logging.warning(
                'Connection error in %s (attempt %d/%d): %s',
                func.__name__,
                connection_attempts,
                CONNECTION_RETRIES,
                e,
            )
            if connection_attempts > CONNECTION_RETRIES:
                raise

            time.sleep(CONNECTION_RETRY_DELAY_SEC)


def retry_on_connection_error(func):
    def retry_wrapper(*args, **kwargs):
        return _execute_with_connection_retries(func, args, kwargs)

    return retry_wrapper


def retry(func):
    def retry_wrapper(*args, **kwargs):
        api_attempts = 0

        while True:
            try:
                return _execute_with_connection_retries(func, args, kwargs)
            except testit_api_client.exceptions.ApiException as e:
                if is_non_retriable_api_exception(e):
                    raise

                api_attempts += 1
                logging.error(e)
                if api_attempts >= API_EXCEPTION_RETRIES:
                    raise

                time.sleep(random.randrange(0, 100) / 100)

    return retry_wrapper
