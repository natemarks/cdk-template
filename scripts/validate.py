"""validate the entire config for an environment
exit 0 if it's valid. exit 1 if not
"""
import argparse
import sys
from config.environment0 import Environment0


def get_args() -> argparse.Namespace:
    """get args"""
    description = (
        "validate all config data for an environment. "
        "exit 0 if valid. exit 1 if not"
    )
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "environment",
        type=str,
        help="[ dev | staging | production]",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    flat_store = Environment0.load_from_json(
        Environment0.environment_data_path(args.environment)
    )
    env = Environment0(flat_store=flat_store)
    if env.valid():
        sys.exit(0)
    sys.exit(1)
