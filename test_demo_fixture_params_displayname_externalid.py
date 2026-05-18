"""
Демо: параметризация через фикстуру params=[{...}] (без pytest.mark.parametrize).

Два варианта: 1) Логика клиента — addDisplayName/addExternalId в теле теста (runtime).
2) Декораторы с плейсхолдером {user_type} — подстановка при коллекции (проблемный кейс без доработки).
"""
import pytest
import testit


USERS_PREPARE = [
    {"user_type": "consultant", "nnumber": 1},
    {"user_type": "admin", "nnumber": 2},
    {"user_type": "viewer", "nnumber": 3},
]


# --- Как у клиента: фикстура users_prepare_fixture, addDisplayName/addExternalId в теле теста ---
@pytest.fixture(
    params=USERS_PREPARE,
    ids=lambda user: user["user_type"],
)
def users_prepare_fixture(request):
    """Как у клиента: return request.param."""
    return dict(request.param)


def test_user(users_prepare_fixture):
    """Клиент: displayName и externalId задаются в теле теста. Ключ — строка 'user_type'."""
    testit.addDisplayName(f"Тест пользователя [{users_prepare_fixture['user_type']}]")
    testit.addExternalId(f"user_test_[{users_prepare_fixture['user_type']}]")
    assert users_prepare_fixture["user_type"] in ("consultant", "admin", "viewer")


# --- Вариант с декораторами и плейсхолдером {user_type} (без доработки: Key for parameter user_type not found) ---
@pytest.fixture(
    params=USERS_PREPARE,
    ids=lambda user: user["user_type"],
)
@testit.step("Получаем список доступных для данного окружения активных пользователей")
def users_prepare_fixture_all_active_param(request):
    """Фикстура с params=[{...}] — в callspec.params попадает имя фикстуры → словарь."""
    fixture_result = dict(request.param)
    fixture_result["token"] = f"token_{fixture_result['nnumber']}"
    return fixture_result


@pytest.fixture
def user_type(request):
    """Извлекает user_type из параметризованной фикстуры (по соглашению имён)."""
    USER_FIXTURE_PREFIX = "users_prepare_fixture_"
    USER_FIXTURE_SUFFIX = "_param"
    for name in request.fixturenames:
        if name.startswith(USER_FIXTURE_PREFIX) and name.endswith(USER_FIXTURE_SUFFIX):
            user = request.getfixturevalue(name)
            if isinstance(user, dict):
                return user.get("user_type")
    return None


@testit.displayName("Получение Информации о (positive) [{user_type}]")
@testit.externalId("get_consultant_family_positive_[{user_type}]")
def test_get_consultant_family_positive(users_prepare_fixture_all_active_param, user_type):
    assert user_type in ("consultant", "admin", "viewer")
    assert users_prepare_fixture_all_active_param["user_type"] == user_type
