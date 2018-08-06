from mattermostgithub import app as mig
import pytest

@pytest.fixture
def app():
    return mig
