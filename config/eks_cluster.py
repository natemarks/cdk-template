#!/usr/bin/env python3
"""data classes for stack/eks_cluster.py

"""
from dataclasses import dataclass
from config.base import (
    get_logger,
    EnvironmentData,
    FlatStore,
    StackConfig,
    NamedStackConfig,
)

module_logger = get_logger(str(__name__))


@dataclass(frozen=False, kw_only=True)
class EksClusterData:  # pylint: disable=too-many-instance-attributes
    """Data required to configure an EKS cluster stack
    NOTE: Frozen is false to allow the post_init to update the attribute
    """

    config_id: str
    api_version: str
    kind: str
    app_name: str
    app_image: str
    app_port: int
    # used to form the construct ID of the stack and each resource
    # example usage: . f"{app_env.stack_prefix}{data.stack_prefix}"
    #  -> DevEksClusterHelloMyResource
    construct_id_prefix: str = ""


# pylint: disable=too-few-public-methods
class EksClusterConfig(NamedStackConfig):
    """manage EksClusterData object"""

    FLATSTORE_PREFIX = f"{StackConfig.BASE_FLATSTORE_PREFIX}/eks_cluster/"
    LOGICAL_STACK_TYPE_PREFIX = "EksCluster"

    def __init__(
        self, flat_store: FlatStore, env_data: EnvironmentData, config_id: str
    ):
        super().__init__(
            flat_store=flat_store, env_data=env_data, config_id=config_id
        )
        self.related_keys = self.get_data_dict(
            flatstore_prefix=f"{type(self).FLATSTORE_PREFIX}{config_id}/",
            logical_stack_type_prefix=type(self).LOGICAL_STACK_TYPE_PREFIX,
            config_id=self.config_id,
        )
        # pylint: disable=missing-kwoa
        try:
            self.data = EksClusterData(
                **self.related_keys
            )  # type: EksClusterData
        except TypeError as err:
            module_logger.error(err)
            self.data = None
