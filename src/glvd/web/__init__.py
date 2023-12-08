# SPDX-License-Identifier: MIT

import collections.abc
import contextlib

from quart import Quart
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine


class QuartDb:
    engine: AsyncEngine

    def __init__(self, app: Quart) -> None:
        # TODO: Use config
        self.engine = create_async_engine(
            "postgresql+asyncpg:///",
            echo=True,
            pool_size=50,
            max_overflow=0,
        )

        setattr(app, 'db_begin', self)

    @contextlib.asynccontextmanager
    async def __call__(self) -> collections.abc.AsyncGenerator[AsyncConnection, None]:
        '''
        Provides an asynchronous SQLAlchemy connection to application.

        All transactions are rolled back, as we don't support writing
        through the application.
        '''
        async with self.engine.begin() as conn:
            yield conn
            await conn.rollback()


def create_app():
    app = Quart(__name__)

    # TODO: Read config

    QuartDb(app)

    from .v1_cves import bp as bp_v1_cves
    app.register_blueprint(bp_v1_cves)

    return app
