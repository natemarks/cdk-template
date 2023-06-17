"""helpers for awsapi modules


"""
import argparse
from dataclasses import dataclass
import boto3
from config.base import get_logger

module_logger = get_logger(str(__name__))


def get_args() -> argparse.Namespace:
    """get args"""
    description = (
        "validate all config data for a hybrid environment. "
        "exit 0 if valid. exit 1 if not"
    )
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "environment",
        type=str,
        help="[sandbox | dev | integration | qeint | staging | production]",
    )
    return parser.parse_args()


@dataclass(frozen=False, kw_only=True)
class AwsCallerIdentity:
    """identity data class. handy for autocompletion"""

    account: str
    arn: str
    user_id: str


def get_caller_identity() -> AwsCallerIdentity:
    """return the current caller identity"""
    client = boto3.client("sts")
    response = client.get_caller_identity()

    return AwsCallerIdentity(
        **{
            "account": response["Account"],
            "arn": response["Arn"],
            "user_id": response["UserId"],
        }
    )
