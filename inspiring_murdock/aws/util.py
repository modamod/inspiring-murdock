"""Util module hoding functions used in the rest of the package."""

import time

import boto3


def session(profile=None, region=None):
    """Util function to return boto3 session

     Args:
         profile: aws profile name to use, defaults to None to use default profile.
         region: aws region name to use, defaults to "us-east-1".

    ."""
    return boto3.session.Session(profile_name=profile, region_name=region)


def to_cf_params(params_dict, use_previous=False):
    """Utility function to convert parameters dict to cloudformation parameters."""
    result = []
    for key, value in params_dict.items():
        result.append(
            {
                "ParameterKey": key,
                "ParameterValue": value,
                "UsePreviousValue": use_previous,
                "ResolvedValue": "",  # Hardcoded, since I am not going to use ssm for parameters just yet
            }
        )
    return result


def get_account_id(session):
    """Utility function that returns account id."""

    sts_client = session.client("sts")
    caller_identity = sts_client.get_caller_identity()

    return caller_identity.get("Account")
