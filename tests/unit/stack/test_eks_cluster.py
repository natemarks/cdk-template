#!/usr/bin/env python3
"""test stack/eks_cluster.py

"""
import pytest
from aws_cdk import App, assertions
from config.environment0 import Environment0
from stack.app_vpc import AppVpcStack, get_app_vpc_stack
from stack.eks_cluster import EksClusterStack, get_eks_cluster_stacks
from tests.helper import Case


@pytest.mark.unit
@pytest.mark.parametrize(
    "",
    [pytest.param(id="dev")],
)
def test_eks_cluster_stack(request, update_golden):
    """Compare the EU Stacks to known good golden files"""

    case = Case(request)
    res = Environment0(flat_store=case.input())
    res.set_configs()

    app = App()

    app_vpc = get_app_vpc_stack(
        app=app,
        environment=res,
        termination_protection=False,
    )  # type: AppVpcStack

    eks_clusters = get_eks_cluster_stacks(
        app=app,
        environment=res,
        termination_protection=False,
        app_vpc_stack=app_vpc,
    )  # type: Dict[str, EksClusterStack]

    templates = {}  # type: Dict[str, cdk.assertions.Template]
    for stk_name, stk in eks_clusters.items():
        templates[stk_name] = assertions.Template.from_stack(stk)

    if update_golden:
        for tpl_name, tpl in templates.items():
            case.update_expected(
                data=tpl.to_json(), file_name=f"{tpl_name}.json"
            )

    for tpl_name, tpl in templates.items():
        tpl.template_matches(case.read_json(f"{tpl_name}.json"))
