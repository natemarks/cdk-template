#!/usr/bin/env python3
# pylint: disable=missing-kwoa, duplicate-code, too-few-public-methods
"""Base classes for managing stack configuration data

Environment Configuration: configuration data common to every stak in the environment

Stack Configuration:  configuration data unique to a stack. A stack that deploys an ECS
cluster requires a different type of configuration data from a stack that deploys a
zookeeper cluster in an ASG

When planning a new stack, decide if it can be deployed more than once in an
environment (app). If it can create a new subclass from NamedStackConfig.  Refer to the
EksCluster example

If not - it's UNIQUE in an environment - create a new subclass from UniqueStackConfig.
refer to the EnvironmentConfig

All the data for an environment is stored in a simple, flat key/value scheme with no
nesting. I call it a "flat store" and it's trivially easy to work with.  The keys are a
prefix chain that allows related values to be grouped together. Values are limited to
simple JSON-supported types: strings, numbers and booleans. We permit a value that is
an array of those, as well. The value can't be a map - that would be nesting

example:
ENVIRONMENT = {
    # DEV ENVIRONMENT WIDE CONFIG DATA
    "/app/env/admin_team": "Operations",
    "/app/env/aws_account_name": "MyApp Dev",
    "/app/env/id": "dev",
    "/app/env/stack_prefix": "Dev",
    "/app/env/aws_account_number": "0123456789",
    "/app/env/default_domain": "dev.myapp.com",
    "/app/env/default_region": "us-east-1",
}

"""
import logging
import sys

from dataclasses import dataclass
from typing import Dict, List

FlatStore = Dict[
    str,
    str | int | bool | List[str | int | bool] | Dict[str, str | int | bool],
]
FLAT_STORE_SEP = (
    "/"  # the flat store key separator. not found in related key Dicts
)


def get_logger(module_name: str) -> logging.Logger:
    """return standard logger
    usage:
    MODULE_LOGGER = get_logger(str(__name__))
    """
    my_logger = logging.getLogger(module_name)
    my_logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        "%(asctime)s - {%(name)s} - {%(filename)s:%(funcName)s:%(lineno)d} - "
        "%(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)

    my_logger.addHandler(console_handler)
    return my_logger


module_logger = get_logger(str(__name__))


def get_key_subtree(flat_store: FlatStore, prefix: str) -> FlatStore:
    """get FlatStore of related keys from global FlatStore
    this DOES NOT filter out keys that contain FLAT_STORE_SEP
    ex. return a simple dict only of the keys and values at the /a/b/c/
        level
    prefix = "/a/b/c/"
    config_data = {
        "/a/b/bkey1": "bval1",
        "/a/b/c/ckey1": "cval1",
        "/a/b/c/ckey2": "cval2",
        "/a/b/c/d/dkey1": "dval1",
    }

    return:
     {
        "ckey1": "cval1,
        "ckey2": "cval2
     }


    :param flat_store:
    :param prefix:
    :return:
    """

    new_dict = {}
    for k, v in flat_store.items():  # pylint: disable=invalid-name
        if k.startswith(prefix):
            key = k.removeprefix(prefix)
            new_dict[key] = v
    return new_dict


@dataclass(frozen=True, kw_only=True)
class EnvironmentData:  # pylint: disable=too-many-instance-attributes
    """App environment config data used for all stacks"""

    admin_team: str  # ex. "Operations"
    aws_account_name: str  # ex. "MyApp Dev"
    aws_account_number: str  # ex. "0123456789"
    default_domain: str  # ex. "dev.myapp.com"
    default_region: str  # ex. "us-east-1"
    config_id: str  # ex. "dev"
    stack_prefix: str  # ex. "Dev"


class StackConfig:
    """base class for a stack configuration data object"""

    BASE_FLATSTORE_PREFIX = "/app/env"

    def __init__(self, flat_store: FlatStore, env_data: EnvironmentData):
        self.flat_store = flat_store  # type: FlatStore
        # related_keys is the FlatStore data containing teh related keys for a single
        # config. The keys will not have prefixes and can be used as dataclass kwargs
        self.related_keys = {}  # type: FlatStore
        self.data = None
        self.flatstore_prefix = None  # type: str
        self.env_data = env_data  # type: EnvironmentData

    @classmethod
    def get_related_keys(cls, flat_store: FlatStore, prefix: str) -> FlatStore:
        """get FlatStore of related keys from global FlatStore
        This filters out keys that contain FLAT_STORE_SEP

        ex. return a simple dict only of the keys and values at the /a/b/c/
            level
        prefix = "/a/b/c/"
        config_data = {
            "/a/b/bkey1": "bval1",
            "/a/b/c/ckey1": "cval1",
            "/a/b/c/ckey2": "cval2",
            "/a/b/c/d/dkey1": "dval1",
        }

        return:
         {
            "ckey1": "cval1,
            "ckey2": "cval2
         }


        :param flat_store:
        :param prefix:
        :return:
        """

        new_dict = {}
        for k, v in flat_store.items():  # pylint: disable=invalid-name
            if k.startswith(prefix):
                key = k.removeprefix(prefix)
                if FLAT_STORE_SEP not in key:
                    new_dict[key] = v
        return new_dict


class UniqueStackConfig(StackConfig):
    """base class for a unique stack config

    a unique stack is one that is only deployed once within an app. It is required in
    for the environment to be valid.It DOES NOT require a config_id attribute to get
    the related keys from the flat store.
    """

    def __init__(self, flat_store: FlatStore, env_data: EnvironmentData):
        super().__init__(flat_store=flat_store, env_data=env_data)
        self.data = None  # type: UniqueStackData
        self.construct_id_prefix = ""

    def get_data_dict(
        self,
        flatstore_prefix: str,
        logical_stack_type_prefix: str,  # ex. "EksCluster"
    ) -> FlatStore:
        """

        :return:
        """
        self.construct_id_prefix = (
            f"{self.env_data.stack_prefix}" f"{logical_stack_type_prefix}"
        )
        result = {
            "construct_id_prefix": self.construct_id_prefix,
        }
        result.update(
            type(self).get_related_keys(self.flat_store, flatstore_prefix)
        )
        return result


class NamedStackConfig(StackConfig):
    """base class for a named stack config

    a named stack is one that can be deployed zero or multiple times (it's optional) in
    an app with different, named configurations. These stacks need a 'config_id' string
    to get the related keys from the flat store.
    """

    def __init__(
        self, flat_store: FlatStore, env_data: EnvironmentData, config_id: str
    ):
        super().__init__(flat_store=flat_store, env_data=env_data)
        self.config_id = config_id  # type: str
        self.data = None
        self.construct_id_prefix = ""

    def get_data_dict(
        self,
        flatstore_prefix: str,
        logical_stack_type_prefix: str,  # ex. "EksCluster"
        config_id: str,
    ) -> FlatStore:
        """

        :return:
        """
        self.construct_id_prefix = (
            f"{self.env_data.stack_prefix}"
            f"{logical_stack_type_prefix}"
            f"{config_id.capitalize()}"
        )
        result = {
            "config_id": config_id,
            "construct_id_prefix": self.construct_id_prefix,
        }
        result.update(
            type(self).get_related_keys(self.flat_store, flatstore_prefix)
        )
        return result
