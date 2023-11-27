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
async def db_conn(db_engine):
    '''
    Provides an asynchronous SQLAlchemy database connection.

    This should never be commited, or it will affect other tests.
    '''
    async with db_engine.begin() as conn:
        yield conn
        await conn.rollback()


@pytest.fixture
async def db_session(db_engine):
    '''
    Provides an asynchronous SQLAlchemy database session.

    This should never be commited, or it will affect other tests.
    '''
    async with async_sessionmaker(db_engine)() as session:
        yield session
        await session.rollback()
