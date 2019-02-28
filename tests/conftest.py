import pytest
from weisaw.api.core import create_app
from weisaw.worker.core import celery_task
from weisaw.api.settings import TestConfig
from datetime import datetime


FAKE_TIME = datetime(2019, 1, 1, 0, 0, 0)


@pytest.fixture(scope="module")
def test_client():

    app_config = TestConfig
    weisaw_app = create_app(app_config)

    weisaw_app.debug = True

    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = weisaw_app.test_client()

    # Establish an application context before running the tests.
    ctx = weisaw_app.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()


@pytest.fixture(scope='module')
def celery_app(request):
    celery_task.conf.update(CELERY_ALWAYS_EAGER=True)
    return celery_task


@pytest.fixture(autouse=True)
def patch_datetime_now(monkeypatch):

    class FreezeTime:
        @classmethod
        def now(cls):
            return FAKE_TIME

    monkeypatch.setattr('tests.test_tasks.datetime', FreezeTime)
    monkeypatch.setattr('weisaw.worker.tasks.datetime', FreezeTime)
    # monkeypatch.setattr(datetime, 'datetime', FreezeTime)
