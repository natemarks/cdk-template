#!/usr/bin/env python3
"""tests for stack/app_vpc.py

"""
# pylint: disable=duplicate-code
import pytest
from aws_cdk import App, assertions
from config.environment0 import Environment0
from stack.app_vpc import get_app_vpc_stack
from tests.helper import Case


@pytest.mark.unit
@pytest.mark.parametrize(
    "",
    [pytest.param(id="dev")],
)
def test_app_vpc_stack(request, update_golden):
    """Compare generated stack to expected"""

    case = Case(request)
    res = Environment0(flat_store=case.input())
    res.set_configs()

    app = App()
    stk = get_app_vpc_stack(
        app=app,
        environment=res,
        termination_protection=False,
    )
    template = assertions.Template.from_stack(stk)
    if update_golden:
        case.update_expected(template.to_json())

    template.template_matches(case.expected())
