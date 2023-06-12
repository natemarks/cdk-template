#!/usr/bin/env python3
# pylint: disable=duplicate-code
"""SubClass of Environment classes
An environment is a deployed instance of the application platform


Subclasses  generally override
 - NAMED_DATA
 - UNIQUE_DATA

 and add set_  methods as appropriate

Create a new subclass of Environment to create a new deployment
"""

from typing import Dict, List
from config.base import (
    FlatStore,
    get_logger,
)
from config.environment import Environment
from config.eks_cluster import EksClusterConfig, EksClusterData
from config.app_vpc import AppVpcConfig, AppVpcData

module_logger = get_logger(str(__name__))


class Environment0(Environment):
    """Deployment 0 implementation of Environment"""

    NAMED_DATA = ["eks_cluster"]  # type: List[str]
    UNIQUE_DATA = ["app_vpc"]

    def __init__(self, flat_store: FlatStore):
        """init attributes for the stack data"""
        super().__init__(flat_store=flat_store)
        self.app_vpc = None  # type: AppVpcData
        self.eks_cluster = {}  # type: Dict[str,EksClusterData|None]

    def set_eks_cluster(self):
        """set self.eks_clusters"""
        config_ids = self.named_config_ids(
            type_prefix=EksClusterConfig.FLATSTORE_PREFIX
        )
        for config_id in config_ids:
            cfg = EksClusterConfig(
                flat_store=self.flat_store,
                env_data=self.environment_data,
                config_id=config_id,
            )
            self.eks_cluster[config_id] = cfg.data

    def set_app_vpc(self):
        """set self.app_vpc"""
        cfg = AppVpcConfig(
            flat_store=self.flat_store,
            env_data=self.environment_data,
        )
        self.app_vpc = cfg.data
