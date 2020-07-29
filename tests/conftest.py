from mattermostgithub import app as mig
import pytest

@pytest.fixture(scope="session")
def app():
    return mig
