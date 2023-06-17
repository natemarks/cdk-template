""" awsapi.helper module
"""
import pytest
from awsapi.helper import get_caller_identity


@pytest.mark.dev
def test_get_caller_identity():
    """just check the account number"""
    result = get_caller_identity()
    assert result.account == "709310380790"
