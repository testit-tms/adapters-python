import urllib3
from testit_api_client.exceptions import ApiException

from testit_python_commons.services.retry import (
    CONNECTION_RETRIES,
    is_non_retriable_api_exception,
    is_retriable_connection_error,
    retry,
    retry_on_connection_error,
)


def test_is_retriable_connection_error_protocol_error():
    exc = urllib3.exceptions.ProtocolError(
        'Connection aborted.',
        ConnectionResetError('Remote end closed connection without response'),
    )
    assert is_retriable_connection_error(exc)


def test_retry_connection_error_retries_and_raises():
    calls = {'count': 0}

    @retry
    def flaky():
        calls['count'] += 1
        raise urllib3.exceptions.ProtocolError('Connection aborted.')

    try:
        flaky()
    except urllib3.exceptions.ProtocolError:
        pass

    assert calls['count'] == CONNECTION_RETRIES + 1


def test_is_non_retriable_api_exception_for_not_found_subclass():
    from testit_api_client.exceptions import NotFoundException

    exc = NotFoundException(status=404, reason='Not Found')
    assert is_non_retriable_api_exception(exc)


def test_retry_does_not_retry_on_404():
    calls = {'count': 0}

    @retry
    def flaky():
        calls['count'] += 1
        raise ApiException(status=404, reason='Not Found')

    try:
        flaky()
    except ApiException:
        pass

    assert calls['count'] == 1


def test_retry_on_connection_error_does_not_retry_api_exception():
    calls = {'count': 0}

    @retry_on_connection_error
    def flaky():
        calls['count'] += 1
        raise ApiException(status=500, reason='error')

    try:
        flaky()
    except ApiException:
        pass

    assert calls['count'] == 1
