# vim: set fileencoding=utf-8 :

import pytest
from typing import Tuple


@pytest.mark.parametrize(
    "vals",
    [
        (True, True),
        (False, False),
    ],
)
def test_example(vals: Tuple[bool, bool]) -> None:
    expected, actual = vals
    assert expected == actual
