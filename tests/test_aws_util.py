"""Test module for inspiring_murdock.aws.util package"""

from inspiring_murdock.aws.util import to_cf_params


def test_to_cf_params():
    empty_params = {}
    assert not to_cf_params(empty_params)
    params = {"Param1": "Value1", "Param2": "Value2", "Param3": "Value3"}
    result = to_cf_params(params)
    assert result
    assert len(result) == 3
    assert result[0].get("ParameterKey") == "Param1"
    assert result[0].get("ParameterValue") == "Value1"
    assert not result[0].get("UsePreviousValue")
    assert result[0].get("ResolvedValue") == ""
