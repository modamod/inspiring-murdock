''' Module holding helper functions and classes to perform unit tests '''

import botocore
import types
from pathlib import Path
import json

class MockClass:
    pass


class PatchSession:
    class Cloudformation:
        exceptions = botocore.exceptions

        def validate_template(self, TemplateBody):
            raise botocore.exceptions.ClientError(
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
            raise botocore.exceptions.ClientError(
                error_response={
                    "Error": {
                        "Code": "Testing",
                        "Message": "This is a testing exception",
                    }
                },
                operation_name="Testing",
            )

        def get_paginator(self, name="describe_stack_events"):
            def paginate(self, StackName):
                with open(f"{Path(__file__).parent}/data/stack_event.json") as fp:
                    return json.load(fp)

            paginator = MockClass()
            paginator.paginate = types.MethodType(paginate, paginator)
            return paginator

    def client(self, service="cloudformation"):
        return self.Cloudformation()


class PatchSessionEmptyEvent(PatchSession):
    class Cloudformation(PatchSession.Cloudformation):

        def get_paginator(self, name="describe_stack_events"):
            def paginate(self, StackName):
                with open(f"{Path(__file__).parent}/data/empty_event.json") as fp:
                    return json.load(fp)

            paginator = MockClass()
            paginator.paginate = types.MethodType(paginate, paginator)
            return paginator

class PatchSessionInProgressEvent(PatchSession):
    class Cloudformation(PatchSession.Cloudformation):
        def get_paginator(self, name="describe_stack_events"):
            def paginate(self, StackName):
                with open(f"{Path(__file__).parent}/data/in_progress_event.json") as fp:
                    return json.load(fp)

            paginator = MockClass()
            paginator.paginate = types.MethodType(paginate, paginator)
            return paginator
