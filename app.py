#!/usr/bin/env python3
# pylint: disable=duplicate-code
"""  CDK Application
"""
import aws_cdk as cdk
from stack.app_vpc import AppVpcStack, get_app_vpc_stack
from stack.eks_cluster import EksClusterStack, get_eks_cluster_stacks

from config.environment0 import Environment0


app = cdk.App()

# set app env name from user input
app_env_name = app.node.try_get_context("app_env")
# create Environment with static project data (ex. data/dev.json)
flat_store = Environment0.load_from_json(
    Environment0.environment_data_path(app_env_name)
)
app_env = Environment0(flat_store=flat_store)
app_env.set_configs()

# tag all the resources in the application
# eventually replace env_id tags with app_env, but some code may look for it
cdk.Tags.of(app).add("env_id", app_env.environment_data.config_id)
cdk.Tags.of(app).add("app_env", app_env.environment_data.config_id)
cdk.Tags.of(app).add("Environment", app_env.environment_data.config_id)
cdk.Tags.of(app).add("iac", "cdk-template")

# set the cdk_environment
cdk_env = cdk.Environment(
    account=app_env.environment_data.aws_account_number,
    region=app_env.environment_data.default_region,
)

app_vpc = get_app_vpc_stack(
    app=app,
    cdk_env=cdk_env,
    environment=app_env,
    termination_protection=False,
)  # type: AppVpcStack


eks_cluster = get_eks_cluster_stacks(
    app=app,
    cdk_env=cdk_env,
    environment=app_env,
    termination_protection=False,
    app_vpc_stack=app_vpc,
)  # type: Dict[str, EksClusterStack]


app.synth()
