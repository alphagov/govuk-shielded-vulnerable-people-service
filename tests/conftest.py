import pytest

@pytest.fixture(scope='session', autouse=True)
def faker_session_locale():
    return ['en_GB']
