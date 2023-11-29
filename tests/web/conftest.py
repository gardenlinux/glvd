# SPDX-License-Identifier: MIT

import pytest

import contextlib

from glvd.web import create_app


@pytest.fixture(scope='class')
def app(db_session_class):
    app = create_app()

    @contextlib.asynccontextmanager
    async def db_begin():
        yield db_session_class
    setattr(app, 'db_begin', db_begin)

    yield app


@pytest.fixture(scope='class')
def client(app):
    return app.test_client()
