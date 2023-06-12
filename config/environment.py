#!/usr/bin/env python3
# pylint: disable=duplicate-code
"""Environment classes
An environment is a deployed instance of the applicatrion platform

Create a new subclass of Environment to create a new deployment
"""
import copy
from dataclasses import asdict
import json
import pathlib
from typing import Any, Dict, List
from config.base import (
    StackConfig,
    FlatStore,
    EnvironmentData,
    get_key_subtree,
    FLAT_STORE_SEP,
    get_logger,
)


module_logger = get_logger(str(__name__))


class Environment:
    """Base class for an environment

    The environment may change substantially from one release to the next. For these
    changes, create new subclasses for this class.

    Environment0 is an example of an Environment subclass

    """

    # stack data types to validate in the class. ALWAYS OVERRIDE IN SUBCLASS
    NAMED_DATA = []  # type: List[str]
    UNIQUE_DATA = []  # type: List[str]

    KEY_PREFIX = {
        "EnvironmentConfig": "/app/env/",
    }

    VALID_ENV_IDS = [
        "dev",
        "staging",
        "production",
    ]

    def __init__(self, flat_store: FlatStore):
        # store flat global config dict
        self.flat_store = flat_store  # type: FlatStore
        self.environment_data = None  # type: EnvironmentData
        self.set_environment_data()

    @classmethod
    def environment_data_path(cls, app_env: str):
        """return the path to an environment JSON file in the project"""
        result = pathlib.Path(__file__).parent.parent / f"data/{app_env}.json"
        return str(result)

    def named_config_ids(self, type_prefix: str) -> List[str]:
        """return a list of all config_id in a FlatStore for a single type of named config

        given a prefix for all of a certain type of NamedStackConfigs (
        ex."/app/env/lambda/bootstrap_rds/")
        """
        result = []  # type: List[str]
        related = get_key_subtree(self.flat_store, type_prefix)
        for key in related:
            config_id = key.split(FLAT_STORE_SEP)[0]
            if not config_id in result:
                result.append(config_id)
        return result

    @classmethod
    def load_from_json(cls, file_path: str):
        """safe json data to self.flat_store"""
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data

    def write_to_json(self, file_path: str):
        """write self._update_flat_store to json file"""
        with open(file_path, "w", encoding="utf-8") as outfile:
            outfile.write(json.dumps(self.flat_store, indent=4))

    def set_environment_data(self):
        """load environment data from default data source(project static data)"""
        related_keys = StackConfig.get_related_keys(
            flat_store=self.flat_store,
            prefix="/app/env/",
        )
        # pylint: disable=missing-kwoa
        self.environment_data = EnvironmentData(**related_keys)

    def all_named_data(self) -> Dict[str, Dict[str, FlatStore]]:
        """using the cls.NAMED_DATA, return the values of all attributes

        Used to make it easy to manage the list of named stack data attributes in the
        subclasses all in one place. This is really important to make it hard to forget
        to add one manually to the validate process

        example:
        cls.NAMED_DATA = ['eks_cluster']

        ->
        [
        {
            'bootstrap_lambdas': ...bootstrap_lambda_attribute value,
            'eks_cluster': ...eks_cluster_attribute_value
        """
        result = {}
        for named in type(self).NAMED_DATA:
            result[named] = getattr(self, named)
        return result

    def all_unique_data(self) -> Dict[str, FlatStore]:
        """using the cls.UNIQUE_DATA, return the values of all attributes

        Used to make it easy to manage the list of unique stack data attributes in the
        subclasses all in one place. This is really important to make it hard to forget
        to add one manually to the validate process

        example:
        cls.UNIQUE = ['app_vpc']

        ->
        {
            'app_vpc': ...app_vpc_attribute value
        """
        result = {}
        for unique in type(self).UNIQUE_DATA:
            result[unique] = getattr(self, unique)
        return result

    def validate_all_named(self):
        """return False if any of the named configs are missing data"""
        result = True
        for attr_type, data in self.all_named_data().items():
            for config, value in data.items():
                if value is None:
                    module_logger.error(
                        "expected data for %s:%s. got None", attr_type, config
                    )
                    result = False
                    continue

                module_logger.info("found data for %s:%s", attr_type, config)
        return result

    def validate_all_unique(self):
        """return False if any of the unique configs are missing data"""
        result = True
        for config, value in self.all_unique_data().items():
            if value is None:
                module_logger.error("expected data for %s. got None", config)
                result = False
                continue

            module_logger.info("found data for %s", config)
        return result

    def set_configs(self):
        """dfggf"""
        configs = []
        configs.extend(type(self).NAMED_DATA)
        configs.extend(type(self).UNIQUE_DATA)
        for config in configs:
            getattr(self, f"set_{config}")()

    def valid(self):
        """validate all environment configs

        If any attribute that should contain a dataclass is set to None, return false
        """
        result = True
        # check for None in places where data should be
        if not self.validate_all_named():
            result = False
        if not self.validate_all_unique():
            result = False
        return result

    def as_dict(self) -> {str, Any}:
        """return the environment object data as a nested dict"""
        # gather the base data
        result = {
            "flat_store": self.flat_store,
            "environment_data": asdict(self.environment_data),
        }
        # NAMED_DATA is overridden in the subclass. use that to find the named stack data
        # ex. named_configs['eks_cluster']['hello']['setting1']
        named_configs = {}
        for named in self.NAMED_DATA:
            this_type = copy.deepcopy(getattr(self, named))
            for config_id, data in this_type.items():
                this_type[config_id] = asdict(data)
                named_configs[named] = this_type
        result.update(named_configs)
        # UNIQUE_DATA is overridden in the subclass.
        # ex. unique_configs['app_vpc']['setting1']
        unique_configs = {}
        for unique in self.UNIQUE_DATA:
            unique_configs[unique] = asdict(getattr(self, unique))
        result.update(unique_configs)
        return result
