#!/usr/bin/env python3
"""Stack for an EKS cluster


"""
from typing import Dict
from constructs import Construct
from aws_cdk import App, Stack, aws_eks as eks, aws_ec2 as ec2
from aws_cdk.lambda_layer_kubectl import KubectlLayer
from aws_cdk import Environment as cdk_environment
from config.environment0 import Environment0
from config.eks_cluster import EksClusterData
from stack.app_vpc import AppVpcStack


class EksClusterStack(Stack):
    """Eks Cluster Stack"""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        data: EksClusterData,
        app_vpc_stack: AppVpcStack,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.data = data  # type: EksClusterData
        # provisioning a cluster
        cluster = eks.Cluster(
            self,
            f"{self.data.construct_id_prefix}EksCluster",
            version=eks.KubernetesVersion.V1_26,
            kubectl_layer=KubectlLayer(
                self, f"{self.data.construct_id_prefix}Kubectl"
            ),
            vpc=app_vpc_stack.vpc,
            vpc_subnets=[
                ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)
            ],
        )

        # apply a kubernetes manifest to the cluster
        cluster.add_manifest(
            "mypod",
            {
                "api_version": self.data.api_version,
                "kind": self.data.kind,
                "metadata": {"name": "mypod"},
                "spec": {
                    "containers": [
                        {
                            "name": self.data.app_name,
                            "image": self.data.app_image,
                            "ports": [{"container_port": self.data.app_port}],
                        }
                    ]
                },
            },
        )


def get_eks_cluster_stacks(
    app: App,
    environment: Environment0,
    app_vpc_stack: AppVpcStack,
    termination_protection=False,
    cdk_env=cdk_environment(),
) -> Dict[str, EksClusterStack]:
    """return the star"""
    result = {}  # type: Dict[str, EksClusterStack]

    for config_id, stack_data in environment.eks_cluster.items():
        result[config_id] = EksClusterStack(
            app,
            f"{stack_data.construct_id_prefix}Stack",
            env=cdk_env,
            data=stack_data,
            termination_protection=termination_protection,
            app_vpc_stack=app_vpc_stack,
        )
        result[config_id].add_dependency(app_vpc_stack)
    return result
