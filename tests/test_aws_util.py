import random

import pytest
from botocore import exceptions
from inspiring_murdock.aws.util import session, to_cf_params


def test_session():
    aws_session = session()
    assert aws_session.region_name == "us-east-1"
    assert aws_session.profile_name == "default"

    with pytest.raises(exceptions.ProfileNotFound):
        session(profile=f"RandomProfileName{random.random()}")


def test_to_cf_params():
    empty_params = {}
    assert not to_cf_params(empty_params)
    params = {"Param1": "Value1", "Param2": "Value2", "Param3": "Value3"}
    result = to_cf_params(params)
    assert result
    assert len(result) == 3
    assert result[0].get('ParameterKey') == 'Param1'
    assert result[0].get('ParameterValue') == 'Value1'
    assert not result[0].get('UsePreviousValue')
    assert result[0].get('ResolvedValue') == ''
