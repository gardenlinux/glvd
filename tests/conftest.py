# SPDX-License-Identifier: MIT

import pytest

import asyncio
import uuid
from unittest.mock import Mock

from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.sql import text

from glvd.database import Base


# Use standard types in all tests.  Extra types needs to be installed and
# require superuser privileges.
import glvd.database.types
setattr(glvd.database.types.DebVersion, 'get_col_spec', Mock(return_value='text'))


# Override with broader scope, so we can use session fixtures
@pytest.fixture(scope='session')
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def db_engine():
    '''
    Provides an asynchronous SQLAlchemy database engine.

    The search path is overriden to only include 'glvd_test', this
    schema is created on setup and destroy on teardown.
    '''
    schema_name = f'glvd_test_{uuid.uuid4().hex}'

    # Use async_fallback, so we can use events below
    engine = create_async_engine(
        'postgresql+asyncpg:///?async_fallback=true',
        echo=True,
    )

    @event.listens_for(engine.sync_engine, 'engine_connect')
    def set_search_path(conn):
        conn.exec_driver_sql(f'SET SESSION search_path TO {schema_name}')
        conn.commit()

    async with engine.begin() as conn:
        await conn.execute(text(f'CREATE SCHEMA {schema_name}'))
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()

    yield engine

    async with engine.begin() as conn:
        await conn.execute(text(f'DROP SCHEMA {schema_name} CASCADE'))


@pytest.fixture
async def db_session(db_engine):
    '''
    Provides an asynchronous SQLAlchemy database session.

    This should never be commited, or it will affect other tests.
    '''
    async with async_sessionmaker(db_engine)() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope='class')
async def db_session_class(db_engine):
    '''
    Provides an asynchronous SQLAlchemy database session.

    Similar to db_session, but scoped on class.  So it can be used in
    combination with @pytest.mark.incremental.

    This should never be commited, or it will affect other tests.
    '''
    async with async_sessionmaker(db_engine)() as session:
        yield session
        await session.rollback()


# Based on
# https://docs.pytest.org/en/7.4.x/example/simple.html#incremental-testing-test-steps
# https://docs.pytest.org/en/7.4.x/license.html
class _PytestIncremental:
    test_failed: dict[type, dict[tuple[int, ...], str]]

    def __init__(self) -> None:
        self.test_failed = {}

    # retrieve the index of the test (if parametrize is used in combination with incremental)
    def _index(self, item: pytest.Function) -> tuple[int, ...]:
        if callspec := getattr(item, 'callspec', None):
            return tuple(callspec.indices.values())
        else:
            return ()

    def runtest_makereport(self, item: pytest.Function, call: pytest.CallInfo) -> None:
        if call.excinfo is not None:
            self.test_failed.setdefault(item.cls, {}).setdefault(
                self._index(item),
                item.originalname or item.name,
            )

    def runtest_setup(self, item: pytest.Function) -> None:
        if test_failed := self.test_failed.get(item.cls, None):
            if (test_name := test_failed.get(self._index(item), None)):
                pytest.xfail('previous test failed ({})'.format(test_name))


dispatch_keywords = {
    'incremental': _PytestIncremental(),
}


def pytest_configure(config: pytest.Config) -> None:
    for k, v in dispatch_keywords.items():
        config.addinivalue_line('markers', k)


def pytest_runtest_makereport(item: pytest.Function, call: pytest.CallInfo) -> None:
    for k, v in dispatch_keywords.items():
        if k in item.keywords:
            v.runtest_makereport(item, call)


def pytest_runtest_setup(item: pytest.Function):
    for k, v in dispatch_keywords.items():
        if k in item.keywords:
            v.runtest_setup(item)
