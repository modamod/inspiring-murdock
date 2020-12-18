''' Module to test inspiring_murdock uitl module '''

import logging
import os
from io import StringIO
from unittest.mock import patch

from inspiring_murdock.util import get_logger


def test_get_logger():
    log = get_logger(level='DEBUG', filename="test.log")
    log.critical("This is a test message")
    with open("test.log") as fd:
        assert "This is a test message" in fd.read()

    with patch("sys.stderr", new=StringIO()) as fake_out: # Patching stderr as it is the default destination for the logs.
        log = get_logger(level='DEBUG')
        log.critical("This is a test message")
        string = fake_out.getvalue()
        assert "This is a test message" in string

    # Cleaning up files.
    try:
        os.remove("test.log")
    except FileNotFoundError:
        pass
