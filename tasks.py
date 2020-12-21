""" Tasks file to invoke actions on AWS infrastructure """
from invoke import task
from inspiring_murdock.aws.cloudformation import is_valid as cf_validate, wait4cf
from inspiring_murdock.aws.util import session
from inspiring_murdock.util import get_logger
import sys
import os

LOGGER = get_logger(
    name="inspiring_murdock", level="DEBUG", filename="logs/inspiring_murdock.log"
)


@task
def is_valid(ctx, cf_name="", profile=None, region="us-east-1"):
    """ Validate cloudformation template """
    try:
        # cf_path = f"cloudformation/{cf_name}.yaml"
        with open(cf_path) as cf_file:
            result = cf_validate(session(profile, region), cf_file.read())
            if result:
                LOGGER.info("Template is valid")
            else:
                LOGGER.warning("Template is invalid or something went wrong")
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
    disalbe_rollback=False,
    change_set=False,
):
    """ Build cloudformation template """

    LOGGER.info(cf_name, profile, region)


@task
def delete_cf(ctx, cf_name, profile=None, region="us-east-1"):
    LOGGER.info(cf_name, profile, region)


@task
def build(
    ctx,
    stacks="",
    profile=None,
    region="us-east-1",
    disalbe_rollback=False,
    change_set=False,
):
    if not stacks:
        for _, _, filenames in os.walk("./cloudformation"):
            stacks = list(map(lambda x: x.split(".")[0], filenames))

        LOGGER.info(stacks)
    # stacks = stacks.split(',') if stacks else


@task
def wait(ctx):
    wait4cf(session(), 'test', 1, 10)
