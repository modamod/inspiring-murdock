import sys
import logging


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
            logger.info("'%s' Stack already exists, use update_stack instead...", stack_name)
            logger.info(exp)
            return False

        logger.error("Something went wrong when building the stack")
        raise

    return result


def wait4cf(session, stack_name, logger=None):
    ''' Function to wait for cloudformation to finish '''
    logger = logging.getLogger("inspiring_murdock") if not logger else logger
