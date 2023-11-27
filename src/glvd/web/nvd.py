# SPDX-License-Identifier: MIT

from quart import Blueprint, current_app, request
from sqlalchemy import (
    bindparam,
    text,
)

bp = Blueprint('nvd', __name__)


# XXX: Can we replace that with a view, which combines data and data_configurations in the database?
stmt_cve_deb_cve_id = (
    text('''
        SELECT
                nvd_cve.data
                , array_to_json(array_remove(array_agg(deb_cve.data_cpe_match), NULL)) AS data_cpe_matchess
            FROM
                nvd_cve
                LEFT OUTER JOIN deb_cve USING (cve_id)
            WHERE cve_id = :cve_id
            GROUP BY (nvd_cve.data)
    ''')
    .bindparams(
        bindparam('cve_id'),
    )
)


@bp.route('/rest/json/cves/2.0+deb')
async def nvd_cve_deb():
    if cve_id := request.args.get('cveId', type=str):
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
