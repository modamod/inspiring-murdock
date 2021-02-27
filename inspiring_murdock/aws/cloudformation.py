import itertools
import logging
import sys
import time

from boto3.session import Session


def is_valid(
    profile_name: str, region: str, template: "json", endpoint_url: str = None
) -> dict:
    """Function to determine if a stack is valid or not.

    Args:
        profile_name:
            AWS profile name to use to create the boto3 session.
        region:
            AWS region name to use to create boto3 session.
        template:
            Cloudformation template body to validate.
            It should be a valid json object.
        endpoint_url:
            AWS Endpoint could be use to mock AWS requests using moto server.
    Returns
        Dict containing the response from cloudformation service.
    """

    cf = Session(profile_name=profile_name, region_name=region).client(
        "cloudformation", endpoint_url=endpoint_url
    )
    result = cf.validate_template(TemplateBody=template)
    return result


def build(
    profile_name,
    region,
    stack_name,
    template_body,
    parameters,
    tags=None,
    capabilities=None,
    disable_rollback=False,
    endpoint_url=None,
):
    """Function to build a cloudformation stack

    Args:
        profile_name:
            AWS profile name to use to create the boto3 session.
        region:
            AWS region name to use to create boto3 session.
        stack_name:
            Cloudformation stack name.
        template_body:
            Cloudformation template body to validate.
            It should be a valid json object.
        parameters:
            List of Cloudformation compatible parameters dict.
            Example:
                [{
                    "ParameterKey": "key",
                    "ParameterValue": "value",
                    "UsePreviousValue": False,
                    "ResolvedValue": "",
                }]
        tags:
            List of Cloudformation compatible tags.
            Example:
                [{
                    "Key": "tag1",
                    "Value": "value1
                }]
        capabilities:
            List of AWS IAM capabilities.
            Example:

        endpoint_url:
            AWS Endpoint could be use to mock AWS requests using moto server.
    """
    if endpoint_url is not None:
        cf = Session(profile_name=profile_name, region_name=region).client(
            "cloudformation", endpoint_url=endpoint_url
        )
    else:
        cf = Session(profile_name=profile_name, region_name=region).client(
            "cloudformation"
        )

    list_capabilities = [] if capabilities is None else capabilities
    list_tags = [] if tags is None else tags

    result = cf.create_stack(
        TemplateBody=template_body,
        Parameters=parameters,
        StackName=stack_name,
        DisableRollback=disable_rollback,
        Capabilities=list_capabilities,
        Tags=list_tags,
    )
    return result


def describe_stack(profile_name, region, stack_name, endpoint_url=None):
    cf = Session(profile_name=profile_name, region_name=region).client(
        "cloudformation", endpoint_url=endpoint_url
    )

    response = cf.describe_stacks(StackName=stack_name)

    return response


def get_cf_status(profile_name, region, stack_name, endpoint_url=None):

    response = describe_stack(
        profile_name, region, stack_name, endpoint_url=endpoint_url
    )

    return {
        "StackStatus": response.get("Stacks")[0].get("StackStatus"),
        "StackStatusReason": response.get("Stacks")[0].get("StackStatusReason"),
    }


def get_cf_events(profile_name, region, stack_name, endpoint_url=None):
    """Function that returns cf events."""
    cf = Session(profile_name=profile_name, region_name=region).client(
        "cloudformation", endpoint_url=endpoint_url
    )
    paginator = cf.get_paginator("describe_stack_events")
    pages = paginator.paginate(StackName=stack_name)
    events = (
        itertools.chain(*map(lambda x: x.get("StackEvents"), pages))
        if pages
        else iter(())
    )
    return events


def delete(profile_name, region, stack_name, endpoint_url=None):

    cf = Session(profile_name=profile_name, region_name=region).client("cloudformation")

    result = cf.delete_stack(StackName=stack_name)

    return result
