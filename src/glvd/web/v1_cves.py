# SPDX-License-Identifier: MIT

from typing import (
    Any,
    cast,
)

from quart import Blueprint, current_app, request
import sqlalchemy as sa
from sqlalchemy import (
    bindparam,
    text,
)

from ..database import AllCve, DebCve, DistCpe
from ..database.types import DebVersion
from ..data.cpe import Cpe
from ..data.dist_cpe import DistCpeMapper

bp = Blueprint('nvd', __name__, url_prefix='/v1/cves')


stmt_cve_id = (
    text('''
        SELECT
                all_cve.data AS cve
            FROM
                all_cve
            WHERE
                cve_id = :cve_id
            GROUP BY
                all_cve.cve_id
    ''')
    .bindparams(
        bindparam('cve_id'),
    )
)

stmt_cpe_version = (
    text('''
        WITH data AS (
            SELECT
                    all_cve.data AS cve
                FROM
                    all_cve
                    INNER JOIN deb_cve USING (cve_id)
                    INNER JOIN dist_cpe ON (deb_cve.dist_id = dist_cpe.id)
                WHERE
                    dist_cpe.cpe_vendor = :cpe_vendor AND
                    dist_cpe.cpe_product = :cpe_product AND
                    dist_cpe.cpe_version LIKE :cpe_version AND
                    deb_cve.deb_source = :deb_source AND
                    (
                        deb_cve.deb_version_fixed > :deb_version OR
                        deb_cve.deb_version_fixed IS NULL
                    )
               ORDER BY
                    all_cve.cve_id
            )
        SELECT
            coalesce(json_agg(data.cve), '[]'::json)::text FROM data
    ''')
    .bindparams(
        bindparam('cpe_vendor'),
        bindparam('cpe_product'),
        bindparam('cpe_version'),
        bindparam('deb_source'),
        bindparam('deb_version'),
    )
)

stmt_cpe_vulnerable = (
    text('''
        WITH data AS (
            SELECT
                    all_cve.data AS cve
                FROM
                    all_cve
                    INNER JOIN deb_cve USING (cve_id)
                    INNER JOIN dist_cpe ON (deb_cve.dist_id = dist_cpe.id)
                WHERE
                    dist_cpe.cpe_vendor = :cpe_vendor AND
                    dist_cpe.cpe_product = :cpe_product AND
                    dist_cpe.cpe_version LIKE :cpe_version AND
                    deb_cve.deb_source LIKE :deb_source AND
                    deb_cve.debsec_vulnerable = TRUE
                ORDER BY
                    all_cve.cve_id
            )
        SELECT
            coalesce(json_agg(data.cve), '[]'::json)::text FROM data
    ''')
    .bindparams(
        bindparam('cpe_vendor'),
        bindparam('cpe_product'),
        bindparam('cpe_version'),
        bindparam('deb_source'),
    )
)

headers_cors: dict[str, str] = {
    'Access-Control-Allow-Origin': '*',
}


@bp.route('/<cve_id>')
async def get_cve_id(cve_id: str) -> tuple[Any, int]:
    stmt = stmt_cve_id.bindparams(cve_id=cve_id)

    async with getattr(current_app, 'db_begin')() as conn:
        data = (await conn.execute(stmt)).one_or_none()

        if data:
            return data[0], 200
        else:
            return 'Not found', 404


@bp.route('/findByCpe')
async def get_cpe_name() -> tuple[Any, int]:
    cpe = request.args.get('cpeName', type=Cpe.parse)
    deb_version = request.args.get('debVersionEnd', type=str)

    if cpe is None:
        return 'No CPE', 400
    if not cpe.is_debian:
        return 'Not Debian related CPE', 400

    if cpe.other_debian.deb_source and deb_version:
        stmt = stmt_cpe_version.bindparams(
            cpe_vendor=cpe.vendor,
            cpe_product=cpe.product,
            cpe_version=cpe.version or '%',
            deb_source=cpe.other_debian.deb_source,
            deb_version=deb_version,
        )
    else:
        stmt = stmt_cpe_vulnerable.bindparams(
            cpe_vendor=cpe.vendor,
            cpe_product=cpe.product,
            cpe_version=cpe.version or '%',
            deb_source=cpe.other_debian.deb_source or '%',
        )

    async with getattr(current_app, 'db_begin')() as conn:
        return (
            (await conn.execute(stmt)).one()[0],
            200
        )


@bp.route('/findBySources', methods=['POST', 'OPTIONS'])
async def get_sources() -> tuple[Any, int, dict[str, str]]:
    # Handle pre-flight request to allow CORS
    if request.method == 'OPTIONS':
        return ('', 204, headers_cors)

    async with getattr(current_app, 'db_begin')() as conn:
        # Aggregate by product/codename
        source_by_dist: dict[tuple[str, str], set[tuple[str, str]]] = {}
        for source in (await request.form).getlist('source[]', type=str):
            s = cast(tuple[str, str, str, str], tuple(source.split('_', 4)))
            source_by_dist.setdefault(s[0:2], set()).add(s[2:4])

        # Create dynamic table (as CTE) to find many sources at the same time
        # XXX: Replace with "real" temporary table, use COPY IN, check if this
        # can remove the enormous time spent on compiling queries
        stmts_source = []
        for i, j in source_by_dist.items():
            dist = DistCpeMapper.new(i[0])(i[1])
            dist_id = (await conn.execute(
                sa.select(DistCpe.id)
                .where(DistCpe.cpe_vendor == dist.cpe_vendor)
                .where(DistCpe.cpe_product == dist.cpe_product)
                .where(DistCpe.cpe_version == dist.cpe_version)
            )).one()[0]

            for source, version in j:
                stmts_source.append(
                    sa.select(
                        sa.literal(dist_id).label('dist_id'),
                        sa.literal(source).label('deb_source'),
                        sa.cast(sa.literal(version), DebVersion).label('deb_version'),
                    )
                )

        # If we found no source at all
        if not stmts_source:
            return ('', 400, headers_cors)

        # We deduplicate source entries ourselves, so we can just ask the db to
        # take all entries via "UNION ALL", instead of forcing it to first sort
        # and remove duplicates by using "UNION"
        subquery_source = sa.union_all(*stmts_source).cte(name='source')

        # Find (unique) CVE ID for given sources
        subquery_cve_id = (
            sa.select(DebCve.cve_id)
            .distinct()
            .join(
                subquery_source,
                sa.and_(
                    DebCve.dist_id == subquery_source.c.dist_id,
                    DebCve.deb_source == subquery_source.c.deb_source,
                    sa.or_(
                        DebCve.deb_version_fixed > subquery_source.c.deb_version,
                        DebCve.deb_version_fixed.is_(None),
                    ),
                )
            )
        ).cte()

        # Find CVE data for given ID
        subquery_cve_data = (
            sa.select(AllCve.data)
            .order_by(AllCve.cve_id)
            .join(subquery_cve_id, AllCve.cve_id == subquery_cve_id.c.cve_id)
        ).cte()

        # Generate JSON array
        query = (
            sa.select(
                sa.func.coalesce(
                    # json_agg() creates a JSON array
                    sa.func.json_agg(subquery_cve_data.c.data),
                    # We never want NULL, so we generate an empty array
                    sa.text("'[]'::json")
                )
            )
        )

        return ((await conn.execute(query)).one()[0], 200, headers_cors)
