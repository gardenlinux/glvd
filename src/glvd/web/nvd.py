# SPDX-License-Identifier: MIT

from quart import Blueprint, current_app, request
from sqlalchemy import (
    bindparam,
    text,
)

from ..data.cpe import Cpe

bp = Blueprint('nvd', __name__)


stmt_cve_deb_cpe_version = (
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
                json_build_object(
                    'format', 'NVD_CVE',
                    'version', '2.0+deb',
                    'vulnerabilities', coalesce(json_agg(data), '[]'::json)
                )::text
            FROM data
    ''')
    .bindparams(
        bindparam('cpe_vendor'),
        bindparam('cpe_product'),
        bindparam('cpe_version'),
        bindparam('deb_source'),
        bindparam('deb_version'),
    )
)

stmt_cve_deb_cpe_vulnerable = (
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
                json_build_object(
                    'format', 'NVD_CVE',
                    'version', '2.0+deb',
                    'vulnerabilities', coalesce(json_agg(data), '[]'::json)
                )::text
            FROM data
    ''')
    .bindparams(
        bindparam('cpe_vendor'),
        bindparam('cpe_product'),
        bindparam('cpe_version'),
        bindparam('deb_source'),
    )
)

stmt_cve_deb_cve_id = (
    text('''
        WITH data AS (
            SELECT
                    all_cve.data AS cve
                FROM
                    all_cve
                WHERE
                    cve_id = :cve_id
                GROUP BY
                    all_cve.cve_id
            )
        SELECT
                json_build_object(
                    'format', 'NVD_CVE',
                    'version', '2.0+deb',
                    'vulnerabilities', coalesce(json_agg(data), '[]'::json)
                )::text
            FROM data
    ''')
    .bindparams(
        bindparam('cve_id'),
    )
)


@bp.route('/rest/json/cves/2.0+deb')
async def nvd_cve_deb():
    if cpe_name := request.args.get('virtualMatchString', type=str):
        cpe = Cpe.parse(cpe_name)
        if not cpe.is_debian:
            return 'Not Debian related CPE', 400
        if cpe.other.deb_source and (deb_version := request.args.get('debVersionEnd', type=str)):
            stmt = stmt_cve_deb_cpe_version.bindparams(
                cpe_vendor=cpe.vendor,
                cpe_product=cpe.product,
                cpe_version=cpe.version or '%',
                deb_source=cpe.other.deb_source,
                deb_version=deb_version,
            )
        else:
            stmt = stmt_cve_deb_cpe_vulnerable.bindparams(
                cpe_vendor=cpe.vendor,
                cpe_product=cpe.product,
                cpe_version=cpe.version or '%',
                deb_source=cpe.other.deb_source or '%',
            )
    elif cve_id := request.args.get('cveId', type=str):
        stmt = stmt_cve_deb_cve_id.bindparams(cve_id=cve_id)

    async with current_app.db_begin() as conn:
        return (
            (await conn.execute(stmt)).one()[0],
            200
        )
