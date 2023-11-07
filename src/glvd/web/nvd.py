# SPDX-License-Identifier: MIT

from quart import Blueprint, current_app, request
from sqlalchemy import select

from ..database import NvdCve


bp = Blueprint('nvd', __name__)


@bp.route('/rest/json/cves/2.0+deb')
async def nvd_cve_deb():
    # XXX: Replace with view
    stmt = select(NvdCve.data)

    if cve_id := request.args.get('cveId', type=str):
        stmt = stmt.where(NvdCve.cve_id == cve_id)

    async with current_app.db_begin() as conn:
        result = await conn.execute(stmt)

        return {
            'format': 'NVD_CVE',
            'version': '2.0+deb',
            'vulnerabilities': [{'cve': i[0]} for i in result],
        }, 200
