# pylint: disable=line-too-long,duplicate-code,redefined-outer-name
""" Test base and example config classes
"""
import pytest
from tests.helper import Case
from config.environment0 import Environment, Environment0


@pytest.mark.unit
@pytest.mark.parametrize(
    "",
    [
        pytest.param(id="dev"),
    ],
)
def test_environment0(request, update_golden):
    """test Environment0 data

    Each test case creates an Environment0 object from flat store data and compares
    the Environment0.as_dict() output to the expected data in the golden file

    """
    case = Case(request)
    res = Environment0(flat_store=case.input())
    res.set_configs()
    if update_golden:
        case.update_expected(res.as_dict())
    assert res.as_dict() == case.expected()


@pytest.mark.unit
@pytest.mark.parametrize(
    "",
    [
        pytest.param(id="dev"),
    ],
)
def test_environment_validate(request, update_golden):
    """validate sets the .valid attribute"""
    case = Case(request)
    res = Environment0(flat_store=case.input())
    res.set_configs()
    if update_golden:
        case.update_expected(res.flat_store)
    assert res.valid()


@pytest.mark.unit
@pytest.mark.parametrize(
    "",
    [
        pytest.param(id="dev"),
    ],
)
def test_environment_data_path(request):
    """use environment_data_path to load an environment
    confirm it correctly returns the path to the project static environment data
    """
    case = Case(request)
    flat_store = Environment.load_from_json(
        Environment0.environment_data_path(case.case_name)
    )
    res = Environment0(flat_store=flat_store)
    res.set_configs()
    assert res.environment_data.config_id == case.case_name
