# SPDX-License-Identifier: MIT

from quart import Blueprint, current_app, request
from sqlalchemy import (
    bindparam,
    text,
)

from ..data.cpe import Cpe

bp = Blueprint('nvd', __name__)


# XXX: Can we replace that with a view, which combines data and data_configurations in the database?
stmt_cve_deb_cpe_version = (
    text('''
        SELECT
                nvd_cve.data,
                array_to_json(
                    array_remove(
                        array_agg(deb_cve.data_cpe_match),
                        NULL
                    )
                ) AS data_cpe_matches
            FROM
                nvd_cve
                LEFT OUTER JOIN deb_cve USING (cve_id)
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
            GROUP BY
                nvd_cve.cve_id
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
        SELECT
                nvd_cve.data,
                array_to_json(
                    array_remove(
                        array_agg(deb_cve.data_cpe_match),
                        NULL
                    )
                ) AS data_cpe_matches
            FROM
                nvd_cve
                LEFT OUTER JOIN deb_cve USING (cve_id)
                INNER JOIN dist_cpe ON (deb_cve.dist_id = dist_cpe.id)
            WHERE
                dist_cpe.cpe_vendor = :cpe_vendor AND
                dist_cpe.cpe_product = :cpe_product AND
                dist_cpe.cpe_version LIKE :cpe_version AND
                deb_cve.deb_source LIKE :deb_source AND
                deb_cve.debsec_vulnerable = TRUE
            GROUP BY
                nvd_cve.cve_id
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
        SELECT
                nvd_cve.data,
                array_to_json(
                    array_remove(
                        array_agg(deb_cve.data_cpe_match),
                        NULL
                    )
                ) AS data_cpe_matches
            FROM
                nvd_cve
                LEFT OUTER JOIN deb_cve USING (cve_id)
            WHERE
                cve_id = :cve_id
            GROUP BY
                nvd_cve.cve_id
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
        results = []
        async for r in await conn.stream(stmt):
            data, data_cpe_matches = r
            if data_cpe_matches:
                data.setdefault('configurations', []).append({
                    'nodes': [{
                        'cpeMatch': data_cpe_matches,
                        'negate': False,
                        'operator': 'OR',
                    }],
                })
            results.append({
                'cve': data,
            })

        return {
            'format': 'NVD_CVE',
            'version': '2.0+deb',
            'vulnerabilities': results,
        }, 200
