#!/usr/bin/env python3
"""data classes for stack/app_vpc.py

"""
from dataclasses import dataclass
from config.base import (
    get_logger,
    EnvironmentData,
    FlatStore,
    StackConfig,
    UniqueStackConfig,
)

module_logger = get_logger(str(__name__))


@dataclass(frozen=True, kw_only=True)
class AppVpcData:  # pylint: disable=too-many-instance-attributes
    """Data required to instantiate stack.app_vpc.AppVpcStack"""

    cidr: str  #
    max_azs: int  # ex. 2 for pre-prod, 3 for prod
    termination_protection: bool  # set for the VPC Stack
    # used to form the construct ID of the stack and each resource
    # example usage: . f"{app_env.stack_prefix}{data.stack_prefix}"
    #  -> DevAppVpcMyResource
    construct_id_prefix: str


# pylint: disable=too-few-public-methods
class AppVpcConfig(UniqueStackConfig):
    """manage an instance of config.app_vpc.AppVpcData"""

    FLATSTORE_PREFIX = f"{StackConfig.BASE_FLATSTORE_PREFIX}/app_vpc/"
    LOGICAL_STACK_TYPE_PREFIX = "AppVpc"

    def __init__(self, flat_store: FlatStore, env_data: EnvironmentData):
        super().__init__(flat_store=flat_store, env_data=env_data)
        self.env_data = env_data

        self.related_keys = self.get_data_dict(
            flatstore_prefix=type(self).FLATSTORE_PREFIX,
            logical_stack_type_prefix=type(self).LOGICAL_STACK_TYPE_PREFIX,
        )
        try:
            # pylint: disable=missing-kwoa
            self.data = AppVpcData(**self.related_keys)  # type: AppVpcData
        except TypeError as err:
            module_logger.error(err)
            self.data = None

    @classmethod
    def to_flat_store(cls, data: AppVpcData) -> FlatStore:
        """return the flat store keys for the given AppVpcData"""
        attributes = ["cidr", "max_azs", "termination_protection"]
        result = {}
        for attr in attributes:
            result[f"{AppVpcConfig.FLATSTORE_PREFIX}{attr}"] = getattr(
                data, attr
            )
        return result
