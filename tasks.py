"""Tasks file to invoke actions on AWS infrastructure."""
import datetime
import json
import os
import pathlib
import sys
import time
from pprint import pprint

import boto3
import botocore
import yaml
from invoke import task

from inspiring_murdock.aws import cloudformation as cf
from inspiring_murdock.aws.util import profile_name, region, to_cf_params
from inspiring_murdock.util import get_config, get_logger

LOGGER = get_logger(
    name="inspiring_murdock", level="DEBUG", filename="logs/inspiring_murdock.log"
)


@task
def is_valid(ctx, cf_name="", profile=None, region="us-east-1", endpoint_url=None):
    """Validate cloudformation template."""
    try:
        cf_path = f"cloudformation/{cf_name}.yaml"
        with open(cf_path) as cf_file:
            result = cf.is_valid(
                profile_name=profile,
                region=region,
                template=json.dumps(yaml.load(cf_file, Loader=yaml.BaseLoader)),
                endpoint_url=endpoint_url,
            )  # The BaseLoader is need to skip converting dates in CF template
            if result:
                LOGGER.info("Template is valid")
            else:
                LOGGER.warning("Template is invalid or something went wrong")
    except botocore.exceptions.ClientError as exp:
        if exp.response.get("Error").get("Code") == "ValidationError":
            LOGGER.error("Unvalid template...")
            LOGGER.error(exp)
        else:
            LOGGER.critical("Something went wrong when validating the template...")
            raise
    except FileNotFoundError:
        LOGGER.error(
            'Cloudformation with "%s" not found on cloudfomation folder...', cf_name
        )


@task
def build_cf(
    ctx,
    cf_name,
    profile=None,
    region="us-east-1",
    disable_rollback=False,
    change_set=False,
    capabilities="CAPABILITY_IAM, CAPABILITY_NAMED_IAM",
    endpoint_url=None,
    wait=False,
):
    """Build cloudformation template."""
    caps = list(map(lambda x: x.strip(), capabilities.split(",")))
    cf_path = f"cloudformation/{cf_name}.yaml"
    cf_params_path = f"cloudformation/parameters/{cf_name}.yaml"
    try:
        sess = boto3.session.Session(profile_name=profile, region_name=region)
        cf.build(
            profile_name=profile,
            region=region,
            stack_name=cf_name,
            template_body=open(cf_path).read(),
            endpoint_url=endpoint_url,
            parameters=to_cf_params(yaml.safe_load(open(cf_params_path))),
            capabilities=caps,
        )
        if wait:
            return wait4cf(
                ctx,
                cf_name,
                profile,
                region,
            )

    except botocore.exceptions.ClientError as exp:
        if exp.response.get("Error").get("Code") == "AlreadyExistsException":
            LOGGER.info(
                "'%s' Stack already exists, use update_stack instead...", cf_name
            )
            LOGGER.info(exp)
            return False

        LOGGER.error("Something went wrong when building the stack")
        raise

    return True


@task
def wait4cf(
    ctx,
    cf_name,
    profile=None,
    region="us-east-1",
    endpoint_url=None,
    sleep_time=15,
    timeout=3600,
):
    """Function to wait for cloudformation to finish."""
    try:
        sess = boto3.session.Session(profile_name=profile, region_name=region)
        start_time = time.time()
        while True:
            status = cf.get_cf_status(sess, cf_name, endpoint_url=endpoint_url)

            if time.time() - start_time >= timeout:
                LOGGER.warning("Waiting for cf status timed out.")
                LOGGER.warning(
                    "latest cf status: %s", status.get("StackStatus", "Unknown")
                )
                raise TimeoutError(
                    "Timedout waiting for CF to finish status(%s)"
                    % status.get("StackStatus", "Unknow")
                )
            elif "_IN_PROGRESS" in status.get("StackStatus"):
                LOGGER.info(
                    "'%s' Current status: '%s'", cf_name, status.get("StackStatus")
                )
                LOGGER.info("Sleeping for %ss", sleep_time)
                time.sleep(sleep_time)
                continue
            else:
                LOGGER.info("Cf status completed")
                LOGGER.info("Status: %s", status.get("StackStatus"))
                LOGGER.info("Status Reason: %s", status.get("StackStatusReason"))
                break
    except botocore.exceptions.ClientError as exp:
        LOGGER.error(
            'Something went wrong while waiting for "%s" to finish building...', cf_name
        )
        LOGGER.exception(exp)
        return False

    return True


@task
def delete_cf(ctx, cf_name, profile=None, region="us-east-1"):

    try:
        sess = boto3.session.Session(profile_name=profile, region_name=region)
        cf.delete(sess, stack_name=cf_name, endpoint_url=None)
    except botocore.exceptions.ClientError as exp:
        LOGGER.error('Something went wrong when deleting "%s"', cf_name)
        LOGGER.error(exp)
    return True


@task
def build(
    ctx,
    stacks="",
    profile=None,
    region="us-east-1",
    disable_rollback=False,
    change_set=False,
    endpoint_url=None,
    config_file=None,
    exclude=None,
    wait=False,
):
    try:
        config = get_config(config_file)
        stacks_order = config.get("stacks_order", [])
        exclude = list(map(lambda x: x.strip(), exclude.split(","))) if exclude else []
        if not stacks:
            for folder, _, filenames in os.walk("./cloudformation"):
                if folder == "./cloudformation":
                    print(filenames)
                    stacks = list(map(lambda x: x.split(".")[0], filenames))
        else:
            stacks = list(map(lambda x: x.strip(), stacks.split(",")))

        for stack in stacks_order:
            if stack in stacks and stack not in exclude:
                result = build_cf(
                    ctx,
                    cf_name=stack,
                    profile=profile,
                    region=region,
                    disable_rollback=disable_rollback,
                    wait=wait,
                )
                if not result:
                    LOGGER.critical('Failed to build stack "%s"', stack)
                    break

    except Exception as exp:
        LOGGER.critical("Unknown issue happened...")
        LOGGER.exception(exp)
        sys.exit(1)


@task
def cf_events(ctx, cf_name, profile=None, region="us-east-1"):
    """Invoke task to print cf stack events."""

    try:
        sess = boto3.session.Session(profile_name=profile, region_name=region)
        result = cf.get_cf_events(sess, cf_name)
        pprint(list(result))
    except botocore.exceptions.ClientError as exp:
        LOGGER.error('Something went wrong when describing "%s" stack events', cf_name)
        LOGGER.exception(exp)
        sys.exit(1)
