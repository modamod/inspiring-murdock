""" Cloudformation module tests """

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import yaml
from botocore import exceptions
from botocore.exceptions import ClientError
from inspiring_murdock.aws.cloudformation import build, is_valid
from inspiring_murdock.aws.util import session, to_cf_params
from inspiring_murdock.util import get_logger
from moto import mock_cloudformation
from io import StringIO
import logging

class PatchSession:
    class Cloudformation:
        exceptions = exceptions

        def validate_template(self, TemplateBody):
            raise ClientError(
                error_response={
                    "Error": {
                        "Code": "Testing",
                        "Message": "This is a testing exception",
                    }
                },
                operation_name="Testing",
            )

        def create_stack(
            self,
            TemplateBody,
            Parameters,
            StackName,
            DisableRollback,
            Capabilities,
            Tags,
        ):
            raise ClientError(
                error_response={
                    "Error": {
                        "Code": "Testing",
                        "Message": "This is a testing exception",
                    }
                },
                operation_name="Testing",
            )

    def client(self, service="cloudformation"):
        return self.Cloudformation()


def patch_validate_template(TemplateBody):  # pylint: disable=unused-argument
    """ Side Effect function used to mock aws cloudformation client validate_template method """

    raise ClientError(
        error_response={
            "Error": {"Code": "Testing", "Message": "This is a testing exception"}
        },
        operation_name="Testing",
    )


@mock_cloudformation
def test_validate_template():
    """ Test function to test validate_template from Cloudfomation invoke module """

    valid_template = open(f"{Path(__file__).parent}/data/valid_template.yaml")
    unvalid_template = open(f"{Path(__file__).parent}/data/unvalid_template.yaml")
    aws_session = session()
    mocked = Mock(
        session,
        side_effect=PatchSession,
    )
    assert is_valid(session=session(), template=valid_template.read())
    assert not is_valid(session=session(), template=unvalid_template.read())
    valid_template.close()
    unvalid_template.close()
    with pytest.raises(
        exceptions.ClientError
    ) as client_exception:  # This is going to raise a ParamValidationError
        with patch.object(
            aws_session.client("cloudformation"),
            "validate_template",
            side_effect=patch_validate_template,
        ):
            valid_template = open(f"{Path(__file__).parent}/data/valid_template.yaml")
            is_valid(session=PatchSession(), template=valid_template.read())
    assert "This is a testing exception" in str(client_exception.value)


@mock_cloudformation
def test_build():
    ''' Test function for build cloudformation task '''
    logger = get_logger()
    try:
        template = open(f"{Path(__file__).parent}/data/sample_template.yaml").read()
        parameters = dict(yaml.safe_load(
            open(f"{Path(__file__).parent}/data/sample_params.yaml")
        ))
    except FileNotFoundError as exp:
        print("File not found", file=sys.stderr)
        pytest.fail(exp)
    except yaml.scanner.ScannerError as yaml_exp:
        print("Malformed yaml file")
        pytest.fail(yaml_exp)
    aws_session = session()
    result = build(
        aws_session,
        "test",
        template,
        to_cf_params(parameters, use_previous=False),
    )
    assert result
    assert result.get("ResponseMetadata").get("HTTPStatusCode") == 200
    with pytest.raises(exceptions.ParamValidationError):
        result = build(
            aws_session, "test", "", to_cf_params(parameters, use_previous=False), logger=logger
        )
    # with patch('sys.stderr', new_callable=StringIO) as fake_out:
    string_stream = StringIO()
    logger.addHandler(logging.StreamHandler(string_stream))
    result = build(
        aws_session,
        "test",
        template,
        to_cf_params(parameters, use_previous=False),
        logger=logger
    )
    assert 'Stack already exists, use update_stack instead...' in string_stream.getvalue()

    with pytest.raises(exceptions.ClientError) as client_exception:
        result = build(
            PatchSession(),
            "test1",
            template,
            to_cf_params(parameters, use_previous=False),
        )
    assert "This is a testing exception" in str(client_exception.value)
