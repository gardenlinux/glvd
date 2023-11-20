# SPDX-License-Identifier: MIT

import pytest

import contextlib

from glvd.web import create_app


@pytest.fixture()
def app(db_conn):
    app = create_app()

    @contextlib.asynccontextmanager
    async def db_begin():
        yield db_conn
    setattr(app, 'db_begin', db_begin)

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()
