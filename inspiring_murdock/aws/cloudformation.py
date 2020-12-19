import sys
import logging
import itertools
import time

from moto import mock_cloudformation


def is_valid(session, template, logger=None):
    """ Function to determine if a stack is valid or not """

    logger = logging.getLogger("inspiring_murdock") if not logger else logger
    cf = session.client("cloudformation")
    try:
        result = cf.validate_template(TemplateBody=template)
    except cf.exceptions.ClientError as exp:
        if (
            exp.response.get("Error").get("Code") == "ValidationError"
        ):  # Going to remove coverage test since coverage can't cover exceptions with if condition
            logger.error("Unvalid template...")
            logger.error(exp)
        else:
            logger.critical("Something went wrong when validating the template...")
            raise
        return False
    return result


def build(
    session,
    stack_name,
    template_body,
    parameters,
    tags=[],
    capabilities=[],
    disable_rollback=False,
    logger=None,
):
    """ Function to build a cloudformation stack """
    cf = session.client("cloudformation")
    logger = logging.getLogger("inspiring_murdock") if not logger else logger
    try:
        result = cf.create_stack(
            TemplateBody=template_body,
            Parameters=parameters,
            StackName=stack_name,
            DisableRollback=disable_rollback,
            Capabilities=capabilities,
            Tags=tags,
        )
    except cf.exceptions.ClientError as exp:
        if exp.response.get("Error").get("Code") == "AlreadyExistsException":
            logger.info(
                "'%s' Stack already exists, use update_stack instead...", stack_name
            )
            logger.info(exp)
            return False

        logger.error("Something went wrong when building the stack")
        raise

    return result


def get_cf_events(session, stack_name, logger=None):
    """ Function that returns cf events """
    logger = logging.getLogger("inspiring_murdock") if not logger else logger
    cf = session.client("cloudformation")
    paginator = cf.get_paginator("describe_stack_events")
    result = []
    try:
        # raise Exception(cf.can_paginate('describe_stack_events'))
        pages = paginator.paginate(StackName=stack_name)
    except cf.exceptions.ClientError as exp:
        logger.error("Something went wrong when waiting for stack status")
        logger.error(exp)
    events = (
        itertools.chain(*map(lambda x: x.get("StackEvents"), pages))
        if pages
        else iter(())
    )
    return events


@mock_cloudformation
def wait4cf(session, stack_name, sleep_time=60, timeout=3600, logger=None):
    """ Function to wait for cloudformation to finish """
    logger = logging.getLogger("inspiring_murdock") if not logger else logger
    start_time = time.time()
    while True:
        events = get_cf_events(session, stack_name, logger=logger)
        try:
            latest_event = next(events)
        except StopIteration:
            latest_event = None

        if not latest_event:
            logger.warning("No events found for %s", stack_name)
            return False

        if time.time() - start_time >= timeout:
            logger.warning("Waiting for cf status timed out.")
            logger.warning(
                "latest cf status: %s", latest_event.get("ResourceStatus", "Unknown")
            )
            raise TimeoutError(
                "Timedout waiting for CF to finish status(%s)"
                % latest_event.get("ResourceStatus", "Unknow")
            )
        elif "_IN_PROGRESS" in latest_event.get("ResourceStatus"):
            logger.info("Current status: '%s'", latest_event.get("ResourceStatus"))
            logger.info("Sleeping for %ss", sleep_time)
            time.sleep(sleep_time)
            continue
        else:
            logger.info("Cf status completed")
            logger.info("Status: %s", latest_event.get("ResourceStatus"))
            break

    return True
