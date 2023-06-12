#!/usr/bin/env python3
""" application vpc

"""
from aws_cdk import App, Stack, aws_ec2 as ec2
from aws_cdk import Environment as cdk_environment
from constructs import Construct
from config.app_vpc import AppVpcData
from config.environment0 import Environment0


class AppVpcStack(Stack):
    """AppVpc Stack"""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        data: Environment0,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.data = data.app_vpc  # type: AppVpcData
        self.app_env = data
        vpc_name = f"my_app_vpc_{self.app_env.environment_data.config_id}"
        self.vpc = ec2.Vpc(
            self,
            f"{self.data.construct_id_prefix}AppVpc",
            max_azs=self.data.max_azs,
            ip_addresses=ec2.IpAddresses.cidr(self.data.cidr),
            vpc_name=vpc_name,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name=f"{vpc_name}_public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                ),
                ec2.SubnetConfiguration(
                    name=f"{vpc_name}_private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                ),
                ec2.SubnetConfiguration(
                    name=f"{vpc_name}_isolated",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                ),
            ],
        )
        # add VPC interface endpoints
        self.vpc.add_interface_endpoint(
            "EC2", service=ec2.InterfaceVpcEndpointAwsService.EC2
        )
        self.vpc.add_interface_endpoint(
            "EC2_MESSAGES",
            service=ec2.InterfaceVpcEndpointAwsService.EC2_MESSAGES,
        )
        self.vpc.add_interface_endpoint(
            "SSM", service=ec2.InterfaceVpcEndpointAwsService.SSM
        )
        self.vpc.add_interface_endpoint(
            "SSM_MESSAGES",
            service=ec2.InterfaceVpcEndpointAwsService.SSM_MESSAGES,
        )
        self.vpc.add_interface_endpoint(
            "SECRETS_MANAGER",
            service=ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER,
        )


def get_app_vpc_stack(
    app: App,
    environment: Environment0,
    termination_protection=False,
    cdk_env=cdk_environment(),
) -> AppVpcStack:
    """return the app_vpc stack"""
    return AppVpcStack(
        app,
        f"{environment.app_vpc.construct_id_prefix}Stack",
        env=cdk_env,
        data=environment,
        termination_protection=termination_protection,
    )
