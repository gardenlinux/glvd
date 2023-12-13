# SPDX-License-Identifier: MIT

import pytest

from glvd.data.cvss import CvssSeverity


class TestCvssSeverity:
    @pytest.mark.parametrize('score,value', [
        (0, CvssSeverity.NONE),
        (1, CvssSeverity.LOW),
        (4, CvssSeverity.MEDIUM),
        (7, CvssSeverity.HIGH),
        (9, CvssSeverity.CRITICAL),
        (10, CvssSeverity.CRITICAL),
    ])
    def test_from_score(self, score, value):
        a = CvssSeverity.from_score(score)
        assert a is value

    @pytest.mark.parametrize('score', [-0.1, 10.1])
    def test_from_score_fail(self, score):
        with pytest.raises(ValueError):
            CvssSeverity.from_score(score)
