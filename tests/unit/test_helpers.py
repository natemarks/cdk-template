""" Test the test helper functions
"""
# pylint: disable=redefined-outer-name
import pytest

from tests.helper import Case


@pytest.mark.unit
@pytest.mark.parametrize(
    "",
    [
        pytest.param(id="111"),
        pytest.param(id="222"),
    ],
)
def test_parametrize_case(request, update_golden):
    """test helper Case class with a table test"""
    res = Case(request)
    if update_golden:
        res.update_expected(res.input().upper())
    assert res.expected() == res.input().upper()


@pytest.mark.unit
def test_simple_case(request, update_golden):
    """test helper Case class with a simple test"""
    res = Case(request)
    if update_golden:
        res.update_expected(res.input().upper())
    assert res.expected() == res.input().upper()
